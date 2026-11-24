using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    public sealed class ScriptRunRequest
    {
        public string ScriptPath { get; set; }
        public string PresetName { get; set; }
        public string Code { get; set; }
        public Dictionary<string, string> Values { get; set; }
    }

    public sealed class EntityParamMetadata
    {
        public string EntryName { get; set; }
        public string ScriptPath { get; set; }
        public string PresetName { get; set; }
        public Dictionary<string, string> Values { get; set; } = new Dictionary<string, string>(StringComparer.Ordinal);
    }

    internal sealed class ScriptRunResult
    {
        public bool Ok { get; set; }
        public string Message { get; set; }
        public List<ObjectId> CreatedIds { get; set; } = new List<ObjectId>();
        public Extents3d? Extents { get; set; }
        public string RawLog { get; set; }
    }

    internal static class ScriptRunner
    {
        /// <summary>
        /// 热更新外壳的部署目录：Plant 3D 内容目录下的 CustomScripts。
        ///
        /// 不写死安装路径——不同年份 / 盘符的安装位置不一样，写死会让外壳
        /// 部署到不存在的目录，表现出来就是"测试被跳过、热更新不生效"。
        /// 目录由 CatalogPublishManager 按实际安装位置探测。
        /// </summary>
        public static string ScriptsDir
        {
            get
            {
                var baseDir = AppDomain.CurrentDomain.BaseDirectory ?? string.Empty;
                var years = new List<string> { "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019" };
                string activeYear = null;
                for (var i = 0; i < years.Count; i++)
                {
                    if (baseDir.IndexOf(years[i], StringComparison.OrdinalIgnoreCase) >= 0)
                    {
                        activeYear = years[i];
                        years.RemoveAt(i);
                        years.Insert(0, activeYear);
                        break;
                    }
                }

                // 优先读取当前年份专属设置；兼容旧版全局 ContentDir，但避免跨版本串用其他年份的默认目录
                var content = !string.IsNullOrEmpty(activeYear)
                    ? UserSettings.GetDirectory("ContentDir_" + activeYear)
                    : null;
                if (string.IsNullOrEmpty(content))
                {
                    var legacyContent = UserSettings.GetDirectory("ContentDir");
                    if (!string.IsNullOrEmpty(legacyContent) &&
                        (string.IsNullOrEmpty(activeYear) ||
                         legacyContent.IndexOf("AutoCAD Plant 3D ", StringComparison.OrdinalIgnoreCase) < 0 ||
                         legacyContent.IndexOf(activeYear, StringComparison.OrdinalIgnoreCase) >= 0))
                    {
                        content = legacyContent;
                    }
                }
                if (!string.IsNullOrEmpty(content) && Directory.Exists(content))
                {
                    var custom = Path.Combine(content, "CustomScripts");
                    if (Directory.Exists(custom)) return custom;
                    return content;
                }

                var env = Environment.GetEnvironmentVariable("PLANT3D_CONTENT_DIR");
                if (!string.IsNullOrEmpty(env) && Directory.Exists(env))
                {
                    var custom = Path.Combine(env, "CustomScripts");
                    if (Directory.Exists(custom)) return custom;
                    return env;
                }

                string[] drives = { "C:\\", "D:\\", "E:\\", "F:\\" };
                foreach (var d in drives)
                {
                    if (!Directory.Exists(d)) continue;
                    foreach (var yr in years)
                    {
                        var cpak = Path.Combine(d, string.Format("AutoCAD Plant 3D {0} Content", yr), "CPak Common");
                        if (Directory.Exists(cpak))
                        {
                            var custom = Path.Combine(cpak, "CustomScripts");
                            if (!Directory.Exists(custom))
                            {
                                try { Directory.CreateDirectory(custom); } catch { }
                            }
                            if (Directory.Exists(custom)) return custom;
                            return cpak;
                        }
                    }
                }
                return @"C:\AutoCAD Plant 3D 2026 Content\CPak Common\CustomScripts";
            }
        }

        private static string AdapterPath
        {
            get
            {
                var cand = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "PLNT3D", "PnP3dACPAdapter.arx");
                if (File.Exists(cand)) return cand;
                if (File.Exists(@"C:\Program Files\Autodesk\AutoCAD 2026\PLNT3D\PnP3dACPAdapter.arx"))
                {
                    return @"C:\Program Files\Autodesk\AutoCAD 2026\PLNT3D\PnP3dACPAdapter.arx";
                }
                return @"C:\Program Files\Autodesk\AutoCAD 2019\PLNT3D\PnP3dACPAdapter.arx";
            }
        }
        private const string ShellName = "DEV_PROXY";
        public const string RegAppName = "P3DPYPAD_META";

        public static readonly List<ObjectId> LastIds = new List<ObjectId>();

        public static string LastScriptPath { get; private set; }
        public static string LastEntryName { get; private set; }
        public static string LastCode { get; private set; }
        public static Dictionary<string, string> LastValues { get; private set; } = new Dictionary<string, string>(StringComparer.Ordinal);

        public static ScriptRunResult Run(ScriptRunRequest request)
        {
            if (request == null)
            {
                throw new ArgumentNullException("request");
            }

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                return Fail("没有打开的图形。");
            }

            var proxy = Path.Combine(ScriptsDir, "DEV_PROXY.py");
            if (!File.Exists(proxy))
            {
                TryDeployProxyScript(proxy);
            }
            if (!File.Exists(proxy))
            {
                return Fail("找不到 DEV_PROXY.py：" + proxy);
            }

            string mapDetail;
            var mapState = EnsureShellRegistered(out mapDetail);
            if (mapState != ShellMapState.Registered)
            {
                var tail = mapState == ShellMapState.Written
                    ? "请完全退出 Plant 3D 再打开（映射表只在启动时读取），然后重新运行。"
                    : "请手动往该文件里加一行 " + ShellName + "=" + ShellName + "，然后完全退出 Plant 3D 再打开。";
                return Fail(
                    "DEV_PROXY 没有注册进 variants.map，TESTACPSCRIPT 找不到它，所以脚本不会执行。\n" +
                    mapDetail + "\n" + tail);
            }

            var parsed = ScriptParser.Parse(request.Code);
            if (string.IsNullOrEmpty(parsed.EntryName))
            {
                return Fail("没有找到 def 函数。请粘贴完整脚本。");
            }

            Directory.CreateDirectory(ScriptsDir);
            var corePath = Path.Combine(ScriptsDir, "dev_core.pyinc");
            var source = ScriptParser.BuildExecutable(parsed, request.Values);
            File.WriteAllText(corePath, source, new UTF8Encoding(false));

            var rev = NextRev();
            var logPath = Path.Combine(ScriptsDir, "dev_reload.log");
            if (File.Exists(logPath))
            {
                File.Delete(logPath);
            }

            EnsureAdapter();

            using (doc.LockDocument())
            {
                EraseLast(doc.Database);
                var before = Snapshot(doc.Database);
                InvokeTest(rev);
                LastIds.Clear();
                LastIds.AddRange(Added(doc.Database, before));
                AttachEntityMetadata(doc.Database, LastIds, parsed.EntryName, request.ScriptPath, request.PresetName, request.Values);
            }

            LastScriptPath = request.ScriptPath;
            LastEntryName = parsed.EntryName;
            LastCode = request.Code;
            LastValues = request.Values != null
                ? new Dictionary<string, string>(request.Values, StringComparer.Ordinal)
                : new Dictionary<string, string>(StringComparer.Ordinal);

            var log = ReadLog();
            var ran = log.IndexOf("REV=" + rev, StringComparison.Ordinal) >= 0;
            if (!ran)
            {
                // 外壳在脚本自身抛异常时写进日志的是 traceback（不含 REV=）。
                // 这种情况脚本其实已经被重新执行过，热更新是生效的，失败源于脚本本身——
                // 不能再统一报成"没有重新执行脚本/无热更新"，那会把真实错误盖掉，
                // 让人误以为测试被跳过而去排查注册表，方向完全跑偏。
                if (log.IndexOf("Traceback (most recent call last)", StringComparison.Ordinal) >= 0)
                {
                    // 真实异常行放最前：批量列表的"异常信息"列取的就是第一行，
                    // 这样用户一眼看到的是 TypeError: xxx，而不是一句泛泛的说明。
                    return Fail(ExtractTracebackCause(log) + "\n"
                                + "脚本执行出错（热更新已生效，异常来自脚本本身，不是测试被跳过）。\n"
                                + parsed.EntryName + "  REV=" + rev + "\n"
                                + log);
                }

                var hint = log.StartsWith("(没有", StringComparison.Ordinal)
                    ? "DEV_PROXY 没有写日志：外壳根本没执行（未注册到 variants.map，或注册后没重启 Plant 3D）。"
                    : "DEV_PROXY 执行了，但日志里没有本次 REV：外壳读到的是旧脚本。";
                return Fail("没有重新执行脚本，图面仍是旧图块。\n" + parsed.EntryName + "  REV=" + rev + "\n" + hint + "\n" + log);
            }

            var ok = log.StartsWith("OK", StringComparison.Ordinal);
            var message = ok
                ? "已生成 " + LastIds.Count + " 个图元。" + parsed.EntryName + "\n" + log
                : "脚本已执行，但失败了。" + parsed.EntryName + "\n" + log;

            var createdList = new List<ObjectId>(LastIds);
            var bounds = CalculateBounds(doc.Database, createdList);

            return new ScriptRunResult
            {
                Ok = ok,
                Message = message,
                CreatedIds = createdList,
                Extents = bounds,
                RawLog = log
            };
        }

        public static Extents3d? CalculateBounds(Database db, IEnumerable<ObjectId> ids)
        {
            var hasBounds = false;
            var total = new Extents3d();

            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var id in ids)
                {
                    if (!id.IsValid || id.IsErased) continue;
                    var ent = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    if (ent != null && ent.Bounds.HasValue)
                    {
                        if (!hasBounds)
                        {
                            total = ent.Bounds.Value;
                            hasBounds = true;
                        }
                        else
                        {
                            total.AddExtents(ent.Bounds.Value);
                        }
                    }
                }
                tr.Commit();
            }

            return hasBounds ? (Extents3d?)total : null;
        }

        public static void ClearModelSpace(Database db)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var space = (BlockTableRecord)tr.GetObject(db.CurrentSpaceId, OpenMode.ForWrite);
                foreach (ObjectId id in space)
                {
                    if (!id.IsValid || id.IsErased) continue;
                    var obj = tr.GetObject(id, OpenMode.ForWrite, false);
                    if (obj != null && !obj.IsErased)
                    {
                        obj.Erase();
                    }
                }
                tr.Commit();
            }
            LastIds.Clear();
        }

        private static string NextRev()
        {
            var path = Path.Combine(ScriptsDir, "dev_rev.txt");
            long rev = 100000;
            if (File.Exists(path))
            {
                long existing;
                if (long.TryParse(File.ReadAllText(path).Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out existing) && existing >= rev)
                {
                    rev = existing + 1;
                }
            }

            File.WriteAllText(path, rev.ToString(CultureInfo.InvariantCulture));
            return rev.ToString(CultureInfo.InvariantCulture);
        }

        private static void InvokeTest(string rev)
        {
            using (var args = new ResultBuffer(
                new TypedValue((int)LispDataType.Text, "TESTACPSCRIPT"),
                new TypedValue((int)LispDataType.Text, "DEV_PROXY"),
                new TypedValue((int)LispDataType.Text, "REV"),
                new TypedValue((int)LispDataType.Text, rev)))
            {
                var result = AcadApp.Invoke(args);
                if (result != null)
                {
                    result.Dispose();
                }
            }
        }

        private static void EnsureAdapter()
        {
            var linker = SystemObjects.DynamicLinker;
            if (linker.IsModuleLoaded("PnP3dACPAdapter.arx"))
            {
                return;
            }

            linker.LoadModule(AdapterPath, false, false);
        }

        // variants.map is the script index Plant 3D builds at startup. A script whose
        // name is missing there is invisible to TESTACPSCRIPT, which fails silently
        // (no exception, no dev_reload.log), so make sure the shell is indexed and
        // report precisely what happened when it is not.
        private enum ShellMapState
        {
            Registered,
            Written,
            Failed
        }

        private static ShellMapState EnsureShellRegistered(out string detail)
        {
            detail = null;
            var path = Path.Combine(ScriptsDir, "variants.map");

            try
            {
                if (File.Exists(path))
                {
                    foreach (var raw in File.ReadAllLines(path))
                    {
                        var line = raw.Trim();
                        if (line.Length == 0 || line[0] == '#')
                        {
                            continue;
                        }

                        var split = line.IndexOf('=');
                        var key = (split < 0 ? line : line.Substring(0, split)).Trim();
                        if (string.Equals(key, ShellName, StringComparison.OrdinalIgnoreCase))
                        {
                            return ShellMapState.Registered;
                        }
                    }
                }

                // Keep the file's original encoding: a BOM-less rewrite of a file whose
                // first line is BOM-prefixed would change how Plant 3D reads that line.
                var exists = File.Exists(path);
                var hadBom = false;
                var text = string.Empty;
                if (exists)
                {
                    var bytes = File.ReadAllBytes(path);
                    hadBom = bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
                    text = File.ReadAllText(path, Encoding.UTF8);
                }
                else
                {
                    Directory.CreateDirectory(ScriptsDir);
                }

                var builder = new StringBuilder(text);
                if (builder.Length > 0 && builder[builder.Length - 1] != '\n')
                {
                    builder.Append("\r\n");
                }

                builder.Append(ShellName).Append('=').Append(ShellName).Append("\r\n");
                File.WriteAllText(path, builder.ToString(), new UTF8Encoding(hadBom));
                detail = "已自动把 " + ShellName + "=" + ShellName + " 写入：" + path;
                return ShellMapState.Written;
            }
            catch (System.Exception ex)
            {
                detail = "写 " + path + " 失败：" + ex.Message;
                return ShellMapState.Failed;
            }
        }

        private static HashSet<ObjectId> Snapshot(Database db)
        {
            var ids = new HashSet<ObjectId>();
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var space = (BlockTableRecord)tr.GetObject(db.CurrentSpaceId, OpenMode.ForRead);
                foreach (ObjectId id in space)
                {
                    ids.Add(id);
                }

                tr.Commit();
            }

            return ids;
        }

        private static List<ObjectId> Added(Database db, HashSet<ObjectId> before)
        {
            var added = new List<ObjectId>();
            var after = Snapshot(db);
            foreach (var id in after)
            {
                if (!before.Contains(id))
                {
                    added.Add(id);
                }
            }

            return added;
        }

        public static void EraseLast(Database db)
        {
            if (LastIds.Count == 0)
            {
                return;
            }

            using (var tr = db.TransactionManager.StartTransaction())
            {
                for (var i = 0; i < LastIds.Count; i++)
                {
                    var id = LastIds[i];
                    if (!id.IsValid || id.IsErased || id.Database != db)
                    {
                        continue;
                    }

                    var obj = tr.GetObject(id, OpenMode.ForWrite, false);
                    if (obj != null && !obj.IsErased)
                    {
                        obj.Erase();
                    }
                }

                tr.Commit();
            }

            LastIds.Clear();
        }

        private static string ReadLog()
        {
            var path = Path.Combine(ScriptsDir, "dev_reload.log");
            if (!File.Exists(path))
            {
                return "(没有 dev_reload.log)";
            }

            return File.ReadAllText(path, Encoding.UTF8).Trim();
        }

        /// <summary>
        /// 从 Python traceback 里取出真正的异常行（最后一行，形如 "TypeError: ..."）。
        /// 用来把脚本的真实错误直接顶到消息开头，而不是埋在整段堆栈里。
        /// </summary>
        private static string ExtractTracebackCause(string log)
        {
            if (string.IsNullOrEmpty(log)) return "脚本执行失败，但日志为空。";

            var lines = log.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
            for (var i = lines.Length - 1; i >= 0; i--)
            {
                var line = lines[i].Trim();
                if (line.Length == 0) continue;
                // 跳过 DEV_PROXY 包装产生的文件帧，只留异常类型与信息
                if (line.StartsWith("File \"", StringComparison.Ordinal)) continue;
                return line;
            }
            return "脚本执行失败，但日志里没有可读的异常行。";
        }

        private static ScriptRunResult Fail(string message)
        {
            return new ScriptRunResult { Ok = false, Message = message };
        }

        private static void TryDeployProxyScript(string targetProxyPath)
        {
            try
            {
                var asmDir = Path.GetDirectoryName(typeof(ScriptRunner).Assembly.Location) ?? string.Empty;
                var candidates = new[]
                {
                    Path.Combine(asmDir, "Resources", "DEV_PROXY.py"),
                    Path.Combine(asmDir, "..", "Resources", "DEV_PROXY.py"),
                    Path.Combine(asmDir, "DEV_PROXY.py")
                };
                foreach (var c in candidates)
                {
                    if (File.Exists(c))
                    {
                        Directory.CreateDirectory(Path.GetDirectoryName(targetProxyPath));
                        File.Copy(c, targetProxyPath, true);
                        return;
                    }
                }
            }
            catch
            {
            }
        }

        public static void AttachEntityMetadata(
            Database db,
            IEnumerable<ObjectId> ids,
            string entryName,
            string scriptPath,
            string presetName,
            IDictionary<string, string> values)
        {
            if (db == null || ids == null) return;
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var rat = (RegAppTable)tr.GetObject(db.RegAppTableId, OpenMode.ForRead);
                    if (!rat.Has(RegAppName))
                    {
                        rat.UpgradeOpen();
                        var record = new RegAppTableRecord { Name = RegAppName };
                        rat.Add(record);
                        tr.AddNewlyCreatedDBObject(record, true);
                    }

                    var sb = new StringBuilder();
                    if (values != null)
                    {
                        foreach (var kv in values)
                        {
                            if (string.IsNullOrEmpty(kv.Key)) continue;
                            if (sb.Length > 0) sb.Append(";");
                            sb.Append(kv.Key).Append("=").Append(kv.Value ?? string.Empty);
                        }
                    }

                    foreach (var id in ids)
                    {
                        if (!id.IsValid || id.IsErased) continue;
                        var ent = tr.GetObject(id, OpenMode.ForWrite, false) as Entity;
                        if (ent == null) continue;
                        using (var rb = new ResultBuffer(
                            new TypedValue((int)DxfCode.ExtendedDataRegAppName, RegAppName),
                            new TypedValue((int)DxfCode.ExtendedDataAsciiString, entryName ?? string.Empty),
                            new TypedValue((int)DxfCode.ExtendedDataAsciiString, scriptPath ?? string.Empty),
                            new TypedValue((int)DxfCode.ExtendedDataAsciiString, presetName ?? string.Empty),
                            new TypedValue((int)DxfCode.ExtendedDataAsciiString, sb.ToString())))
                        {
                            ent.XData = rb;
                        }
                    }
                    tr.Commit();
                }
            }
            catch
            {
            }
        }

        public static EntityParamMetadata ReadEntityMetadata(Database db, ObjectId id)
        {
            if (db == null || id.IsNull || !id.IsValid || id.IsErased)
            {
                return null;
            }

            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var ent = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    if (ent == null) return null;

                    var rb = ent.GetXDataForApplication(RegAppName);
                    if (rb != null)
                    {
                        using (rb)
                        {
                            var arr = rb.AsArray();
                            if (arr != null && arr.Length >= 5)
                            {
                                var meta = new EntityParamMetadata
                                {
                                    EntryName = arr[1].Value != null ? arr[1].Value.ToString() : string.Empty,
                                    ScriptPath = arr[2].Value != null ? arr[2].Value.ToString() : string.Empty,
                                    PresetName = arr[3].Value != null ? arr[3].Value.ToString() : string.Empty
                                };
                                var paramStr = arr[4].Value != null ? arr[4].Value.ToString() : string.Empty;
                                ParseParamStringInto(paramStr, meta.Values);
                                return meta;
                            }
                        }
                    }
                }
            }
            catch
            {
            }

            // Fallback to last executed script metadata if available
            if (!string.IsNullOrEmpty(LastEntryName))
            {
                return new EntityParamMetadata
                {
                    EntryName = LastEntryName,
                    ScriptPath = LastScriptPath ?? string.Empty,
                    Values = new Dictionary<string, string>(LastValues, StringComparer.Ordinal)
                };
            }

            return null;
        }

        public static void ParseParamStringInto(string paramDef, IDictionary<string, string> target)
        {
            if (string.IsNullOrWhiteSpace(paramDef) || target == null) return;
            var pairs = paramDef.Split(new[] { ';', ',' }, StringSplitOptions.RemoveEmptyEntries);
            for (var i = 0; i < pairs.Length; i++)
            {
                var eq = pairs[i].IndexOf('=');
                if (eq > 0)
                {
                    var k = pairs[i].Substring(0, eq).Trim();
                    var v = pairs[i].Substring(eq + 1).Trim();
                    if (!string.IsNullOrEmpty(k))
                    {
                        target[k] = v;
                    }
                }
            }
        }
    }
}
