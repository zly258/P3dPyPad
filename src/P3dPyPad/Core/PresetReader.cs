using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace P3dPyPad
{
    // Reads one .csv preset matrix: first line = header (names), each following line
    // = one preset row keyed by those names.
    public sealed class PresetRow
    {
        public string Name { get; set; }
        public string DisplayName { get; set; }
        public Dictionary<string, string> Values { get; set; }

        public bool TryGetValue(string paramName, out string value)
        {
            value = null;
            if (Values == null || string.IsNullOrEmpty(paramName))
            {
                return false;
            }

            // 1. 精确匹配（忽略大小写）
            if (Values.TryGetValue(paramName, out value) && !string.IsNullOrWhiteSpace(value))
            {
                return true;
            }

            // 2. 智能别名映射匹配
            var aliases = GetAliases(paramName);
            for (var i = 0; i < aliases.Length; i++)
            {
                if (Values.TryGetValue(aliases[i], out value) && !string.IsNullOrWhiteSpace(value))
                {
                    return true;
                }
            }

            return false;
        }

        private static string[] GetAliases(string name)
        {
            var upper = name.ToUpperInvariant();
            switch (upper)
            {
                case "D":
                    return new[] { "OD", "管径", "管径OD", "管外径", "D_PIPE", "D_RING", "D_CASING", "D_BASE", "D_OUT", "DIA" };
                case "OD":
                    return new[] { "D", "管径", "管径OD", "管外径", "D_PIPE" };
                case "SH":
                    return new[] { "SUPPORT_H", "H", "中心高", "支承高", "固定高" };
                case "SL":
                    return new[] { "L_BODY", "L_CLAMP", "L", "管座长", "托长", "支座长" };
                case "SW":
                    return new[] { "W_BODY", "W", "底板宽", "宽度" };
                case "ST":
                    return new[] { "T", "板厚", "底厚", "THICK" };
                case "L":
                    return new[] { "L_SPAN", "L_TOTAL", "L_BODY", "L_MIN", "L_EXT", "L_CLAMP", "SL", "跨长", "长度", "总长", "板长" };
                case "H":
                    return new[] { "H_FREE", "H_BODY", "H_SECTION", "SH", "高度", "中心高", "总高" };
                case "W":
                    return new[] { "W_BODY", "W_SECTION", "SW", "B", "宽度", "截面宽" };
                case "B":
                    return new[] { "W", "板宽", "宽度", "带宽" };
                case "T":
                    return new[] { "ST", "TF", "板厚", "厚度", "壁厚", "T_WALL" };
                case "TF":
                    return new[] { "T", "翼缘厚" };
                case "D_PARAM":
                case "D1":
                    return new[] { "D", "OD", "PIN_D", "THREAD_D" };
                case "D2":
                    return new[] { "D", "OD", "PIN_D", "THREAD_D" };
                default:
                    if (upper == "D" || upper == "DIA" || upper == "THREAD_D" || upper == "PIN_D")
                    {
                        return new[] { "D", "THREAD_D", "PIN_D", "孔径", "销孔径", "螺纹径", "螺杆径" };
                    }
                    return new string[0];
            }
        }

        // 可编辑 ComboBox 会把选中项回填到输入框，回填内容取自 ToString()。
        // 这里必须返回规格名（而不是带参数摘要的 DisplayName），否则输入框里显示
        // "1  [D=159, SH=250]" 这类长串，再次输入关键字时匹配不到任何项。
        // 下拉列表的两列内容由 ItemTemplate 直接绑定 Name / DisplayName，不受影响。
        public override string ToString()
        {
            return string.IsNullOrEmpty(Name) ? (string.IsNullOrEmpty(DisplayName) ? "(row)" : DisplayName) : Name;
        }
    }

    internal static class PresetReader
    {
        public static List<PresetRow> ReadAll(string path)
        {
            var result = new List<PresetRow>();
            if (string.IsNullOrEmpty(path) || !File.Exists(path))
            {
                return result;
            }

            List<string> lines;
            using (var reader = new StreamReader(path, Encoding.UTF8, true))
            {
                lines = new List<string>();
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    lines.Add(line);
                }
            }

            string header = null;
            for (var i = 0; i < lines.Count; i++)
            {
                if (string.IsNullOrWhiteSpace(lines[i]))
                {
                    continue;
                }

                var cells = ParseLine(lines[i]);
                if (header == null)
                {
                    header = string.Join(",", cells);
                    continue;
                }

                // 过滤仅含单位标记或无实质数字的无效行
                var nonEmptyCount = 0;
                var hasDigit = false;
                for (var k = 0; k < cells.Count; k++)
                {
                    var text = cells[k].Trim();
                    if (!string.IsNullOrEmpty(text))
                    {
                        nonEmptyCount++;
                        for (var cIdx = 0; cIdx < text.Length; cIdx++)
                        {
                            if (char.IsDigit(text[cIdx]))
                            {
                                hasDigit = true;
                                break;
                            }
                        }
                    }
                }

                if (nonEmptyCount < 2 || !hasDigit)
                {
                    continue;
                }

                var names = SplitHeader(header);
                var values = new Dictionary<string, string>(StringComparer.Ordinal);
                for (var j = 0; j < names.Length; j++)
                {
                    var rawVal = j < cells.Count ? cells[j].Trim() : string.Empty;
                    rawVal = SanitizeCellValue(rawVal);
                    values[names[j]] = rawVal;
                }

                var name = CellName(cells, names);
                var display = BuildDisplayName(name, values, names);

                var row = new PresetRow
                {
                    Name = name,
                    DisplayName = display,
                    Values = values
                };
                result.Add(row);
            }

            return result;
        }

        private static string BuildDisplayName(string name, Dictionary<string, string> values, string[] names)
        {
            // 规格名已经在下拉列表第一列显示，这里只拼参数摘要，避免 "1  [D=159, SH=250]"
            // 这种“名字重复一遍”的冗余，也让第二列不会因为名字太长把摘要挤掉。
            var highlights = new List<string>();
            var candidateKeys = new[] { "OD", "管径", "DN", "SPEC", "规格", "D", "SH", "L", "H", "B", "W", "LOAD_KN", "荷载" };

            foreach (var key in candidateKeys)
            {
                string val;
                if (values.TryGetValue(key, out val) && !string.IsNullOrWhiteSpace(val) && val != name)
                {
                    highlights.Add(key + "=" + val.Trim());
                    if (highlights.Count >= 3)
                    {
                        break;
                    }
                }
            }

            if (highlights.Count == 0)
            {
                return string.Empty;
            }

            var sb = new StringBuilder();
            sb.Append('[');
            sb.Append(string.Join(", ", highlights));
            sb.Append(']');
            return sb.ToString();
        }

        private static string CellName(IList<string> cells, string[] names)
        {
            for (var i = 0; i < names.Length; i++)
            {
                var n = names[i].Trim().ToLowerInvariant();
                if (n == "partnumber" || n == "型号" || n == "预设名" || n == "名称" || n == "name" || n == "规格")
                {
                    return cells.Count > i ? cells[i].Trim() : string.Empty;
                }
            }

            return cells.Count > 0 ? cells[0].Trim() : string.Empty;
        }

        private static string[] SplitHeader(string header)
        {
            var cells = ParseLine(header);
            var names = new string[cells.Count];
            for (var i = 0; i < cells.Count; i++)
            {
                names[i] = cells[i];
            }

            return names;
        }

        private static List<string> ParseLine(string line)
        {
            var result = new List<string>();
            var current = new StringBuilder();
            var inQuotes = false;
            for (var i = 0; i < line.Length; i++)
            {
                var c = line[i];
                if (inQuotes)
                {
                    if (c == '"')
                    {
                        if (i + 1 < line.Length && line[i + 1] == '"')
                        {
                            current.Append('"');
                            i++;
                        }
                        else
                        {
                            inQuotes = false;
                        }
                    }
                    else
                    {
                        current.Append(c);
                    }
                }
                else
                {
                    if (c == '"')
                    {
                        inQuotes = true;
                    }
                    else if (c == ',')
                    {
                        result.Add(current.ToString().Trim());
                        current.Length = 0;
                    }
                    else
                    {
                        current.Append(c);
                    }
                }
            }

            result.Add(current.ToString().Trim());
            return result;
        }

        private static string SanitizeCellValue(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return string.Empty;
            raw = raw.Trim();

            // 1. 去除内部空格（如 "3. 0" -> "3.0"）
            if (raw.Contains(" "))
            {
                var noSpace = raw.Replace(" ", "");
                double d;
                if (double.TryParse(noSpace, System.Globalization.NumberStyles.Any, System.Globalization.CultureInfo.InvariantCulture, out d))
                {
                    return noSpace;
                }
            }

            // 2. 清洗 OCR 杂质后缀（如 "17台" -> "17", "82台" -> "82"）
            if (!raw.StartsWith("M", StringComparison.OrdinalIgnoreCase) && !raw.StartsWith("DN", StringComparison.OrdinalIgnoreCase))
            {
                var m = System.Text.RegularExpressions.Regex.Match(raw, @"^([+-]?\d+(?:\.\d+)?)");
                if (m.Success && m.Length < raw.Length)
                {
                    var suffix = raw.Substring(m.Length).Trim();
                    if (suffix.Length <= 4)
                    {
                        return m.Value;
                    }
                }
            }

            return raw;
        }
    }
}
