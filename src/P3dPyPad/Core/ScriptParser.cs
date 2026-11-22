using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace P3dPyPad
{
    public sealed class ScriptParameter
    {
        public string Name { get; set; }
        public string TypeName { get; set; }
        public string DefaultText { get; set; }
        public string Tooltip { get; set; }
        public string TooltipLong { get; set; }
        public string ParamGroup { get; set; }
        public bool Ask4Dist { get; set; }
    }

    public sealed class ParsedScript
    {
        public ParsedScript()
        {
            Parameters = new List<ScriptParameter>();
            Group = "Support";
            Ports = 1;
            LengthUnit = "mm";
        }

        public string EntryName { get; set; }
        public string Group { get; set; }
        public int Ports { get; set; }
        public string LengthUnit { get; set; }
        public string TooltipShort { get; set; }
        public string TooltipLong { get; set; }
        public string FirstPortEndtypes { get; set; }
        public List<ScriptParameter> Parameters { get; set; }
        public string Body { get; set; }
    }

    internal static class ScriptParser
    {
        private static readonly HashSet<string> MetaNames = new HashSet<string>(StringComparer.Ordinal)
        {
            "TooltipShort", "TooltipLong", "Ask4Dist", "Value", "Type", "Name", "EnumValues"
        };

        private static readonly HashSet<string> TypeNames = new HashSet<string>(StringComparer.Ordinal)
        {
            "LENGTH", "LENGTH0", "ANGLE", "INT", "STRING", "STR", "TEXT", "BOOL", "ENUM"
        };

        public static ParsedScript Parse(string source)
        {
            var text = Normalize(source);
            var result = new ParsedScript();
            var pending = new List<ScriptParameter>();
            var sawActivate = false;
            var functions = new List<FunctionDef>();
            var index = 0;
            while (index < text.Length)
            {
                var line = index;
                while (line < text.Length && (text[line] == ' ' || text[line] == '\t'))
                {
                    line++;
                }

                if (line >= text.Length)
                {
                    break;
                }

                if (text[line] == '#')
                {
                    index = NextLine(text, index);
                    continue;
                }

                if (line == index && text[line] == '@')
                {
                    var nameEnd = DecoratorNameEnd(text, line);
                    var name = ShortName(text, line + 1, nameEnd);
                    var contentStart = nameEnd;
                    while (contentStart < text.Length && (text[contentStart] == ' ' || text[contentStart] == '\t'))
                    {
                        contentStart++;
                    }

                    string content = null;
                    if (contentStart < text.Length && text[contentStart] == '(')
                    {
                        var end = SkipBalanced(text, contentStart);
                        content = text.Substring(contentStart + 1, Math.Max(0, end - contentStart - 2));
                        index = end;
                    }
                    else
                    {
                        index = contentStart;
                    }

                    if (name == "param" && content != null)
                    {
                        var param = ParseParam(content);
                        if (param != null)
                        {
                            pending.Add(param);
                        }
                    }
                    else if (name == "activate")
                    {
                        sawActivate = true;
                        if (content != null)
                        {
                            ParseActivate(content, result);
                        }
                    }

                    if (index < text.Length && text[index] == '\r')
                    {
                        index++;
                    }

                    if (index < text.Length && text[index] == '\n')
                    {
                        index++;
                    }

                    continue;
                }

                if (StartsWithKeyword(text, line, "def"))
                {
                    var nameStart = line + 3;
                    while (nameStart < text.Length && (text[nameStart] == ' ' || text[nameStart] == '\t'))
                    {
                        nameStart++;
                    }

                    var nameEnd = nameStart;
                    while (nameEnd < text.Length && (char.IsLetterOrDigit(text[nameEnd]) || text[nameEnd] == '_'))
                    {
                        nameEnd++;
                    }

                    var paren = nameEnd;
                    while (paren < text.Length && (text[paren] == ' ' || text[paren] == '\t'))
                    {
                        paren++;
                    }

                    var function = new FunctionDef
                    {
                        Name = text.Substring(nameStart, nameEnd - nameStart),
                        FromActivate = sawActivate
                    };
                    if (paren < text.Length && text[paren] == '(')
                    {
                        var end = SkipBalanced(text, paren);
                        var inner = text.Substring(paren + 1, Math.Max(0, end - paren - 2));
                        function.Signature = ParseSignature(inner);
                        index = end;
                    }
                    else
                    {
                        index = nameEnd;
                    }

                    function.Parameters = Merge(function.Signature, pending);
                    functions.Add(function);
                    pending.Clear();
                    sawActivate = false;
                    continue;
                }

                index = NextLine(text, index);
            }

            FunctionDef entry = null;
            for (var i = 0; i < functions.Count; i++)
            {
                if (functions[i].FromActivate)
                {
                    entry = functions[i];
                    break;
                }
            }

            if (entry == null && functions.Count > 0)
            {
                entry = functions[0];
            }

            if (entry != null)
            {
                result.EntryName = entry.Name;
                result.Parameters = entry.Parameters;
            }

            result.Body = StripModuleDecorators(text);
            return result;
        }

        public static string BuildExecutable(ParsedScript parsed, IDictionary<string, string> values)
        {
            var builder = new StringBuilder();
            builder.AppendLine("# -*- coding: utf-8 -*-");
            builder.Append("ACP_ENTRY = ");
            builder.Append(PyString(parsed.EntryName ?? string.Empty));
            builder.AppendLine();
            builder.Append("ACP_ARGS = {");
            var first = true;
            var parameters = parsed.Parameters ?? new List<ScriptParameter>();
            for (var i = 0; i < parameters.Count; i++)
            {
                var param = parameters[i];
                string text;
                if (values == null || !values.TryGetValue(param.Name, out text))
                {
                    text = param.DefaultText;
                }

                if (!first)
                {
                    builder.Append(", ");
                }

                first = false;
                builder.Append(PyString(param.Name));
                builder.Append(": ");
                builder.Append(PyLiteral(param, text));
            }

            builder.AppendLine("}");
            builder.AppendLine(parsed.Body ?? string.Empty);
            builder.AppendLine("def ACP_DEV_BUILD(s, *args, **ignored):");
            builder.AppendLine("    fn = globals().get(ACP_ENTRY)");
            builder.AppendLine("    if fn is None:");
            builder.AppendLine("        raise RuntimeError('script function not found: %s' % ACP_ENTRY)");
            builder.AppendLine("    code = fn.func_code");
            builder.AppendLine("    names = code.co_varnames[:code.co_argcount]");
            builder.AppendLine("    defaults = fn.func_defaults or ()");
            builder.AppendLine("    first = len(names) - len(defaults)");
            builder.AppendLine("    has_kw = bool(code.co_flags & 8)");
            builder.AppendLine("    packed = ACP_ARGS or {}");
            builder.AppendLine("    call = {}");
            builder.AppendLine("    for i in range(1, len(names)):");
            builder.AppendLine("        name = names[i]");
            builder.AppendLine("        if name in packed:");
            builder.AppendLine("            call[name] = packed[name]");
            builder.AppendLine("        elif i >= first:");
            builder.AppendLine("            call[name] = defaults[i - first]");
            builder.AppendLine("    if has_kw:");
            builder.AppendLine("        for key in packed:");
            builder.AppendLine("            if key not in call:");
            builder.AppendLine("                call[key] = packed[key]");
            builder.AppendLine("    return fn(s, **call)");
            return builder.ToString();
        }

        private static List<ScriptParameter> Merge(List<ScriptParameter> signature, List<ScriptParameter> declared)
        {
            var merged = new List<ScriptParameter>();
            var declaredByName = new Dictionary<string, ScriptParameter>(StringComparer.Ordinal);
            for (var i = 0; i < declared.Count; i++)
            {
                declaredByName[declared[i].Name] = declared[i];
            }

            var seen = new HashSet<string>(StringComparer.Ordinal);
            if (signature != null)
            {
                for (var i = 0; i < signature.Count; i++)
                {
                    var item = signature[i];
                    ScriptParameter meta;
                    if (declaredByName.TryGetValue(item.Name, out meta))
                    {
                        if (string.IsNullOrEmpty(item.TypeName))
                        {
                            item.TypeName = meta.TypeName;
                        }

                        if (string.IsNullOrEmpty(item.Tooltip))
                        {
                            item.Tooltip = meta.Tooltip;
                        }

                    if (string.IsNullOrEmpty(item.TooltipLong))
                    {
                        item.TooltipLong = meta.TooltipLong;
                    }

                    if (string.IsNullOrEmpty(item.DefaultText))
                    {
                        item.DefaultText = meta.DefaultText;
                    }
                }

                NormalizeDefault(item);
                merged.Add(item);
                seen.Add(item.Name);
            }
        }

        for (var i = 0; i < declared.Count; i++)
        {
            if (!seen.Contains(declared[i].Name))
            {
                NormalizeDefault(declared[i]);
                merged.Add(declared[i]);
            }
        }

        return merged;
    }

        private static string CanonicalType(string type)
        {
            if (type == "STR" || type == "TEXT")
            {
                return "STRING";
            }

            return type;
        }

        private static void NormalizeDefault(ScriptParameter item)
    {
        string text;
        if (!TryUnquote(item.DefaultText, out text))
        {
            return;
        }

        item.DefaultText = text;
        if (string.IsNullOrEmpty(item.TypeName))
        {
            item.TypeName = "STRING";
        }
    }

    private static bool TryUnquote(string raw, out string text)
    {
        text = null;
        if (string.IsNullOrEmpty(raw))
        {
            return false;
        }

        raw = raw.Trim();
        if (raw.Length > 1 && (raw[0] == 'u' || raw[0] == 'U' || raw[0] == 'r' || raw[0] == 'R'))
        {
            raw = raw.Substring(1).TrimStart();
        }

        if (raw.Length < 2)
        {
            return false;
        }

        var quote = raw[0];
        if ((quote != '"' && quote != '\'') || raw[raw.Length - 1] != quote)
        {
            return false;
        }

        text = raw.Substring(1, raw.Length - 2).Replace("\\\\", "\\").Replace("\\n", "\n").Replace("\\t", "\t");
        if (quote == '"')
        {
            text = text.Replace("\\\"", "\"");
        }
        else
        {
            text = text.Replace("\\'", "'");
        }

        return true;
    }

        private static List<ScriptParameter> ParseSignature(string inner)
        {
            var result = new List<ScriptParameter>();
            var parts = SplitArgs(inner);
            for (var i = 0; i < parts.Count; i++)
            {
                var part = parts[i].Trim();
                if (part.Length == 0 || part.StartsWith("*", StringComparison.Ordinal))
                {
                    continue;
                }

                string name;
                string value;
                var eq = IndexOfEquals(part);
                if (eq < 0)
                {
                    name = part;
                    value = string.Empty;
                }
                else
                {
                    name = part.Substring(0, eq).Trim();
                    value = part.Substring(eq + 1).Trim();
                }

                if (i == 0 || name == "s")
                {
                    continue;
                }

                if (!IsIdentifier(name))
                {
                    continue;
                }

                result.Add(new ScriptParameter
                {
                    Name = name,
                    DefaultText = value
                });
            }

            return result;
        }

        private static ScriptParameter ParseParam(string content)
        {
            var assigns = FindAssignments(content);
            string explicitName = null;
            string typeName = null;
            string tooltip = null;
            string tooltipLong = null;
            string value = null;
            string firstName = null;
            string firstType = null;
            for (var i = 0; i < assigns.Count; i++)
            {
                var item = assigns[i];
                if (item.Name == "Name" && item.IsString)
                {
                    explicitName = item.StringValue;
                }
                else if (item.Name == "Type" && !item.IsString)
                {
                    typeName = item.RawValue;
                }
                else if (item.Name == "TooltipShort" && item.IsString)
                {
                    tooltip = item.StringValue;
                }
                else if (item.Name == "TooltipLong" && item.IsString)
                {
                    tooltipLong = item.StringValue;
                }
                else if (item.Name == "Value")
                {
                    value = item.IsString ? item.StringValue : item.RawValue;
                }
                else if (firstName == null && !MetaNames.Contains(item.Name) && !item.IsString && TypeNames.Contains(item.RawValue))
                {
                    firstName = item.Name;
                    firstType = CanonicalType(item.RawValue);
                }
            }

            var name = !string.IsNullOrEmpty(explicitName) ? explicitName : firstName;
            if (!IsIdentifier(name))
            {
                return null;
            }

            return new ScriptParameter
            {
                Name = name,
                TypeName = CanonicalType(!string.IsNullOrEmpty(typeName) ? typeName : firstType),
                Tooltip = tooltip,
                TooltipLong = tooltipLong,
                DefaultText = value,
                ParamGroup = "MainDimensions"
            };
        }

        private static void ParseActivate(string content, ParsedScript target)
        {
            var assigns = FindAssignments(content);
            for (var i = 0; i < assigns.Count; i++)
            {
                var item = assigns[i];
                if (item.Name == "Group" && item.IsString && !string.IsNullOrEmpty(item.StringValue))
                {
                    target.Group = item.StringValue;
                }
                else if (item.Name == "TooltipShort" && item.IsString)
                {
                    target.TooltipShort = item.StringValue;
                }
                else if (item.Name == "TooltipLong" && item.IsString)
                {
                    target.TooltipLong = item.StringValue;
                }
                else if (item.Name == "LengthUnit" && item.IsString && !string.IsNullOrEmpty(item.StringValue))
                {
                    target.LengthUnit = item.StringValue;
                }
                else if (item.Name == "FirstPortEndtypes" && item.IsString)
                {
                    target.FirstPortEndtypes = item.StringValue;
                }
                else if (item.Name == "Ports")
                {
                    int p;
                    var raw = item.IsString ? item.StringValue : item.RawValue;
                    if (int.TryParse(raw, NumberStyles.Integer, CultureInfo.InvariantCulture, out p) && p >= 1 && p <= 8)
                    {
                        target.Ports = p;
                    }
                }
            }
        }

        private static List<Assignment> FindAssignments(string content)
        {
            var result = new List<Assignment>();
            var index = 0;
            while (index < content.Length)
            {
                while (index < content.Length && (char.IsWhiteSpace(content[index]) || content[index] == ','))
                {
                    index++;
                }

                if (index >= content.Length)
                {
                    break;
                }

                if (!IsNameChar(content[index]))
                {
                    index = SkipValue(content, index);
                    continue;
                }

                var start = index;
                while (index < content.Length && (char.IsLetterOrDigit(content[index]) || content[index] == '_'))
                {
                    index++;
                }

                var name = content.Substring(start, index - start);
                while (index < content.Length && (content[index] == ' ' || content[index] == '\t'))
                {
                    index++;
                }

                if (index >= content.Length || content[index] != '=')
                {
                    continue;
                }

                index++;
                while (index < content.Length && (content[index] == ' ' || content[index] == '\t'))
                {
                    index++;
                }

                var assignment = new Assignment { Name = name };
                if (index < content.Length && (content[index] == '"' || content[index] == '\''))
                {
                    assignment.IsString = true;
                    assignment.StringValue = ReadString(content, ref index);
                }
                else
                {
                    var valueStart = index;
                    index = SkipValue(content, index);
                    assignment.RawValue = content.Substring(valueStart, index - valueStart).Trim();
                }

                result.Add(assignment);
            }

            return result;
        }

        private static int SkipValue(string text, int index)
        {
            var depth = 0;
            char quote = '\0';
            for (; index < text.Length; index++)
            {
                var c = text[index];
                if (quote != '\0')
                {
                    if (c == '\\' && index + 1 < text.Length)
                    {
                        index++;
                        continue;
                    }

                    if (c == quote)
                    {
                        quote = '\0';
                    }

                    continue;
                }

                if (c == '"' || c == '\'')
                {
                    quote = c;
                    continue;
                }

                if (c == '(' || c == '[' || c == '{')
                {
                    depth++;
                }
                else if (c == ')' || c == ']' || c == '}')
                {
                    if (depth == 0)
                    {
                        break;
                    }

                    depth--;
                }
                else if (c == ',' && depth == 0)
                {
                    break;
                }
            }

            return index;
        }

        private static string ReadString(string text, ref int index)
        {
            var quote = text[index++];
            var builder = new StringBuilder();
            while (index < text.Length)
            {
                var c = text[index++];
                if (c == '\\' && index < text.Length)
                {
                    builder.Append(text[index++]);
                    continue;
                }

                if (c == quote)
                {
                    break;
                }

                builder.Append(c);
            }

            return builder.ToString();
        }

        private static List<string> SplitArgs(string inner)
        {
            var result = new List<string>();
            var start = 0;
            var depth = 0;
            char quote = '\0';
            for (var i = 0; i < inner.Length; i++)
            {
                var c = inner[i];
                if (quote != '\0')
                {
                    if (c == '\\' && i + 1 < inner.Length)
                    {
                        i++;
                    }
                    else if (c == quote)
                    {
                        quote = '\0';
                    }

                    continue;
                }

                if (c == '"' || c == '\'')
                {
                    quote = c;
                }
                else if (c == '(' || c == '[' || c == '{')
                {
                    depth++;
                }
                else if (c == ')' || c == ']' || c == '}')
                {
                    depth--;
                }
                else if (c == ',' && depth == 0)
                {
                    result.Add(inner.Substring(start, i - start));
                    start = i + 1;
                }
            }

            result.Add(inner.Substring(start));
            return result;
        }

        private static string StripModuleDecorators(string text)
        {
            var builder = new StringBuilder();
            var index = 0;
            while (index < text.Length)
            {
                if (text[index] == '@')
                {
                    index = SkipDecorator(text, index);
                    if (index < text.Length && text[index] == '\r')
                    {
                        index++;
                    }

                    if (index < text.Length && text[index] == '\n')
                    {
                        index++;
                    }

                    continue;
                }

                var next = text.IndexOf('\n', index);
                if (next < 0)
                {
                    builder.Append(text.Substring(index));
                    break;
                }

                builder.Append(text, index, next - index + 1);
                index = next + 1;
            }

            return builder.ToString();
        }

        private static int SkipDecorator(string text, int atIndex)
        {
            var index = DecoratorNameEnd(text, atIndex);
            while (index < text.Length && (text[index] == ' ' || text[index] == '\t'))
            {
                index++;
            }

            if (index < text.Length && text[index] == '(')
            {
                return SkipBalanced(text, index);
            }

            return index;
        }

        private static int DecoratorNameEnd(string text, int atIndex)
        {
            var index = atIndex + 1;
            while (index < text.Length && (char.IsLetterOrDigit(text[index]) || text[index] == '_' || text[index] == '.'))
            {
                index++;
            }

            return index;
        }

        private static string ShortName(string text, int start, int end)
        {
            var raw = text.Substring(start, Math.Max(0, end - start));
            var dot = raw.LastIndexOf('.');
            return dot >= 0 ? raw.Substring(dot + 1) : raw;
        }

        private static int SkipBalanced(string text, int openIndex)
        {
            var depth = 0;
            char quote = '\0';
            for (var i = openIndex; i < text.Length; i++)
            {
                var c = text[i];
                if (quote != '\0')
                {
                    if (c == '\\' && i + 1 < text.Length)
                    {
                        i++;
                        continue;
                    }

                    if (c == quote)
                    {
                        quote = '\0';
                    }

                    continue;
                }

                if (c == '"' || c == '\'')
                {
                    quote = c;
                    continue;
                }

                if (c == '(')
                {
                    depth++;
                }
                else if (c == ')')
                {
                    depth--;
                    if (depth == 0)
                    {
                        return i + 1;
                    }
                }
            }

            return text.Length;
        }

        private static string PyLiteral(ScriptParameter param, string text)
        {
            text = (text ?? string.Empty).Trim();
            string unquoted;
            if (TryUnquote(text, out unquoted))
            {
                text = unquoted;
            }
            var type = param.TypeName ?? string.Empty;
            if (type == "STRING" || type == "ENUM")
            {
                return PyString(text);
            }

            if (type == "BOOL" || text == "True" || text == "False")
            {
                return IsTrue(text) ? "True" : "False";
            }

            double number;
            if (TryNumber(text, out number))
            {
                if (type == "INT")
                {
                    return Math.Truncate(number).ToString(CultureInfo.InvariantCulture);
                }

                var literal = number.ToString("0.########", CultureInfo.InvariantCulture);
                if (literal.IndexOf('.') < 0 && literal.IndexOf('E') < 0 && literal.IndexOf('e') < 0)
                {
                    literal += ".0";
                }

                return literal;
            }

            if (text.Length == 0)
            {
                return type == "STRING" || type == "ENUM" ? "u\"\"" : "0.0";
            }

            // 防御：若类型是数值类型，但无法直接解析为数字（如带中文杂质），回退为默认值或提取的数字
            if (type == "LENGTH" || type == "LENGTH0" || type == "ANGLE" || type == "INT")
            {
                var match = System.Text.RegularExpressions.Regex.Match(text, @"^[+-]?\d+(?:\.\d+)?");
                if (match.Success)
                {
                    double extracted;
                    if (double.TryParse(match.Value, NumberStyles.Float, CultureInfo.InvariantCulture, out extracted))
                    {
                        var lit = extracted.ToString("0.########", CultureInfo.InvariantCulture);
                        if (lit.IndexOf('.') < 0) lit += ".0";
                        return lit;
                    }
                }

                if (!string.IsNullOrEmpty(param.DefaultText))
                {
                    return param.DefaultText;
                }
                return "0.0";
            }

            return PyString(text);
        }

        private static bool IsTrue(string text)
        {
            return text == "1" || string.Equals(text, "True", StringComparison.OrdinalIgnoreCase) || string.Equals(text, "yes", StringComparison.OrdinalIgnoreCase);
        }

        private static bool TryNumber(string text, out double number)
        {
            if (double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out number))
            {
                return true;
            }

            return double.TryParse(text, NumberStyles.Float, CultureInfo.CurrentCulture, out number);
        }

        private static string PyString(string text)
        {
            var builder = new StringBuilder();
            builder.Append("u\"");
            for (var i = 0; i < text.Length; i++)
            {
                var c = text[i];
                if (c == '\\' || c == '"')
                {
                    builder.Append('\\');
                    builder.Append(c);
                }
                else if (c == '\n')
                {
                    builder.Append("\\n");
                }
                else if (c == '\r')
                {
                    builder.Append("\\r");
                }
                else if (c < 32 || c > 126)
                {
                    builder.Append("\\u");
                    builder.Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                }
                else
                {
                    builder.Append(c);
                }
            }

            builder.Append('"');
            return builder.ToString();
        }

        private static bool StartsWithKeyword(string text, int index, string keyword)
        {
            if (index + keyword.Length > text.Length)
            {
                return false;
            }

            if (string.CompareOrdinal(text, index, keyword, 0, keyword.Length) != 0)
            {
                return false;
            }

            var after = index + keyword.Length;
            return after >= text.Length || !(char.IsLetterOrDigit(text[after]) || text[after] == '_');
        }

        private static bool IsIdentifier(string name)
        {
            if (string.IsNullOrEmpty(name) || !(char.IsLetter(name[0]) || name[0] == '_'))
            {
                return false;
            }

            for (var i = 1; i < name.Length; i++)
            {
                if (!char.IsLetterOrDigit(name[i]) && name[i] != '_')
                {
                    return false;
                }
            }

            return true;
        }

        private static bool IsNameChar(char c)
        {
            return char.IsLetter(c) || c == '_';
        }

        private static int IndexOfEquals(string text)
        {
            char quote = '\0';
            for (var i = 0; i < text.Length; i++)
            {
                var c = text[i];
                if (quote != '\0')
                {
                    if (c == '\\' && i + 1 < text.Length)
                    {
                        i++;
                    }
                    else if (c == quote)
                    {
                        quote = '\0';
                    }

                    continue;
                }

                if (c == '"' || c == '\'')
                {
                    quote = c;
                }
                else if (c == '=')
                {
                    return i;
                }
            }

            return -1;
        }

        private static int NextLine(string text, int index)
        {
            var next = text.IndexOf('\n', index);
            return next < 0 ? text.Length : next + 1;
        }

        private static string Normalize(string source)
        {
            return (source ?? string.Empty).Replace("\r\n", "\n").Replace('\r', '\n');
        }

        private sealed class FunctionDef
        {
            public string Name { get; set; }
            public bool FromActivate { get; set; }
            public List<ScriptParameter> Signature { get; set; }
            public List<ScriptParameter> Parameters { get; set; }
        }

        private sealed class Assignment
        {
            public string Name { get; set; }
            public string RawValue { get; set; }
            public bool IsString { get; set; }
            public string StringValue { get; set; }
        }
    }
}
