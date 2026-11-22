using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace P3dPyPad
{
    /// <summary>
    /// 批量测试收尾报告：把本轮每个脚本的结果落成一个纯文本日志，
    /// 失败的脚本连同完整错误信息单独列一段，方便事后逐条排查。
    /// 用 UTF-8(BOM) + CRLF，记事本双击打开不会乱码。
    /// </summary>
    internal static class BatchReport
    {
        public static string Write(
            string outputDir,
            string sourceDir,
            IList<BatchItemResult> items,
            TimeSpan elapsed,
            bool cancelled)
        {
            if (string.IsNullOrEmpty(outputDir) || items == null)
            {
                return null;
            }

            try
            {
                Directory.CreateDirectory(outputDir);

                var path = Path.Combine(outputDir, "batch_report.txt");

                File.WriteAllText(path, Build(sourceDir, outputDir, items, elapsed, cancelled), new UTF8Encoding(true));

                // 结构化 JSON 报告，供外部无人值守自动化调度器 (Python / CI / Skill) 直接无损解析
                var jsonPath = Path.Combine(outputDir, "batch_report.json");
                File.WriteAllText(jsonPath, BuildJson(sourceDir, outputDir, items, elapsed, cancelled), new UTF8Encoding(false));

                return path;
            }
            catch (Exception)
            {
                // 报告写不出来不能影响批量测试本身的结论。
                return null;
            }
        }

        private static string Build(
            string sourceDir,
            string outputDir,
            IList<BatchItemResult> items,
            TimeSpan elapsed,
            bool cancelled)
        {
            var success = 0;
            for (var i = 0; i < items.Count; i++)
            {
                if (items[i].Success)
                {
                    success++;
                }
            }

            var failed = items.Count - success;
            var nl = "\r\n";
            var sb = new StringBuilder();

            sb.Append("P3dPyPad 批量测试报告").Append(nl);
            sb.Append(new string('=', 60)).Append(nl);
            sb.Append("生成时间 : ").Append(DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")).Append(nl);
            sb.Append("脚本目录 : ").Append(sourceDir ?? string.Empty).Append(nl);
            sb.Append("出图目录 : ").Append(outputDir).Append(nl);
            sb.Append("运行状态 : ").Append(cancelled ? "已中断（以下仅为已执行的脚本）" : "已完成").Append(nl);
            sb.Append("总耗时   : ").Append(elapsed.TotalSeconds.ToString("F1")).Append(" 秒").Append(nl);
            sb.Append("汇总     : 共 ").Append(items.Count)
              .Append(" 个脚本，成功 ").Append(success)
              .Append("，失败 ").Append(failed).Append(nl);
            sb.Append(nl);

            // 失败清单放最前面：这是打开报告第一眼要看的东西。
            sb.Append("失败清单 (").Append(failed).Append(')').Append(nl);
            sb.Append(new string('-', 60)).Append(nl);
            if (failed == 0)
            {
                sb.Append("无失败脚本。").Append(nl);
            }
            else
            {
                var wrote = false;
                for (var i = 0; i < items.Count; i++)
                {
                    var item = items[i];
                    if (item.Success)
                    {
                        continue;
                    }

                    wrote = true;
                    sb.Append('[').Append(item.Index).Append("] ").Append(item.ScriptName)
                      .Append("  入口: ").Append(string.IsNullOrEmpty(item.EntryName) ? "(未识别)" : item.EntryName)
                      .Append("  耗时: ").Append(item.DurationMs).Append(" ms").Append(nl);
                    sb.Append("    路径: ").Append(item.ScriptPath ?? string.Empty).Append(nl);
                    sb.Append("    错误:").Append(nl);
                    AppendIndented(sb, item.ErrorMessage, "      ");
                    sb.Append(nl);
                }

                if (!wrote)
                {
                    sb.Append("无失败脚本。").Append(nl);
                }
            }

            sb.Append(nl);
            sb.Append("全部明细").Append(nl);
            sb.Append(new string('-', 60)).Append(nl);
            if (items.Count == 0)
            {
                sb.Append("本轮没有处理任何脚本。").Append(nl);
            }

            for (var i = 0; i < items.Count; i++)
            {
                var item = items[i];
                sb.Append(item.Success ? "OK   " : "FAIL ")
                  .Append('[').Append(item.Index).Append("] ")
                  .Append(PadRight(item.ScriptName, 28))
                  .Append("图元 ").Append(PadLeft(item.EntityCount.ToString(), 4))
                  .Append("  ").Append(PadLeft(item.DurationMs.ToString(), 6)).Append(" ms");

                if (item.HasImage)
                {
                    sb.Append("  ").Append(item.ImageFileName);
                }
                else if (!item.Success && !string.IsNullOrEmpty(item.ShortErrorMessage))
                {
                    sb.Append("  ").Append(item.ShortErrorMessage);
                }

                sb.Append(nl);
            }

            return sb.ToString();
        }

        private static void AppendIndented(StringBuilder sb, string text, string indent)
        {
            if (string.IsNullOrEmpty(text))
            {
                sb.Append(indent).Append("(脚本没有给出错误信息)").Append("\r\n");
                return;
            }

            var lines = text.Replace("\r\n", "\n").Replace('\r', '\n').Split('\n');
            for (var i = 0; i < lines.Length; i++)
            {
                sb.Append(indent).Append(lines[i]).Append("\r\n");
            }
        }

        // 报告是等宽对齐的纯文本，这两处按字符数补空格即可（中文宽度不齐可接受，
        // 明细列以固定顺序排布，靠列顺序而不是严格对齐来读）。
        private static string PadRight(string text, int width)
        {
            text = text ?? string.Empty;
            return text.Length >= width ? text : text + new string(' ', width - text.Length);
        }

        private static string PadLeft(string text, int width)
        {
            text = text ?? string.Empty;
            return text.Length >= width ? text : new string(' ', width - text.Length) + text;
        }

        private static string BuildJson(
            string sourceDir,
            string outputDir,
            IList<BatchItemResult> items,
            TimeSpan elapsed,
            bool cancelled)
        {
            var success = 0;
            for (var i = 0; i < items.Count; i++)
            {
                if (items[i].Success) success++;
            }
            var failed = items.Count - success;
            var sb = new StringBuilder();
            sb.Append("{\n");
            sb.AppendFormat("  \"generated\": \"{0}\",\n", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            sb.AppendFormat("  \"source_dir\": \"{0}\",\n", EscapeJson(sourceDir ?? string.Empty));
            sb.AppendFormat("  \"output_dir\": \"{0}\",\n", EscapeJson(outputDir ?? string.Empty));
            sb.AppendFormat("  \"total\": {0},\n", items.Count);
            sb.AppendFormat("  \"success\": {0},\n", success);
            sb.AppendFormat("  \"failed\": {0},\n", failed);
            sb.AppendFormat("  \"duration_seconds\": {0:F2},\n", elapsed.TotalSeconds);
            sb.AppendFormat("  \"cancelled\": {0},\n", cancelled ? "true" : "false");
            sb.Append("  \"results\": [\n");
            for (var i = 0; i < items.Count; i++)
            {
                var it = items[i];
                sb.Append("    {\n");
                sb.AppendFormat("      \"index\": {0},\n", it.Index);
                sb.AppendFormat("      \"script_name\": \"{0}\",\n", EscapeJson(it.ScriptName ?? string.Empty));
                sb.AppendFormat("      \"script_path\": \"{0}\",\n", EscapeJson(it.ScriptPath ?? string.Empty));
                sb.AppendFormat("      \"entry\": \"{0}\",\n", EscapeJson(it.EntryName ?? string.Empty));
                sb.AppendFormat("      \"success\": {0},\n", it.Success ? "true" : "false");
                sb.AppendFormat("      \"entity_count\": {0},\n", it.EntityCount);
                sb.AppendFormat("      \"duration_ms\": {0},\n", it.DurationMs);
                sb.AppendFormat("      \"image_path\": \"{0}\",\n", EscapeJson(it.ImagePath ?? string.Empty));
                sb.AppendFormat("      \"error\": \"{0}\"\n", EscapeJson(it.ErrorMessage ?? string.Empty));
                sb.Append(i < items.Count - 1 ? "    },\n" : "    }\n");
            }
            sb.Append("  ]\n}");
            return sb.ToString();
        }

        private static string EscapeJson(string str)
        {
            if (string.IsNullOrEmpty(str)) return string.Empty;
            return str.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\r", "\\r").Replace("\n", "\\n").Replace("\t", "\\t");
        }
    }
}
