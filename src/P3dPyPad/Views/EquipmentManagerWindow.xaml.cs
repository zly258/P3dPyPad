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
    /// 两栏式现代化 Plant 3D 设备创建与编辑窗口。
    /// 支持：
    /// 1. 创建模式：左栏搜索/分类/卡片选型 + 右栏高清可缩放预览图与尺寸/特性/管嘴独立 Tab；
    /// 2. 编辑模式：左栏超大高清可缩放预览图 + 右栏位号/标高与尺寸/特性/管嘴独立 Tab，支持不关窗实时应用刷新。
    /// </summary>
    public partial class EquipmentManagerWindow : Window
    {
        private sealed class CategoryFilterItem
        {
            public string Key { get; set; }
            public string Label { get; set; }
            public override string ToString() => Label;
        }

        private EquipmentDialogMode _mode;
        private List<EquipmentTemplateItem> _allTemplates = new List<EquipmentTemplateItem>();
        private EquipmentEditSession _session;
        private string _equipmentFolder = string.Empty;

        // 预览图缩放与平移状态
        private double _zoom = 1.0;
        private bool _isPanning;
        private Point _panStart;
        private double _panOriginX;
        private double _panOriginY;

        public EquipmentManagerWindow()
            : this(EquipmentDialogMode.Create, null)
        {
        }

        public EquipmentManagerWindow(EquipmentDialogMode mode, EquipmentEditSession initialSession = null)
        {
            LocalizationManager.EnsureInitialized(this);
            InitializeComponent();
            _mode = mode;

            ApplyModeLayout();
            if (_mode == EquipmentDialogMode.Create)
            {
                LoadCatalog();
            }
            else if (initialSession != null)
            {
                BindSession(initialSession);
            }
        }

        public void SwitchToCreateMode()
        {
            _mode = EquipmentDialogMode.Create;
            ApplyModeLayout();
            if (_allTemplates.Count == 0)
            {
                LoadCatalog();
            }
            else if (TemplateListBox.SelectedItem is EquipmentTemplateItem tpl)
            {
                var session = EquipmentBridge.CreateSessionFromTemplate(tpl);
                BindSession(session);
            }
        }

        public void SwitchToEditMode(EquipmentEditSession session)
        {
            _mode = EquipmentDialogMode.Edit;
            ApplyModeLayout();
            BindSession(session);
        }

        private void ApplyModeLayout()
        {
            var isEdit = _mode == EquipmentDialogMode.Edit;

            Title = isEdit
                ? LocalizationManager.T("EqWinTitleEdit", "Plant 3D 编辑设备 (PYEQEDIT)", "Plant 3D Edit Equipment (PYEQEDIT)")
                : LocalizationManager.T("EqWinTitleCreate", "Plant 3D 创建设备 (PYEQCREATE)", "Plant 3D Create Equipment (PYEQCREATE)");

            ModeBadge.Background = new SolidColorBrush(isEdit
                ? Color.FromRgb(0xD9, 0x77, 0x06)
                : Color.FromRgb(0x25, 0x63, 0xEB));
            ModeBadgeText.Text = isEdit
                ? LocalizationManager.T("EqModeEdit", "编辑设备", "Edit Equipment")
                : LocalizationManager.T("EqModeCreate", "创建设备", "Create Equipment");

            CreateCatalogPanel.Visibility = isEdit ? Visibility.Collapsed : Visibility.Visible;
            EditPreviewPanel.Visibility = isEdit ? Visibility.Visible : Visibility.Collapsed;

            CreateTopCard.Visibility = isEdit ? Visibility.Collapsed : Visibility.Visible;
            CreatePreviewSplitter.Visibility = isEdit ? Visibility.Collapsed : Visibility.Visible;
            CreatePreviewRow.Height = isEdit ? new GridLength(0) : new GridLength(235);
            CreatePreviewRow.MinHeight = isEdit ? 0 : 170;
            CreatePreviewSplitterRow.Height = isEdit ? new GridLength(0) : new GridLength(6);

            EditGeneralBar.Visibility = isEdit ? Visibility.Visible : Visibility.Collapsed;
            PickEquipmentButton.Visibility = isEdit ? Visibility.Visible : Visibility.Collapsed;
            RefreshCatalogButton.Visibility = isEdit ? Visibility.Collapsed : Visibility.Visible;

            ApplyButton.Visibility = isEdit ? Visibility.Visible : Visibility.Collapsed;
            PrimaryActionButton.Content = isEdit
                ? LocalizationManager.T("EqBtnOkUpdate", "确定并更新", "OK & Update")
                : LocalizationManager.T("EqBtnCreatePlace", "在图面创建放置", "Create & Place");

            AddNozzleButton.IsEnabled = isEdit;
            EditNozzleButton.IsEnabled = isEdit;
        }

        private void LoadCatalog()
        {
            _allTemplates = EquipmentCatalogService.LoadTemplates(out _equipmentFolder);
            RebuildCategoryFilter();
            ApplyTemplateFilter();

            StatusText.Text = string.IsNullOrEmpty(_equipmentFolder)
                ? LocalizationManager.T("EqStatusNoDir", "未检测到 Plant 3D equipment 目录，请先打开 Plant 3D 项目。", "Plant 3D equipment directory not found.")
                : string.Format(
                    LocalizationManager.T("EqStatusLoaded", "已加载 {0} 台设备模板（目录：{1}）", "Loaded {0} equipment templates ({1})"),
                    _allTemplates.Count,
                    _equipmentFolder);
        }

        private void RebuildCategoryFilter()
        {
            var prevKey = (CategoryComboBox.SelectedItem as CategoryFilterItem)?.Key ?? string.Empty;
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
            TemplateListBox.ItemsSource = filtered;

            if (CatalogCountText != null)
            {
                var customCount = filtered.Count(t => t.IsCustom);
                CatalogCountText.Text = string.Format(
                    LocalizationManager.T("EqListCount", "显示 {0} / {1} 台设备（自定义 {2} 台）", "Showing {0} / {1} (Custom: {2})"),
                    filtered.Count,
                    _allTemplates.Count,
                    customCount);
            }

            if (filtered.Count > 0)
            {
                var toSelect = filtered.FirstOrDefault(t => string.Equals(t.Name, prevName, StringComparison.OrdinalIgnoreCase)) ?? filtered[0];
                TemplateListBox.SelectedItem = toSelect;
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
                HeaderSubtitleText.Text = string.Empty;
                ParamsGrid.ItemsSource = null;
                PropsGrid.ItemsSource = null;
                NozzlesGrid.ItemsSource = null;
                SetPreviewImage(null);
                return;
            }

            HeaderTitleText.Text = session.DisplayName ?? session.EquipmentName;
            HeaderSubtitleText.Text = string.Format("{0}  |  {1}  |  {2}",
                session.CategoryDisplayName,
                session.EquipmentName,
                session.LengthUnit);

            var img = session.Template?.FullPreview;
            SetPreviewImage(img);

            if (_mode == EquipmentDialogMode.Edit)
            {
                EditTagTextBox.Text = session.EquipmentTag ?? string.Empty;
                EditElevationTextBox.Text = session.Elevation.ToString("0.###", CultureInfo.InvariantCulture);
                EditElevationUnitText.Text = session.LengthUnit;
                EditSummaryName.Text = session.DisplayName;
                EditSummaryMeta.Text = string.Format("分类：{0}\n脚本代号：{1}\n图元句柄：{2}",
                    session.CategoryDisplayName,
                    session.EquipmentName,
                    session.TargetObjectId.IsNull ? "-" : session.TargetObjectId.Handle.ToString());
            }
            else
            {
                TagTextBox.Text = session.EquipmentTag ?? string.Empty;
                ElevationTextBox.Text = session.Elevation.ToString("0.###", CultureInfo.InvariantCulture);
                ElevationUnitText.Text = session.LengthUnit;
                RotationTextBox.Text = session.RotationDegrees.ToString("0.##", CultureInfo.InvariantCulture);
            }

            ParamsGrid.ItemsSource = session.Parameters;
            NozzlesGrid.ItemsSource = session.Nozzles;
            ApplyPropertyFilter();

            ParamsTab.Header = string.Format(LocalizationManager.T("EqTabParams", "尺寸参数 ({0})", "Dimensions ({0})"), session.Parameters.Count);
            PropsTab.Header = string.Format(LocalizationManager.T("EqTabProps", "工程特性 ({0})", "Properties ({0})"), session.Properties.Count);
            NozzlesTab.Header = string.Format(LocalizationManager.T("EqTabNozzles", "管嘴信息 ({0})", "Nozzles ({0})"), session.Nozzles.Count);
        }

        private void SetPreviewImage(ImageSource img)
        {
            CreatePreviewImage.Source = img;
            EditPreviewImage.Source = img;
            var emptyVis = img == null ? Visibility.Visible : Visibility.Collapsed;
            CreatePreviewEmptyText.Visibility = emptyVis;
            EditPreviewEmptyText.Visibility = emptyVis;
        }

        private void ApplyPropertyFilter()
        {
            if (_session == null || PropsGrid == null) return;
            var q = (PropSearchBox?.Text ?? string.Empty).Trim();
            if (PropSearchPlaceholder != null)
            {
                PropSearchPlaceholder.Visibility = string.IsNullOrEmpty(q) ? Visibility.Visible : Visibility.Collapsed;
            }
            var commonOnly = CommonPropsOnlyCheck?.IsChecked == true;

            var filtered = _session.Properties.Where(p =>
            {
                if (commonOnly && !p.IsCommon) return false;
                if (!string.IsNullOrEmpty(q))
                {
                    var m1 = (p.LabelText ?? string.Empty).IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0;
                    var m2 = (p.Name ?? string.Empty).IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0;
                    var m3 = (p.Value ?? string.Empty).IndexOf(q, StringComparison.OrdinalIgnoreCase) >= 0;
                    if (!m1 && !m2 && !m3) return false;
                }
                return true;
            }).ToList();

            PropsGrid.ItemsSource = filtered;
        }

        private bool SyncGeneralInputsToSession(out string validationError)
        {
            validationError = null;
            if (_session == null)
            {
                validationError = LocalizationManager.T("EqErrNoSelection", "请先选择一个设备。", "Please select an equipment first.");
                return false;
            }

            // 提交 DataGrid 正在编辑的单元格
            ParamsGrid.CommitEdit(DataGridEditingUnit.Cell, true);
            ParamsGrid.CommitEdit(DataGridEditingUnit.Row, true);
            PropsGrid.CommitEdit(DataGridEditingUnit.Cell, true);
            PropsGrid.CommitEdit(DataGridEditingUnit.Row, true);
            NozzlesGrid.CommitEdit(DataGridEditingUnit.Cell, true);
            NozzlesGrid.CommitEdit(DataGridEditingUnit.Row, true);

            if (_mode == EquipmentDialogMode.Edit)
            {
                _session.EquipmentTag = (EditTagTextBox.Text ?? string.Empty).Trim();
                if (!double.TryParse((EditElevationTextBox.Text ?? "0").Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out var elev))
                {
                    validationError = LocalizationManager.T("EqErrBadElev", "标高必须是有效数字。", "Elevation must be a valid number.");
                    return false;
                }
                _session.Elevation = elev;
            }
            else
            {
                _session.EquipmentTag = (TagTextBox.Text ?? string.Empty).Trim();
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
            }

            // 校验数值型尺寸参数
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

        // ==================== 事件处理 ====================

        private void FilterChanged(object sender, EventArgs e)
        {
            ApplyTemplateFilter();
        }

        private void ClearSearch_Click(object sender, RoutedEventArgs e)
        {
            SearchBox.Text = string.Empty;
            SearchBox.Focus();
        }

        private void PropFilterChanged(object sender, EventArgs e)
        {
            ApplyPropertyFilter();
        }

        private void TemplateListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_mode != EquipmentDialogMode.Create) return;
            if (TemplateListBox.SelectedItem is EquipmentTemplateItem tpl)
            {
                var session = EquipmentBridge.CreateSessionFromTemplate(tpl);
                BindSession(session);
            }
        }

        private void RefreshCatalog_Click(object sender, RoutedEventArgs e)
        {
            LoadCatalog();
        }

        private void PickEquipment_Click(object sender, RoutedEventArgs e)
        {
            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null) return;

            Hide();
            try
            {
                if (EquipmentBridge.TrySelectAndLoadEquipmentForEdit(doc, _allTemplates, out var session, out var err))
                {
                    BindSession(session);
                    StatusText.Text = LocalizationManager.T("EqStatusPicked", "已加载所选设备参数，可直接修改。", "Loaded selected equipment.");
                }
                else if (!string.IsNullOrEmpty(err))
                {
                    StatusText.Text = err;
                }
            }
            finally
            {
                Show();
                Activate();
            }
        }

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
            StatusText.Text = LocalizationManager.T("EqStatusReset", "已恢复所有尺寸参数为默认值。", "Restored default dimensions.");
        }

        private void ApplyEdit_Click(object sender, RoutedEventArgs e)
        {
            if (!SyncGeneralInputsToSession(out var err))
            {
                MessageBox.Show(this, err, Title, MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (EquipmentBridge.ApplyEditToEquipment(doc, _session, out var updateErr))
            {
                StatusText.Text = LocalizationManager.T("EqStatusUpdated", "设备已实时更新到当前图形。", "Equipment updated in drawing.");
            }
            else
            {
                StatusText.Text = updateErr ?? "更新失败";
                MessageBox.Show(this, updateErr ?? "更新失败", Title, MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void PrimaryAction_Click(object sender, RoutedEventArgs e)
        {
            if (!SyncGeneralInputsToSession(out var err))
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

            if (_mode == EquipmentDialogMode.Edit)
            {
                if (EquipmentBridge.ApplyEditToEquipment(doc, _session, out var updateErr))
                {
                    Close();
                }
                else
                {
                    StatusText.Text = updateErr ?? "更新失败";
                    MessageBox.Show(this, updateErr ?? "更新失败", Title, MessageBoxButton.OK, MessageBoxImage.Error);
                }
                return;
            }

            // 创建模式：临时隐藏窗口让用户在 CAD 图面点选放置点与旋转角
            Hide();
            try
            {
                if (EquipmentBridge.PlaceNewEquipment(doc, _session, out var createdId, out var createErr))
                {
                    StatusText.Text = string.Format(
                        LocalizationManager.T("EqStatusCreated", "已成功创建设备：{0}（句柄 {1}）", "Created equipment: {0} (Handle {1})"),
                        _session.DisplayName,
                        createdId.Handle);
                    // 重新刷新一次新会话以准备连续创建（保留同一模板）
                    if (_session.Template != null)
                    {
                        var next = EquipmentBridge.CreateSessionFromTemplate(_session.Template);
                        next.RotationDegrees = _session.RotationDegrees;
                        next.Elevation = _session.Elevation;
                        BindSession(next);
                    }
                }
                else if (!string.IsNullOrEmpty(createErr))
                {
                    StatusText.Text = createErr;
                    MessageBox.Show(this, createErr, Title, MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            finally
            {
                Show();
                Activate();
            }
        }

        private void AddNozzle_Click(object sender, RoutedEventArgs e)
        {
            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null) return;
            Close();
            doc.SendStringToExecute("_PLANTNOZZLEADD ", true, false, false);
        }

        private void EditNozzle_Click(object sender, RoutedEventArgs e)
        {
            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null) return;
            Close();
            doc.SendStringToExecute("_PLANTNOZZLEEDIT ", true, false, false);
        }

        private void Close_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }

        // ==================== 预览图滚轮缩放 / 拖拽平移 / 全屏看图 ====================

        private void SetZoom(double newZoom)
        {
            _zoom = Math.Max(0.5, Math.Min(6.0, newZoom));
            CreatePreviewScale.ScaleX = _zoom;
            CreatePreviewScale.ScaleY = _zoom;
            EditPreviewScale.ScaleX = _zoom;
            EditPreviewScale.ScaleY = _zoom;
            var pct = string.Format("{0:0}%", _zoom * 100);
            CreateZoomResetButton.Content = pct;
            EditZoomResetButton.Content = pct;
        }

        private void ResetZoom()
        {
            SetZoom(1.0);
            CreatePreviewTranslate.X = 0;
            CreatePreviewTranslate.Y = 0;
            EditPreviewTranslate.X = 0;
            EditPreviewTranslate.Y = 0;
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
            _panOriginX = _mode == EquipmentDialogMode.Edit ? EditPreviewTranslate.X : CreatePreviewTranslate.X;
            _panOriginY = _mode == EquipmentDialogMode.Edit ? EditPreviewTranslate.Y : CreatePreviewTranslate.Y;
            el.CaptureMouse();
        }

        private void Preview_MouseMove(object sender, MouseEventArgs e)
        {
            if (!_isPanning) return;
            var el = sender as UIElement;
            if (el == null) return;
            var cur = e.GetPosition(el);
            var dx = cur.X - _panStart.X;
            var dy = cur.Y - _panStart.Y;
            if (_mode == EquipmentDialogMode.Edit)
            {
                EditPreviewTranslate.X = _panOriginX + dx;
                EditPreviewTranslate.Y = _panOriginY + dy;
            }
            else
            {
                CreatePreviewTranslate.X = _panOriginX + dx;
                CreatePreviewTranslate.Y = _panOriginY + dy;
            }
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
                Title = (_session.DisplayName ?? _session.EquipmentName) + " — 高清示意图",
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
    }
}
