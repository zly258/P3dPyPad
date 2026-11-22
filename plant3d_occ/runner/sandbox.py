import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
# -*- coding: utf-8 -*-
import functools
import importlib.abc
import importlib.machinery
import json
import os
import re
import sys
import types
import zipfile

if __package__ is None or __package__ == "":
    pkg_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from plant3d_occ.core.session import OccSession
    from plant3d_occ.core.body import OccBody
    from plant3d_occ.core import math3d
    from plant3d_occ import primitives
    from plant3d_occ.primitives import divsub
    from plant3d_occ.decompiler import decompile_pyc_bytes
else:
    from ..core.session import OccSession
    from ..core.body import OccBody
    from ..core import math3d
    from .. import primitives
    from ..primitives import divsub
    from ..decompiler import decompile_pyc_bytes


def _py2_range(*args):
    return list(range(*(int(round(a)) for a in args)))


class DummyModule(types.ModuleType):
    def __init__(self, name):
        super(DummyModule, self).__init__(name)


def _wrap_activated_function(fn, meta=None):
    """Wraps a Plant 3D component/sub-component function with `pyvariant.activate` sub-frame semantics."""
    if getattr(fn, "_plant_wrapped", False):
        if meta:
            fn._plant_activate_meta = dict(meta)
        return fn

    @functools.wraps(fn)
    def _wrapped(*args, **kwargs):
        if not args or not isinstance(args[0], OccSession):
            return fn(*args, **kwargs)

        s: OccSession = args[0]
        start_body_idx = len(s.bodies)
        saved_ports = list(s.ports)
        saved_grips = list(s.grips)
        s._call_depth = getattr(s, "_call_depth", 0) + 1
        s.ports = []
        try:
            ret = fn(*args, **kwargs)
            new_bodies = [b for b in s.bodies[start_body_idx:] if not b.erased and b.shape is not None]
            result_body = ret if isinstance(ret, OccBody) else None
            if result_body is None and new_bodies:
                result_body = new_bodies[0]
                for extra_b in new_bodies[1:]:
                    result_body.uniteWith(extra_b)
                    extra_b.erase()

            local_ports = list(s.ports)
            if result_body is not None and local_ports:
                result_body.setSubComponentPoints(local_ports)
            return result_body if result_body is not None else ret
        finally:
            s._call_depth -= 1
            if s._call_depth > 0:
                s.ports = saved_ports
                s.grips = saved_grips
                s.linear_dimensions = s.grips
            else:
                if not s.ports and saved_ports:
                    s.ports = saved_ports

    _wrapped._plant_activate = True
    _wrapped._plant_wrapped = True
    _wrapped._plant_activate_meta = dict(meta) if meta else {}
    return _wrapped


def _find_variants_zip():
    env_p = os.environ.get("PLANT3D_VARIANTS_ZIP")
    if env_p and os.path.isfile(env_p):
        return env_p

    # Check user's saved catalog config (~/.p3dpypad_catalog_config.json)
    cfg_path = os.path.expanduser("~/.p3dpypad_catalog_config.json")
    if os.path.isfile(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as fp:
                cfg = json.load(fp)
            cdir = cfg.get("content_dir", "")
            if cdir:
                vz = os.path.join(cdir, "variants.zip")
                if os.path.isfile(vz):
                    return vz
        except Exception:
            pass

    candidates = [
        "/working_dir/c_7405d0cc1af3ce0a/work/CPak_Common/variants.zip",
        "/working_dir/c_7405d0cc1af3ce0a/work/CPak_Common/CPak Common/variants.zip",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "variants.zip")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "CPak_Common", "variants.zip")),
    ]
    for year in ("2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019"):
        for drive in ("C:", "D:", "E:"):
            candidates.append(f"{drive}/AutoCAD Plant 3D {year} Content/CPak Common/variants.zip")

    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


class VariantsZipImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Auto-decompiles and caches `varmain.*` and `aqa.*` submodules on-demand from `variants.zip`."""

    def __init__(self, zip_path):
        self.zip_path = zip_path
        self._zf = None
        self._index = {}
        self._dirs = set()
        self._code_cache = {}
        self._module_cache = {}
        self._indexed = False

    def _ensure_index(self):
        if self._indexed:
            return
        self._indexed = True
        self._build_index()

    def _build_index(self):
        if not self.zip_path or not os.path.isfile(self.zip_path):
            return
        try:
            self._zf = zipfile.ZipFile(self.zip_path, "r")
            for name in self._zf.namelist():
                if not name.endswith(".pyc"):
                    continue
                no_ext = name[:-4].lower()
                self._index[no_ext] = name
                r_slash = no_ext.rfind("/")
                if r_slash != -1:
                    self._dirs.add(no_ext[:r_slash])
        except Exception:
            pass

    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(("varmain.", "aqa.")):
            return None
        if fullname in sys.modules:
            return None

        self._ensure_index()
        if not self._zf:
            return None

        rel_slash = fullname.replace(".", "/").lower()
        init_key = rel_slash + "/__init__"
        if rel_slash in self._index or init_key in self._index or rel_slash in self._dirs:
            is_pkg = (init_key in self._index or rel_slash in self._dirs) and (rel_slash not in self._index)
            return importlib.machinery.ModuleSpec(fullname, self, is_package=is_pkg)
        return None

    def create_module(self, spec):
        if spec.name in self._module_cache:
            return self._module_cache[spec.name]
        mod = types.ModuleType(spec.name)
        if spec.submodule_search_locations is not None:
            mod.__path__ = [spec.name]
        return mod

    def exec_module(self, module):
        fullname = module.__name__
        if fullname in self._module_cache:
            cached = self._module_cache[fullname]
            module.__dict__.update(cached.__dict__)
            return

        rel_slash = fullname.replace(".", "/").lower()
        entry_name = self._index.get(rel_slash) or self._index.get(rel_slash + "/__init__")
        module.__dict__["range"] = _py2_range
        module.__dict__["xrange"] = _py2_range
        module.__dict__["aqa"] = sys.modules.get("aqa")
        module.__dict__["_p2_cmp"] = math3d._p2_cmp

        if entry_name:
            if entry_name not in self._code_cache:
                raw_pyc = self._zf.read(entry_name)
                src = decompile_pyc_bytes(raw_pyc, use_p2_cmp=True)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", SyntaxWarning)
                    self._code_cache[entry_name] = compile(src, f"<variants.zip/{entry_name}>", "exec")
            exec(self._code_cache[entry_name], module.__dict__)
            for k, v in list(module.__dict__.items()):
                if callable(v) and isinstance(v, types.FunctionType) and not k.startswith("_"):
                    co_obj = getattr(v, "__code__", None)
                    if co_obj and co_obj.co_argcount >= 1 and co_obj.co_varnames[0] == "s":
                        module.__dict__[k] = _wrap_activated_function(v)

        parent_name, _, child_attr = fullname.rpartition(".")
        if parent_name and parent_name in sys.modules:
            setattr(sys.modules[parent_name], child_attr, module)
        self._module_cache[fullname] = module


_VARIANTS_IMPORTER = None
_MOCK_ENV_INITIALIZED = False


def _ensure_variants_importer():
    global _VARIANTS_IMPORTER
    if _VARIANTS_IMPORTER is not None:
        # Ensure cached submodules remain registered in sys.modules
        for mod_name, mod_obj in _VARIANTS_IMPORTER._module_cache.items():
            if mod_name not in sys.modules:
                sys.modules[mod_name] = mod_obj
        return _VARIANTS_IMPORTER
    zpath = _find_variants_zip()
    if zpath:
        _VARIANTS_IMPORTER = VariantsZipImporter(zpath)
        sys.meta_path.append(_VARIANTS_IMPORTER)
    return _VARIANTS_IMPORTER


def build_mock_environment():
    if not hasattr(types, "StringType"):
        types.StringType = str
    import string as _py_string
    if not hasattr(_py_string, "upper"):
        _py_string.upper = lambda s: str(s).upper()
        _py_string.lower = lambda s: str(s).lower()
        _py_string.strip = lambda s, chars=None: str(s).strip(chars)
        _py_string.split = lambda s, sep=None, maxsplit=-1: str(s).split(sep, maxsplit)
        _py_string.join = lambda words, sep=" ": str(sep).join(words)
        _py_string.find = lambda s, sub, *a: str(s).find(sub, *a)
        _py_string.replace = lambda s, old, new, *a: str(s).replace(old, new, *a)
        _py_string.atof = float
        _py_string.atoi = int
    """Constructs and caches the AutoCAD Plant 3D runtime environment (`aqa.math`, `varmain.*`, `pyvariant`)."""
    global _MOCK_ENV_INITIALIZED
    if _MOCK_ENV_INITIALIZED and "varmain.primitiv" in sys.modules and "aqa.math" in sys.modules:
        _ensure_variants_importer()
        return

    aqa = sys.modules.get("aqa") or DummyModule("aqa")
    aqa.__path__ = ["aqa"]
    aqa_math = sys.modules.get("aqa.math") or DummyModule("aqa.math")
    for attr in dir(math3d):
        if not attr.startswith("_"):
            setattr(aqa_math, attr, getattr(math3d, attr))
    aqa.math = aqa_math
    sys.modules["aqa"] = aqa
    sys.modules["aqa.math"] = aqa_math
    sys.modules["pybasmath"] = aqa_math

    aqa_trace = DummyModule("aqa.debug.trace")
    aqa_trace. trace = lambda *a, **kw: None
    sys.modules["aqa.debug"] = DummyModule("aqa.debug")
    sys.modules["aqa.debug.trace"] = aqa_trace

    varmain = sys.modules.get("varmain") or DummyModule("varmain")
    varmain.__path__ = ["varmain"]
    varmain_primitiv = DummyModule("varmain.primitiv")
    varmain_var_basic = DummyModule("varmain.var_basic")

    for attr in dir(primitives):
        if not attr.startswith("_"):
            val = getattr(primitives, attr)
            setattr(varmain_primitiv, attr, val)
            setattr(varmain_var_basic, attr, val)
    setattr(varmain_var_basic, "_p2_cmp", math3d._p2_cmp)

    varmain_custom = DummyModule("varmain.custom")

    def activate(*args, **kw):
        def dec(f):
            w = _wrap_activated_function(f, meta=kw)
            w._plant_activate = True
            return w
        if len(args) == 1 and callable(args[0]):
            w = _wrap_activated_function(args[0], meta=kw)
            w._plant_activate = True
            return w
        return dec

    def group(*args, **kw):
        def dec(f):
            return f
        return dec

    def param(*args, **kw):
        def dec(f):
            return f
        return dec

    def enum(*args, **kw):
        def dec(f):
            return f
        return dec

    varmain_custom.activate = activate
    varmain_custom.group = group
    varmain_custom.param = param
    varmain_custom.enum = enum
    varmain_custom.LENGTH = "LENGTH"
    varmain_custom.LENGTH0 = "LENGTH0"
    varmain_custom.ANGLE = "ANGLE"
    varmain_custom.INT = "INT"
    varmain_custom.BOOL = "BOOL"
    varmain_custom.ENUM = "ENUM"
    varmain_custom.STRING = "STRING"

    pyvariant_mod = DummyModule("pyvariant")
    for k in dir(varmain_primitiv):
        if not k.startswith("_"):
            setattr(pyvariant_mod, k, getattr(varmain_primitiv, k))
    pyvariant_mod.activate = activate
    sys.modules["pyvariant"] = pyvariant_mod

    varmain_divsub = DummyModule("varmain.divsub")
    varmain_divsub.__path__ = ["varmain.divsub"]
    divsub_exports = {}
    for attr in dir(divsub):
        if attr.startswith("_"):
            continue
        value = getattr(divsub, attr)
        if callable(value):
            divsub_exports[attr] = value

    _DIVSUB_MODULES = {
        "divutil": ["NUT_BOLT_HEAD_6_001", "CSTE_U", "CSTE_I", "CSTE_L", "CORNERBOX"],
        "cnut6_001": ["CNUT6_001", "NUT_BOLT_HEAD_6_001"],
        "cbolt6_001": ["CBOLT6_001", "NUT_BOLT_HEAD_6_001"],
        "cbolt_001": ["CBOLT_001"],
        "cste_h": ["CSTE_H", "CSTE_I"],
        "cste_i": ["CSTE_I", "CSTE_H"],
        "cste_u": ["CSTE_U"],
        "cste_l": ["CSTE_L"],
        "cste_t": ["CSTE_T"],
        "cste_c": ["CSTE_C"],
        "cste_o": ["CSTE_O"],
        "cste_r": ["CSTE_R"],
        "cste_f": ["CSTE_F"],
        "cste_z": ["CSTE_Z"],
        "cadapt_sq2ro": ["CADAPT_SQ2RO"],
        "cadapt_sq2sq": ["CADAPT_SQ2SQ"],
    }
    for module_name, exports in _DIVSUB_MODULES.items():
        sub = DummyModule("varmain.divsub." + module_name)
        for name in exports:
            if name in divsub_exports:
                setattr(sub, name, divsub_exports[name])
        sub.__all__ = [n for n in exports if hasattr(sub, n)]
        setattr(varmain_divsub, module_name, sub)
        sys.modules["varmain.divsub." + module_name] = sub

    for name, value in divsub_exports.items():
        setattr(varmain_divsub, name, value)
    varmain_divsub.__all__ = sorted(divsub_exports)
    varmain.divsub = varmain_divsub
    sys.modules["varmain.divsub"] = varmain_divsub

    varmain.primitiv = varmain_primitiv
    varmain.var_basic = varmain_var_basic
    varmain.custom = varmain_custom

    sys.modules["varmain"] = varmain
    sys.modules["varmain.primitiv"] = varmain_primitiv
    sys.modules["varmain.var_basic"] = varmain_var_basic
    sys.modules["varmain.custom"] = varmain_custom

    _ensure_variants_importer()
    _MOCK_ENV_INITIALIZED = True


inject_mock_environment = build_mock_environment


def _primitive_names():
    names = set()
    for module in (primitives, divsub):
        for attr in dir(module):
            if not attr.startswith("_"):
                names.add(attr)
    return names


def _find_entry_name(module_globals, source, filename_hint=None):
    if filename_hint:
        if filename_hint in module_globals and callable(module_globals[filename_hint]):
            return filename_hint
        for k, v in module_globals.items():
            if k.upper() == filename_hint.upper() and callable(v):
                return k

    reserved = _primitive_names()
    defined_in_source = [m.group(1) for m in re.finditer(r"^\s*def\s+([A-Za-z0-9_]+)\s*\(", source, re.M)]
    for name in defined_in_source:
        val = module_globals.get(name)
        if callable(val) and getattr(val, "_plant_activate", False) and name not in reserved:
            return name

    for match in re.finditer(r"^\s*def\s+([A-Za-z0-9_]+)\s*\(\s*s\b", source, re.M):
        name = match.group(1)
        if name in reserved:
            continue
        if callable(module_globals.get(name)):
            return name

    activated_candidates = [
        name for name, value in module_globals.items()
        if callable(value) and getattr(value, "_plant_activate", False) and name not in reserved
    ]
    if activated_candidates:
        return activated_candidates[-1]

    for name, value in module_globals.items():
        if callable(value) and name[:1].isupper() and name not in reserved:
            return name
    return None


def execute_script_source(code_text, filename_hint=None, origin="<script>"):
    """Executes script source in the Plant 3D sandbox environment, returning (module_globals, entry_name)."""
    import importlib

    build_mock_environment()

    def _safe_reload(mod):
        if mod is sys or getattr(mod, "__name__", "") == "sys":
            return sys
        try:
            return importlib.reload(mod)
        except Exception:
            return mod

    module_globals = {
        "reload": _safe_reload,
        "range": _py2_range,
        "xrange": _py2_range,
        "aqa": sys.modules.get("aqa"),
        "_p2_cmp": math3d._p2_cmp,
    }
    added_setencoding = not hasattr(sys, "setdefaultencoding")
    if added_setencoding:
        sys.setdefaultencoding = lambda encoding=None: None  # noqa: E731
    try:
        exec(compile(code_text, origin, "exec"), module_globals)
    finally:
        if added_setencoding:
            try:
                del sys.setdefaultencoding
            except AttributeError:
                pass

    entry_name = _find_entry_name(module_globals, code_text, filename_hint)
    for k, v in list(module_globals.items()):
        if callable(v) and isinstance(v, types.FunctionType) and not k.startswith("_"):
            co_obj = getattr(v, "__code__", None)
            if co_obj and co_obj.co_argcount >= 1 and co_obj.co_varnames[0] == "s":
                is_ent = (k == entry_name)
                w = _wrap_activated_function(v)
                if not is_ent and not getattr(v, "_plant_activate", False):
                    w._plant_activate = False
                module_globals[k] = w
    return module_globals, entry_name


def run_script_in_sandbox(script_path, kwargs=None):
    """Executes a Plant 3D script file in the sandbox, returning (session, entry_name, final_shapes)."""
    with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
        code_text = f.read()

    filename_base = os.path.splitext(os.path.basename(script_path))[0]
    module_globals, entry_name = execute_script_source(
        code_text, filename_hint=filename_base, origin=script_path
    )
    if not entry_name:
        raise RuntimeError("未在脚本中找到可执行的主入口函数: " + script_path)

    entry_fn = module_globals[entry_name]
    s = OccSession()
    params = dict(kwargs) if kwargs else {}
    entry_fn(s, **params)

    shapes = s.get_final_shapes()
    return s, entry_name, shapes
