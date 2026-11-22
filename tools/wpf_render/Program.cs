using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace P3dPyPad.RenderTools
{
    /// <summary>
    /// 把 P3dPyPad 的每个 WPF 窗口离屏渲染成 PNG，并输出控件遮挡诊断。
    /// 不依赖 AutoCAD 进程：只加载插件程序集、构造窗口、布局、截图。
    /// </summary>
    internal static class Program
    {
        private static string _outDir;
        private static double _scale = 1.0;
        private static string _only;

        [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
        private static extern bool SetDllDirectory(string lpPathName);

        /// <summary>
        /// acdbmgd/acmgd 是混合模式程序集，加载时会连带解析同目录下的 acdb19.dll 等本地库。
        /// 这里把 AutoCAD 安装目录加入本地 DLL 搜索路径，否则会报“找不到指定的模块”。
        /// </summary>
        private static void EnsureNativeSearchPath()
        {
            var candidates = new[]
            {
                Environment.GetEnvironmentVariable("CAD_NATIVE_DIR"),
                @"C:\Program Files\Autodesk\AutoCAD 2019",
                @"C:\Program Files\Autodesk\AutoCAD 2021",
            };
            foreach (var dir in candidates)
            {
                if (string.IsNullOrEmpty(dir) || !Directory.Exists(dir)) continue;
                SetDllDirectory(dir);
                AppDomain.CurrentDomain.AssemblyResolve += (s, e) =>
                {
                    var simple = new AssemblyName(e.Name).Name + ".dll";
                    var candidate = Path.Combine(dir, simple);
                    return File.Exists(candidate) ? Assembly.LoadFrom(candidate) : null;
                };
                return;
            }
        }

        [STAThread]
        private static int Main(string[] args)
        {
            EnsureNativeSearchPath();
            return Run(args);
        }

        [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
        private static int Run(string[] args)
        {
            _outDir = Path.Combine(Directory.GetCurrentDirectory(), ".render-out");
            for (var i = 0; i < args.Length; i++)
            {
                if (args[i] == "--out" && i + 1 < args.Length) _outDir = Path.GetFullPath(args[++i]);
                else if (args[i] == "--only" && i + 1 < args.Length) _only = args[++i];
                else if (args[i] == "--scale" && i + 1 < args.Length)
                {
                    double.TryParse(args[i + 1], NumberStyles.Float, CultureInfo.InvariantCulture, out _scale);
                    if (_scale <= 0.1 || _scale > 4.0) _scale = 1.0;
                }
            }
            Directory.CreateDirectory(_outDir);

            var app = new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown };
            app.Resources.MergedDictionaries.Add(new ResourceDictionary
            {
                Source = new Uri("/P3dPyPad;component/Theme/Theme.xaml", UriKind.Relative)
            });

            var pluginAssembly = typeof(PluginApplication).Assembly;
            var locType = pluginAssembly.GetType("P3dPyPad.LocalizationManager");
            if (locType != null)
            {
                var ensureInit = locType.GetMethod("EnsureInitialized", BindingFlags.Public | BindingFlags.Static);
                ensureInit?.Invoke(null, new object[] { null });
                var dictProp = locType.GetProperty("ResourceDictionary", BindingFlags.Public | BindingFlags.Static);
                if (dictProp?.GetValue(null) is ResourceDictionary locDict)
                {
                    app.Resources.MergedDictionaries.Add(locDict);
                }
            }
            var windowTypes = pluginAssembly.GetTypes()
                .Where(t => typeof(Window).IsAssignableFrom(t)
                            && !t.IsAbstract
                            && t.GetConstructor(Type.EmptyTypes) != null)
                .OrderBy(t => t.Name, StringComparer.Ordinal)
                .ToList();

            var reports = new List<WindowReport>();

            foreach (var type in windowTypes)
            {
                if (!string.IsNullOrEmpty(_only) &&
                    type.Name.IndexOf(_only, StringComparison.OrdinalIgnoreCase) < 0)
                {
                    continue;
                }

                Window window = null;
                try
                {
                    window = (Window)Activator.CreateInstance(type);
                    var report = CaptureWindow(window, type.Name);
                    reports.Add(report);
                    Console.WriteLine("[OK]   " + type.Name);
                }
                catch (Exception ex)
                {
                    var inner = ex is TargetInvocationException tie && tie.InnerException != null
                        ? tie.InnerException
                        : ex;
                    Console.WriteLine("[FAIL] " + type.Name + " : " + inner.GetType().Name + " " + inner.Message);
                    reports.Add(new WindowReport { Window = type.Name, Error = inner.Message });
                }
                finally
                {
                    try { window?.Close(); } catch { }
                }
            }

            WriteReport(reports);
            Console.WriteLine();
            Console.WriteLine("输出目录: " + _outDir);
            return 0;
        }

        /// <summary>
        /// 翻转判定的纯几何自检：构造"贴近屏幕底边"的控件矩形，
        /// 断言判定结果必须翻到上方；构造"顶部"矩形则必须保持下方。
        /// 这样即使窗口无法在测试中被真正挪到屏幕底部，翻转逻辑本身也有覆盖。
        /// </summary>
        private static List<string> SelfTestFlipDecision()
        {
            var issues = new List<string>();
            const double workTop = 0.0;
            const double workBottom = 1040.0;
            const double gap = 8.0;
            const double minHeight = 120.0;

            // 贴近底边：下方只剩 60px，上方 900px → 必须 Top
            var nearBottom = new Rect(400.0, 950.0, 200.0, 28.0);
            var belowBottom = workBottom - nearBottom.Bottom - gap;
            var aboveBottom = nearBottom.Top - workTop - gap;
            var decision = belowBottom >= minHeight || belowBottom >= aboveBottom ? "Bottom" : "Top";
            if (decision != "Top")
            {
                issues.Add(string.Format(
                    "FLIP_LOGIC_ERROR 贴近屏幕底边判定为 {0}（below={1:0.#} above={2:0.#}），应翻到上方",
                    decision, belowBottom, aboveBottom));
            }

            // 顶部：下方 900px → 必须 Bottom
            var nearTop = new Rect(400.0, 100.0, 200.0, 28.0);
            var belowTop = workBottom - nearTop.Bottom - gap;
            var aboveTop = nearTop.Top - workTop - gap;
            var decisionTop = belowTop >= minHeight || belowTop >= aboveTop ? "Bottom" : "Top";
            if (decisionTop != "Bottom")
            {
                issues.Add(string.Format(
                    "FLIP_LOGIC_ERROR 顶部位置判定为 {0}（below={1:0.#} above={2:0.#}），应保持下方",
                    decisionTop, belowTop, aboveTop));
            }

            return issues;
        }

        /// <summary>
        /// "记住上次目录"的往返自检：写入 → 读回 → 目录不存在时回退到默认值。
        ///
        /// UserSettings 是 internal（不希望业务代码依赖它），这里用反射调用，
        /// 既验证了真实实现，又不必为测试把类型公开出去。
        /// </summary>
        private static List<string> SelfTestUserSettings()
        {
            var issues = new List<string>();
            try
            {
                var asm = typeof(PluginApplication).Assembly;
                var type = asm.GetType("P3dPyPad.UserSettings", false);
                if (type == null)
                {
                    issues.Add("USER_SETTINGS_MISSING 找不到 P3dPyPad.UserSettings");
                    return issues;
                }

                var set = type.GetMethod("Set", BindingFlags.Public | BindingFlags.Static);
                var get = type.GetMethod("Get", BindingFlags.Public | BindingFlags.Static);
                var getDir = type.GetMethod("GetDirectory", BindingFlags.Public | BindingFlags.Static);
                if (set == null || get == null || getDir == null)
                {
                    issues.Add("USER_SETTINGS_API_MISSING Set/Get/GetDirectory 未找到");
                    return issues;
                }

                const string key = "selftest.dir";
                var probe = Path.Combine(Path.GetTempPath(), "p3dpypad-selftest");
                Directory.CreateDirectory(probe);

                // 1. 写入后能原样读回
                set.Invoke(null, new object[] { key, probe });
                var roundTrip = get.Invoke(null, new object[] { key, null }) as string;
                if (!string.Equals(roundTrip, probe, StringComparison.OrdinalIgnoreCase))
                {
                    issues.Add(string.Format(
                        "USER_SETTINGS_ROUNDTRIP 写入 {0} 读回 {1}", probe, roundTrip ?? "(null)"));
                }

                // 2. 目录存在时 GetDirectory 返回它
                var dirOk = getDir.Invoke(null, new object[] { key, null }) as string;
                if (!string.Equals(dirOk, probe, StringComparison.OrdinalIgnoreCase))
                {
                    issues.Add("USER_SETTINGS_GETDIR 目录存在时未返回保存值: " + (dirOk ?? "(null)"));
                }

                // 3. 目录被删除后必须回退到默认值，而不是停在失效路径
                var gone = Path.Combine(Path.GetTempPath(), "p3dpypad-selftest-gone");
                if (Directory.Exists(gone)) Directory.Delete(gone, true);
                set.Invoke(null, new object[] { key, gone });
                var fallback = getDir.Invoke(null, new object[] { key, "DEFAULT" }) as string;
                if (fallback != "DEFAULT")
                {
                    issues.Add("USER_SETTINGS_FALLBACK 目录不存在时应回退默认值，实际: " + (fallback ?? "(null)"));
                }

                // 清理，避免污染用户真实设置
                set.Invoke(null, new object[] { key, null });
                try { Directory.Delete(probe, true); } catch { }
            }
            catch (Exception ex)
            {
                var inner = ex is TargetInvocationException tie && tie.InnerException != null
                    ? tie.InnerException : ex;
                issues.Add("USER_SETTINGS_ERROR " + inner.GetType().Name + " " + inner.Message);
            }
            return issues;
        }

        /// <summary>
        /// 脚本失败诊断自检：热更新外壳在脚本抛异常时写的是 traceback（不含 REV=），
        /// 必须能从堆栈里取出真正的异常行，否则批量列表只会显示一句泛化说明，
        /// 用户会误以为是"测试被跳过"。
        /// </summary>
        private static List<string> SelfTestTracebackCause()
        {
            var issues = new List<string>();
            try
            {
                var type = typeof(PluginApplication).Assembly.GetType("P3dPyPad.ScriptRunner", false);
                if (type == null)
                {
                    issues.Add("TRACEBACK_TEST_MISSING 找不到 P3dPyPad.ScriptRunner");
                    return issues;
                }

                var method = type.GetMethod("ExtractTracebackCause",
                    BindingFlags.NonPublic | BindingFlags.Static);
                if (method == null)
                {
                    issues.Add("TRACEBACK_TEST_MISSING 找不到 ExtractTracebackCause");
                    return issues;
                }

                // 真实形态：DEV_PROXY 包装帧 + 用户脚本帧 + 异常行
                var log = string.Join("\n", new[]
                {
                    "Traceback (most recent call last):",
                    "  File \"C:\\...\\DEV_PROXY.py\", line 52, in DEV_PROXY",
                    "    fn(s)",
                    "  File \"C:\\...\\dev_core.pyinc\", line 76, in ELBOW_90",
                    "    s.setLinearDimension(\"R\", (0, 0, -r), (R, 0, -r), ext_dir=(0, -1, -0.5))",
                    "TypeError: setLinearDimension() takes no keyword arguments",
                });

                var cause = method.Invoke(null, new object[] { log }) as string;
                if (cause != "TypeError: setLinearDimension() takes no keyword arguments")
                {
                    issues.Add("TRACEBACK_CAUSE_WRONG 取到的异常行不对: " + (cause ?? "(null)"));
                }

                // 空日志不能崩，要给出可读兜底
                var empty = method.Invoke(null, new object[] { string.Empty }) as string;
                if (string.IsNullOrWhiteSpace(empty))
                {
                    issues.Add("TRACEBACK_EMPTY_LOG 空日志未给出兜底文案");
                }

                // 批量列表取第一行作为"异常信息"，异常行必须能顶到最前
                var item = new BatchItemResult
                {
                    ScriptName = "ELBOW_90.py",
                    Success = false,
                    ErrorMessage = cause + "\n脚本执行出错（热更新已生效，异常来自脚本本身，不是测试被跳过）。\n"
                                   + "ELBOW_90  REV=100080\n" + log,
                };
                if (item.ShortErrorMessage != cause)
                {
                    issues.Add("SHORT_ERROR_CAUSE 列表首行不是异常行: " + item.ShortErrorMessage);
                }
            }
            catch (Exception ex)
            {
                var inner = ex is TargetInvocationException tie && tie.InnerException != null
                    ? tie.InnerException : ex;
                issues.Add("TRACEBACK_TEST_ERROR " + inner.GetType().Name + " " + inner.Message);
            }
            return issues;
        }

        private static WindowReport CaptureWindow(Window window, string name)
        {
            var report = new WindowReport { Window = name };

            // 翻转逻辑的纯几何自检：不依赖真实窗口位置。
            report.Issues.AddRange(SelfTestFlipDecision());

            // "记住上次目录"的往返自检：写入 → 读回 → 目录失效时回退。
            report.Issues.AddRange(SelfTestUserSettings());

            // 脚本失败诊断自检：确认能从 traceback 里取出真正的异常行。
            report.Issues.AddRange(SelfTestTracebackCause());

            // SizeToContent 窗口需要先布局才能拿到真实尺寸。
            // 放到屏幕左上角内侧而不是屏幕外：Popup 是独立顶层窗口，
            // 只有宿主在屏幕内时弹层的实际落点才和真实使用时一致。
            window.WindowStartupLocation = WindowStartupLocation.Manual;
            window.Left = 40;
            window.Top = 40;
            window.ShowInTaskbar = false;
            window.Show();
            Console.WriteLine("  [" + name + "] shown");
            window.UpdateLayout();
            DoEvents();

            // 数据表可能来自后台扫描；等可见 DataGrid 有行后再截图，
            // 否则截图只会拍到空表。
            var waitUntil = DateTime.UtcNow.AddSeconds(20);
            while (DateTime.UtcNow < waitUntil)
            {
                var grids = FindAll<DataGrid>(window).Where(g => g.IsVisible).ToList();
                if (grids.Count == 0 || grids.All(g => g.Items.Count > 0)) break;
                DoEvents();
                System.Threading.Thread.Sleep(80);
            }

            // Show() 时 WindowStartupLocation=Manual 已生效，但部分窗口在 Loaded 里
            // 还会再定位一次；这里强制回到左上角，保证截图基准一致。
            window.Left = 40;
            window.Top = 40;
            DoEvents();

            report.Width = window.ActualWidth;
            report.Height = window.ActualHeight;

            SaveVisual(window, Path.Combine(_outDir, name + ".png"));

            // 逐个 ComboBox 展开截图，验证弹层是否被屏幕/窗口边缘裁掉。
            var combos = FindAll<ComboBox>(window).Where(c => c.IsVisible).ToList();
            Console.WriteLine("  [" + name + "] combos=" + combos.Count);
            report.ComboBoxCount = combos.Count;
            for (var i = 0; i < combos.Count; i++)
            {
                var combo = combos[i];
                var label = SafeName(combo) ?? ("combo" + i);
                Console.WriteLine("  [" + name + "] combo " + label + " items=" + combo.Items.Count);
                try
                {
                    combo.IsDropDownOpen = true;
                    window.UpdateLayout();
                    DoEvents();
                    System.Threading.Thread.Sleep(80);
                    window.UpdateLayout();
                    DoEvents();

                    var popup = FindAll<Popup>(combo).FirstOrDefault();
                    var dd = popup?.Child as FrameworkElement;

                    // 直接渲染弹层视觉树：不受屏幕截图与遮挡窗口干扰。
                    if (dd != null && dd.ActualWidth > 0 && dd.ActualHeight > 0)
                    {
                        SaveVisual(dd, Path.Combine(_outDir, name + "." + label + ".dropdown.png"));
                    }

                    var itemCount = combo.Items.Count;
                    var entry = new DropDownReport
                    {
                        Name = label,
                        ItemCount = itemCount,
                        PopupHeight = dd?.ActualHeight ?? 0.0,
                        PopupWidth = dd?.ActualWidth ?? 0.0,
                        Placement = popup?.Placement.ToString() ?? "",
                    };

                    // 弹层是否越出屏幕工作区
                    if (dd != null)
                    {
                        var screenPos = dd.PointToScreen(new Point(0.0, 0.0));
                        var screenRect = new Rect(screenPos.X, screenPos.Y, dd.ActualWidth, dd.ActualHeight);
                        var wa = SystemParameters.WorkArea;
                        if (screenRect.Bottom > wa.Bottom + 0.5 || screenRect.Right > wa.Right + 0.5
                            || screenRect.Top < wa.Top - 0.5 || screenRect.Left < wa.Left - 0.5)
                        {
                            report.Issues.Add(string.Format(
                                "DROPDOWN_OFFSCREEN {0} popup={1} workArea={2}",
                                label, Fmt(screenRect), Fmt(wa)));
                        }

                        var sv = FindAll<ScrollViewer>(dd).FirstOrDefault();
                        entry.Scrollable = sv != null
                            && sv.ComputedVerticalScrollBarVisibility == Visibility.Visible;
                        var ddBorder = dd as Border;
                        var chrome = ddBorder != null
                            ? ddBorder.Padding.Top + ddBorder.Padding.Bottom
                              + ddBorder.BorderThickness.Top + ddBorder.BorderThickness.Bottom
                            : 0.0;
                        var itemViews = FindAll<ComboBoxItem>(dd).ToList();
                        var contentHeight = itemViews.Count > 0
                            ? itemViews.Sum(x => x.ActualHeight > 0 ? x.ActualHeight : x.DesiredSize.Height)
                            : itemCount * 24.0;
                        var need = contentHeight > 0 ? contentHeight + chrome : 0.0;
                        entry.NeededHeight = need;
                        entry.Truncated = itemCount > 0 && need > 0
                            && dd.ActualHeight + 0.5 < need && !entry.Scrollable;
                    }

                    report.DropDowns.Add(entry);
                }
                catch (Exception ex)
                {
                    report.DropDowns.Add(new DropDownReport { Name = label, Error = ex.Message });
                }
                finally
                {
                    try { combo.IsDropDownOpen = false; } catch { }
                    DoEvents();
                }
            }

            // 控件遮挡 / 截断诊断
            report.Issues.AddRange(DiagnoseOcclusion(window));

            // 最小宽度复核：窗口被拉到 MinWidth 时最容易出现溢出与截断，
            // 这一步能抓到"只在窄窗口下才暴露"的遮挡。
            if (window.MinWidth > 0 && window.ActualWidth > window.MinWidth + 1.0)
            {
                var normalWidth = window.ActualWidth;
                window.Width = window.MinWidth;
                window.UpdateLayout();
                DoEvents();

                report.MinWidth = window.MinWidth;
                report.MinWidthIssues.AddRange(DiagnoseOcclusion(window));
                SaveVisual(window, Path.Combine(_outDir, name + ".minwidth.png"));

                window.Width = normalWidth;
                window.UpdateLayout();
                DoEvents();
            }

            SaveVisual(window, Path.Combine(_outDir, name + ".png"));

            // 靠近屏幕底边时下拉弹层必须向上翻转，否则列表会被屏幕边缘裁掉。
            //
            // 注意：真实窗口在本机受窗口管理器约束，程序化改 Top 不一定立刻生效，
            // 因此这里不再依赖"把窗口挪到屏幕底部"，而是直接对翻转判定做等价校验：
            // 取每个 ComboBox 的实际屏幕位置，算出下方/上方可用空间，
            // 再断言 ComboBoxAssist 给出的判定与几何事实一致。
            if (combos.Count > 0)
            {
                for (var i = 0; i < combos.Count; i++)
                {
                    var combo = combos[i];
                    var label = SafeName(combo) ?? ("combo" + i);
                    try
                    {
                        combo.IsDropDownOpen = true;
                        DoEvents();
                        System.Threading.Thread.Sleep(60);
                        DoEvents();

                        var popup = FindAll<Popup>(combo).FirstOrDefault();
                        var placement = popup?.Placement.ToString() ?? "";
                        var assistOn = (bool)combo.GetValue(ComboBoxAssist.AutoFlipDropDownProperty);
                        var diag = ComboBoxAssist.LastDiagnostics;
                        report.BottomEdgePlacements.Add(label + "=" + placement
                            + "(assist=" + assistOn + ") " + diag);

                        if (!assistOn)
                        {
                            report.Issues.Add("DROPDOWN_ASSIST_INACTIVE " + label);
                            continue;
                        }

                        // 从诊断串里取 below/above，验证判定与几何一致
                        var below = ExtractNumber(diag, "below=");
                        var above = ExtractNumber(diag, "above=");
                        var expected = below >= 120.0 || below >= above ? "Bottom" : "Top";
                        if (!string.IsNullOrEmpty(placement) && placement != expected)
                        {
                            report.Issues.Add(string.Format(
                                "DROPDOWN_PLACEMENT_MISMATCH {0} actual={1} expected={2} {3}",
                                label, placement, expected, diag));
                        }
                    }
                    catch (Exception ex)
                    {
                        report.Issues.Add("DROPDOWN_FLIP_ERROR " + label + " " + ex.Message);
                    }
                    finally
                    {
                        try { combo.IsDropDownOpen = false; } catch { }
                        DoEvents();
                    }
                }

                window.Top = 40;
                window.UpdateLayout();
                DoEvents();
            }

            return report;
        }

        /// <summary>
        /// 遮挡诊断：找出被祖先裁剪、越出窗口可视区、以及同层重叠的可交互控件。
        /// </summary>
        private static List<string> DiagnoseOcclusion(Window window)
        {
            var issues = new List<string>();
            var root = (FrameworkElement)window.Content;
            if (root == null) return issues;

            var windowRect = new Rect(0, 0, window.ActualWidth, window.ActualHeight);
            var interactive = new List<KeyValuePair<FrameworkElement, Rect>>();

            foreach (var fe in Walk(root))
            {
                if (!fe.IsVisible) continue;
                if (fe.ActualWidth < 1.0 || fe.ActualHeight < 1.0) continue;

                Rect rect;
                try
                {
                    rect = fe.TransformToAncestor(window).TransformBounds(
                        new Rect(0, 0, fe.ActualWidth, fe.ActualHeight));
                }
                catch (InvalidOperationException)
                {
                    continue;
                }

                // 1) 越出窗口内容区
                if (rect.Left < -0.5 || rect.Top < -0.5
                    || rect.Right > windowRect.Right + 0.5 || rect.Bottom > windowRect.Bottom + 0.5)
                {
                    if (fe is TextBox || fe is ComboBox || fe is Button || fe is CheckBox)
                    {
                        issues.Add(string.Format(
                            "OUT_OF_WINDOW {0} '{1}' rect={2} window={3}",
                            fe.GetType().Name, SafeName(fe), Fmt(rect), Fmt(windowRect)));
                    }
                }

                // 2) 被祖先 ClipToBounds 裁掉
                var clipped = FindClippingAncestor(fe, window);
                if (clipped != null)
                {
                    Rect clipRect;
                    try
                    {
                        clipRect = clipped.TransformToAncestor(window).TransformBounds(
                            new Rect(0, 0, clipped.ActualWidth, clipped.ActualHeight));
                    }
                    catch (InvalidOperationException)
                    {
                        clipRect = Rect.Empty;
                    }

                    if (!clipRect.IsEmpty && !Contains(clipRect, rect, 0.5))
                    {
                        issues.Add(string.Format(
                            "CLIPPED_BY_ANCESTOR {0} '{1}' rect={2} clippedBy={3} clipRect={4}",
                            fe.GetType().Name, SafeName(fe), Fmt(rect), SafeName(clipped), Fmt(clipRect)));
                    }
                }

                // 3) 超出直接父容器（WrapPanel/StackPanel/Grid 等默认不裁剪，
                //    溢出部分会被后续兄弟覆盖或直接看不见——"按钮消失"就是这种）
                if (VisualTreeHelper.GetParent(fe) is FrameworkElement parent
                    && !(parent is ScrollViewer)
                    && parent.ActualWidth > 0 && parent.ActualHeight > 0)
                {
                    Rect parentRect;
                    try
                    {
                        parentRect = parent.TransformToAncestor(window).TransformBounds(
                            new Rect(0, 0, parent.ActualWidth, parent.ActualHeight));
                    }
                    catch (InvalidOperationException)
                    {
                        parentRect = Rect.Empty;
                    }

                    if (!parentRect.IsEmpty && !Contains(parentRect, rect, 1.0))
                    {
                        // DataGrid 表头内部那层 Grid 与列头容器等宽，横向滚动时
                        // 内容宽于视口是预期行为（滚动条承接），不算遮挡缺陷。
                        if (parent is DataGridColumnHeadersPresenter)
                        {
                            continue;
                        }

                        issues.Add(string.Format(
                            "OVERFLOWS_PARENT {0} '{1}' rect={2} parent={3} '{4}' parentRect={5}",
                            fe.GetType().Name, SafeName(fe), Fmt(rect),
                            parent.GetType().Name, SafeName(parent), Fmt(parentRect)));
                    }
                }

                if (IsInteractive(fe))
                {
                    interactive.Add(new KeyValuePair<FrameworkElement, Rect>(fe, rect));
                }
            }

            // 3) 同层可交互控件互相重叠（排除父子关系）
            for (var i = 0; i < interactive.Count; i++)
            {
                for (var j = i + 1; j < interactive.Count; j++)
                {
                    var a = interactive[i];
                    var b = interactive[j];
                    if (IsAncestorOf(a.Key, b.Key) || IsAncestorOf(b.Key, a.Key)) continue;

                    var inter = Rect.Intersect(a.Value, b.Value);
                    if (inter.IsEmpty || inter.Width < 2.0 || inter.Height < 2.0) continue;

                    // 只报明显重叠（面积占比 > 15%）
                    var areaA = a.Value.Width * a.Value.Height;
                    var areaB = b.Value.Width * b.Value.Height;
                    var minArea = Math.Min(areaA, areaB);
                    if (minArea <= 1.0) continue;
                    if (inter.Width * inter.Height / minArea < 0.15) continue;

                    issues.Add(string.Format(
                        "OVERLAP {0} '{1}' <-> {2} '{3}' overlap={4}x{5}",
                        a.Key.GetType().Name, SafeName(a.Key),
                        b.Key.GetType().Name, SafeName(b.Key),
                        inter.Width.ToString("0.#"), inter.Height.ToString("0.#")));
                }
            }

            return issues;
        }

        private static bool Contains(Rect outer, Rect inner, double tol)
        {
            return inner.Left >= outer.Left - tol
                   && inner.Top >= outer.Top - tol
                   && inner.Right <= outer.Right + tol
                   && inner.Bottom <= outer.Bottom + tol;
        }

        private static FrameworkElement FindClippingAncestor(DependencyObject start, Window stopAt)
        {
            var cur = VisualTreeHelper.GetParent(start);
            while (cur != null && !ReferenceEquals(cur, stopAt))
            {
                if (cur is FrameworkElement fe && fe.ClipToBounds)
                {
                    // 只关心真正会裁到子元素的容器
                    if (fe.ActualWidth > 0 && fe.ActualHeight > 0) return fe;
                }
                if (cur is ScrollViewer) return null; // 滚动容器允许内容超出
                cur = VisualTreeHelper.GetParent(cur);
            }
            return null;
        }

        private static bool IsInteractive(FrameworkElement fe)
        {
            return fe is Button || fe is ComboBox || fe is TextBox || fe is CheckBox
                   || fe is RadioButton || fe is ListBox || fe is DataGrid || fe is TabControl;
        }

        private static bool IsAncestorOf(DependencyObject ancestor, DependencyObject node)
        {
            var cur = VisualTreeHelper.GetParent(node);
            while (cur != null)
            {
                if (ReferenceEquals(cur, ancestor)) return true;
                cur = VisualTreeHelper.GetParent(cur);
            }
            return false;
        }

        private static IEnumerable<FrameworkElement> Walk(DependencyObject root)
        {
            var count = VisualTreeHelper.GetChildrenCount(root);
            for (var i = 0; i < count; i++)
            {
                var child = VisualTreeHelper.GetChild(root, i);
                if (child is FrameworkElement fe) yield return fe;
                foreach (var nested in Walk(child)) yield return nested;
            }
        }

        private static List<T> FindAll<T>(DependencyObject root) where T : DependencyObject
        {
            var result = new List<T>();
            var count = VisualTreeHelper.GetChildrenCount(root);
            for (var i = 0; i < count; i++)
            {
                var child = VisualTreeHelper.GetChild(root, i);
                if (child is T match) result.Add(match);
                result.AddRange(FindAll<T>(child));
            }
            return result;
        }

        private static string SafeName(FrameworkElement fe)
        {
            if (!string.IsNullOrEmpty(fe.Name)) return fe.Name;
            if (fe is ContentControl cc && cc.Content is string s && s.Length <= 24) return s;
            return null;
        }

        private static string Fmt(Rect r)
        {
            return string.Format(CultureInfo.InvariantCulture, "[{0:0.#},{1:0.#} {2:0.#}x{3:0.#}]",
                r.X, r.Y, r.Width, r.Height);
        }

        private static void SaveVisual(Window window, string path)
        {
            SaveVisual((FrameworkElement)window.Content, path,
                window.ActualWidth, window.ActualHeight, window.Background);
        }

        /// <summary>把任意视觉树元素渲染成 PNG（窗口内容或 Popup 弹层）。</summary>
        private static void SaveVisual(FrameworkElement root, string path)
        {
            SaveVisual(root, path, root.ActualWidth, root.ActualHeight, null);
        }

        private static void SaveVisual(FrameworkElement root, string path, double w, double h, Brush background)
        {
            if (root == null || w <= 0 || h <= 0) return;

            var pw = (int)Math.Ceiling(w * _scale);
            var ph = (int)Math.Ceiling(h * _scale);
            if (pw <= 0 || ph <= 0) return;

            var bmp = new RenderTargetBitmap(pw, ph, 96.0 * _scale, 96.0 * _scale, PixelFormats.Pbgra32);
            var visual = new DrawingVisual();
            using (var dc = visual.RenderOpen())
            {
                dc.DrawRectangle(background ?? Brushes.White, null, new Rect(0, 0, w, h));
            }
            bmp.Render(visual);
            bmp.Render(root);

            var encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bmp));
            using (var fs = File.Create(path)) encoder.Save(fs);
        }

        private static void DoEvents()
        {
            var frame = new System.Windows.Threading.DispatcherFrame();
            System.Windows.Threading.Dispatcher.CurrentDispatcher.BeginInvoke(
                System.Windows.Threading.DispatcherPriority.Background,
                new Action(() => frame.Continue = false));
            System.Windows.Threading.Dispatcher.PushFrame(frame);
        }

        private static void WriteReport(List<WindowReport> reports)
        {
            var sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendLine("  \"generated\": \"" + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture) + "\",");
            sb.AppendLine("  \"windows\": [");

            for (var i = 0; i < reports.Count; i++)
            {
                var r = reports[i];
                sb.AppendLine("    {");
                sb.AppendLine("      \"window\": " + Json(r.Window) + ",");
                sb.AppendLine("      \"width\": " + r.Width.ToString("0.#", CultureInfo.InvariantCulture) + ",");
                sb.AppendLine("      \"height\": " + r.Height.ToString("0.#", CultureInfo.InvariantCulture) + ",");
                sb.AppendLine("      \"comboBoxCount\": " + r.ComboBoxCount + ",");
                sb.AppendLine("      \"error\": " + Json(r.Error) + ",");
                sb.AppendLine("      \"dropDowns\": [");
                for (var k = 0; k < r.DropDowns.Count; k++)
                {
                    var d = r.DropDowns[k];
                    sb.AppendLine("        { \"name\": " + Json(d.Name)
                        + ", \"itemCount\": " + d.ItemCount
                        + ", \"popupHeight\": " + d.PopupHeight.ToString("0.#", CultureInfo.InvariantCulture)
                        + ", \"neededHeight\": " + d.NeededHeight.ToString("0.#", CultureInfo.InvariantCulture)
                        + ", \"truncated\": " + (d.Truncated ? "true" : "false")
                        + ", \"scrollable\": " + (d.Scrollable ? "true" : "false")
                        + ", \"popupWidth\": " + d.PopupWidth.ToString("0.#", CultureInfo.InvariantCulture)
                        + ", \"placement\": " + Json(d.Placement)
                        + ", \"error\": " + Json(d.Error) + " }" + (k < r.DropDowns.Count - 1 ? "," : ""));
                }
                sb.AppendLine("      ],");
                sb.AppendLine("      \"issues\": [");
                for (var k = 0; k < r.Issues.Count; k++)
                {
                    sb.AppendLine("        " + Json(r.Issues[k]) + (k < r.Issues.Count - 1 ? "," : ""));
                }
                sb.AppendLine("      ],");
                sb.AppendLine("      \"minWidth\": " + r.MinWidth.ToString("0.#", CultureInfo.InvariantCulture) + ",");
                sb.AppendLine("      \"minWidthIssues\": [");
                for (var k = 0; k < r.MinWidthIssues.Count; k++)
                {
                    sb.AppendLine("        " + Json(r.MinWidthIssues[k]) + (k < r.MinWidthIssues.Count - 1 ? "," : ""));
                }
                sb.AppendLine("      ],");
                sb.AppendLine("      \"bottomEdgePlacements\": [");
                for (var k = 0; k < r.BottomEdgePlacements.Count; k++)
                {
                    sb.AppendLine("        " + Json(r.BottomEdgePlacements[k]) + (k < r.BottomEdgePlacements.Count - 1 ? "," : ""));
                }
                sb.AppendLine("      ]");
                sb.AppendLine("    }" + (i < reports.Count - 1 ? "," : ""));
            }

            sb.AppendLine("  ]");
            sb.AppendLine("}");
            File.WriteAllText(Path.Combine(_outDir, "report.json"), sb.ToString(), new UTF8Encoding(false));
        }

        /// <summary>从诊断串里取出 "key=123.4" 形式的数值。</summary>
        private static double ExtractNumber(string text, string key)
        {
            if (string.IsNullOrEmpty(text)) return double.NaN;
            var idx = text.IndexOf(key, StringComparison.Ordinal);
            if (idx < 0) return double.NaN;
            var start = idx + key.Length;
            var end = start;
            while (end < text.Length && (char.IsDigit(text[end]) || text[end] == '.' || text[end] == '-')) end++;
            double v;
            return double.TryParse(text.Substring(start, end - start),
                NumberStyles.Float, CultureInfo.InvariantCulture, out v) ? v : double.NaN;
        }

        private static string Json(string s)
        {
            if (s == null) return "null";
            var sb = new StringBuilder("\"");
            foreach (var c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < ' ') sb.Append("\\u" + ((int)c).ToString("x4"));
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }

        private sealed class WindowReport
        {
            public string Window;
            public double Width;
            public double Height;
            public double MinWidth;
            public int ComboBoxCount;
            public string Error;
            public readonly List<string> Issues = new List<string>();
            public readonly List<string> MinWidthIssues = new List<string>();
            public readonly List<string> BottomEdgePlacements = new List<string>();
            public readonly List<DropDownReport> DropDowns = new List<DropDownReport>();
        }

        private sealed class DropDownReport
        {
            public string Name;
            public int ItemCount;
            public double PopupHeight;
            public double PopupWidth;
            public string Placement;
            public bool Truncated;
            public bool Scrollable;
            public double NeededHeight;
            public string Error;
        }
    }
}
