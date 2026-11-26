using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Text;
using System.Windows;

namespace P3dPyPad
{
    public enum LanguageOption
    {
        Auto = 0,
        Chinese = 1,
        English = 2
    }

    /// <summary>
    /// AutoCAD Plant 3D C# 插件中/英文双语国际化 (i18n) 管理器。
    /// 支持：
    /// 1. 默认自动匹配操作系统语言；
    /// 2. 用户在任意窗口手动切换并持久化保存至 %APPDATA%\P3dPyPad\settings.json；
    /// 3. 通过 WPF Application.Current.Resources 资源字典与事件驱动全局窗口与 Ribbon 实时热切换。
    /// </summary>
    public static class LocalizationManager
    {
        private static readonly string SettingsFile = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "P3dPyPad",
            "settings.json");

        private static LanguageOption _currentOption = LanguageOption.Auto;
        private static bool _effectiveIsChinese = true;

        public static event Action LanguageChanged;

        static LocalizationManager()
        {
            _currentOption = LoadConfiguredOption();
            _effectiveIsChinese = ResolveIsChinese(_currentOption);
            UpdateResourceDictionary();
        }

        public static LanguageOption CurrentOption => _currentOption;
        public static bool IsChinese => _effectiveIsChinese;
        public static string CurrentCultureCode => _effectiveIsChinese ? "zh-CN" : "en-US";

        public static LanguageOption DetectSystemOption()
        {
            try
            {
                var culture = CultureInfo.CurrentUICulture;
                if (culture.Name.StartsWith("zh", StringComparison.OrdinalIgnoreCase))
                {
                    return LanguageOption.Chinese;
                }
            }
            catch
            {
            }
            return LanguageOption.English;
        }

        private static bool ResolveIsChinese(LanguageOption option)
        {
            if (option == LanguageOption.Auto)
            {
                return DetectSystemOption() == LanguageOption.Chinese;
            }
            return option == LanguageOption.Chinese;
        }

        private static LanguageOption LoadConfiguredOption()
        {
            try
            {
                if (File.Exists(SettingsFile))
                {
                    var text = File.ReadAllText(SettingsFile, Encoding.UTF8);
                    if (text.Contains("\"language\":\"zh\"")) return LanguageOption.Chinese;
                    if (text.Contains("\"language\":\"en\"")) return LanguageOption.English;
                    if (text.Contains("\"language\":\"auto\"")) return LanguageOption.Auto;
                }
            }
            catch
            {
            }
            return LanguageOption.Auto;
        }

        private static void SaveConfiguredOption(LanguageOption option)
        {
            try
            {
                var dir = Path.GetDirectoryName(SettingsFile);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

                string langKey = option == LanguageOption.Chinese ? "zh" : (option == LanguageOption.English ? "en" : "auto");
                var json = "{\n  \"language\": \"" + langKey + "\"\n}";
                File.WriteAllText(SettingsFile, json, new UTF8Encoding(false));
            }
            catch
            {
            }
        }

        public static void SetLanguage(LanguageOption option)
        {
            _currentOption = option;
            _effectiveIsChinese = ResolveIsChinese(option);
            SaveConfiguredOption(option);
            UpdateResourceDictionary();

            try
            {
                LanguageChanged?.Invoke();
            }
            catch
            {
            }
        }

        public static string T(string key, string fallbackZh = null, string fallbackEn = null)
        {
            string val;
            var dict = _effectiveIsChinese ? StringsZh : StringsEn;
            if (dict.TryGetValue(key, out val))
            {
                return val;
            }
            return _effectiveIsChinese ? (fallbackZh ?? key) : (fallbackEn ?? fallbackZh ?? key);
        }

        private static readonly ResourceDictionary _stringResourceDict = new ResourceDictionary();

        public static ResourceDictionary ResourceDictionary => _stringResourceDict;

        public static void EnsureInitialized(FrameworkElement element = null)
        {
            try
            {
                if (Application.Current == null)
                {
                    try
                    {
                        var app = new Application
                        {
                            ShutdownMode = ShutdownMode.OnExplicitShutdown
                        };
                    }
                    catch { }
                }

                // 在非 WPF 原生宿主 (AutoCAD) 中，防止由于关闭窗口触发 WPF 默认的 OnLastWindowClose 导致 Application 进入关闭状态
                var currentApp = Application.Current;
                if (currentApp != null)
                {
                    try
                    {
                        if (currentApp.ShutdownMode != ShutdownMode.OnExplicitShutdown)
                        {
                            currentApp.ShutdownMode = ShutdownMode.OnExplicitShutdown;
                        }

                        // 若已误触发 IsShuttingDown，反射复位标志位，彻底杜绝 LoadComponent 抛出“应用程序对象正在关闭”
                        var fieldShuttingDown = typeof(Application).GetField("_isShuttingDown", BindingFlags.Instance | BindingFlags.NonPublic);
                        if (fieldShuttingDown != null && (bool)fieldShuttingDown.GetValue(currentApp))
                        {
                            fieldShuttingDown.SetValue(currentApp, false);
                        }

                        var fieldAppIsClosing = typeof(Application).GetField("_appIsClosing", BindingFlags.Instance | BindingFlags.NonPublic);
                        if (fieldAppIsClosing != null && (bool)fieldAppIsClosing.GetValue(currentApp))
                        {
                            fieldAppIsClosing.SetValue(currentApp, false);
                        }
                    }
                    catch { }
                }

                UpdateResourceDictionary();

                if (Application.Current != null && !Application.Current.Resources.MergedDictionaries.Contains(_stringResourceDict))
                {
                    Application.Current.Resources.MergedDictionaries.Add(_stringResourceDict);
                }

                if (element != null)
                {
                    if (!element.Resources.MergedDictionaries.Contains(_stringResourceDict))
                    {
                        element.Resources.MergedDictionaries.Add(_stringResourceDict);
                    }
                }
            }
            catch
            {
            }
        }

        private static void UpdateResourceDictionary()
        {
            try
            {
                var dict = _effectiveIsChinese ? StringsZh : StringsEn;
                foreach (var kv in dict)
                {
                    _stringResourceDict["Loc." + kv.Key] = kv.Value;
                }
            }
            catch
            {
            }
        }

        #region 双语字典清单

        private static readonly Dictionary<string, string> StringsZh = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            // 通用
            { "Ready", "就绪" },
            { "Browse", "浏览" },
            { "Close", "关闭" },

            // ScriptPadWindow
            { "PadWindowTitle", "Plant 3D 参数化构件单件测试器 (PYPAD)" },
            { "SelectScript", "选择脚本..." },
            { "NoScriptSelected", "未选择脚本" },
            { "PresetTable", "规格表..." },
            { "NoPresetTable", "无预设表" },
            { "SaveScript", "保存 (Ctrl+S)" },
            { "RunModelF5", "生成 3D 模型 (F5)" },
            { "PresetLabel", "规格" },
            { "ResetDefaults", "还原默认" },
            { "ParamNameColumn", "参数名" },
            { "ValueColumn", "取值" },
            { "ExecutionLogTitle", "执行与调试日志" },

            // BatchTestWindow
            { "BatchWindowTitle", "Plant 3D 构件批量测试器 (PYBATCH)" },
            { "ScriptDirLabel", "脚本目录:" },
            { "OutputDirLabel", "出图目录:" },
            { "StartBatchBtn", "开始批量测试" },
            { "StopBatchBtn", "停止" },
            { "FilterLabel", "结果筛选:" },
            { "FilterAll", "全部结果" },
            { "FilterSuccess", "仅看成功" },
            { "FilterFailed", "仅看失败" },
            { "OpenOutputDirBtn", "打开出图目录" },

            // Ribbon (脚本测试 / 批量测试 / 语言切换 / 关于)
            { "RibbonTabTitle", "参数化构件" },
            { "RibbonPanelTest", "测试" },
            { "RibbonBtnPad", "脚本测试" },
            { "RibbonBtnPadTip", "打开参数化构件单件测试器，实时热更新生成 3D 模型 (命令: PYPAD)" },
            { "RibbonBtnBatch", "批量测试" },
            { "RibbonBtnBatchTip", "批量运行目录下所有构件脚本，生成测试截图与测试报告 (命令: PYBATCH)" },
            { "RibbonPanelEquipment", "设备" },
            { "RibbonBtnEqCreate", "创建设备" },
            { "RibbonBtnEqCreateTip", "打开优化版 Plant 3D 设备浏览器，支持搜索、高清缩放预览与参数配置创建原生设备 (命令: PYEQCREATE)" },
            { "RibbonBtnEqEdit", "编辑设备" },
            { "RibbonBtnEqEditTip", "拾取图面上的 Plant 3D 设备，直观修改尺寸参数、位号与工程特性并实时更新 (命令: PYEQEDIT)" },
            { "RibbonPanelSettings", "设置" },
            { "RibbonBtnLangTip", "中英文双语界面即时切换 (中 / EN)" },
            { "RibbonBtnAbout", "关于" },
            { "RibbonBtnAboutTip", "查看 P3dPyPad 插件版本与功能说明 (命令: PYABOUT)" },
            { "AboutTitle", "关于 P3dPyPad" },
            { "AboutDesc", "AutoCAD Plant 3D 参数化构件开发与批量测试工具箱" },
            { "AboutVersion", "版本: v1.0.0 (2026.11)" },
            { "AboutLinksHeader", "项目与支持" },
            { "AboutDevLabel", "开发者：" },
            { "AboutRepoLabel", "仓库地址：" },
            { "AboutEmailLabel", "联系邮箱：" },
            { "AboutSponsorLabel", "赞助地址：" },
            { "AboutSponsorText", "爱发电 (Afdian)" },
            { "AboutLicenseLabel", "开源协议：" },
        };

        private static readonly Dictionary<string, string> StringsEn = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            // General
            { "Ready", "Ready" },
            { "Browse", "Browse" },
            { "Close", "Close" },

            // ScriptPadWindow
            { "PadWindowTitle", "Plant 3D Parametric Script Single Test Bench (PYPAD)" },
            { "SelectScript", "Select Script..." },
            { "NoScriptSelected", "No Script Selected" },
            { "PresetTable", "Presets..." },
            { "NoPresetTable", "No Preset Table" },
            { "SaveScript", "Save (Ctrl+S)" },
            { "RunModelF5", "Run & Build 3D (F5)" },
            { "PresetLabel", "Preset" },
            { "ResetDefaults", "Reset Defaults" },
            { "ParamNameColumn", "Parameter" },
            { "ValueColumn", "Value" },
            { "ExecutionLogTitle", "Execution & Debug Logs" },

            // BatchTestWindow
            { "BatchWindowTitle", "Plant 3D Batch Test Bench (PYBATCH)" },
            { "ScriptDirLabel", "Script Dir:" },
            { "OutputDirLabel", "Output Dir:" },
            { "StartBatchBtn", "Start Batch Test" },
            { "StopBatchBtn", "Stop" },
            { "FilterLabel", "Filter:" },
            { "FilterAll", "All Results" },
            { "FilterSuccess", "Success Only" },
            { "FilterFailed", "Failed Only" },
            { "OpenOutputDirBtn", "Open Output Folder" },

            // Ribbon (Script Test / Batch Test / Language / About)
            { "RibbonTabTitle", "Parametric Components" },
            { "RibbonPanelTest", "Testing" },
            { "RibbonBtnPad", "Script Test" },
            { "RibbonBtnPadTip", "Open parametric single component test bench to generate 3D models (Command: PYPAD)" },
            { "RibbonBtnBatch", "Batch Test" },
            { "RibbonBtnBatchTip", "Batch run scripts in folder, auto-generate screenshots and test report (Command: PYBATCH)" },
            { "RibbonPanelEquipment", "Equipment" },
            { "RibbonBtnEqCreate", "Create Equipment" },
            { "RibbonBtnEqCreateTip", "Open modern Plant 3D equipment browser with search, zoomable preview and parameter editor (Command: PYEQCREATE)" },
            { "RibbonBtnEqEdit", "Edit Equipment" },
            { "RibbonBtnEqEditTip", "Pick a Plant 3D equipment in drawing to edit dimensions, tag and properties with live update (Command: PYEQEDIT)" },
            { "RibbonPanelSettings", "Settings" },
            { "RibbonBtnLangTip", "Switch UI language between Chinese and English (中 / EN)" },
            { "RibbonBtnAbout", "About" },
            { "RibbonBtnAboutTip", "View P3dPyPad plugin version and features (Command: PYABOUT)" },
            { "AboutTitle", "About P3dPyPad" },
            { "AboutDesc", "AutoCAD Plant 3D Parametric Component Dev & Batch Test Suite" },
            { "AboutVersion", "Version: v1.0.0 (2026.11)" },
            { "AboutLinksHeader", "Links & Support" },
            { "AboutDevLabel", "Developer: " },
            { "AboutRepoLabel", "Repository: " },
            { "AboutEmailLabel", "Email: " },
            { "AboutSponsorLabel", "Sponsor: " },
            { "AboutSponsorText", "Afdian (爱发电)" },
            { "AboutLicenseLabel", "License: " },
        };

        #endregion
    }
}
