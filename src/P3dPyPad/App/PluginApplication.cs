using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using Autodesk.AutoCAD.Runtime;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

[assembly: ExtensionApplication(typeof(P3dPyPad.PluginApplication))]
[assembly: CommandClass(typeof(P3dPyPad.PluginApplication))]

namespace P3dPyPad
{
    public sealed class PluginApplication : IExtensionApplication
    {
        private static ScriptPadWindow _window;
        private static BatchTestWindow _batchWindow;
        private static bool _ribbonAttached;

        static PluginApplication()
        {
            AppDomain.CurrentDomain.AssemblyResolve += ResolvePluginAssembly;
        }

        public void Initialize()
        {
            // 普通 AutoCAD 也会加载本程序集，这里直接静默退出：
            // 不创建 Ribbon，不写启动信息，不初始化任何 UI 侧资源。
            if (!ProductGuard.IsPlant3D)
            {
                return;
            }

            EnsureRibbon();

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.Editor.WriteMessage(
                    "\nP3dPyPad 已加载。命令: PYPAD 单个测试 | PYBATCH 批量测试 | " +
                    "PYBATCH_RUN 无人值守批量测试 | PYLANG 切换语言 | PYABOUT 关于\n");
            }
        }

        public void Terminate()
        {
            if (_window != null)
            {
                _window.Close();
                _window = null;
            }
            if (_batchWindow != null)
            {
                _batchWindow.Close();
                _batchWindow = null;
            }
        }

        [CommandMethod("PYPAD", CommandFlags.Session)]
        public void ShowPad()
        {
            if (!EnsurePlant3D()) return;
            OpenSingleTest(null);
        }

        [CommandMethod("PYBATCH", CommandFlags.Session)]
        public void ShowBatch()
        {
            if (!EnsurePlant3D()) return;
            OpenBatchTest(null);
        }

        /// <summary>
        /// 无人值守自动化批量测试入口：支持从命令行、LISP 或 COM 自动化静默调用，无需人工点开窗口。
        /// 可通过环境变量 P3D_BATCH_SRC / P3D_BATCH_OUT 覆盖输入输出目录。
        /// 执行完毕后自动写入 batch_report.json 与 unattended_done.flag。
        /// </summary>
        [CommandMethod("PYBATCH_RUN", CommandFlags.Session)]
        public void RunBatchHeadless()
        {
            if (!EnsurePlant3D()) return;

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null) return;

            var ed = doc.Editor;
            var srcEnv = Environment.GetEnvironmentVariable("P3D_BATCH_SRC");
            var outEnv = Environment.GetEnvironmentVariable("P3D_BATCH_OUT");

            var cfgFile = Path.Combine(Path.GetTempPath(), "p3d_batch_cfg.txt");
            if (File.Exists(cfgFile))
            {
                try
                {
                    var lines = File.ReadAllLines(cfgFile);
                    if (string.IsNullOrEmpty(srcEnv) && lines.Length > 0 && Directory.Exists(lines[0].Trim()))
                    {
                        srcEnv = lines[0].Trim();
                    }
                    if (string.IsNullOrEmpty(outEnv) && lines.Length > 1 && !string.IsNullOrEmpty(lines[1].Trim()))
                    {
                        outEnv = lines[1].Trim();
                    }
                }
                catch { }
            }

            var srcDir = !string.IsNullOrEmpty(srcEnv) && Directory.Exists(srcEnv)
                ? Path.GetFullPath(srcEnv)
                : null;

            if (string.IsNullOrEmpty(srcDir) || !Directory.Exists(srcDir))
            {
                ed.WriteMessage("\n[P3dPyPad] 未指定批量测试源目录，请设置 P3D_BATCH_SRC 或配置文件。\n");
                return;
            }

            var outDir = !string.IsNullOrEmpty(outEnv)
                ? Path.GetFullPath(outEnv)
                : null;
            if (string.IsNullOrEmpty(outDir))
            {
                ed.WriteMessage("\n[P3dPyPad] 未指定批量测试输出目录，请设置 P3D_BATCH_OUT 或配置文件。\n");
                return;
            }

            Directory.CreateDirectory(outDir);

            ed.WriteMessage(string.Format("\n[P3dPyPad] 开始无人值守批量测试...\n  源目录: {0}\n  输出目录: {1}\n", srcDir, outDir));

            var sw = System.Diagnostics.Stopwatch.StartNew();
            var results = BatchRunner.RunDirectory(
                doc,
                srcDir,
                outDir,
                recursive: true,
                onProgress: (item, cur, total) =>
                {
                    ed.WriteMessage(string.Format("\n[{0}/{1}] {2} -> {3} ({4}ms)",
                        cur, total, item.ScriptName, item.StatusDisplay, item.DurationMs));
                },
                isCancelled: () => false
            );
            sw.Stop();

            var reportPath = BatchReport.Write(outDir, srcDir, results, sw.Elapsed, false);
            var flagPath = Path.Combine(outDir, "unattended_done.flag");
            File.WriteAllText(flagPath, DateTime.Now.ToString("o") + "\n" + (reportPath ?? string.Empty));

            try
            {
                // 标记当前图形已保存，防止无人值守退出时被 AutoCAD“是否保存图形”提示阻塞挂起
                var prop = doc.GetType().GetProperty("AcadDocument");
                if (prop != null)
                {
                    var acadDoc = prop.GetValue(doc, null);
                    if (acadDoc != null)
                    {
                        var savedProp = acadDoc.GetType().GetProperty("Saved");
                        if (savedProp != null && savedProp.CanWrite)
                        {
                            savedProp.SetValue(acadDoc, true, null);
                        }
                    }
                }
            }
            catch { }

            ed.WriteMessage(string.Format("\n[P3dPyPad] 无人值守批量测试完成！总数: {0}, 耗时: {1:F1}s, 报告: {2}\n",
                results.Count, sw.Elapsed.TotalSeconds, reportPath));
        }

        [CommandMethod("PYLANG", CommandFlags.Session)]
        public void ToggleLanguage()
        {
            if (!EnsurePlant3D()) return;

            var next = LocalizationManager.IsChinese ? LanguageOption.English : LanguageOption.Chinese;
            LocalizationManager.SetLanguage(next);
            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                doc.Editor.WriteMessage(string.Format("\nP3dPyPad: UI 语言已切换为 {0} ({1})\n",
                    LocalizationManager.IsChinese ? "中文 (Chinese)" : "English",
                    LocalizationManager.CurrentCultureCode));
            }
        }

        [CommandMethod("PYABOUT", CommandFlags.Session)]
        public void ShowAbout()
        {
            if (!EnsurePlant3D()) return;

            var win = new AboutWindow();
            AcadApp.ShowModalWindow(win);
        }

        public static void OpenSingleTest(string scriptPath)
        {
            if (!ProductGuard.EnsurePlant3D()) return;

            if (_window == null)
            {
                _window = new ScriptPadWindow();
                _window.Closed += delegate { _window = null; };
                AcadApp.ShowModelessWindow(_window);
            }
            else
            {
                if (_window.WindowState == System.Windows.WindowState.Minimized)
                {
                    _window.WindowState = System.Windows.WindowState.Normal;
                }
                _window.Activate();
            }

            if (!string.IsNullOrEmpty(scriptPath) && File.Exists(scriptPath))
            {
                _window.OpenScriptPath(scriptPath);
            }
        }

        public static void OpenBatchTest(string folderPath)
        {
            if (!ProductGuard.EnsurePlant3D()) return;

            if (_batchWindow == null)
            {
                _batchWindow = new BatchTestWindow();
                _batchWindow.Closed += delegate { _batchWindow = null; };
                AcadApp.ShowModelessWindow(_batchWindow);
            }
            else
            {
                if (_batchWindow.WindowState == System.Windows.WindowState.Minimized)
                {
                    _batchWindow.WindowState = System.Windows.WindowState.Normal;
                }
                _batchWindow.Activate();
            }

            if (!string.IsNullOrEmpty(folderPath) && Directory.Exists(folderPath))
            {
                _batchWindow.SetSourceDirectory(folderPath);
            }
        }

        private static Assembly ResolvePluginAssembly(object sender, ResolveEventArgs args)
        {
            var name = new AssemblyName(args.Name).Name + ".dll";
            var folder = Path.GetDirectoryName(typeof(PluginApplication).Assembly.Location);
            var searchDirs = new[]
            {
                folder,
                AppDomain.CurrentDomain.BaseDirectory,
                Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "PLNT3D"),
            };

            foreach (var dir in searchDirs)
            {
                if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) continue;
                var candidate = Path.Combine(dir, name);
                if (File.Exists(candidate))
                {
                    return Assembly.LoadFrom(candidate);
                }
            }

            return null;
        }

        private static bool EnsurePlant3D()
        {
            if (!ProductGuard.EnsurePlant3D())
            {
                return false;
            }

            EnsureRibbon();
            return true;
        }

        private static void EnsureRibbon()
        {
            if (_ribbonAttached)
            {
                return;
            }

            try
            {
                LocalizationManager.EnsureInitialized();
            }
            catch { }

            try
            {
                RibbonSetup.AttachToComponentManager();
                _ribbonAttached = true;
            }
            catch { }
        }
    }
}
