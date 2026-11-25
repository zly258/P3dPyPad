using System;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.Windows;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    /// <summary>
    /// AutoCAD Plant 3D 原生 Ribbon 构建器：
    /// 纯色圆角色块 + 白色 Material Design 图标，按命令用颜色区分。
    /// 面板：【脚本测试 / 批量测试】与【语言切换 / 关于】。
    /// 同时监听启动空闲事件与工作空间切换（WSCURRENT / MENUNAME），防止 Plant 3D 切换三维配管工作空间后冲掉自定义选项卡。
    /// </summary>
    internal static class RibbonSetup
    {
        private const string TabId = "P3DPYPAD_TAB";
        private static readonly Uri IconDictionaryUri =
            new Uri("pack://application:,,,/P3dPyPad;component/Theme/Icons.xaml", UriKind.Absolute);
        private static ResourceDictionary _iconResources;
        private static bool _hooksRegistered;
        private static bool _idlePending;

        private static readonly Color PadAccent = Color.FromRgb(0x25, 0x63, 0xEB);
        private static readonly Color BatchAccent = Color.FromRgb(0x7C, 0x3A, 0xED);
        private static readonly Color EqCreateAccent = Color.FromRgb(0x05, 0x96, 0x69);
        private static readonly Color EqEditAccent = Color.FromRgb(0xD9, 0x77, 0x06);
        private static readonly Color LanguageAccent = Color.FromRgb(0x47, 0x55, 0x69);
        private static readonly Color AboutAccent = Color.FromRgb(0x64, 0x74, 0x8B);

        static RibbonSetup()
        {
            LocalizationManager.LanguageChanged += OnLanguageChanged;
        }

        private static void OnLanguageChanged()
        {
            var ribbon = ComponentManager.Ribbon;
            if (ribbon != null)
            {
                Rebuild(ribbon);
            }
        }

        public static void AttachToComponentManager()
        {
            if (!_hooksRegistered)
            {
                _hooksRegistered = true;
                AcadApp.SystemVariableChanged += OnSystemVariableChanged;
            }

            if (ComponentManager.Ribbon != null)
            {
                Build(ComponentManager.Ribbon);
            }
            else
            {
                ComponentManager.ItemInitialized -= OnItemInitialized;
                ComponentManager.ItemInitialized += OnItemInitialized;
            }

            // Plant 3D 启动阶段会在插件 Initialize 之后加载三维配管工作空间并重建 Ribbon，
            // 挂载一次 Idle 回调确保工作空间就绪后选项卡依然存在。
            ScheduleEnsureOnIdle();
        }

        public static void Detach()
        {
            ComponentManager.ItemInitialized -= OnItemInitialized;
            if (_idlePending)
            {
                AcadApp.Idle -= OnApplicationIdle;
                _idlePending = false;
            }
            if (_hooksRegistered)
            {
                AcadApp.SystemVariableChanged -= OnSystemVariableChanged;
                _hooksRegistered = false;
            }
        }

        private static void ScheduleEnsureOnIdle()
        {
            if (_idlePending)
            {
                return;
            }
            _idlePending = true;
            AcadApp.Idle += OnApplicationIdle;
        }

        private static void OnApplicationIdle(object sender, EventArgs e)
        {
            var ribbon = ComponentManager.Ribbon;
            if (ribbon == null)
            {
                return;
            }

            AcadApp.Idle -= OnApplicationIdle;
            _idlePending = false;

            try
            {
                Build(ribbon);
            }
            catch
            {
            }
        }

        private static void OnSystemVariableChanged(object sender, SystemVariableChangedEventArgs e)
        {
            if (e == null || string.IsNullOrEmpty(e.Name))
            {
                return;
            }

            if (string.Equals(e.Name, "WSCURRENT", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(e.Name, "MENUNAME", StringComparison.OrdinalIgnoreCase))
            {
                ScheduleEnsureOnIdle();
            }
        }

        private static void OnItemInitialized(object sender, RibbonItemEventArgs e)
        {
            var ribbon = ComponentManager.Ribbon;
            if (ribbon == null)
            {
                return;
            }

            ComponentManager.ItemInitialized -= OnItemInitialized;
            Build(ribbon);
            ScheduleEnsureOnIdle();
        }

        public static void Rebuild(RibbonControl ribbon)
        {
            for (var i = ribbon.Tabs.Count - 1; i >= 0; i--)
            {
                if (string.Equals(ribbon.Tabs[i].Id, TabId, StringComparison.Ordinal))
                {
                    ribbon.Tabs.RemoveAt(i);
                }
            }
            Build(ribbon);
        }

        private static void Build(RibbonControl ribbon)
        {
            for (var i = 0; i < ribbon.Tabs.Count; i++)
            {
                if (string.Equals(ribbon.Tabs[i].Id, TabId, StringComparison.Ordinal))
                {
                    return;
                }
            }

            // 面板一：测试（单个测试 / 批量测试）
            var panelTest = new RibbonPanelSource { Title = LocalizationManager.T("RibbonPanelTest") };
            panelTest.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_PAD",
                LocalizationManager.T("RibbonBtnPad"),
                LocalizationManager.T("RibbonBtnPadTip"),
                PadAccent,
                "Icon.Geo.Play",
                "PYPAD"));
            panelTest.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_BATCH",
                LocalizationManager.T("RibbonBtnBatch"),
                LocalizationManager.T("RibbonBtnBatchTip"),
                BatchAccent,
                "Icon.Geo.Copy",
                "PYBATCH"));

            // 面板二：设备（创建设备 / 编辑设备）
            var panelEquipment = new RibbonPanelSource { Title = LocalizationManager.T("RibbonPanelEquipment") };
            panelEquipment.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_EQCREATE",
                LocalizationManager.T("RibbonBtnEqCreate"),
                LocalizationManager.T("RibbonBtnEqCreateTip"),
                EqCreateAccent,
                "Icon.Geo.Plus",
                "PYEQCREATE"));
            panelEquipment.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_EQEDIT",
                LocalizationManager.T("RibbonBtnEqEdit"),
                LocalizationManager.T("RibbonBtnEqEditTip"),
                EqEditAccent,
                "Icon.Geo.Edit",
                "PYEQEDIT"));

            // 面板三：设置（语言切换 / 关于）
            var panelSettings = new RibbonPanelSource { Title = LocalizationManager.T("RibbonPanelSettings") };
            panelSettings.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_LANG",
                LocalizationManager.IsChinese ? "中 / EN" : "EN / 中",
                LocalizationManager.T("RibbonBtnLangTip"),
                LanguageAccent,
                "Icon.Geo.Translate",
                "PYLANG"));
            panelSettings.Items.Add(CreateLargeButton(
                "P3DPYPAD_CMD_ABOUT",
                LocalizationManager.T("RibbonBtnAbout"),
                LocalizationManager.T("RibbonBtnAboutTip"),
                AboutAccent,
                "Icon.Geo.Info",
                "PYABOUT"));

            var tab = new RibbonTab
            {
                Title = LocalizationManager.T("RibbonTabTitle"),
                Id = TabId,
                IsVisible = true
            };
            tab.Panels.Add(new RibbonPanel { Source = panelTest });
            tab.Panels.Add(new RibbonPanel { Source = panelEquipment });
            tab.Panels.Add(new RibbonPanel { Source = panelSettings });
            ribbon.Tabs.Add(tab);
        }

        private static RibbonButton CreateLargeButton(
            string id,
            string text,
            string toolTip,
            Color accent,
            string iconKey,
            string command)
        {
            return new RibbonButton
            {
                Id = id,
                Name = text,
                Text = text,
                ShowText = true,
                ShowImage = true,
                Size = RibbonItemSize.Large,
                Orientation = System.Windows.Controls.Orientation.Vertical,
                Image = CreateRibbonIcon(accent, iconKey, 16),
                LargeImage = CreateRibbonIcon(accent, iconKey, 32),
                ToolTip = toolTip,
                CommandHandler = new CommandRelay(command)
            };
        }

        /// <summary>
        /// 生成圆角色块图标：底色区分命令，白色 Material Design 图标居中放大，
        /// 16px/32px 下都保持清晰。
        /// </summary>
        private static ImageSource CreateRibbonIcon(Color accent, string iconKey, double size)
        {
            var pad = size * 0.04;
            var radius = size * 0.22;
            var block = new RectangleGeometry(
                new Rect(pad, pad, size - pad * 2.0, size - pad * 2.0),
                radius,
                radius);
            block.Freeze();

            var brush = new SolidColorBrush(accent);
            brush.Freeze();

            var group = new DrawingGroup();
            var background = new GeometryDrawing(brush, null, block);
            background.Freeze();
            group.Children.Add(background);

            var glyph = GetIconGeometry(iconKey);
            if (glyph != null)
            {
                var scale = size * 0.68 / 24.0;
                var offset = (size - 24.0 * scale) / 2.0;
                var transform = new TransformGroup();
                transform.Children.Add(new ScaleTransform(scale, scale));
                transform.Children.Add(new TranslateTransform(offset, offset));
                transform.Freeze();

                var glyphDrawing = new GeometryDrawing(Brushes.White, null, glyph);
                glyphDrawing.Freeze();

                var glyphGroup = new DrawingGroup { Transform = transform };
                glyphGroup.Children.Add(glyphDrawing);
                glyphGroup.Freeze();
                group.Children.Add(glyphGroup);
            }

            group.Freeze();

            var image = new DrawingImage(group);
            image.Freeze();
            return image;
        }

        private static Geometry GetIconGeometry(string key)
        {
            if (_iconResources == null)
            {
                _iconResources = new ResourceDictionary { Source = IconDictionaryUri };
            }

            var geometry = _iconResources[key] as Geometry;
            if (geometry != null && !geometry.IsFrozen && geometry.CanFreeze)
            {
                geometry.Freeze();
            }

            return geometry;
        }

        private sealed class CommandRelay : ICommand
        {
            private readonly string _command;

            public CommandRelay(string command)
            {
                _command = command;
            }

            public event EventHandler CanExecuteChanged
            {
                add { }
                remove { }
            }

            public bool CanExecute(object parameter)
            {
                return AcadApp.DocumentManager.MdiActiveDocument != null;
            }

            public void Execute(object parameter)
            {
                var doc = AcadApp.DocumentManager.MdiActiveDocument;
                if (doc != null)
                {
                    doc.SendStringToExecute(_command + " ", true, false, false);
                }
            }
        }
    }
}
