// -*- coding: utf-8 -*-
/**
 * AutoCAD Plant 3D 构件 Python 脚本浏览器端极速转译与沙箱执行引擎
 * 针对 Plant 3D 参数化构件脚本语法进行针对性解析、参数提取与 WebAssembly 几何造型映射
 */

export function toRadians(deg) {
  return (Number(deg) * Math.PI) / 180.0;
}

export function toDegrees(rad) {
  return (Number(rad) * 180.0) / Math.PI;
}

export function range(...args) {
  let start = 0, stop = 0, step = 1;
  if (args.length === 1) {
    stop = Number(args[0]);
  } else if (args.length === 2) {
    start = Number(args[0]);
    stop = Number(args[1]);
  } else if (args.length >= 3) {
    start = Number(args[0]);
    stop = Number(args[1]);
    step = Number(args[2]);
  }
  const res = [];
  if (step > 0) {
    for (let i = start; i < stop; i += step) res.push(i);
  } else if (step < 0) {
    for (let i = start; i > stop; i += step) res.push(i);
  }
  return res;
}

/**
 * 从 Python 脚本中提取元数据、构件信息与默认参数列表
 */
export function extractScriptMetadata(pyCode) {
  const meta = {
    functionName: '',
    title: '参数化构件',
    description: '',
    params: []
  };

  if (!pyCode) return meta;

  const activateMatch = pyCode.match(/@activate\s*\(([\s\S]*?)\)/);
  if (activateMatch) {
    const actStr = activateMatch[1];
    const shortMatch = actStr.match(/TooltipShort\s*=\s*[uU]?["']([^"']+)["']/);
    const longMatch = actStr.match(/TooltipLong\s*=\s*[uU]?["']([^"']+)["']/);
    if (shortMatch) meta.title = shortMatch[1];
    if (longMatch) meta.description = longMatch[1];
  }

  const paramDescriptions = {};
  const paramRegex = /@param\s*\(\s*([A-Za-z0-9_]+)\s*=\s*([^,\)]+)(?:[\s\S]*?TooltipShort\s*=\s*[uU]?["']([^"']+)["'])?(?:[\s\S]*?TooltipLong\s*=\s*[uU]?["']([^"']+)["'])?/g;
  let pMatch;
  while ((pMatch = paramRegex.exec(pyCode)) !== null) {
    const pName = pMatch[1];
    const pType = (pMatch[2] || '').trim();
    const pShort = pMatch[3] || '';
    const pLong = pMatch[4] || '';
    paramDescriptions[pName] = {
      type: pType,
      short: pShort,
      long: pLong
    };
  }

  const defMatch = pyCode.match(/def\s+([A-Za-z0-9_]+)\s*\(\s*s\s*,?([\s\S]*?)\)\s*:/);
  if (defMatch) {
    meta.functionName = defMatch[1];
    if (meta.title === '参数化构件') {
      meta.title = meta.functionName;
    }

    const rawParams = defMatch[2];
    const paramTokens = rawParams.split(',');
    for (let token of paramTokens) {
      token = token.trim();
      if (!token || token.startsWith('**') || token.startsWith('*')) continue;

      const eqIdx = token.indexOf('=');
      let name = token;
      let defaultVal = null;
      if (eqIdx !== -1) {
        name = token.substring(0, eqIdx).trim();
        let valStr = token.substring(eqIdx + 1).trim();
        if (valStr.startsWith('u"') || valStr.startsWith("u'")) valStr = valStr.substring(1);
        if ((valStr.startsWith('"') && valStr.endsWith('"')) || (valStr.startsWith("'") && valStr.endsWith("'"))) {
          defaultVal = valStr.substring(1, valStr.length - 1);
        } else if (!isNaN(Number(valStr))) {
          defaultVal = Number(valStr);
        } else {
          defaultVal = valStr;
        }
      }

      const pDesc = paramDescriptions[name] || {};
      meta.params.push({
        name,
        defaultValue: defaultVal,
        label: pDesc.short || name,
        description: pDesc.long || '',
        type: typeof defaultVal === 'number' ? 'number' : 'string'
      });
    }
  }

  return meta;
}

/**
 * 转换 Python 函数调用中的关键字参数为 JS 对象参数 (采用精准括号平衡扫描)
 */
function convertKwargsInLine(line) {
  let res = '';
  let i = 0;
  while (i < line.length) {
    const match = line.substring(i).match(/\b([A-Z0-9_]+)\s*\(\s*s\s*,\s*/);
    if (!match) {
      res += line.substring(i);
      break;
    }
    const funcName = match[1];
    const matchIndex = i + match.index;
    res += line.substring(i, matchIndex);

    const startArgs = matchIndex + match[0].length;
    let depth = 1;
    let endArgs = -1;
    for (let j = startArgs; j < line.length; j++) {
      const c = line[j];
      if (c === '(' || c === '[' || c === '{') depth++;
      else if (c === ')' || c === ']' || c === '}') {
        depth--;
        if (depth === 0) {
          endArgs = j;
          break;
        }
      }
    }

    if (endArgs === -1) {
      res += line.substring(matchIndex);
      break;
    }

    const argsStr = line.substring(startArgs, endArgs);
    if (!argsStr.includes('=')) {
      res += `${funcName}(s, ${argsStr})`;
      i = endArgs + 1;
      continue;
    }

    const parts = [];
    let cur = '';
    let d = 0;
    for (let k = 0; k < argsStr.length; k++) {
      const c = argsStr[k];
      if (c === '(' || c === '[' || c === '{') d++;
      else if (c === ')' || c === ']' || c === '}') d--;
      else if (c === ',' && d === 0) {
        parts.push(cur.trim());
        cur = '';
        continue;
      }
      cur += c;
    }
    if (cur.trim()) parts.push(cur.trim());

    const positional = [];
    const kwargs = [];
    for (let part of parts) {
      const eqIdx = part.indexOf('=');
      if (eqIdx !== -1 && part[eqIdx - 1] !== '=' && part[eqIdx + 1] !== '=' && part[eqIdx - 1] !== '!' && part[eqIdx - 1] !== '<' && part[eqIdx - 1] !== '>') {
        const k = part.substring(0, eqIdx).trim();
        const v = part.substring(eqIdx + 1).trim();
        kwargs.push(`${k}: ${v}`);
      } else {
        positional.push(part);
      }
    }

    if (kwargs.length > 0) {
      if (positional.length === 0) {
        res += `${funcName}(s, { ${kwargs.join(', ')} })`;
      } else {
        res += `${funcName}(s, ${positional.join(', ')}, { ${kwargs.join(', ')} })`;
      }
    } else {
      res += `${funcName}(s, ${argsStr})`;
    }
    i = endArgs + 1;
  }
  return res;
}

/**
 * 转换 Python 三元表达式: A if COND else B -> ((COND) ? (A) : (B))
 */
function convertPythonTernary(str) {
  let s = str;
  let guard = 0;
  while (guard++ < 20) {
    const ifIdx = s.indexOf(' if ');
    if (ifIdx === -1) break;

    let depth = 0;
    let elseIdx = -1;
    for (let i = ifIdx + 4; i < s.length; i++) {
      const c = s[i];
      if (c === '(' || c === '[' || c === '{') depth++;
      else if (c === ')' || c === ']' || c === '}') {
        if (depth === 0) break;
        depth--;
      } else if (depth === 0 && s.substring(i, i + 6) === ' else ') {
        elseIdx = i;
        break;
      }
    }
    if (elseIdx === -1) break;

    const cond = s.substring(ifIdx + 4, elseIdx).trim();

    let bDepth = 0;
    let startIdx = 0;
    for (let i = ifIdx - 1; i >= 0; i--) {
      const c = s[i];
      if (c === ')' || c === ']' || c === '}') bDepth++;
      else if (c === '(' || c === '[' || c === '{') {
        if (bDepth === 0) { startIdx = i + 1; break; }
        bDepth--;
      } else if (bDepth === 0 && (c === ',' || c === '=' || c === ';')) {
        startIdx = i + 1;
        break;
      }
    }
    const truePart = s.substring(startIdx, ifIdx).trim();

    let fDepth = 0;
    let endIdx = s.length;
    for (let i = elseIdx + 6; i < s.length; i++) {
      const c = s[i];
      if (c === '(' || c === '[' || c === '{') fDepth++;
      else if (c === ')' || c === ']' || c === '}') {
        if (fDepth === 0) { endIdx = i; break; }
        fDepth--;
      } else if (fDepth === 0 && (c === ',' || c === ';')) {
        endIdx = i;
        break;
      }
    }
    const falsePart = s.substring(elseIdx + 6, endIdx).trim();

    const replacement = '((' + convertPythonCondition(cond) + ') ? (' + truePart + ') : (' + falsePart + '))';
    s = s.substring(0, startIdx) + (startIdx > 0 && (s[startIdx - 1] === '=' || s[startIdx - 1] === ',') ? ' ' : '') + replacement + s.substring(endIdx);
  }
  return s;
}

function convertTuplesToArrays(line) {
  // 1. Python 单元素元组 (x,) -> [x]
  line = line.replace(/\(\s*([^(),]+)\s*,\s*\)/g, '[$1]');

  // 2. 通用元组解析: 如果括号前不是函数名，且括号顶层包含逗号，转为数组 [...]
  const keywords = new Set(['in', 'return', 'yield', 'if', 'else', 'and', 'or', 'not', 'of']);

  function transform(s) {
    let res = '';
    let i = 0;
    while (i < s.length) {
      const c = s[i];
      if (c === "'" || c === '"') {
        const q = c;
        res += c;
        i++;
        while (i < s.length && s[i] !== q) {
          if (s[i] === '\\') res += s[i++];
          if (i < s.length) res += s[i++];
        }
        if (i < s.length) res += s[i++];
        continue;
      }

      if (c === '(') {
        let j = res.length - 1;
        while (j >= 0 && /\s/.test(res[j])) j--;
        let isFuncCall = false;
        if (j >= 0 && /[A-Za-z0-9_]/.test(res[j])) {
          let wordEnd = j + 1;
          while (j >= 0 && /[A-Za-z0-9_]/.test(res[j])) j--;
          const word = res.substring(j + 1, wordEnd);
          if (!keywords.has(word)) {
            isFuncCall = true;
          }
        }

        let depth = 1;
        let k = i + 1;
        let hasCommaAtDepth0 = false;
        let inS = false, inD = false;
        while (k < s.length && depth > 0) {
          const ch = s[k];
          if (ch === "'" && !inD && s[k - 1] !== '\\') inS = !inS;
          else if (ch === '"' && !inS && s[k - 1] !== '\\') inD = !inD;
          else if (!inS && !inD) {
            if (ch === '(' || ch === '[' || ch === '{') depth++;
            else if (ch === ')' || ch === ']' || ch === '}') {
              depth--;
              if (depth === 0) break;
            } else if (ch === ',' && depth === 1) {
              hasCommaAtDepth0 = true;
            }
          }
          k++;
        }

        if (depth === 0) {
          const inner = s.substring(i + 1, k);
          const transformedInner = transform(inner);
          if (!isFuncCall && hasCommaAtDepth0) {
            let clean = transformedInner.trim();
            if (clean.endsWith(',')) clean = clean.slice(0, -1).trim();
            res += '[' + clean + ']';
          } else {
            res += '(' + transformedInner + ')';
          }
          i = k + 1;
          continue;
        }
      }
      res += c;
      i++;
    }
    return res;
  }

  return transform(line);
}

/**
 * 安全剔除 Python 行尾注释 (严格忽略字符串内部的 '#' 字符)
 */
function stripPythonComment(line) {
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === "'" && !inDouble && (i === 0 || line[i - 1] !== '\\')) {
      inSingle = !inSingle;
    } else if (c === '"' && !inSingle && (i === 0 || line[i - 1] !== '\\')) {
      inDouble = !inDouble;
    } else if (c === '#' && !inSingle && !inDouble) {
      return line.substring(0, i);
    }
  }
  return line;
}

/**
 * 合并跨行的未闭合圆括号、方括号或花括号行 (Python 隐式行延续机制)
 */
function joinContinuationLines(rawLines) {
  const joined = [];
  let buffer = '';
  let parenDepth = 0;
  let indent = '';

  for (let i = 0; i < rawLines.length; i++) {
    const l = rawLines[i];
    const code = stripPythonComment(l);
    const trimmed = code.trim();
    if (!trimmed && parenDepth === 0) continue;

    if (parenDepth === 0) {
      const match = code.match(/^[ \t]*/);
      indent = match ? match[0] : '';
      buffer = trimmed;
    } else {
      buffer += ' ' + trimmed;
    }

    let inS = false;
    let inD = false;
    for (let j = 0; j < trimmed.length; j++) {
      const c = trimmed[j];
      if (c === "'" && !inD && (j === 0 || trimmed[j - 1] !== '\\')) inS = !inS;
      else if (c === '"' && !inS && (j === 0 || trimmed[j - 1] !== '\\')) inD = !inD;
      else if (!inS && !inD) {
        if (c === '(' || c === '[' || c === '{') parenDepth++;
        else if (c === ')' || c === ']' || c === '}') {
          if (parenDepth > 0) parenDepth--;
        }
      }
    }

    if (parenDepth === 0) {
      joined.push(indent + buffer);
      buffer = '';
    }
  }

  if (buffer) {
    joined.push(indent + buffer);
  }
  return joined;
}

/**
 * 针对 Plant 3D 构件代码的 Python 到 JavaScript 转译器
 */
export function transpilePythonToJs(pyCode) {
  const declaredVars = new Set();
  const meta = extractScriptMetadata(pyCode);
  for (let p of meta.params) {
    declaredVars.add(p.name);
  }

  // 预置常见构件辅助函数与公共变量声明
  ['CSGR000_util', 'CSGR000', '_exc_stk', 'kw', '__kwargs'].forEach(v => declaredVars.add(v));

  const rawLines = pyCode.split(/\r?\n/);
  const joinedLines = joinContinuationLines(rawLines);
  let functionName = meta.functionName || 'PLANT_COMPONENT';

  // 1. 过滤所有 def 前的装饰器与头部导包，保留 def 及其后续函数体代码
  let defIdx = -1;
  const lines = [];

  for (let i = 0; i < joinedLines.length; i++) {
    const l = joinedLines[i];
    const trimmed = l.trim();
    if (defIdx === -1) {
      if (trimmed.startsWith('def ')) {
        defIdx = i;
        lines.push(l);
      }
      continue;
    }
    lines.push(l);
  }

  if (defIdx === -1) {
    return {
      jsCode: `function ${functionName}(s, __kwargs = {}) { return null; }`,
      functionName
    };
  }

  const jsLines = [];
  const indentStack = [0];

  jsLines.push('// --- 自动转译生成的 JavaScript 执行函数 ---');

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];

    let codePart = stripPythonComment(line);

    const trimmed = codePart.trim();
    if (!trimmed) continue;
    if (trimmed.startsWith('@')) continue;
    if (trimmed.startsWith('from ') || trimmed.startsWith('import ')) continue;
    if (trimmed.startsWith('reload(sys)') || trimmed.startsWith('sys.setdefaultencoding')) continue;
    if (trimmed.startsWith('try:') || trimmed.startsWith('except')) continue;
    if (trimmed === 'pass') continue;

    const indentMatch = codePart.match(/^([ \t]*)/);
    const indentLevel = indentMatch ? indentMatch[1].replace(/\t/g, '    ').length : 0;

    const isElse = trimmed === 'else:' || trimmed.startsWith('else:');
    const isElif = (trimmed.startsWith('elif ') && trimmed.endsWith(':')) || trimmed.startsWith('elif ');

    while (indentStack.length > 1 && indentLevel < indentStack[indentStack.length - 1]) {
      indentStack.pop();
      jsLines.push(' '.repeat(indentStack[indentStack.length - 1]) + '}');
    }

    const defMatch = trimmed.match(/^def\s+([A-Za-z0-9_]+)\s*\(\s*s\s*,?([\s\S]*?)\)\s*:/);
    if (defMatch) {
      functionName = defMatch[1];
      indentStack.push(indentLevel + 4);
      jsLines.push(' '.repeat(indentLevel) + `function ${functionName}(s, __kwargs = {}) {`);

      for (let p of meta.params) {
        if (p.type === 'number') {
          jsLines.push(' '.repeat(indentLevel + 2) + `let ${p.name} = __kwargs.${p.name} !== undefined ? Number(__kwargs.${p.name}) : ${p.defaultValue};`);
        } else {
          jsLines.push(' '.repeat(indentLevel + 2) + `let ${p.name} = __kwargs.${p.name} !== undefined ? String(__kwargs.${p.name}) : ${JSON.stringify(p.defaultValue)};`);
        }
      }
      continue;
    }

    // while 循环语句支持
    if (trimmed.startsWith('while ') && trimmed.endsWith(':')) {
      const cond = trimmed.substring(6, trimmed.length - 1).trim();
      jsLines.push(' '.repeat(indentLevel) + `while (${convertPythonCondition(cond)}) {`);
      indentStack.push(indentLevel + 4);
      continue;
    }

    // 单行 if 语句: if COND: STMT
    const singleIfMatch = trimmed.match(/^if\s+(.*?)\s*:\s*(.+)$/);
    if (singleIfMatch && !trimmed.endsWith(':')) {
      const cond = singleIfMatch[1].trim();
      const body = processStatement(singleIfMatch[2].trim(), declaredVars);
      jsLines.push(' '.repeat(indentLevel) + `if (${convertPythonCondition(cond)}) { ${body} }`);
      continue;
    }

    if (trimmed.startsWith('if ') && trimmed.endsWith(':')) {
      const cond = trimmed.substring(3, trimmed.length - 1).trim();
      jsLines.push(' '.repeat(indentLevel) + `if (${convertPythonCondition(cond)}) {`);
      indentStack.push(indentLevel + 4);
      continue;
    } else if (isElif) {
      if (jsLines.length > 0 && jsLines[jsLines.length - 1].trim() === '}') {
        jsLines.pop();
      }
      const colonIdx = trimmed.indexOf(':');
      const cond = trimmed.substring(5, colonIdx !== -1 ? colonIdx : trimmed.length).trim();
      const rest = colonIdx !== -1 ? trimmed.substring(colonIdx + 1).trim() : '';
      if (rest) {
        const body = processStatement(rest, declaredVars);
        jsLines.push(' '.repeat(indentLevel) + `} else if (${convertPythonCondition(cond)}) { ${body} }`);
      } else {
        jsLines.push(' '.repeat(indentLevel) + `} else if (${convertPythonCondition(cond)}) {`);
        indentStack.push(indentLevel + 4);
      }
      continue;
    } else if (isElse) {
      if (jsLines.length > 0 && jsLines[jsLines.length - 1].trim() === '}') {
        jsLines.pop();
      }
      const rest = trimmed.substring(5).trim();
      if (rest) {
        const body = processStatement(rest, declaredVars);
        jsLines.push(' '.repeat(indentLevel) + `} else { ${body} }`);
      } else {
        jsLines.push(' '.repeat(indentLevel) + `} else {`);
        indentStack.push(indentLevel + 4);
      }
      continue;
    }

    // 支持单变量与解构元组循环: for x in ... / for sx, sy in ...
    const forMatch = trimmed.match(/^for\s+([A-Za-z0-9_,\s]+)\s+in\s+(.*?)\s*:$/);
    if (forMatch) {
      const loopVars = forMatch[1].split(',').map(v => v.trim()).filter(Boolean);
      let iterable = forMatch[2].trim();
      iterable = convertTuplesToArrays(iterable);
      iterable = convertPythonMathAndTypes(iterable);
      if (iterable.startsWith('(') && iterable.endsWith(')')) {
        let clean = iterable.slice(1, -1).trim();
        if (clean.endsWith(',')) clean = clean.slice(0, -1).trim();
        iterable = '[' + clean + ']';
      }
      if (loopVars.length > 1) {
        jsLines.push(' '.repeat(indentLevel) + `for (let [${loopVars.join(', ')}] of ${iterable}) {`);
      } else {
        jsLines.push(' '.repeat(indentLevel) + `for (let ${loopVars[0]} of ${iterable}) {`);
      }
      loopVars.forEach(v => declaredVars.add(v));
      indentStack.push(indentLevel + 4);
      continue;
    }

    const statement = processStatement(trimmed, declaredVars);
    jsLines.push(' '.repeat(indentLevel) + statement);
  }

  while (indentStack.length > 1) {
    indentStack.pop();
    jsLines.push(' '.repeat(indentStack[indentStack.length - 1]) + '}');
  }

  return {
    jsCode: jsLines.join('\n'),
    functionName
  };
}

/**
 * 转换普通 Python 语句（支持分号分隔多语句、解构赋值与变量自动声明）
 */
function processStatement(stmtStr, declaredVars) {
  const subStatements = stmtStr.split(';').map(s => s.trim()).filter(Boolean);
  const converted = subStatements.map(stmt => {
    let s = convertKwargsInLine(stmt);
    s = convertTuplesToArrays(s);
    s = convertPythonTernary(s);
    s = convertPythonMathAndTypes(s);

    const unpackMatch = s.match(/^([A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)+)\s*=\s*(.*)$/);
    if (unpackMatch) {
      const vars = unpackMatch[1].split(',').map(v => v.trim());
      const expr = unpackMatch[2].trim();
      const undeclared = vars.filter(v => !declaredVars.has(v));
      undeclared.forEach(v => declaredVars.add(v));
      const letPrefix = undeclared.length > 0 ? `let ${undeclared.join(', ')}; ` : '';
      let wrappedExpr = expr;
      if (expr.startsWith('[') && expr.endsWith(']')) {
        wrappedExpr = expr;
      } else if (expr.startsWith('(') && expr.endsWith(')')) {
        wrappedExpr = '[' + expr.slice(1, -1) + ']';
      } else if (expr.includes(',')) {
        wrappedExpr = `[${expr}]`;
      }
      return `${letPrefix}[${vars.join(', ')}] = ${wrappedExpr}`;
    }

    const assignMatch = s.match(/^([A-Za-z0-9_]+)\s*=\s*(.*)$/);
    if (assignMatch) {
      const varName = assignMatch[1];
      if (!declaredVars.has(varName) && !s.startsWith('let ') && !s.startsWith('const ') && !s.startsWith('var ')) {
        declaredVars.add(varName);
        return 'let ' + s;
      }
    }
    return s;
  });

  let res = converted.join('; ');
  if (!res.endsWith(';') && !res.endsWith('{') && !res.endsWith('}')) {
    res += ';';
  }
  return res;
}

function convertPythonCondition(cond) {
  let c = cond;
  c = c.replace(/\bis\s+not\s+None\b/g, '!== null');
  c = c.replace(/\bis\s+None\b/g, '=== null');
  c = c.replace(/\bis\s+not\b/g, '!==');
  c = c.replace(/\bis\b/g, '===');
  c = c.replace(/\band\b/g, '&&');
  c = c.replace(/\bor\b/g, '||');
  c = c.replace(/\bnot\b/g, '!');
  c = c.replace(/\bTrue\b/g, 'true');
  c = c.replace(/\bFalse\b/g, 'false');
  c = c.replace(/\bNone\b/g, 'null');
  c = convertPythonMathAndTypes(c);
  return c;
}

function convertPythonMathAndTypes(str) {
  let s = str;
  s = s.replace(/\bmath\.([A-Za-z0-9_]+)/g, '$1');

  s = s.replace(/\bfloat\s*\(/g, 'Number(');
  s = s.replace(/\bint\s*\(/g, 'Math.round(');
  s = s.replace(/\bstr\s*\(/g, 'String(');

  s = s.replace(/\bmax\s*\(/g, 'Math.max(');
  s = s.replace(/\bmin\s*\(/g, 'Math.min(');
  s = s.replace(/\babs\s*\(/g, 'Math.abs(');
  s = s.replace(/\bsqrt\s*\(/g, 'Math.sqrt(');
  s = s.replace(/\bsin\s*\(/g, 'Math.sin(');
  s = s.replace(/\bcos\s*\(/g, 'Math.cos(');
  s = s.replace(/\btan\s*\(/g, 'Math.tan(');
  s = s.replace(/\bradians\s*\(/g, 'toRadians(');
  s = s.replace(/\bdegrees\s*\(/g, 'toDegrees(');
  s = s.replace(/\bpi\b/g, 'Math.PI');

  s = s.replace(/\bis\s+not\s+None\b/g, '!== null');
  s = s.replace(/\bis\s+None\b/g, '=== null');
  s = s.replace(/\bis\s+not\b/g, '!==');
  s = s.replace(/\bis\b/g, '===');
  s = s.replace(/\band\b/g, '&&');
  s = s.replace(/\bor\b/g, '||');
  s = s.replace(/\bnot\b/g, '!');

  s = s.replace(/\bTrue\b/g, 'true');
  s = s.replace(/\bFalse\b/g, 'false');
  s = s.replace(/\bNone\b/g, 'null');

  return s;
}

const declaredVars = new Set();
function ensureVarDeclarations(line) {
  const subStatements = line.split(';').map(s => s.trim()).filter(Boolean);
  const transformed = subStatements.map(stmt => {
    const unpackMatch = stmt.match(/^([A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)+)\s*=\s*(.*)$/);
    if (unpackMatch) {
      const vars = unpackMatch[1].split(',').map(v => v.trim());
      const expr = unpackMatch[2].trim();
      const needsLet = vars.some(v => !declaredVars.has(v));
      vars.forEach(v => declaredVars.add(v));
      return (needsLet ? 'let ' : '') + `[${vars.join(', ')}] = [${expr}]`;
    }

    const assignMatch = stmt.match(/^([A-Za-z0-9_]+)\s*=\s*(.*)$/);
    if (assignMatch) {
      const varName = assignMatch[1];
      const expr = assignMatch[2];
      if (!declaredVars.has(varName) && !stmt.startsWith('let ') && !stmt.startsWith('const ') && !stmt.startsWith('var ')) {
        declaredVars.add(varName);
        return `let ${varName} = ${expr}`;
      }
    }
    return stmt;
  });
  return transformed.join('; ');
}

/**
 * 执行 Plant 3D 构件代码并在传入的 kernel 上构建实体
 */
export async function runPlant3dScript(pyCode, params = {}, kernel) {
  declaredVars.clear();
  const startTime = performance.now();

  const meta = extractScriptMetadata(pyCode);
  const { jsCode, functionName } = transpilePythonToJs(pyCode);

  const session = new kernel.OccSession();

  const sandboxContext = {
    s: session,
    BOX: (s, ...a) => kernel.BOX(s, ...a),
    CYLINDER: (s, ...a) => kernel.CYLINDER(s, ...a),
    CONE: (s, ...a) => kernel.CONE(s, ...a),
    TORUS: (s, ...a) => kernel.TORUS(s, ...a),
    ARC3D: (s, ...a) => kernel.ARC3D(s, ...a),
    ARC3D2: (s, ...a) => kernel.ARC3D2(s, ...a),
    SPHERE: (s, ...a) => kernel.SPHERE(s, ...a),
    HALFSPHERE: (s, ...a) => kernel.HALFSPHERE(s, ...a),
    ELLIPSOIDHEAD: (s, ...a) => kernel.ELLIPSOIDHEAD(s, ...a),
    CORNERBOX: (s, ...a) => kernel.CORNERBOX(s, ...a),
    len: x => (x ? (x.length !== undefined ? x.length : (x.size !== undefined ? x.size : Object.keys(x).length)) : 0),
    areEqual: (a, b, tol = 1e-4) => Math.abs(Number(a) - Number(b)) <= tol,
    asRadiants: toRadians,
    asDegrees: toDegrees,
    mcPi: Math.PI,
    toRadians,
    toDegrees,
    range,
    Math,
    Number,
    String
  };

  const finalParams = {};
  for (let p of meta.params) {
    finalParams[p.name] = p.defaultValue;
  }
  Object.assign(finalParams, params);

  const fnFactory = new Function(
    ...Object.keys(sandboxContext),
    `
    ${jsCode}
    if (typeof ${functionName} === 'function') {
      return ${functionName}(s, ${JSON.stringify(finalParams)});
    }
    return null;
    `
  );

  const retBody = fnFactory(...Object.values(sandboxContext));
  const finalShape = session.getMergedShape() || (retBody && retBody.shape);

  const executionTimeMs = Math.round(performance.now() - startTime);

  return {
    success: finalShape && !finalShape.IsNull(),
    session,
    shape: finalShape,
    meta,
    finalParams,
    executionTimeMs
  };
}
