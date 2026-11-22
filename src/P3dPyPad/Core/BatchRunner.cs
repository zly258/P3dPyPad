using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading;
using Autodesk.AutoCAD.ApplicationServices;

namespace P3dPyPad
{
    public sealed class BatchItemResult
    {
        public int Index { get; set; }
        public string ScriptName { get; set; }
        public string ScriptPath { get; set; }
        public string EntryName { get; set; }
        public bool Success { get; set; }
        public int EntityCount { get; set; }
        public string ImagePath { get; set; }
        public string ErrorMessage { get; set; }
        public long DurationMs { get; set; }

        public string StatusDisplay => Success ? "成功" : "失败";
        public string ImageFileName => !string.IsNullOrEmpty(ImagePath) ? Path.GetFileName(ImagePath) : string.Empty;
        public bool HasImage => Success && !string.IsNullOrEmpty(ImagePath);
        public bool HasError => !Success && !string.IsNullOrEmpty(ErrorMessage);

        public string ShortErrorMessage
        {
            get
            {
                if (string.IsNullOrEmpty(ErrorMessage)) return string.Empty;
                var lines = ErrorMessage.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

                // 取“原因”那一行，而不是最后一行：错误信息往往是
                // "原因 / REV=… / 排查提示 / (细节)" 的堆叠，末尾多半是括号里的补充说明。
                string first = null;
                for (var i = 0; i < lines.Length; i++)
                {
                    var l = lines[i].Trim();
                    if (l.Length == 0 || l.StartsWith("REV=", StringComparison.Ordinal) || l.StartsWith("OK", StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (first == null)
                    {
                        first = l;
                    }

                    if (!l.StartsWith("(", StringComparison.Ordinal))
                    {
                        return l;
                    }
                }

                return first ?? lines[0].Trim();
            }
        }
    }

    internal static class BatchRunner
    {
        public static List<BatchItemResult> RunDirectory(
            Document doc,
            string folderPath,
            string outputDir,
            bool recursive,
            Action<BatchItemResult, int, int> onProgress,
            Func<bool> isCancelled)
        {
            var results = new List<BatchItemResult>();
            if (doc == null || string.IsNullOrEmpty(folderPath) || !Directory.Exists(folderPath))
            {
                return results;
            }

            if (string.IsNullOrEmpty(outputDir))
            {
                outputDir = Path.Combine(folderPath, "cad_renders");
            }
            Directory.CreateDirectory(outputDir);

            var option = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
            var pyFiles = Directory.GetFiles(folderPath, "*.py", option);

            var db = doc.Database;

            // 批处理开始前清空一次残留图元
            using (doc.LockDocument())
            {
                ScriptRunner.ClearModelSpace(db);
            }

            for (var idx = 0; idx < pyFiles.Length; idx++)
            {
                if (isCancelled != null && isCancelled())
                {
                    break;
                }

                var pyPath = pyFiles[idx];
                var fileName = Path.GetFileName(pyPath);
                if (fileName.StartsWith("_") || fileName.StartsWith("dev_"))
                {
                    continue;
                }

                var item = new BatchItemResult
                {
                    Index = idx + 1,
                    ScriptName = fileName,
                    ScriptPath = pyPath
                };

                var sw = System.Diagnostics.Stopwatch.StartNew();

                try
                {
                    var code = File.ReadAllText(pyPath, Encoding.UTF8);
                    var parsed = ScriptParser.Parse(code);
                    item.EntryName = parsed.EntryName;

                    if (string.IsNullOrEmpty(parsed.EntryName))
                    {
                        item.Success = false;
                        item.ErrorMessage = "未找到 def 入口函数";
                    }
                    else
                    {
                        // 1. 读取同名 CSV 首行参数作为预设
                        var csvPath = Path.ChangeExtension(pyPath, ".csv");
                        PresetRow firstPreset = null;
                        if (File.Exists(csvPath))
                        {
                            var presets = PresetReader.ReadAll(csvPath);
                            if (presets.Count > 0)
                            {
                                firstPreset = presets[0];
                            }
                        }

                        // 2. 组装参数
                        var values = new Dictionary<string, string>(StringComparer.Ordinal);
                        for (var i = 0; i < parsed.Parameters.Count; i++)
                        {
                            var p = parsed.Parameters[i];
                            string val;
                            if (firstPreset != null && firstPreset.TryGetValue(p.Name, out val) && !string.IsNullOrWhiteSpace(val))
                            {
                                values[p.Name] = val;
                            }
                            else
                            {
                                values[p.Name] = p.DefaultText ?? string.Empty;
                            }
                        }

                        // 3. 执行脚本生成模型
                        var runRes = ScriptRunner.Run(new ScriptRunRequest
                        {
                            ScriptPath = pyPath,
                            PresetName = firstPreset != null ? firstPreset.Name : string.Empty,
                            Code = code,
                            Values = values
                        });

                        item.Success = runRes.Ok && runRes.CreatedIds != null && runRes.CreatedIds.Count > 0;
                        item.EntityCount = runRes.CreatedIds != null ? runRes.CreatedIds.Count : 0;

                        if (item.Success)
                        {
                            // 4. 每个构件只生成一张轴测着色截图
                            using (doc.LockDocument())
                            {
                                var stem = Path.GetFileNameWithoutExtension(pyPath);
                                var isoPath = Path.Combine(outputDir, stem + "_iso.png");
                                ViewportHelper.CaptureIsometricOnly(
                                    doc,
                                    runRes.Extents,
                                    isoPath,
                                    item.EntryName
                                );
                                item.ImagePath = isoPath;

                                // 5. 立即擦除图元，准备下一个测试
                                ScriptRunner.ClearModelSpace(db);
                            }
                        }
                        else
                        {
                            item.ErrorMessage = runRes.Message;
                        }
                    }
                }
                catch (Exception ex)
                {
                    item.Success = false;
                    item.ErrorMessage = ex.Message;
                }
                finally
                {
                    sw.Stop();
                    item.DurationMs = sw.ElapsedMilliseconds;
                    results.Add(item);

                    if (onProgress != null)
                    {
                        onProgress(item, idx + 1, pyFiles.Length);
                    }
                }
            }

            return results;
        }
    }
}
