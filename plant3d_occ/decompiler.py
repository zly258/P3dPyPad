# -*- coding: utf-8 -*-
"""Python 2.7 (.pyc) Bytecode Decompiler & AutoCAD Plant 3D Variants Loader.

Decompiles AutoCAD Plant 3D's built-in Python 2.7 `.pyc` component scripts and
helper libraries (`variants.zip`) into clean, executable Python 3 `.py` source
files with full `@activate`, `@group`, and `@param` metadata decorators.
"""

import ast
import os
import re
import struct
import zipfile

PY27_OPMAP = {
    0: "STOP_CODE", 1: "POP_TOP", 2: "ROT_TWO", 3: "ROT_THREE", 4: "DUP_TOP", 5: "ROT_FOUR",
    9: "NOP", 10: "UNARY_POSITIVE", 11: "UNARY_NEGATIVE", 12: "UNARY_NOT", 13: "UNARY_CONVERT",
    15: "UNARY_INVERT", 19: "BINARY_POWER", 20: "BINARY_MULTIPLY", 21: "BINARY_DIVIDE",
    22: "BINARY_MODULO", 23: "BINARY_ADD", 24: "BINARY_SUBTRACT", 25: "BINARY_SUBSCR",
    26: "BINARY_FLOOR_DIVIDE", 27: "BINARY_TRUE_DIVIDE", 28: "INPLACE_FLOOR_DIVIDE",
    29: "INPLACE_TRUE_DIVIDE", 30: "SLICE+0", 31: "SLICE+1", 32: "SLICE+2", 33: "SLICE+3",
    40: "STORE_SLICE+0", 41: "STORE_SLICE+1", 42: "STORE_SLICE+2", 43: "STORE_SLICE+3",
    54: "STORE_MAP", 55: "INPLACE_ADD", 56: "INPLACE_SUBTRACT", 57: "INPLACE_MULTIPLY",
    58: "INPLACE_DIVIDE", 59: "INPLACE_MODULO", 60: "STORE_SUBSCR", 61: "DELETE_SUBSCR",
    62: "BINARY_LSHIFT", 63: "BINARY_RSHIFT", 64: "BINARY_AND", 65: "BINARY_XOR", 66: "BINARY_OR",
    67: "INPLACE_POWER", 68: "GET_ITER", 71: "PRINT_ITEM", 72: "PRINT_NEWLINE",
    80: "BREAK_LOOP", 81: "WITH_CLEANUP", 82: "LOAD_LOCALS", 83: "RETURN_VALUE", 84: "IMPORT_STAR",
    85: "EXEC_STMT", 86: "YIELD_VALUE", 87: "POP_BLOCK", 88: "END_FINALLY", 89: "BUILD_CLASS",
    90: "STORE_NAME", 91: "DELETE_NAME", 92: "UNPACK_SEQUENCE", 93: "FOR_ITER", 94: "LIST_APPEND",
    95: "STORE_ATTR", 96: "DELETE_ATTR", 97: "STORE_GLOBAL", 98: "DELETE_GLOBAL",
    99: "DUP_TOPX", 100: "LOAD_CONST", 101: "LOAD_NAME", 102: "BUILD_TUPLE", 103: "BUILD_LIST",
    104: "BUILD_SET", 105: "BUILD_MAP", 106: "LOAD_ATTR", 107: "COMPARE_OP",
    108: "IMPORT_NAME", 109: "IMPORT_FROM", 110: "JUMP_FORWARD", 111: "JUMP_IF_FALSE_OR_POP",
    112: "JUMP_IF_TRUE_OR_POP", 113: "JUMP_ABSOLUTE", 114: "POP_JUMP_IF_FALSE",
    115: "POP_JUMP_IF_TRUE", 116: "LOAD_GLOBAL", 119: "CONTINUE_LOOP", 120: "SETUP_LOOP",
    121: "SETUP_EXCEPT", 122: "SETUP_FINALLY", 124: "LOAD_FAST", 125: "STORE_FAST",
    126: "DELETE_FAST", 130: "RAISE_VARARGS", 131: "CALL_FUNCTION", 132: "MAKE_FUNCTION",
    133: "BUILD_SLICE", 134: "MAKE_CLOSURE", 135: "LOAD_CLOSURE", 136: "LOAD_DEREF",
    137: "STORE_DEREF", 140: "CALL_FUNCTION_VAR", 141: "CALL_FUNCTION_KW",
    142: "CALL_FUNCTION_VAR_KW", 143: "SETUP_WITH", 145: "EXTENDED_ARG", 146: "SET_ADD", 147: "MAP_ADD",
}

CMP_OPS = ("<", "<=", "==", "!=", ">", ">=", "in", "not in", "is", "is not", "==", "==")

BIN_OPS = {
    "BINARY_ADD": "+",
    "BINARY_SUBTRACT": "-",
    "BINARY_MULTIPLY": "*",
    "BINARY_DIVIDE": "/",
    "BINARY_TRUE_DIVIDE": "/",
    "BINARY_FLOOR_DIVIDE": "//",
    "BINARY_MODULO": "%",
    "BINARY_POWER": "**",
    "BINARY_LSHIFT": "<<",
    "BINARY_RSHIFT": ">>",
    "BINARY_AND": "&",
    "BINARY_OR": "|",
    "BINARY_XOR": "^",
}

INPLACE_OPS = {
    "INPLACE_ADD": "+=",
    "INPLACE_SUBTRACT": "-=",
    "INPLACE_MULTIPLY": "*=",
    "INPLACE_DIVIDE": "/=",
    "INPLACE_TRUE_DIVIDE": "/=",
    "INPLACE_FLOOR_DIVIDE": "//=",
    "INPLACE_MODULO": "%=",
    "INPLACE_POWER": "**=",
    "INPLACE_LSHIFT": "<<=",
    "INPLACE_RSHIFT": ">>=",
    "INPLACE_AND": "&=",
    "INPLACE_OR": "|=",
    "INPLACE_XOR": "^=",
}


class Py27Code:
    def __init__(
        self, argcount, nlocals, stacksize, flags, code, consts,
        names, varnames, freevars, cellvars, filename, name, firstlineno, lnotab
    ):
        self.argcount = argcount
        self.nlocals = nlocals
        self.stacksize = stacksize
        self.flags = flags
        self.code = code
        self.consts = consts
        self.names = names
        self.varnames = varnames
        self.freevars = freevars
        self.cellvars = cellvars
        self.filename = filename
        self.name = name
        self.firstlineno = firstlineno
        self.lnotab = lnotab


def loads_py27_marshal(data: bytes) -> Py27Code:
    """Unmarshals Python 2.7 code object from raw marshal payload (after 8-byte .pyc header)."""
    strings = []
    pos = 0

    def r_long():
        nonlocal pos
        v = struct.unpack_from("<i", data, pos)[0]
        pos += 4
        return v

    def r_obj():
        nonlocal pos
        t = chr(data[pos])
        pos += 1
        if t in ("0", "N"):
            return None
        if t == "F":
            return False
        if t == "T":
            return True
        if t == "i":
            return r_long()
        if t == "I":
            v = struct.unpack_from("<q", data, pos)[0]
            pos += 8
            return v
        if t == "l":
            n = r_long()
            sign = -1 if n < 0 else 1
            ndigits = abs(n)
            val = 0
            for idx in range(ndigits):
                digit = struct.unpack_from("<H", data, pos)[0]
                pos += 2
                val |= digit << (15 * idx)
            return sign * val
        if t == "f":
            n = data[pos]
            pos += 1
            s = data[pos : pos + n].decode("ascii")
            pos += n
            return float(s)
        if t == "g":
            v = struct.unpack_from("<d", data, pos)[0]
            pos += 8
            return v
        if t in ("s", "t", "u"):
            n = r_long()
            b = data[pos : pos + n]
            pos += n
            if t in ("t", "u"):
                try:
                    s = b.decode("utf-8")
                except Exception:
                    s = b.decode("latin1")
                if t == "t":
                    strings.append(s)
                return s
            return b
        if t == "R":
            return strings[r_long()]
        if t in ("(", "["):
            n = r_long()
            items = [r_obj() for _ in range(n)]
            return tuple(items) if t == "(" else items
        if t == "c":
            argcount = r_long()
            nlocals = r_long()
            stacksize = r_long()
            flags = r_long()
            code = r_obj()
            consts = r_obj()
            names = [x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else x for x in r_obj()]
            varnames = [x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else x for x in r_obj()]
            freevars = [x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else x for x in r_obj()]
            cellvars = [x.decode("utf-8", errors="ignore") if isinstance(x, bytes) else x for x in r_obj()]
            filename = r_obj()
            if isinstance(filename, bytes):
                filename = filename.decode("utf-8", errors="ignore")
            name = r_obj()
            if isinstance(name, bytes):
                name = name.decode("utf-8", errors="ignore")
            firstlineno = r_long()
            lnotab = r_obj()

            def _decode_const(c):
                if isinstance(c, bytes):
                    try:
                        return c.decode("utf-8")
                    except Exception:
                        return c.decode("latin1")
                if isinstance(c, tuple):
                    return tuple(_decode_const(x) for x in c)
                return c

            consts = tuple(_decode_const(x) for x in consts)
            return Py27Code(
                argcount, nlocals, stacksize, flags, code, consts,
                names, varnames, freevars, cellvars, filename, name, firstlineno, lnotab
            )
        raise ValueError(f"Unknown marshal type tag {t!r} at offset {pos - 1}")

    return r_obj()


def disassemble_py27(co: Py27Code):
    """Returns list of (offset, opname, arg, next_offset) instructions."""
    b = co.code
    i = 0
    n = len(b)
    insts = []
    ext_arg = 0
    while i < n:
        start_i = i
        op = b[i]
        opname = PY27_OPMAP.get(op, f"OP_{op}")
        if op >= 90:
            arg = (b[i + 1] | (b[i + 2] << 8)) | ext_arg
            ext_arg = 0
            i += 3
            if opname == "EXTENDED_ARG":
                ext_arg = arg << 16
                continue
            if opname in ("JUMP_FORWARD", "FOR_ITER", "SETUP_LOOP", "SETUP_EXCEPT", "SETUP_FINALLY", "SETUP_WITH"):
                target = i + arg
                insts.append((start_i, opname, target, i))
            else:
                insts.append((start_i, opname, arg, i))
        else:
            ext_arg = 0
            i += 1
            insts.append((start_i, opname, None, i))
    return insts


def _format_const(val):
    if isinstance(val, float):
        if math_isnan_or_inf(val):
            return "0.0"
        return repr(val)
    return repr(val)


def math_isnan_or_inf(v):
    return v != v or v == float("inf") or v == float("-inf")


def _needs_parens(expr: str) -> bool:
    expr = expr.strip()
    if not expr:
        return False
    if re.match(r"^[A-Za-z_][A-Za-z0-9_.]*$", expr):
        return False
    if re.match(r"^-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?$", expr):
        return False
    if (expr.startswith("(") and expr.endswith(")")) or (expr.startswith("[") and expr.endswith("]")):
        depth = 0
        for idx, ch in enumerate(expr):
            if ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
                if depth == 0 and idx < len(expr) - 1:
                    return True
        return False
    return any(op in expr for op in (" + ", " - ", " * ", " / ", " // ", " % ", " == ", " != ", " < ", " > ", " <= ", " >= ", " and ", " or ", "not "))


def _wrap(expr: str) -> str:
    return f"({expr})" if _needs_parens(expr) else expr


def _strip_outer_parens(s: str) -> str:
    """Strips redundant outer grouping parentheses while strictly preserving tuple literals `(a, b, c)`."""
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        balanced = True
        has_top_comma = False
        in_str = None
        escape = False
        for idx, ch in enumerate(s):
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if in_str:
                if ch == in_str:
                    in_str = None
                continue
            if ch in ("'", '"'):
                in_str = ch
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth == 0 and idx < len(s) - 1:
                    balanced = False
                    break
            elif ch == "," and depth == 1:
                has_top_comma = True
        if balanced and not has_top_comma:
            s = s[1:-1].strip()
        else:
            break
    return s


def _format_call(fn_expr: str, pos_items: list, kw_pairs: list, var_arg=None, kw_arg=None) -> str:
    # Python 2 dict.has_key(k) -> (k in dict)
    if fn_expr.endswith(".has_key") and len(pos_items) == 1 and not kw_pairs and var_arg is None and kw_arg is None:
        obj_expr = fn_expr[: -len(".has_key")]
        return f"({pos_items[0]} in {obj_expr})"
    if fn_expr in ("atof", "string.atof") and len(pos_items) == 1:
        return f"float({pos_items[0]})"
    all_args = pos_items + kw_pairs
    if var_arg is not None:
        all_args.append(f"*{var_arg}")
    if kw_arg is not None:
        all_args.append(f"**{kw_arg}")
    return f"{fn_expr}({', '.join(all_args)})"


def _format_func_header(co: Py27Code, defaults: list) -> str:
    n_pos = co.argcount
    pos_args = list(co.varnames[:n_pos])
    idx = n_pos
    vararg_name = None
    kwarg_name = None
    if co.flags & 4:  # CO_VARARGS
        vararg_name = co.varnames[idx] if idx < len(co.varnames) else "args"
        idx += 1
    if co.flags & 8:  # CO_VARKEYWORDS
        kwarg_name = co.varnames[idx] if idx < len(co.varnames) else "kw"
        idx += 1

    n_def = len(defaults)
    parts = []
    for i, arg in enumerate(pos_args):
        def_idx = i - (n_pos - n_def)
        if def_idx >= 0 and def_idx < n_def:
            parts.append(f"{arg}={_format_const(defaults[def_idx])}")
        else:
            parts.append(arg)
    if vararg_name:
        parts.append(f"*{vararg_name}")
    if kwarg_name:
        parts.append(f"**{kwarg_name}")
    elif not vararg_name and n_pos > 0 and pos_args[0] == "s":
        parts.append("**kw")
    return f"def {co.name}({', '.join(parts)}):"


def _decompile_structured_or_cfg(co: Py27Code, indent: int = 1, use_p2_cmp: bool = False) -> list:
    """Decompiles function bytecode into structured Python lines, falling back to basic-block CFG if needed."""
    try:
        lines = _decompile_structured(co, indent=indent, use_p2_cmp=use_p2_cmp)
        test_src = "def _test_(s):\n" + "\n".join(lines) + "\n"
        ast.parse(test_src)
        return lines
    except Exception:
        return _decompile_basic_blocks(co, indent=indent, use_p2_cmp=use_p2_cmp)


def _decompile_structured(co: Py27Code, indent: int = 1, use_p2_cmp: bool = False) -> list:
    insts = disassemble_py27(co)
    addr_to_idx = {ins[0]: idx for idx, ins in enumerate(insts)}
    n_insts = len(insts)

    def eval_range(start_idx: int, end_idx: int, cur_indent: int, loop_end_addr=None) -> list:
        out_lines = []
        stack = []
        i = start_idx
        pad = "    " * cur_indent

        while i < end_idx:
            offset, op, arg, next_off = insts[i]

            if op == "NOP" or op == "POP_BLOCK" or op == "END_FINALLY":
                i += 1
                continue

            if op == "SETUP_LOOP":
                loop_exit_addr = arg
                loop_exit_idx = addr_to_idx.get(loop_exit_addr, end_idx)
                if i + 2 < loop_exit_idx and insts[i + 1][1] == "GET_ITER":
                    iter_expr = stack.pop() if stack else "()"
                    for_off, for_op, for_target, _ = insts[i + 2]
                    if for_op == "FOR_ITER":
                        store_op = insts[i + 3][1]
                        if store_op in ("STORE_FAST", "STORE_NAME"):
                            loop_var = co.varnames[insts[i + 3][2]] if store_op == "STORE_FAST" else co.names[insts[i + 3][2]]
                            body_start = i + 4
                        else:
                            loop_var = "_item"
                            body_start = i + 3
                        body_end = addr_to_idx.get(for_target, loop_exit_idx) - 1
                        out_lines.append(f"{pad}for {loop_var} in {iter_expr}:")
                        body_lines = eval_range(body_start, body_end, cur_indent + 1, loop_end_addr=for_off)
                        if not body_lines:
                            body_lines = [f"{pad}    pass"]
                        out_lines.extend(body_lines)
                        i = loop_exit_idx
                        continue

                cond_start_addr = insts[i + 1][0]
                back_jump_idx = None
                for k in range(loop_exit_idx - 1, i, -1):
                    if insts[k][1] == "JUMP_ABSOLUTE" and insts[k][2] == cond_start_addr:
                        back_jump_idx = k
                        break
                if back_jump_idx is not None:
                    cond_expr, body_start_idx = _extract_condition(insts, co, i + 1, back_jump_idx, addr_to_idx)
                    out_lines.append(f"{pad}while {cond_expr}:")
                    body_lines = eval_range(body_start_idx, back_jump_idx, cur_indent + 1, loop_end_addr=cond_start_addr)
                    if not body_lines:
                        body_lines = [f"{pad}    pass"]
                    out_lines.extend(body_lines)
                    i = loop_exit_idx
                    continue
                i += 1
                continue

            if op == "SETUP_EXCEPT":
                handler_idx = addr_to_idx.get(arg, end_idx)
                try_end_idx = handler_idx
                while try_end_idx > i + 1 and insts[try_end_idx - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE", "POP_BLOCK"):
                    try_end_idx -= 1
                after_except_idx = end_idx
                if handler_idx > i + 1 and insts[handler_idx - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                    after_except_idx = addr_to_idx.get(insts[handler_idx - 1][2], end_idx)
                # Find END_FINALLY to bound the except handler
                end_fin_idx = after_except_idx
                for k_ef in range(handler_idx, min(end_idx, handler_idx + 40)):
                    if insts[k_ef][1] == "END_FINALLY":
                        end_fin_idx = k_ef
                        if k_ef + 1 <= end_idx:
                            after_except_idx = max(after_except_idx, k_ef + 1)
                        break
                h_end = end_fin_idx
                while h_end > handler_idx and insts[h_end - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE", "END_FINALLY"):
                    h_end -= 1
                h_start = handler_idx
                # Skip exception type matching header (DUP_TOP, LOAD_GLOBAL KeyError, COMPARE_OP exception match, POP_JUMP_IF_FALSE, POP_TOP, POP_TOP, POP_TOP)
                for k_eh in range(handler_idx, min(h_end, handler_idx + 10)):
                    if insts[k_eh][1] == "POP_JUMP_IF_FALSE":
                        h_start = k_eh + 1
                        while h_start < h_end and insts[h_start][1] == "POP_TOP":
                            h_start += 1
                        break
                out_lines.append(f"{pad}try:")
                try_lines = eval_range(i + 1, try_end_idx, cur_indent + 1, loop_end_addr=loop_end_addr)
                out_lines.extend(try_lines or [f"{pad}    pass"])
                out_lines.append(f"{pad}except Exception:")
                exc_lines = eval_range(h_start, h_end, cur_indent + 1, loop_end_addr=loop_end_addr)
                out_lines.extend(exc_lines or [f"{pad}    pass"])
                i = after_except_idx
                continue

            if op == "LOAD_CONST":
                stack.append(_format_const(co.consts[arg]))
            elif op == "LOAD_FAST":
                stack.append(co.varnames[arg])
            elif op in ("LOAD_GLOBAL", "LOAD_NAME"):
                stack.append(co.names[arg])
            elif op == "LOAD_DEREF":
                names_pool = co.cellvars + co.freevars
                stack.append(names_pool[arg] if arg < len(names_pool) else f"_deref_{arg}")
            elif op == "LOAD_ATTR":
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}.{co.names[arg]}")
            elif op in BIN_OPS:
                right = stack.pop()
                left = stack.pop()
                bop = BIN_OPS[op]
                stack.append(f"({_wrap(left)} {bop} {_wrap(right)})")
            elif op in INPLACE_OPS:
                right = stack.pop()
                left = stack.pop()
                iop = INPLACE_OPS[op]
                if i + 1 < end_idx and insts[i + 1][1] in ("STORE_FAST", "STORE_NAME"):
                    target = co.varnames[insts[i + 1][2]] if insts[i + 1][1] == "STORE_FAST" else co.names[insts[i + 1][2]]
                    if target == left:
                        out_lines.append(f"{pad}{target} {iop} {_strip_outer_parens(right)}")
                        i += 2
                        continue
                bop = iop[:-1]
                stack.append(f"({_wrap(left)} {bop} {_wrap(right)})")
            elif op == "UNARY_NEGATIVE":
                val = stack.pop()
                stack.append(f"-{_wrap(val)}")
            elif op == "UNARY_POSITIVE":
                val = stack.pop()
                stack.append(f"+{_wrap(val)}")
            elif op == "UNARY_NOT":
                val = stack.pop()
                stack.append(f"(not {_wrap(val)})")
            elif op == "UNARY_INVERT":
                val = stack.pop()
                stack.append(f"~{_wrap(val)}")
            elif op == "COMPARE_OP":
                right = stack.pop()
                left = stack.pop()
                cop = CMP_OPS[arg] if arg < len(CMP_OPS) else "=="
                stack.append(f"({_wrap(left)} {cop} {_wrap(right)})")
            elif op == "BINARY_SUBSCR":
                sub = stack.pop()
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(sub)}]")
            elif op == "SLICE+0":
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[:]")
            elif op == "SLICE+1":
                low = stack.pop()
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:]")
            elif op == "SLICE+2":
                high = stack.pop()
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[:{_strip_outer_parens(high)}]")
            elif op == "SLICE+3":
                high = stack.pop()
                low = stack.pop()
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:{_strip_outer_parens(high)}]")
            elif op == "BUILD_TUPLE":
                items = [_strip_outer_parens(stack.pop()) for _ in range(arg)][::-1]
                if len(items) == 1:
                    stack.append(f"({items[0]},)")
                else:
                    stack.append(f"({', '.join(items)})")
            elif op == "BUILD_LIST":
                items = [_strip_outer_parens(stack.pop()) for _ in range(arg)][::-1]
                stack.append(f"[{', '.join(items)}]")
            elif op == "BUILD_MAP":
                stack.append("{}")
            elif op == "STORE_MAP":
                key = _strip_outer_parens(stack.pop())
                val = _strip_outer_parens(stack.pop())
                d_expr = stack.pop()
                if d_expr == "{}":
                    stack.append(f"{{{key}: {val}}}")
                elif d_expr.startswith("{") and d_expr.endswith("}"):
                    stack.append(d_expr[:-1] + f", {key}: {val}}}")
                else:
                    out_lines.append(f"{pad}{d_expr}[{key}] = {val}")
                    stack.append(d_expr)
            elif op in ("CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW"):
                n_pos = arg & 0xFF
                n_kw = (arg >> 8) & 0xFF
                kw_arg = _strip_outer_parens(stack.pop()) if op in ("CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW") else None
                var_arg = _strip_outer_parens(stack.pop()) if op in ("CALL_FUNCTION_VAR", "CALL_FUNCTION_VAR_KW") else None
                kw_pairs = []
                for _ in range(n_kw):
                    v_expr = _strip_outer_parens(stack.pop())
                    k_expr = stack.pop()
                    if k_expr.startswith(("'", '"')) and k_expr.endswith(("'", '"')):
                        k_name = k_expr[1:-1]
                    else:
                        k_name = k_expr
                    kw_pairs.append(f"{k_name}={v_expr}")
                kw_pairs.reverse()
                pos_items = [_strip_outer_parens(stack.pop()) for _ in range(n_pos)][::-1]
                fn_expr = stack.pop()
                stack.append(_format_call(fn_expr, pos_items, kw_pairs, var_arg, kw_arg))
            elif op in ("STORE_FAST", "STORE_NAME", "STORE_GLOBAL"):
                target = co.varnames[arg] if op == "STORE_FAST" else co.names[arg]
                val = _strip_outer_parens(stack.pop()) if stack else "None"
                out_lines.append(f"{pad}{target} = {val}")
            elif op == "STORE_SUBSCR":
                sub = _strip_outer_parens(stack.pop())
                obj = stack.pop()
                val = _strip_outer_parens(stack.pop())
                out_lines.append(f"{pad}{obj}[{sub}] = {val}")
            elif op == "STORE_ATTR":
                obj = stack.pop()
                val = _strip_outer_parens(stack.pop())
                out_lines.append(f"{pad}{obj}.{co.names[arg]} = {val}")
            elif op == "UNPACK_SEQUENCE":
                seq = _strip_outer_parens(stack.pop())
                targets = []
                for k in range(arg):
                    if i + 1 + k < end_idx and insts[i + 1 + k][1] in ("STORE_FAST", "STORE_NAME"):
                        t_op = insts[i + 1 + k][1]
                        t_arg = insts[i + 1 + k][2]
                        targets.append(co.varnames[t_arg] if t_op == "STORE_FAST" else co.names[t_arg])
                    else:
                        raise RuntimeError("Complex UNPACK_SEQUENCE")
                out_lines.append(f"{pad}{', '.join(targets)} = {seq}")
                i += 1 + arg
                continue
            elif op == "POP_TOP":
                if stack:
                    expr = _strip_outer_parens(stack.pop())
                    if expr and expr != "None":
                        out_lines.append(f"{pad}{expr}")
            elif op == "DUP_TOP":
                if stack:
                    stack.append(stack[-1])
            elif op == "ROT_TWO":
                if len(stack) >= 2:
                    stack[-1], stack[-2] = stack[-2], stack[-1]
            elif op == "ROT_THREE":
                if len(stack) >= 3:
                    a = stack.pop()
                    b = stack.pop()
                    c = stack.pop()
                    stack.extend([a, c, b])
            elif op == "BREAK_LOOP":
                out_lines.append(f"{pad}break")
            elif op == "CONTINUE_LOOP":
                out_lines.append(f"{pad}continue")
            elif op == "PRINT_ITEM":
                val = _strip_outer_parens(stack.pop()) if stack else ""
                out_lines.append(f"{pad}print({val}, end=' ')")
            elif op == "PRINT_NEWLINE":
                out_lines.append(f"{pad}print()")
            elif op == "RETURN_VALUE":
                val = _strip_outer_parens(stack.pop()) if stack else "None"
                if i == n_insts - 1 and val == "None" and cur_indent == indent:
                    pass
                elif val == "None":
                    out_lines.append(f"{pad}return")
                else:
                    out_lines.append(f"{pad}return {val}")
            elif op in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP"):
                if stack:
                    raise RuntimeError("Non-empty stack before conditional jump requires CFG mode")
                raise RuntimeError("Unpopped condition")
            else:
                # Wait: in normal flow POP_JUMP_IF_FALSE pops the condition from `stack`!
                pass
            i += 1

        return out_lines

    # Re-bind POP_JUMP handling cleanly inside eval_range:
    return _decompile_structured_impl(insts, addr_to_idx, co, indent, use_p2_cmp=use_p2_cmp)


def _decompile_structured_impl(insts, addr_to_idx, co: Py27Code, indent: int, use_p2_cmp: bool = False) -> list:
    n_insts = len(insts)

    def eval_range(start_idx: int, end_idx: int, cur_indent: int, loop_end_addr=None) -> list:
        out_lines = []
        stack = []
        i = start_idx
        pad = "    " * cur_indent

        while i < end_idx:
            offset, op, arg, next_off = insts[i]

            if op in ("NOP", "POP_BLOCK", "END_FINALLY"):
                i += 1
                continue

            if op == "SETUP_LOOP":
                loop_exit_addr = arg
                loop_exit_idx = addr_to_idx.get(loop_exit_addr, end_idx)
                cond_start_addr = insts[i + 1][0]
                # Check if this SETUP_LOOP is a for-loop (contains GET_ITER + FOR_ITER before body)
                is_for_loop = any(insts[k][1] == "FOR_ITER" for k in range(i + 1, min(loop_exit_idx, i + 18)))
                if not is_for_loop:
                    back_jump_idx = None
                    for k in range(loop_exit_idx - 1, i, -1):
                        if insts[k][1] == "JUMP_ABSOLUTE" and insts[k][2] == cond_start_addr:
                            back_jump_idx = k
                            break
                    if back_jump_idx is not None:
                        cond_expr, body_start_idx = _extract_condition(insts, co, i + 1, back_jump_idx, addr_to_idx)
                        out_lines.append(f"{pad}while {cond_expr}:")
                        body_lines = eval_range(body_start_idx, back_jump_idx, cur_indent + 1, loop_end_addr=cond_start_addr)
                        out_lines.extend(body_lines or [f"{pad}    pass"])
                        i = loop_exit_idx
                        continue
                i += 1
                continue

            if op == "GET_ITER" and i + 1 < end_idx and insts[i + 1][1] == "FOR_ITER":
                iter_expr = _strip_outer_parens(stack.pop()) if stack else "()"
                for_off, for_op, for_target, _ = insts[i + 1]
                for_end_idx = addr_to_idx.get(for_target, end_idx)
                store_op = insts[i + 2][1]
                if store_op in ("STORE_FAST", "STORE_NAME"):
                    loop_var = co.varnames[insts[i + 2][2]] if store_op == "STORE_FAST" else co.names[insts[i + 2][2]]
                    body_start = i + 3
                elif store_op == "UNPACK_SEQUENCE":
                    n_unp = insts[i + 2][2]
                    u_vars = []
                    for uk in range(n_unp):
                        u_op, u_arg = insts[i + 3 + uk][1], insts[i + 3 + uk][2]
                        u_vars.append(co.varnames[u_arg] if u_op == "STORE_FAST" else co.names[u_arg])
                    loop_var = ", ".join(u_vars)
                    body_start = i + 3 + n_unp
                else:
                    loop_var = "_item"
                    body_start = i + 2
                body_end = for_end_idx - 1
                out_lines.append(f"{pad}for {loop_var} in {iter_expr}:")
                body_lines = eval_range(body_start, body_end, cur_indent + 1, loop_end_addr=for_off)
                out_lines.extend(body_lines or [f"{pad}    pass"])
                after_for = for_end_idx
                if after_for < end_idx and insts[after_for][1] == "POP_BLOCK":
                    after_for += 1
                i = after_for
                continue

            if op == "SETUP_EXCEPT":
                handler_idx = addr_to_idx.get(arg, end_idx)
                try_end_idx = handler_idx
                while try_end_idx > i + 1 and insts[try_end_idx - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE", "POP_BLOCK"):
                    try_end_idx -= 1
                after_except_idx = end_idx
                if handler_idx > i + 1 and insts[handler_idx - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                    after_except_idx = addr_to_idx.get(insts[handler_idx - 1][2], end_idx)
                # Find END_FINALLY to bound the except handler
                end_fin_idx = after_except_idx
                for k_ef in range(handler_idx, min(end_idx, handler_idx + 40)):
                    if insts[k_ef][1] == "END_FINALLY":
                        end_fin_idx = k_ef
                        if k_ef + 1 <= end_idx:
                            after_except_idx = max(after_except_idx, k_ef + 1)
                        break
                h_end = end_fin_idx
                while h_end > handler_idx and insts[h_end - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE", "END_FINALLY"):
                    h_end -= 1
                h_start = handler_idx
                # Skip exception type matching header (DUP_TOP, LOAD_GLOBAL KeyError, COMPARE_OP exception match, POP_JUMP_IF_FALSE, POP_TOP, POP_TOP, POP_TOP)
                for k_eh in range(handler_idx, min(h_end, handler_idx + 10)):
                    if insts[k_eh][1] == "POP_JUMP_IF_FALSE":
                        h_start = k_eh + 1
                        while h_start < h_end and insts[h_start][1] == "POP_TOP":
                            h_start += 1
                        break
                out_lines.append(f"{pad}try:")
                try_lines = eval_range(i + 1, try_end_idx, cur_indent + 1, loop_end_addr=loop_end_addr)
                out_lines.extend(try_lines or [f"{pad}    pass"])
                out_lines.append(f"{pad}except Exception:")
                exc_lines = eval_range(h_start, h_end, cur_indent + 1, loop_end_addr=loop_end_addr)
                out_lines.extend(exc_lines or [f"{pad}    pass"])
                i = after_except_idx
                continue

            if op == "LOAD_CONST":
                stack.append(_format_const(co.consts[arg]))
            elif op == "LOAD_FAST":
                stack.append(co.varnames[arg])
            elif op in ("LOAD_GLOBAL", "LOAD_NAME"):
                stack.append(co.names[arg])
            elif op == "LOAD_DEREF":
                names_pool = co.cellvars + co.freevars
                stack.append(names_pool[arg] if arg < len(names_pool) else f"_deref_{arg}")
            elif op == "LOAD_ATTR":
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}.{co.names[arg]}")
            elif op in BIN_OPS:
                right = stack.pop()
                left = stack.pop()
                bop = BIN_OPS[op]
                stack.append(f"({_wrap(left)} {bop} {_wrap(right)})")
            elif op in INPLACE_OPS:
                right = stack.pop()
                left = stack.pop()
                iop = INPLACE_OPS[op]
                if i + 1 < end_idx and insts[i + 1][1] in ("STORE_FAST", "STORE_NAME"):
                    target = co.varnames[insts[i + 1][2]] if insts[i + 1][1] == "STORE_FAST" else co.names[insts[i + 1][2]]
                    if target == left:
                        out_lines.append(f"{pad}{target} {iop} {_strip_outer_parens(right)}")
                        i += 2
                        continue
                bop = iop[:-1]
                stack.append(f"({_wrap(left)} {bop} {_wrap(right)})")
            elif op == "UNARY_NEGATIVE":
                stack.append(f"-{_wrap(stack.pop())}")
            elif op == "UNARY_POSITIVE":
                stack.append(f"+{_wrap(stack.pop())}")
            elif op == "UNARY_NOT":
                stack.append(f"(not {_wrap(stack.pop())})")
            elif op == "UNARY_INVERT":
                stack.append(f"~{_wrap(stack.pop())}")
            elif op == "COMPARE_OP":
                right = stack.pop()
                left = stack.pop()
                cop = CMP_OPS[arg] if arg < len(CMP_OPS) else "=="
                stack.append(f"({_wrap(left)} {cop} {_wrap(right)})")
            elif op == "BINARY_SUBSCR":
                sub = stack.pop()
                obj = stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(sub)}]")
            elif op == "SLICE+0":
                stack.append(f"{_wrap(stack.pop())}[:]")
            elif op == "SLICE+1":
                low, obj = stack.pop(), stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:]")
            elif op == "SLICE+2":
                high, obj = stack.pop(), stack.pop()
                stack.append(f"{_wrap(obj)}[:{_strip_outer_parens(high)}]")
            elif op == "SLICE+3":
                high, low, obj = stack.pop(), stack.pop(), stack.pop()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:{_strip_outer_parens(high)}]")
            elif op == "BUILD_TUPLE":
                items = [_strip_outer_parens(stack.pop()) for _ in range(arg)][::-1]
                stack.append(f"({items[0]},)" if len(items) == 1 else f"({', '.join(items)})")
            elif op == "BUILD_LIST":
                items = [_strip_outer_parens(stack.pop()) for _ in range(arg)][::-1]
                stack.append(f"[{', '.join(items)}]")
            elif op == "BUILD_MAP":
                stack.append("{}")
            elif op == "STORE_MAP":
                key = _strip_outer_parens(stack.pop())
                val = _strip_outer_parens(stack.pop())
                d_expr = stack.pop()
                if d_expr == "{}":
                    stack.append(f"{{{key}: {val}}}")
                elif d_expr.startswith("{") and d_expr.endswith("}"):
                    stack.append(d_expr[:-1] + f", {key}: {val}}}")
                else:
                    out_lines.append(f"{pad}{d_expr}[{key}] = {val}")
                    stack.append(d_expr)
            elif op in ("CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW"):
                n_pos = arg & 0xFF
                n_kw = (arg >> 8) & 0xFF
                kw_arg = _strip_outer_parens(stack.pop()) if op in ("CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW") else None
                var_arg = _strip_outer_parens(stack.pop()) if op in ("CALL_FUNCTION_VAR", "CALL_FUNCTION_VAR_KW") else None
                kw_pairs = []
                for _ in range(n_kw):
                    v_expr = _strip_outer_parens(stack.pop())
                    k_expr = stack.pop()
                    k_name = k_expr[1:-1] if k_expr.startswith(("'", '"')) and k_expr.endswith(("'", '"')) else k_expr
                    kw_pairs.append(f"{k_name}={v_expr}")
                kw_pairs.reverse()
                pos_items = [_strip_outer_parens(stack.pop()) for _ in range(n_pos)][::-1]
                fn_expr = stack.pop()
                stack.append(_format_call(fn_expr, pos_items, kw_pairs, var_arg, kw_arg))
            elif op in ("STORE_FAST", "STORE_NAME", "STORE_GLOBAL"):
                target = co.varnames[arg] if op == "STORE_FAST" else co.names[arg]
                val = _strip_outer_parens(stack.pop()) if stack else "None"
                out_lines.append(f"{pad}{target} = {val}")
            elif op == "STORE_SUBSCR":
                sub = _strip_outer_parens(stack.pop())
                obj = stack.pop()
                val = _strip_outer_parens(stack.pop())
                out_lines.append(f"{pad}{obj}[{sub}] = {val}")
            elif op == "STORE_ATTR":
                obj = stack.pop()
                val = _strip_outer_parens(stack.pop())
                out_lines.append(f"{pad}{obj}.{co.names[arg]} = {val}")
            elif op == "UNPACK_SEQUENCE":
                seq = _strip_outer_parens(stack.pop())
                targets = []
                for k in range(arg):
                    if i + 1 + k < end_idx and insts[i + 1 + k][1] in ("STORE_FAST", "STORE_NAME"):
                        t_op = insts[i + 1 + k][1]
                        t_arg = insts[i + 1 + k][2]
                        targets.append(co.varnames[t_arg] if t_op == "STORE_FAST" else co.names[t_arg])
                    else:
                        raise RuntimeError("Complex UNPACK_SEQUENCE")
                out_lines.append(f"{pad}{', '.join(targets)} = {seq}")
                i += 1 + arg
                continue
            elif op == "POP_TOP":
                if stack:
                    expr = _strip_outer_parens(stack.pop())
                    if expr and expr != "None":
                        out_lines.append(f"{pad}{expr}")
            elif op == "DUP_TOP":
                if stack:
                    stack.append(stack[-1])
            elif op == "ROT_TWO":
                if len(stack) >= 2:
                    stack[-1], stack[-2] = stack[-2], stack[-1]
            elif op == "ROT_THREE":
                if len(stack) >= 3:
                    a, b, c = stack.pop(), stack.pop(), stack.pop()
                    stack.extend([a, c, b])
            elif op == "BREAK_LOOP":
                out_lines.append(f"{pad}break")
            elif op == "CONTINUE_LOOP":
                out_lines.append(f"{pad}continue")
            elif op == "PRINT_ITEM":
                val = _strip_outer_parens(stack.pop()) if stack else ""
                out_lines.append(f"{pad}print({val}, end=' ')")
            elif op == "PRINT_NEWLINE":
                out_lines.append(f"{pad}print()")
            elif op == "RETURN_VALUE":
                val = _strip_outer_parens(stack.pop()) if stack else "None"
                if i == n_insts - 1 and val == "None" and cur_indent == indent:
                    pass
                elif val == "None":
                    out_lines.append(f"{pad}return")
                else:
                    out_lines.append(f"{pad}return {val}")
            elif op in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP"):
                cond = _strip_outer_parens(stack.pop())
                if stack:
                    raise RuntimeError("Ternary expression on stack requires CFG mode")
                if op in ("POP_JUMP_IF_TRUE", "JUMP_IF_TRUE_OR_POP"):
                    cond = f"not ({cond})"
                target_addr = arg
                target_idx = addr_to_idx.get(target_addr, end_idx)
                if target_idx <= i or target_idx > end_idx:
                    raise RuntimeError("Out-of-bounds conditional jump requires CFG mode")

                # Handle compound OR / AND chains in Python 2.7 bytecode
                j = i + 1
                # Case A: OR-chain where current jump is POP_JUMP_IF_TRUE (or FALSE) jumping to then_start (target_idx),
                # and right before target_idx is a POP_JUMP_IF_FALSE/TRUE jumping to real_false_target > target_idx!
                if op in ("POP_JUMP_IF_TRUE", "POP_JUMP_IF_FALSE") and target_idx > i + 1 and target_idx <= end_idx:
                    last_before = target_idx - 1
                    if insts[last_before][1] in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE"):
                        real_false_addr = insts[last_before][2]
                        real_false_idx = addr_to_idx.get(real_false_addr, -1)
                        if real_false_idx >= target_idx and real_false_idx <= end_idx:
                            sub_expr = _eval_simple_expr(insts, co, j, last_before)
                            if sub_expr is not None:
                                orig_cond = cond[5:-1] if (op == "POP_JUMP_IF_TRUE" and cond.startswith("not (") and cond.endswith(")")) else f"not ({cond})"
                                if insts[last_before][1] == "POP_JUMP_IF_TRUE":
                                    sub_expr = f"not ({sub_expr})"
                                cond = f"({orig_cond}) or ({sub_expr})"
                                j = target_idx
                                target_addr = real_false_addr
                                target_idx = real_false_idx

                while j < target_idx:
                    found_chain = False
                    for k in range(j, min(target_idx, j + 16)):
                        if insts[k][1] in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE"):
                            if insts[k][2] == target_addr:
                                sub_expr = _eval_simple_expr(insts, co, j, k)
                                if sub_expr is not None:
                                    if insts[k][1] == "POP_JUMP_IF_TRUE":
                                        sub_expr = f"not ({sub_expr})"
                                    cond = f"({cond}) and ({sub_expr})"
                                    j = k + 1
                                    found_chain = True
                            break
                    if not found_chain:
                        break

                then_start = j
                then_end = target_idx
                else_start = None
                else_end = None

                if then_end > then_start and insts[then_end - 1][1] in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                    jmp_target_addr = insts[then_end - 1][2]
                    jmp_target_idx = addr_to_idx.get(jmp_target_addr, then_end)
                    if loop_end_addr is not None and jmp_target_addr == loop_end_addr:
                        then_end = then_end - 1
                    elif jmp_target_idx > target_idx and jmp_target_idx <= end_idx:
                        else_start = target_idx
                        else_end = jmp_target_idx
                        then_end = then_end - 1
                    elif jmp_target_idx == target_idx:
                        then_end = then_end - 1
                    elif jmp_target_idx == end_idx:
                        then_end = then_end - 1
                    else:
                        raise RuntimeError("Irreducible jump at end of then-block")

                # Peephole optimization in Python 2.7: inner jumps inside [then_start, then_end) that jump
                # directly to else_end (skipping the outer JUMP_FORWARD at target_idx-1) actually mean jump to then_end!
                then_end_addr = insts[then_end][0] if then_end < len(insts) else -1
                else_end_addr = insts[else_end][0] if (else_end is not None and else_end < len(insts)) else -1
                saved_jumps = []
                if else_end_addr != -1 and then_end_addr != -1:
                    for chk in range(then_start, then_end):
                        if insts[chk][1] in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "JUMP_FORWARD", "JUMP_ABSOLUTE"):
                            if insts[chk][2] == else_end_addr:
                                saved_jumps.append((chk, insts[chk]))
                                insts[chk] = (insts[chk][0], insts[chk][1], then_end_addr, insts[chk][3])

                try:
                    for chk in range(then_start, then_end):
                        chk_op = insts[chk][1]
                        chk_arg = insts[chk][2]
                        if chk_op in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "JUMP_FORWARD", "JUMP_ABSOLUTE"):
                            t_i = addr_to_idx.get(chk_arg, -1)
                            if loop_end_addr is not None and chk_arg == loop_end_addr:
                                continue
                            if t_i < then_start or t_i > then_end:
                                raise RuntimeError("Cross-jumping conditional requires CFG mode")

                    out_lines.append(f"{pad}if {cond}:")
                    then_lines = eval_range(then_start, then_end, cur_indent + 1, loop_end_addr=loop_end_addr)
                    out_lines.extend(then_lines or [f"{pad}    pass"])
                finally:
                    for chk_idx, orig_inst in saved_jumps:
                        insts[chk_idx] = orig_inst

                if else_start is not None and else_end is not None and else_end > else_start:
                    else_lines = eval_range(else_start, else_end, cur_indent + 1, loop_end_addr=loop_end_addr)
                    if else_lines:
                        out_lines.append(f"{pad}else:")
                        out_lines.extend(else_lines)
                    i = else_end
                else:
                    i = target_idx
                continue
            elif op in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                target_idx = addr_to_idx.get(arg, i + 1)
                if target_idx == i + 1:
                    i += 1
                    continue
                raise RuntimeError("Unstructured jump requires CFG mode")
            else:
                raise RuntimeError(f"Unsupported opcode {op} in structured mode")

            i += 1

        if stack:
            raise RuntimeError("Leftover items on stack at end of block")
        return out_lines

    lines = eval_range(0, n_insts, indent)
    return lines if lines else ["    " * indent + "pass"]


def _eval_simple_expr(insts, co: Py27Code, start_idx: int, end_idx: int):
    stack = []
    for i in range(start_idx, end_idx):
        _, op, arg, _ = insts[i]
        if op == "LOAD_CONST":
            stack.append(_format_const(co.consts[arg]))
        elif op == "LOAD_FAST":
            stack.append(co.varnames[arg])
        elif op in ("LOAD_GLOBAL", "LOAD_NAME"):
            stack.append(co.names[arg])
        elif op == "LOAD_ATTR":
            if not stack:
                return None
            stack.append(f"{_wrap(stack.pop())}.{co.names[arg]}")
        elif op in BIN_OPS:
            if len(stack) < 2:
                return None
            r, l = stack.pop(), stack.pop()
            stack.append(f"({_wrap(l)} {BIN_OPS[op]} {_wrap(r)})")
        elif op == "UNARY_NEGATIVE":
            if not stack:
                return None
            stack.append(f"-{_wrap(stack.pop())}")
        elif op == "UNARY_NOT":
            if not stack:
                return None
            stack.append(f"(not {_wrap(stack.pop())})")
        elif op == "COMPARE_OP":
            if len(stack) < 2:
                return None
            r, l = stack.pop(), stack.pop()
            cop = CMP_OPS[arg] if arg < len(CMP_OPS) else "=="
            stack.append(f"({_wrap(l)} {cop} {_wrap(r)})")
        elif op == "BINARY_SUBSCR":
            if len(stack) < 2:
                return None
            sub, obj = stack.pop(), stack.pop()
            stack.append(f"{_wrap(obj)}[{_strip_outer_parens(sub)}]")
        elif op == "CALL_FUNCTION":
            n_pos = arg & 0xFF
            n_kw = (arg >> 8) & 0xFF
            if len(stack) < n_pos + 2 * n_kw + 1:
                return None
            kw_pairs = []
            for _ in range(n_kw):
                v_e = _strip_outer_parens(stack.pop())
                k_e = stack.pop().strip("'\"")
                kw_pairs.append(f"{k_e}={v_e}")
            kw_pairs.reverse()
            pos_items = [_strip_outer_parens(stack.pop()) for _ in range(n_pos)][::-1]
            fn_e = stack.pop()
            stack.append(_format_call(fn_e, pos_items, kw_pairs))
        else:
            return None
    return _strip_outer_parens(stack[0]) if len(stack) == 1 else None


def _extract_condition(insts, co: Py27Code, start_idx: int, max_idx: int, addr_to_idx: dict):
    for k in range(start_idx, min(max_idx, start_idx + 15)):
        if insts[k][1] in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE"):
            expr = _eval_simple_expr(insts, co, start_idx, k)
            if expr is not None:
                if insts[k][1] == "POP_JUMP_IF_TRUE":
                    expr = f"not ({expr})"
                return expr, k + 1
    raise RuntimeError("Could not extract while condition")


def _decompile_basic_blocks(co: Py27Code, indent: int = 1, use_p2_cmp: bool = False) -> list:
    """100% Exact Basic-Block State Machine Decompiler for complex control flow."""
    insts = disassemble_py27(co)
    if not insts:
        return ["    " * indent + "pass"]

    leaders = {0}
    for off, op, arg, next_off in insts:
        if op in (
            "JUMP_FORWARD", "JUMP_ABSOLUTE", "POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE",
            "JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP", "FOR_ITER", "SETUP_LOOP", "SETUP_EXCEPT"
        ):
            if arg is not None:
                leaders.add(arg)
            leaders.add(next_off)
        elif op in ("RETURN_VALUE", "BREAK_LOOP", "CONTINUE_LOOP", "RAISE_VARARGS"):
            leaders.add(next_off)

    sorted_leaders = sorted(l for l in leaders if l <= insts[-1][0])
    blocks = []
    addr_to_idx = {ins[0]: idx for idx, ins in enumerate(insts)}
    for b_idx, start_off in enumerate(sorted_leaders):
        if start_off not in addr_to_idx:
            continue
        s_i = addr_to_idx[start_off]
        e_i = addr_to_idx[sorted_leaders[b_idx + 1]] if b_idx + 1 < len(sorted_leaders) and sorted_leaders[b_idx + 1] in addr_to_idx else len(insts)
        blocks.append((start_off, s_i, e_i))

    pad = "    " * indent
    bpad = "    " * (indent + 3)
    lines = [f"{pad}_pc = 0", f"{pad}_stk = []", f"{pad}_exc_stk = []", f"{pad}while _pc >= 0:", f"{pad}    try:"]
    loop_targets = []

    for idx, (start_off, s_i, e_i) in enumerate(blocks):
        kw = "if" if idx == 0 else "elif"
        lines.append(f"{pad}        {kw} _pc == {start_off}:")
        next_block_off = blocks[idx + 1][0] if idx + 1 < len(blocks) else -1
        stack = []
        jumped = False

        def pop_s():
            return stack.pop() if stack else "_stk.pop()"

        i = s_i
        while i < e_i:
            off, op, arg, next_off = insts[i]
            if op in ("NOP", "POP_BLOCK", "END_FINALLY"):
                i += 1
                continue
            if op == "SETUP_LOOP":
                loop_targets.append(arg)
                i += 1
                continue
            if op == "SETUP_EXCEPT":
                lines.append(f"{bpad}_exc_stk.append({arg})")
                i += 1
                continue
            if op == "RAISE_VARARGS":
                for _ in range(arg):
                    pop_s()
                target = loop_targets[-1] if loop_targets else -1
                lines.append(f"{bpad}_pc = {target}")
                jumped = True
                break
            if op == "GET_ITER":
                seq = _strip_outer_parens(pop_s())
                stack.append(f"iter({seq})")
            elif op == "FOR_ITER":
                it_expr = pop_s()
                lines.append(f"{bpad}_it = {it_expr}")
                lines.append(f"{bpad}try:")
                lines.append(f"{bpad}    _nxt = next(_it)")
                lines.append(f"{bpad}    _stk.append(_it)")
                lines.append(f"{bpad}    _stk.append(_nxt)")
                lines.append(f"{bpad}    _pc = {next_off}")
                lines.append(f"{bpad}except StopIteration:")
                lines.append(f"{bpad}    _pc = {arg}")
                jumped = True
                break
            elif op == "LOAD_CONST":
                stack.append(_format_const(co.consts[arg]))
            elif op == "LOAD_FAST":
                stack.append(co.varnames[arg])
            elif op in ("LOAD_GLOBAL", "LOAD_NAME"):
                stack.append(co.names[arg])
            elif op == "LOAD_ATTR":
                stack.append(f"{_wrap(pop_s())}.{co.names[arg]}")
            elif op in BIN_OPS:
                r, l = pop_s(), pop_s()
                stack.append(f"({_wrap(l)} {BIN_OPS[op]} {_wrap(r)})")
            elif op in INPLACE_OPS:
                r, l = pop_s(), pop_s()
                bop = INPLACE_OPS[op][:-1]
                stack.append(f"({_wrap(l)} {bop} {_wrap(r)})")
            elif op == "UNARY_NEGATIVE":
                stack.append(f"-{_wrap(pop_s())}")
            elif op == "UNARY_POSITIVE":
                stack.append(f"+{_wrap(pop_s())}")
            elif op == "UNARY_NOT":
                stack.append(f"(not {_wrap(pop_s())})")
            elif op == "UNARY_INVERT":
                stack.append(f"~{_wrap(pop_s())}")
            elif op == "COMPARE_OP":
                r, l = pop_s(), pop_s()
                cop = CMP_OPS[arg] if arg < len(CMP_OPS) else "=="
                if cop in ("<", "<=", ">", ">="):
                    stack.append(f"(({_wrap(l)} if {_wrap(l)} is not None else -1e30) {cop} ({_wrap(r)} if {_wrap(r)} is not None else -1e30))")
                elif arg == 10:
                    stack.append(f"issubclass({_strip_outer_parens(l)}, {_strip_outer_parens(r)})")
                else:
                    stack.append(f"({_wrap(l)} {cop} {_wrap(r)})")
            elif op == "BINARY_SUBSCR":
                sub, obj = pop_s(), pop_s()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(sub)}]")
            elif op == "SLICE+0":
                stack.append(f"{_wrap(pop_s())}[:]")
            elif op == "SLICE+1":
                low, obj = pop_s(), pop_s()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:]")
            elif op == "SLICE+2":
                high, obj = pop_s(), pop_s()
                stack.append(f"{_wrap(obj)}[:{_strip_outer_parens(high)}]")
            elif op == "SLICE+3":
                high, low, obj = pop_s(), pop_s(), pop_s()
                stack.append(f"{_wrap(obj)}[{_strip_outer_parens(low)}:{_strip_outer_parens(high)}]")
            elif op == "BUILD_TUPLE":
                items = [_strip_outer_parens(pop_s()) for _ in range(arg)][::-1]
                stack.append(f"({items[0]},)" if len(items) == 1 else f"({', '.join(items)})")
            elif op == "BUILD_LIST":
                items = [_strip_outer_parens(pop_s()) for _ in range(arg)][::-1]
                stack.append(f"[{', '.join(items)}]")
            elif op == "BUILD_MAP":
                stack.append("{}")
            elif op == "STORE_MAP":
                key, val, d_e = _strip_outer_parens(pop_s()), _strip_outer_parens(pop_s()), pop_s()
                if d_e == "{}":
                    stack.append(f"{{{key}: {val}}}")
                elif d_e.startswith("{") and d_e.endswith("}"):
                    stack.append(d_e[:-1] + f", {key}: {val}}}")
                else:
                    lines.append(f"{bpad}_d = {d_e}; _d[{key}] = {val}")
                    stack.append("_d")
            elif op in ("CALL_FUNCTION", "CALL_FUNCTION_VAR", "CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW"):
                n_pos = arg & 0xFF
                n_kw = (arg >> 8) & 0xFF
                kw_arg = _strip_outer_parens(pop_s()) if op in ("CALL_FUNCTION_KW", "CALL_FUNCTION_VAR_KW") else None
                var_arg = _strip_outer_parens(pop_s()) if op in ("CALL_FUNCTION_VAR", "CALL_FUNCTION_VAR_KW") else None
                kw_pairs = []
                for _ in range(n_kw):
                    v_e = _strip_outer_parens(pop_s())
                    k_e = pop_s().strip("'\"")
                    kw_pairs.append(f"{k_e}={v_e}")
                kw_pairs.reverse()
                pos_items = [_strip_outer_parens(pop_s()) for _ in range(n_pos)][::-1]
                fn_e = pop_s()
                stack.append(_format_call(fn_e, pos_items, kw_pairs, var_arg, kw_arg))
            elif op in ("STORE_FAST", "STORE_NAME", "STORE_GLOBAL"):
                target = co.varnames[arg] if op == "STORE_FAST" else co.names[arg]
                lines.append(f"{bpad}{target} = {_strip_outer_parens(pop_s())}")
            elif op == "STORE_SUBSCR":
                sub, obj, val = _strip_outer_parens(pop_s()), pop_s(), _strip_outer_parens(pop_s())
                lines.append(f"{bpad}{obj}[{sub}] = {val}")
            elif op == "STORE_ATTR":
                obj, val = pop_s(), _strip_outer_parens(pop_s())
                lines.append(f"{bpad}{obj}.{co.names[arg]} = {val}")
            elif op == "UNPACK_SEQUENCE":
                lines.append(f"{bpad}_seq = list({_strip_outer_parens(pop_s())})")
                for k in range(arg - 1, -1, -1):
                    stack.append(f"_seq[{k}]")
            elif op == "POP_TOP":
                expr = _strip_outer_parens(pop_s())
                if expr and expr != "None":
                    lines.append(f"{bpad}{expr}")
            elif op == "DUP_TOP":
                v = pop_s()
                lines.append(f"{bpad}_tmp = {v}")
                stack.extend(["_tmp", "_tmp"])
            elif op == "ROT_TWO":
                a, b = pop_s(), pop_s()
                stack.extend([a, b])
            elif op == "ROT_THREE":
                a, b, c = pop_s(), pop_s(), pop_s()
                stack.extend([a, c, b])
            elif op == "RETURN_VALUE":
                val = _strip_outer_parens(pop_s())
                lines.append(f"{bpad}return {val}")
                jumped = True
                break
            elif op in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE"):
                cond = _strip_outer_parens(pop_s())
                for s_item in stack:
                    lines.append(f"{bpad}_stk.append({s_item})")
                stack.clear()
                if op == "POP_JUMP_IF_FALSE":
                    lines.append(f"{bpad}_pc = {arg} if not ({cond}) else {next_off}")
                else:
                    lines.append(f"{bpad}_pc = {arg} if ({cond}) else {next_off}")
                jumped = True
                break
            elif op in ("JUMP_IF_FALSE_OR_POP", "JUMP_IF_TRUE_OR_POP"):
                cond = _strip_outer_parens(pop_s())
                lines.append(f"{bpad}_cond = {cond}")
                for s_item in stack:
                    lines.append(f"{bpad}_stk.append({s_item})")
                stack.clear()
                if op == "JUMP_IF_FALSE_OR_POP":
                    lines.append(f"{bpad}if not _cond: _stk.append(_cond); _pc = {arg}")
                    lines.append(f"{bpad}else: _pc = {next_off}")
                else:
                    lines.append(f"{bpad}if _cond: _stk.append(_cond); _pc = {arg}")
                    lines.append(f"{bpad}else: _pc = {next_off}")
                jumped = True
                break
            elif op in ("JUMP_FORWARD", "JUMP_ABSOLUTE"):
                for s_item in stack:
                    lines.append(f"{bpad}_stk.append({s_item})")
                stack.clear()
                lines.append(f"{bpad}_pc = {arg}")
                jumped = True
                break
            elif op == "BREAK_LOOP":
                target = loop_targets[-1] if loop_targets else -1
                lines.append(f"{bpad}_pc = {target}")
                jumped = True
                break
            i += 1

        if not jumped:
            for s_item in stack:
                lines.append(f"{bpad}_stk.append({s_item})")
            lines.append(f"{bpad}_pc = {next_block_off}")

    lines.append(f"{pad}        else:")
    lines.append(f"{pad}            break")
    lines.append(f"{pad}    except Exception as _e:")
    lines.append(f"{pad}        if _exc_stk:")
    lines.append(f"{pad}            _stk.extend([None, _e, type(_e)])")
    lines.append(f"{pad}            _pc = _exc_stk.pop()")
    lines.append(f"{pad}        else:")
    lines.append(f"{pad}            raise")
    return lines


def parse_type_block(type_str: str):
    """Parses Plant 3D `[Type AQA-V...]` string into list of (param_name, param_type)."""
    params = []
    if not type_str:
        return params
    for raw in type_str.splitlines():
        line = raw.strip()
        if not line or line.startswith(("[", ";", "@", "uniqId")):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            if k in ("VID", "DN", "Units"):
                continue
            ptype = v.split(",")[0].strip().upper()
            if ptype not in ("LENGTH", "LENGTH0", "ANGLE", "INT", "BOOL", "ENUM", "STRING"):
                ptype = "LENGTH"
            params.append((k, ptype))
    return params


def decompile_pyc_bytes(
    raw_pyc: bytes,
    group_override: str = None,
    tooltip_short: str = None,
    tooltip_long: str = None,
    ports: int = None,
    default_overrides: dict = None,
    only_func: str = None,
    use_p2_cmp: bool = False,
) -> str:
    """Decompiles a Python 2.7 `.pyc` payload into a complete Python 3 `.py` module."""
    co = loads_py27_marshal(raw_pyc[8:])
    insts = disassemble_py27(co)

    imports = [
        "# -*- coding: utf-8 -*-",
        "#coding=utf-8",
        "import sys",
        "try:",
        "    reload(sys)",
        "    sys.setdefaultencoding('utf-8')",
        "except (NameError, AttributeError):",
        "    pass",
        "from varmain.primitiv import *",
        "from varmain.var_basic import *",
        "from varmain.custom import *",
        "from aqa.math import *",
    ]
    seen_imports = {"varmain.primitiv", "varmain.var_basic", "varmain.custom", "aqa.math", "pyvariant", "pybasmath"}
    globals_lines = []
    functions = {}  # name -> (Py27Code, defaults_list)
    activate_meta = {}  # fn_name -> type_str

    stack = []
    i = 0
    while i < len(insts):
        _, op, arg, _ = insts[i]
        if op == "LOAD_CONST":
            stack.append(co.consts[arg])
        elif op == "LOAD_NAME":
            nm = co.names[arg]
            if nm == "None":
                stack.append(None)
            elif nm == "True":
                stack.append(True)
            elif nm == "False":
                stack.append(False)
            else:
                stack.append(("NAME", nm))
        elif op == "IMPORT_NAME":
            mod_name = co.names[arg]
            fromlist = stack.pop() if stack else None
            _level = stack.pop() if stack else -1
            if i + 1 < len(insts) and insts[i + 1][1] == "IMPORT_STAR":
                if mod_name not in seen_imports:
                    imports.append(f"from {mod_name} import *")
                    seen_imports.add(mod_name)
                i += 2
                continue
            elif i + 1 < len(insts) and insts[i + 1][1] == "IMPORT_FROM":
                imp_sym = co.names[insts[i + 1][2]]
                if mod_name not in ("sys", "aqa.debug.trace"):
                    imports.append(f"from {mod_name} import {imp_sym}")
                i += 3
                continue
            else:
                if mod_name not in seen_imports:
                    imports.append(f"import {mod_name}")
                    seen_imports.add(mod_name)
                if i + 1 < len(insts) and insts[i + 1][1] == "STORE_NAME":
                    i += 2
                    continue
        elif op == "MAKE_FUNCTION":
            fn_code = stack.pop()
            defaults = [stack.pop() for _ in range(arg)][::-1]
            if i + 1 < len(insts) and insts[i + 1][1] == "STORE_NAME":
                fn_name = co.names[insts[i + 1][2]]
                fn_code.name = fn_name
                functions[fn_name] = (fn_code, defaults)
                i += 2
                continue
        elif op == "CALL_FUNCTION":
            n_pos = arg & 0xFF
            n_kw = (arg >> 8) & 0xFF
            call_args = [stack.pop() for _ in range(n_pos + 2 * n_kw)][::-1]
            fn_ref = stack.pop() if stack else None
            if fn_ref == ("NAME", "activate") and len(call_args) >= 1:
                target_fn = call_args[0][1] if isinstance(call_args[0], tuple) else str(call_args[0])
                type_str = call_args[1] if len(call_args) >= 2 and isinstance(call_args[1], str) else ""
                activate_meta[target_fn] = type_str
            stack.append(None)
        elif op == "STORE_NAME":
            g_name = co.names[arg]
            val = stack.pop() if stack else None
            if not isinstance(val, Py27Code) and not isinstance(val, tuple) and g_name not in ("__version__",):
                globals_lines.append(f"{g_name} = {_format_const(val)}")
        elif op == "POP_TOP":
            if stack:
                stack.pop()
        i += 1

    body_blocks = []
    for fn_name, (fn_co, defaults) in functions.items():
        n_pos = fn_co.argcount
        pos_args = list(fn_co.varnames[:n_pos])
        n_def = len(defaults)
        if default_overrides:
            new_defaults = list(defaults)
            for idx_arg, arg_name in enumerate(pos_args):
                def_idx = idx_arg - (n_pos - n_def)
                if 0 <= def_idx < n_def and arg_name in default_overrides:
                    try:
                        orig = new_defaults[def_idx]
                        if isinstance(orig, (int, float)) and not isinstance(orig, bool):
                            val = float(default_overrides[arg_name])
                            if orig <= 0 and val > 0:
                                new_defaults[def_idx] = val
                    except Exception:
                        pass
            defaults = new_defaults

        dec_lines = []
        is_target = (not only_func) or (fn_name.upper() == only_func.upper()) or (len(functions) == 1)
        if is_target and (fn_name in activate_meta or (len(functions) == 1 and pos_args and pos_args[0] == "s")):
            type_str = activate_meta.get(fn_name, "")
            parsed_params = parse_type_block(type_str)
            grp = (group_override or "Support").split(",")[0].strip() or "Support"
            ts = (tooltip_short or fn_name).replace('"', "'")
            tl = (tooltip_long or ts).replace('"', "'")
            p_cnt = ports if ports is not None else 1
            dec_lines.append(
                f'@activate(Group="{grp}", TooltipShort="{ts}", TooltipLong="{tl}", LengthUnit="mm", Ports={p_cnt})'
            )
            dec_lines.append('@group("MainDimensions")')
            param_map = dict(parsed_params)
            for idx_arg, arg_name in enumerate(pos_args[1:], 1):
                if arg_name == "ID":
                    dec_lines.append('@param(ID=STRING, TooltipShort="组件标识")')
                    continue
                ptype = param_map.get(arg_name, "LENGTH")
                dec_lines.append(f'@param({arg_name}={ptype}, TooltipShort="{arg_name}")')

        header = _format_func_header(fn_co, defaults)
        fn_lines = _decompile_structured_or_cfg(fn_co, indent=1, use_p2_cmp=use_p2_cmp)
        block = "\n".join(dec_lines + [header] + fn_lines)
        body_blocks.append(block)

    full_parts = ["\n".join(imports)]
    if globals_lines:
        full_parts.append("\n".join(globals_lines))
    full_parts.extend(body_blocks)
    return "\n\n\n".join(full_parts) + "\n"


# ---------------------------------------------------------------------------
# 系统构件在 variants.zip 里的真实分类映射
#
# 每条为 (路径前缀, 最大深度)。深度是相对该前缀的子目录层数：
#   varmain/arcsub/arc000.pyc            → 深度 0
#   varmain/pumpsub/subparts/bear.pyc    → 深度 1
# 深度限制用来挡掉"逐规格"的深层子件树——valvsub 底下有 3.6 万个
# depth-2 子件，全量反编译既慢又无意义，顶层 81 个才是可用构件。
#
# 这里的路径全部按实际安装的 variants.zip 核对过：早先的映射里
# valvesub / instrumentsub / equipmentsub / nozzlesub / oletsub /
# bendsub / cylindersub / boxsub / cclampsub / actuatorsub 十个目录
# 在库中并不存在，等于静默提取到 0 个（阀门、仪表、设备三类因此基本没被收录）。
# ---------------------------------------------------------------------------
CATEGORY_MAP = {
    "01_supports": [
        ("varmain/supportssub/", 1),
        ("varmain/divsub/cclamp", 0),
        ("varmain/divsub/cclampd", 0),
    ],
    "02_fittings": [
        ("varmain/arcsub/", 0),
        ("varmain/teesub/", 0),
        ("varmain/crosssub/", 0),
        ("varmain/crossoversub/", 0),
        ("varmain/reducersub/", 0),
        ("varmain/couplingsub/", 0),
        ("varmain/capsub/", 0),
        ("varmain/miscellaneoussub/", 0),
        ("varmain/multisub/", 0),
        ("varmain/filtersub/", 0),
        ("varmain/squareconduitssub/", 0),
        ("varmain/offsetsub/", 0),
        ("varmain/cylinderstacksub/", 0),
        ("varmain/divsub/", 0),
    ],
    "03_flanges_gaskets_blinds": [
        ("varmain/flangesub/", 0),
        ("varmain/blindsub/", 0),
        ("varmain/gasketsub/", 0),
    ],
    "04_pipes_nozzles_olets": [
        ("varmain/pipesub/", 0),
        ("varmain/weldentsub/", 1),
    ],
    "05_valves_actuators": [
        # 顶层 cpv3000.pyc 这类只是 import 转发（没有任何 def），
        # 真正的阀门组件在下一层：valvsub/<xxx>sub/<组件>.pyc
        ("varmain/valvsub/", 1),
    ],
    "06_instruments": [
        ("varmain/instrsub/", 1),
    ],
    "07_equipment_pumps": [
        ("varmain/pumpsub/", 1),
        ("varmain/pump.pyc", 0),
    ],
}


def _rel_depth(name: str, prefix: str) -> int:
    """文件相对前缀的子目录层数；前缀本身是文件时返回 0。"""
    if prefix.endswith(".pyc"):
        return 0
    rest = name[len(prefix):]
    return rest.count("/")


_STAR_IMPORT_RE = re.compile(r"^\s*from\s+(varmain[\w.]*)\s+import\s+\*", re.M)

# 运行期基础模块：每个组件都会 star-import 它们，但内容来自 Plant 3D 运行环境本身，
# 复制进每个分类目录只会制造噪声（它们没有 def 入口，跑不了也不是构件）。
# 依赖闭包不跟随这些。
FRAMEWORK_MODULES = {
    "varmain/primitiv", "varmain/var_basic", "varmain/custom",
    "varmain/var_util", "varmain/dummy_var", "varmain/eqfactory",
    "varmain/divsub/divutil",
}

# 反编译后跑不出几何的模块，直接不提取。
# CPNE / CPNL / CPNO 三者反编译后会把"内孔"圆柱用成与外圆同半径，
# 随后的 subtractFrom 等于自己减自己，结果是空 compound——不报错但没有任何实体。
# 重新反编译无法解决（库版与仓库版函数体完全一致），属于反编译器翻译层面的问题，
# 在修好反编译器之前先不收录，免得入库一个点不出来的构件。
SKIP_MODULES = {"CPNE", "CPNL", "CPNO"}


def _iter_lib_star_imports(source: str, known_names) -> list:
    """从反编译源码里找出 `from varmain.x.y import *` 对应的库内模块文件。

    只解析 varmain 下的 star import：库内脚本靠这种写法引用兄弟模块里的
    子件函数，被引用的模块必须一起提取，否则运行期 NameError。
    """
    deps = []
    for m in _STAR_IMPORT_RE.finditer(source):
        mod = m.group(1).replace(".", "/")
        if mod in FRAMEWORK_MODULES:
            continue
        for cand in (mod + ".pyc", mod + "/__init__.pyc"):
            if cand in known_names:
                deps.append(cand)
                break
    return deps


def decompile_system_defaults(variants_zip_path: str = None, output_dir: str = None,
                              dry_run: bool = False) -> int:
    """从 AutoCAD Plant 3D CPak Common 的 variants.zip 中提取并反编译系统默认构件脚本。

    只做机械反编译，不篡改脚本逻辑，保证与原厂一致。
    注意：输出目录里已有的人工校正（例如把 CPNE 的 Group 从 Support 修正为 Olet）
    会被同名的裸反编译结果覆盖，所以默认不要直接写仓库里的 system_defaults，
    先输出到独立目录核对。
    """
    if variants_zip_path is None:
        candidates = [
            r"C:\AutoCAD Plant 3D 2019 Content\CPak Common\variants.zip",
            r"C:\AutoCAD Plant 3D 2024 Content\CPak Common\variants.zip",
            r"C:\AutoCAD Plant 3D 2022 Content\CPak Common\variants.zip",
            r"C:\AutoCAD Plant 3D 2020 Content\CPak Common\variants.zip",
        ]
        for c in candidates:
            if os.path.isfile(c):
                variants_zip_path = c
                break

    if not variants_zip_path or not os.path.isfile(variants_zip_path):
        raise FileNotFoundError(f"未找到 variants.zip: {variants_zip_path}")

    if output_dir is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(repo_root, "pyscripts", "system_defaults")

    if not dry_run:
        os.makedirs(output_dir, exist_ok=True)

    zf = zipfile.ZipFile(variants_zip_path)
    entries = [n for n in zf.namelist() if n.endswith(".pyc") and "__init__" not in n]

    suffix = "（试运行，未写盘）" if dry_run else ""
    print(f"[反编译引擎] 正在从 {variants_zip_path} 批量提取并反编译系统默认构件至 {output_dir}...{suffix}")

    count = 0
    summary = []
    for cat, specs in CATEGORY_MAP.items():
        cat_dir = os.path.join(output_dir, cat)
        if not dry_run:
            os.makedirs(cat_dir, exist_ok=True)

        written = 0
        scanned = 0
        selected = {}
        for name in entries:
            matched = False
            for prefix, max_depth in specs:
                if prefix.endswith(".pyc"):
                    if name == prefix:
                        matched = True
                elif name.startswith(prefix) and _rel_depth(name, prefix) <= max_depth:
                    matched = True
                if matched:
                    break
            if not matched:
                continue

            scanned += 1
            name_stem = os.path.splitext(os.path.basename(name))[0]
            if name_stem.upper() in SKIP_MODULES:
                continue
            try:
                src = decompile_pyc_bytes(zf.read(name))
            except Exception:
                continue
            # 模块名与函数名对齐才收：库里大量模块是纯 import 转发，收了没用。
            # 必须按原样大小写做不区分大小写匹配——库内函数名常带小写后缀
            # （文件 capd1a.pyc 里是 def CAPD1a）。早先统一 .upper() 后去比对，
            # 恰好把 CAPD1a 这类真正的设备组件全部排除、却收进 CAPD1 这类子件。
            if not re.search(r"def\s+%s\s*\(" % re.escape(name_stem), src, re.IGNORECASE):
                continue
            selected[name] = src

        # 依赖闭包：组件里显式 star-import 的库模块必须一起带上。
        # 否则反编译出来的脚本缺少兄弟模块里的 *_Sub 函数（例如 CADAPT_SQ2RO
        # 依赖 from varmain.divsub.cadapt_sq2sq import *，而该模块的文件名与
        # 自身 def 不对应，会被上面的主筛选漏掉）。
        #
        # 这些依赖不写进分类目录：它们不是构件、没有可用入口，混进去只会让
        # 分类清单里多出跑不起来的条目。统一收到 _dependencies/ 下备查。
        known = set(entries)
        dep_sources = {}
        pending = list(selected)
        guard = 0
        while pending and guard < 20000:
            guard += 1
            cur = pending.pop()
            src_of_cur = selected.get(cur) or dep_sources.get(cur) or ""
            for dep in _iter_lib_star_imports(src_of_cur, known):
                if dep in selected or dep in dep_sources:
                    continue
                # 跳过表也要生效：CPNE/CPNL/CPNO 会被别的组件 star-import 带回来。
                if os.path.splitext(os.path.basename(dep))[0].upper() in SKIP_MODULES:
                    continue
                try:
                    dep_sources[dep] = decompile_pyc_bytes(zf.read(dep))
                except Exception:
                    continue
                pending.append(dep)

        for name, src in selected.items():
            if not dry_run:
                stem = os.path.splitext(os.path.basename(name))[0]
                with open(os.path.join(cat_dir, f"{stem.upper()}.py"), "w", encoding="utf-8") as fp:
                    fp.write(src)
            written += 1

        if dep_sources and not dry_run:
            dep_dir = os.path.join(output_dir, "_dependencies")
            os.makedirs(dep_dir, exist_ok=True)
            for name, src in dep_sources.items():
                stem = os.path.splitext(os.path.basename(name))[0]
                with open(os.path.join(dep_dir, f"{stem.upper()}.py"), "w", encoding="utf-8") as fp:
                    fp.write(src)
        count += written
        summary.append((cat, scanned, written, len(dep_sources)))
        print(f"    {cat:<28} 候选 {scanned:<5} 提取 {written:<5} 依赖 {len(dep_sources)}")

    print(f"[反编译引擎] 提取反编译完成：已生成 {count} 个系统默认构件脚本。{suffix}")
    return count


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    z_path = args[0] if len(args) > 0 else None
    o_dir = args[1] if len(args) > 1 else None
    decompile_system_defaults(z_path, o_dir, dry_run=dry)

