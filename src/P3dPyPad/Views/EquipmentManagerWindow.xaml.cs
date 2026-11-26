using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    /// <summary>
    /// 两栏式 Plant 3D 设备创建窗口（仅保留设备选择、可缩放示意图、标高/旋转与尺寸参数）。
    /// </summary>
    public partial class EquipmentManagerWindow : Window
    {
        private sealed class CategoryFilterItem
        {
            public string Key { get; set; }
            public string Label { get; set; }
            public override string ToString() => Label;
        }

        private List<EquipmentTemplateItem> _allTemplates = new List<EquipmentTemplateItem>();
        private EquipmentEditSession _session;
        private string _equipmentFolder = string.Empty;

        private double _zoom = 1.0;
        private bool _isPanning;
        private Point _panStart;
        private double _panOriginX;
        private double _panOriginY;

        private bool _isRestoringState;
        private static bool _prefsLoaded;
        private static string _lastSourceFilter = "All";
        private static string _lastCategoryKey = string.Empty;
        private static string _lastTemplateName = string.Empty;
        private static string _lastElevation = string.Empty;
        private static string _lastRotation = string.Empty;
        private static readonly Dictionary<string, Dictionary<string, string>> _savedParamsByTemplate =
            new Dictionary<string, Dictionary<string, string>>(StringComparer.OrdinalIgnoreCase);

        public EquipmentManagerWindow()
        {
            LocalizationManager.EnsureInitialized(this);
            InitializeComponent();
            Title = LocalizationManager.T("EqWinTitleCreate", "创建设备", "Create Equipment");
            EnsurePrefsLoaded();
            RestoreSourceFilter();
            LoadCatalog();
            Closing += (s, e) => SavePreferences();
        }

        private void LoadCatalog()
        {
            _allTemplates = EquipmentCatalogService.LoadTemplates(out _equipmentFolder);
            RebuildCategoryFilter();
            ApplyTemplateFilter();

            StatusText.Text = string.IsNullOrEmpty(_equipmentFolder)
                ? LocalizationManager.T("EqStatusNoDir", "未找到设备目录", "Equipment directory not found")
                : string.Format(
                    LocalizationManager.T("EqStatusLoaded", "共 {0} 台设备", "{0} equipment templates"),
                    _allTemplates.Count);
        }

        private void RebuildCategoryFilter()
        {
            var prevKey = _isRestoringState
                ? _lastCategoryKey
                : ((CategoryComboBox.SelectedItem as CategoryFilterItem)?.Key ?? _lastCategoryKey ?? string.Empty);
            var items = new List<CategoryFilterItem>
            {
                new CategoryFilterItem
                {
                    Key = string.Empty,
                    Label = string.Format(LocalizationManager.T("EqCatAll", "全部分类 ({0})", "All Categories ({0})"), _allTemplates.Count)
                }
            };

            var groups = _allTemplates
                .GroupBy(t => t.CategoryKey ?? string.Empty, StringComparer.OrdinalIgnoreCase)
                .Select(g => new
                {
                    Key = g.Key,
                    Name = g.First().CategoryDisplayName,
                    Count = g.Count()
                })
                .OrderByDescending(g => g.Count)
                .ThenBy(g => g.Name, StringComparer.CurrentCultureIgnoreCase);

            foreach (var g in groups)
            {
                items.Add(new CategoryFilterItem
                {
                    Key = g.Key,
                    Label = string.Format("{0} ({1})", g.Name, g.Count)
                });
            }

            CategoryComboBox.ItemsSource = items;
            var selected = items.FirstOrDefault(i => string.Equals(i.Key, prevKey, StringComparison.OrdinalIgnoreCase)) ?? items[0];
            CategoryComboBox.SelectedItem = selected;
        }

        private void ApplyTemplateFilter()
        {
            if (TemplateListBox == null) return;

            var query = (SearchBox?.Text ?? string.Empty).Trim();
            if (SearchPlaceholder != null)
            {
                SearchPlaceholder.Visibility = string.IsNullOrEmpty(query) ? Visibility.Visible : Visibility.Collapsed;
            }
            if (ClearSearchButton != null)
            {
                ClearSearchButton.Visibility = string.IsNullOrEmpty(query) ? Visibility.Collapsed : Visibility.Visible;
            }

            var catKey = (CategoryComboBox?.SelectedItem as CategoryFilterItem)?.Key ?? string.Empty;
            var customOnly = FilterCustomRadio?.IsChecked == true;
            var builtInOnly = FilterBuiltInRadio?.IsChecked == true;

            var filtered = _allTemplates.Where(t =>
            {
                if (customOnly && !t.IsCustom) return false;
                if (builtInOnly && t.IsCustom) return false;
                if (!string.IsNullOrEmpty(catKey) && !string.Equals(t.CategoryKey, catKey, StringComparison.OrdinalIgnoreCase))
                {
                    return false;
                }
                if (!string.IsNullOrEmpty(query))
                {
                    var matchName = (t.DisplayName ?? string.Empty).IndexOf(query, StringComparison.OrdinalIgnoreCase) >= 0;
                    var matchCode = (t.Name ?? string.Empty).IndexOf(query, StringComparison.OrdinalIgnoreCase) >= 0;
                    var matchCat = (t.CategoryDisplayName ?? string.Empty).IndexOf(query, StringComparison.OrdinalIgnoreCase) >= 0;
                    if (!matchName && !matchCode && !matchCat) return false;
                }
                return true;
            }).ToList();

            var prevName = (TemplateListBox.SelectedItem as EquipmentTemplateItem)?.Name;
            if (string.IsNullOrEmpty(prevName)) prevName = _lastTemplateName;
            TemplateListBox.ItemsSource = filtered;

            if (filtered.Count > 0)
            {
                var toSelect = filtered.FirstOrDefault(t => string.Equals(t.Name, prevName, StringComparison.OrdinalIgnoreCase)) ?? filtered[0];
                TemplateListBox.SelectedItem = toSelect;
                TemplateListBox.ScrollIntoView(toSelect);
            }
            else
            {
                BindSession(null);
            }
        }

        private void BindSession(EquipmentEditSession session)
        {
            _session = session;
            ResetZoom();

            if (session == null)
            {
                HeaderTitleText.Text = LocalizationManager.T("EqNoneSelected", "未选择设备", "No equipment selected");
                ParamsGrid.ItemsSource = null;
                SetPreviewImage(null);
                ParamsGroupBox.Header = LocalizationManager.T("EqTabParamsSimple", "尺寸参数", "Dimensions");
                return;
            }

            HeaderTitleText.Text = session.DisplayName ?? session.EquipmentName;
            SetPreviewImage(session.Template?.FullPreview);

            ElevationTextBox.Text = session.Elevation.ToString("0.###", CultureInfo.InvariantCulture);
            ElevationUnitText.Text = session.LengthUnit;
            RotationTextBox.Text = session.RotationDegrees.ToString("0.##", CultureInfo.InvariantCulture);

            ParamsGrid.ItemsSource = session.Parameters;
            ParamsGroupBox.Header = string.Format(
                LocalizationManager.T("EqTabParams", "尺寸参数 ({0})", "Dimensions ({0})"),
                session.Parameters.Count);
        }

        private void SetPreviewImage(ImageSource img)
        {
            CreatePreviewImage.Source = img;
            CreatePreviewEmptyText.Visibility = img == null ? Visibility.Visible : Visibility.Collapsed;
        }

        private bool SyncInputsToSession(out string validationError)
        {
            validationError = null;
            if (_session == null)
            {
                validationError = LocalizationManager.T("EqErrNoSelection", "请先选择一个设备。", "Please select an equipment first.");
                return false;
            }

            ParamsGrid.CommitEdit(DataGridEditingUnit.Cell, true);
            ParamsGrid.CommitEdit(DataGridEditingUnit.Row, true);

            if (!double.TryParse((ElevationTextBox.Text ?? "0").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out var elev))
            {
                validationError = LocalizationManager.T("EqErrBadElev", "标高必须是有效数字。", "Elevation must be a valid number.");
                return false;
            }
            if (!double.TryParse((RotationTextBox.Text ?? "0").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out var rot))
            {
                validationError = LocalizationManager.T("EqErrBadRot", "旋转角度必须是有效数字。", "Rotation angle must be a valid number.");
                return false;
            }

            _session.Elevation = elev;
            _session.RotationDegrees = rot;

            foreach (var p in _session.Parameters)
            {
                var pt = (p.ParamType ?? string.Empty).ToLowerInvariant();
                if (pt == "d" || pt == "d0" || pt == "a" || pt == "r")
                {
                    if (!double.TryParse((p.Value ?? string.Empty).Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out var num))
                    {
                        validationError = string.Format(
                            LocalizationManager.T("EqErrBadParam", "参数 {0} 的值 \"{1}\" 不是有效数字。", "Parameter {0} value \"{1}\" is not a valid number."),
                            p.Name, p.Value);
                        return false;
                    }
                    if (pt == "d" && num <= 0)
                    {
                        validationError = string.Format(
                            LocalizationManager.T("EqErrNonPosParam", "尺寸参数 {0} 必须大于 0。", "Dimension parameter {0} must be > 0."),
                            p.Name);
                        return false;
                    }
                }
            }

            return true;
        }

        private void FilterChanged(object sender, EventArgs e)
        {
            if (_isRestoringState) return;
            ApplyTemplateFilter();
        }

        private void ClearSearch_Click(object sender, RoutedEventArgs e)
        {
            SearchBox.Text = string.Empty;
            SearchBox.Focus();
        }

        private void TemplateListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_session != null && !_isRestoringState)
            {
                CaptureCurrentSessionToMemory();
            }

            if (TemplateListBox.SelectedItem is EquipmentTemplateItem tpl)
            {
                _lastTemplateName = tpl.Name ?? string.Empty;
                var session = EquipmentBridge.CreateSessionFromTemplate(tpl);
                ApplySavedParamsToSession(session);
                BindSession(session);
            }
        }

        private void RefreshCatalog_Click(object sender, RoutedEventArgs e) => LoadCatalog();

        private void ResetParams_Click(object sender, RoutedEventArgs e)
        {
            if (_session == null) return;
            foreach (var p in _session.Parameters)
            {
                if (!string.IsNullOrEmpty(p.DefaultValue))
                {
                    p.Value = p.DefaultValue;
                }
            }
            if (!string.IsNullOrEmpty(_session.Template?.Name))
            {
                _savedParamsByTemplate.Remove(_session.Template?.Name);
                SaveParamsDictionary();
            }
            StatusText.Text = LocalizationManager.T("EqStatusReset", "已恢复默认尺寸", "Default dimensions restored");
        }

        private void PrimaryAction_Click(object sender, RoutedEventArgs e)
        {
            if (!SyncInputsToSession(out var err))
            {
                MessageBox.Show(this, err, Title, MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                MessageBox.Show(this, LocalizationManager.T("EqErrNoDoc", "没有打开的图形文档。", "No active drawing document."), Title, MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            Hide();
            var created = false;
            try
            {
                if (EquipmentBridge.PlaceNewEquipment(doc, _session, out var createdId, out var createErr))
                {
                    created = true;
                    SavePreferences();
                    doc.Editor.WriteMessage(string.Format(
                        "\n[P3dPyPad] 已创建设备：{0}（句柄 {1}）\n",
                        _session.DisplayName,
                        createdId.Handle));
                    Close();
                    return;
                }

                if (!string.IsNullOrEmpty(createErr))
                {
                    StatusText.Text = createErr;
                    Show();
                    Activate();
                    MessageBox.Show(this, createErr, Title, MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
            }
            finally
            {
                if (!created && IsLoaded)
                {
                    Show();
                    Activate();
                }
            }
        }

        private void Close_Click(object sender, RoutedEventArgs e) => Close();

        // ==================== 预览图缩放 / 平移 / 大图 ====================

        private void SetZoom(double newZoom)
        {
            _zoom = Math.Max(0.5, Math.Min(6.0, newZoom));
            CreatePreviewScale.ScaleX = _zoom;
            CreatePreviewScale.ScaleY = _zoom;
            CreateZoomResetButton.Content = string.Format("{0:0}%", _zoom * 100);
        }

        private void ResetZoom()
        {
            SetZoom(1.0);
            CreatePreviewTranslate.X = 0;
            CreatePreviewTranslate.Y = 0;
        }

        private void ZoomIn_Click(object sender, RoutedEventArgs e) => SetZoom(_zoom * 1.25);
        private void ZoomOut_Click(object sender, RoutedEventArgs e) => SetZoom(_zoom / 1.25);
        private void ZoomReset_Click(object sender, RoutedEventArgs e) => ResetZoom();

        private void Preview_MouseWheel(object sender, MouseWheelEventArgs e)
        {
            SetZoom(e.Delta > 0 ? _zoom * 1.18 : _zoom / 1.18);
            e.Handled = true;
        }

        private void Preview_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ClickCount == 2)
            {
                ResetZoom();
                return;
            }
            var el = sender as UIElement;
            if (el == null) return;
            _isPanning = true;
            _panStart = e.GetPosition(el);
            _panOriginX = CreatePreviewTranslate.X;
            _panOriginY = CreatePreviewTranslate.Y;
            el.CaptureMouse();
        }

        private void Preview_MouseMove(object sender, MouseEventArgs e)
        {
            if (!_isPanning) return;
            var el = sender as UIElement;
            if (el == null) return;
            var cur = e.GetPosition(el);
            CreatePreviewTranslate.X = _panOriginX + (cur.X - _panStart.X);
            CreatePreviewTranslate.Y = _panOriginY + (cur.Y - _panStart.Y);
        }

        private void Preview_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            if (!_isPanning) return;
            _isPanning = false;
            (sender as UIElement)?.ReleaseMouseCapture();
        }

        private void OpenFullPreview_Click(object sender, RoutedEventArgs e)
        {
            var img = _session?.Template?.FullPreview;
            if (img == null) return;

            var viewer = new Window
            {
                Title = _session.DisplayName ?? _session.EquipmentName,
                Width = 860,
                Height = 760,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Owner = this,
                Background = Brushes.White
            };

            var scale = new ScaleTransform(1, 1);
            var translate = new TranslateTransform(0, 0);
            var group = new TransformGroup();
            group.Children.Add(scale);
            group.Children.Add(translate);

            var image = new Image
            {
                Source = img,
                Stretch = Stretch.Uniform,
                RenderTransformOrigin = new Point(0.5, 0.5),
                RenderTransform = group
            };
            RenderOptions.SetBitmapScalingMode(image, BitmapScalingMode.HighQuality);

            var border = new Border { Background = Brushes.White, ClipToBounds = true, Child = image };
            var panning = false;
            var start = new Point();
            double ox = 0, oy = 0;

            border.MouseWheel += (s, ev) =>
            {
                var next = Math.Max(0.5, Math.Min(8.0, scale.ScaleX * (ev.Delta > 0 ? 1.2 : 1.0 / 1.2)));
                scale.ScaleX = next;
                scale.ScaleY = next;
            };
            border.MouseLeftButtonDown += (s, ev) =>
            {
                if (ev.ClickCount == 2)
                {
                    scale.ScaleX = 1;
                    scale.ScaleY = 1;
                    translate.X = 0;
                    translate.Y = 0;
                    return;
                }
                panning = true;
                start = ev.GetPosition(border);
                ox = translate.X;
                oy = translate.Y;
                border.CaptureMouse();
            };
            border.MouseMove += (s, ev) =>
            {
                if (!panning) return;
                var cur = ev.GetPosition(border);
                translate.X = ox + (cur.X - start.X);
                translate.Y = oy + (cur.Y - start.Y);
            };
            border.MouseLeftButtonUp += (s, ev) =>
            {
                if (!panning) return;
                panning = false;
                border.ReleaseMouseCapture();
            };

            viewer.Content = border;
            viewer.ShowDialog();
        }

        // ==================== 记忆上次选择与参数 ====================

        private static string GetParamsPrefsPath()
        {
            return System.IO.Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "P3dPyPad",
                "equipment_params.json");
        }

        private static void EnsurePrefsLoaded()
        {
            if (_prefsLoaded) return;
            _prefsLoaded = true;
            _lastSourceFilter = UserSettings.Get("EqLastSource", "All") ?? "All";
            _lastCategoryKey = UserSettings.Get("EqLastCategory", string.Empty) ?? string.Empty;
            _lastTemplateName = UserSettings.Get("EqLastTemplate", string.Empty) ?? string.Empty;
            _lastElevation = UserSettings.Get("EqLastElevation", string.Empty) ?? string.Empty;
            _lastRotation = UserSettings.Get("EqLastRotation", string.Empty) ?? string.Empty;
            LoadParamsDictionary();
        }

        private void RestoreSourceFilter()
        {
            _isRestoringState = true;
            try
            {
                if (string.Equals(_lastSourceFilter, "Custom", StringComparison.OrdinalIgnoreCase) && FilterCustomRadio != null)
                {
                    FilterCustomRadio.IsChecked = true;
                }
                else if (string.Equals(_lastSourceFilter, "BuiltIn", StringComparison.OrdinalIgnoreCase) && FilterBuiltInRadio != null)
                {
                    FilterBuiltInRadio.IsChecked = true;
                }
                else if (FilterAllRadio != null)
                {
                    FilterAllRadio.IsChecked = true;
                }
            }
            finally
            {
                _isRestoringState = false;
            }
        }

        private void CaptureCurrentSessionToMemory()
        {
            if (_session == null || string.IsNullOrEmpty(_session.Template?.Name)) return;

            // 提交 DataGrid 中正在编辑的单元格
            if (ParamsGrid != null)
            {
                ParamsGrid.CommitEdit(DataGridEditingUnit.Cell, true);
                ParamsGrid.CommitEdit(DataGridEditingUnit.Row, true);
            }

            var dict = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (var p in _session.Parameters)
            {
                if (!string.IsNullOrEmpty(p.Name) && !string.Equals(p.Value, p.DefaultValue, StringComparison.Ordinal))
                {
                    dict[p.Name] = p.Value ?? string.Empty;
                }
            }

            if (dict.Count > 0)
            {
                _savedParamsByTemplate[_session.Template?.Name] = dict;
            }
            else
            {
                _savedParamsByTemplate.Remove(_session.Template?.Name);
            }

            if (ElevationTextBox != null && !string.IsNullOrWhiteSpace(ElevationTextBox.Text))
            {
                _lastElevation = ElevationTextBox.Text.Trim();
            }
            if (RotationTextBox != null && !string.IsNullOrWhiteSpace(RotationTextBox.Text))
            {
                _lastRotation = RotationTextBox.Text.Trim();
            }
        }

        private void ApplySavedParamsToSession(EquipmentEditSession session)
        {
            if (session == null) return;

            if (!string.IsNullOrEmpty(session.Template?.Name) &&
                _savedParamsByTemplate.TryGetValue(session.Template?.Name, out var saved) &&
                saved != null)
            {
                foreach (var p in session.Parameters)
                {
                    if (!string.IsNullOrEmpty(p.Name) && saved.TryGetValue(p.Name, out var val) && !string.IsNullOrEmpty(val))
                    {
                        p.Value = val;
                    }
                }
            }

            if (double.TryParse(_lastElevation, NumberStyles.Float, CultureInfo.InvariantCulture, out var elev))
            {
                session.Elevation = elev;
            }
            if (double.TryParse(_lastRotation, NumberStyles.Float, CultureInfo.InvariantCulture, out var rot))
            {
                session.RotationDegrees = rot;
            }
        }

        private void SavePreferences()
        {
            try
            {
                CaptureCurrentSessionToMemory();

                _lastSourceFilter = FilterCustomRadio?.IsChecked == true ? "Custom"
                    : FilterBuiltInRadio?.IsChecked == true ? "BuiltIn"
                    : "All";
                _lastCategoryKey = (CategoryComboBox?.SelectedItem as CategoryFilterItem)?.Key ?? string.Empty;
                _lastTemplateName = (TemplateListBox?.SelectedItem as EquipmentTemplateItem)?.Name ?? _lastTemplateName ?? string.Empty;

                UserSettings.Set("EqLastSource", _lastSourceFilter);
                UserSettings.Set("EqLastCategory", _lastCategoryKey);
                UserSettings.Set("EqLastTemplate", _lastTemplateName);
                UserSettings.Set("EqLastElevation", _lastElevation);
                UserSettings.Set("EqLastRotation", _lastRotation);
                SaveParamsDictionary();
            }
            catch
            {
                // 忽略偏好保存异常，避免影响主流程
            }
        }

        private static void LoadParamsDictionary()
        {
            try
            {
                var path = GetParamsPrefsPath();
                if (!System.IO.File.Exists(path)) return;

                var serializer = new System.Runtime.Serialization.Json.DataContractJsonSerializer(
                    typeof(Dictionary<string, Dictionary<string, string>>));
                using (var fs = System.IO.File.OpenRead(path))
                {
                    if (serializer.ReadObject(fs) is Dictionary<string, Dictionary<string, string>> data)
                    {
                        _savedParamsByTemplate.Clear();
                        foreach (var kv in data)
                        {
                            if (!string.IsNullOrEmpty(kv.Key) && kv.Value != null)
                            {
                                _savedParamsByTemplate[kv.Key] = new Dictionary<string, string>(kv.Value, StringComparer.OrdinalIgnoreCase);
                            }
                        }
                    }
                }
            }
            catch
            {
                // 忽略损坏的缓存文件
            }
        }

        private static void SaveParamsDictionary()
        {
            try
            {
                var path = GetParamsPrefsPath();
                var dir = System.IO.Path.GetDirectoryName(path);
                if (!string.IsNullOrEmpty(dir)) System.IO.Directory.CreateDirectory(dir);

                var plain = new Dictionary<string, Dictionary<string, string>>();
                foreach (var kv in _savedParamsByTemplate)
                {
                    plain[kv.Key] = new Dictionary<string, string>(kv.Value);
                }

                var serializer = new System.Runtime.Serialization.Json.DataContractJsonSerializer(
                    typeof(Dictionary<string, Dictionary<string, string>>));
                using (var fs = System.IO.File.Create(path))
                {
                    serializer.WriteObject(fs, plain);
                }
            }
            catch
            {
                // 忽略写入异常
            }
        }
    }
}
