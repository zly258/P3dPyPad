using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Forms;
using System.Windows.Media;
using System.Windows.Shell;
using Autodesk.AutoCAD.ApplicationServices;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    public partial class BatchTestWindow : Window
    {
        private readonly ObservableCollection<BatchItemResult> _items = new ObservableCollection<BatchItemResult>();
        private ICollectionView _itemsView;
        private bool _isCancelled = false;
        private bool _isRunning = false;

        public BatchTestWindow()
        {
            LocalizationManager.EnsureInitialized(this);
            InitializeComponent();
            _itemsView = CollectionViewSource.GetDefaultView(_items);
            _itemsView.Filter = FilterItem;
            ResultGrid.ItemsSource = _itemsView;

            InitLanguageCombo();
            LocalizationManager.LanguageChanged += OnLanguageChanged;
            OnLanguageChanged();

            // 不设置任何默认初始目录：源目录与出图目录都由用户显式选择。
            UpdateProgressText(0, 0);
        }

        private bool _suppressLangCombo;

        private void InitLanguageCombo()
        {
            if (LanguageCombo == null) return;
            _suppressLangCombo = true;
            try
            {
                switch (LocalizationManager.CurrentOption)
                {
                    case LanguageOption.Auto: LanguageCombo.SelectedIndex = 0; break;
                    case LanguageOption.Chinese: LanguageCombo.SelectedIndex = 1; break;
                    case LanguageOption.English: LanguageCombo.SelectedIndex = 2; break;
                }
            }
            finally
            {
                _suppressLangCombo = false;
            }
        }

        private void LanguageCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_suppressLangCombo || LanguageCombo == null) return;
            switch (LanguageCombo.SelectedIndex)
            {
                case 0: LocalizationManager.SetLanguage(LanguageOption.Auto); break;
                case 1: LocalizationManager.SetLanguage(LanguageOption.Chinese); break;
                case 2: LocalizationManager.SetLanguage(LanguageOption.English); break;
            }
        }

        private void OnLanguageChanged()
        {
            Title = LocalizationManager.T("BatchWindowTitle");
            InitLanguageCombo();
        }

        /// <summary>切换脚本目录。出图目录不自动填充，由用户显式选择。</summary>
        public void SetSourceDirectory(string folderPath)
        {
            if (string.IsNullOrEmpty(folderPath) || !Directory.Exists(folderPath))
            {
                return;
            }
            SourceDirBox.Text = folderPath;
        }

        private bool FilterItem(object obj)
        {
            var item = obj as BatchItemResult;
            if (item == null || FilterCombo == null)
            {
                return true;
            }
            if (FilterCombo.SelectedIndex == 1)
            {
                return item.Success;
            }
            if (FilterCombo.SelectedIndex == 2)
            {
                return !item.Success;
            }
            return true;
        }

        private void FilterCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_itemsView != null)
            {
                _itemsView.Refresh();
            }
        }

        private void UpdateProgressText(int current, int total)
        {
            if (ProgressText != null)
            {
                ProgressText.Text = string.Format("{0} / {1}", current, total);
            }
        }

        private void BrowseSource_Click(object sender, RoutedEventArgs e)
        {
            using (var dlg = new FolderBrowserDialog())
            {
                dlg.Description = "选择包含 Plant 3D Python 脚本的目录";

                if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    SetSourceDirectory(dlg.SelectedPath);
                }
            }
        }

        private void BrowseOutput_Click(object sender, RoutedEventArgs e)
        {
            using (var dlg = new FolderBrowserDialog())
            {
                dlg.Description = "选择批量测试截图输出保存目录";

                if (dlg.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    OutputDirBox.Text = dlg.SelectedPath;
                }
            }
        }

        private void StartBatch_Click(object sender, RoutedEventArgs e)
        {
            var folder = SourceDirBox.Text.Trim();
            if (string.IsNullOrEmpty(folder) || !Directory.Exists(folder))
            {
                System.Windows.MessageBox.Show("请先选择有效的脚本目录！", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc == null)
            {
                System.Windows.MessageBox.Show("未检测到打开的 AutoCAD 图形文档！", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
                return;
            }

            _items.Clear();
            _isCancelled = false;
            _isRunning = true;

            var outDir = OutputDirBox.Text.Trim();
            if (string.IsNullOrEmpty(outDir))
            {
                System.Windows.MessageBox.Show("请先选择有效的出图目录！", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
                _isRunning = false;
                return;
            }

            StartButton.IsEnabled = false;
            StopButton.IsEnabled = true;
            SourceDirBox.IsEnabled = false;
            OutputDirBox.IsEnabled = false;

            StatusText.Text = "正在递归扫描目录并准备开始批量测试...";
            BatchProgress.Value = 0;
            if (WindowTaskbarInfo != null)
            {
                WindowTaskbarInfo.ProgressState = TaskbarItemProgressState.Indeterminate;
            }

            var sw = Stopwatch.StartNew();
            var successCount = 0;
            var failCount = 0;

            try
            {
                BatchRunner.RunDirectory(
                    doc,
                    folder,
                    outDir,
                    true,
                    (item, current, total) =>
                    {
                        Dispatcher.Invoke(() =>
                        {
                            _items.Add(item);
                            if (item.Success) successCount++;
                            else failCount++;

                            BatchProgress.Maximum = total;
                            BatchProgress.Value = current;
                            UpdateProgressText(current, total);

                            if (WindowTaskbarInfo != null)
                            {
                                WindowTaskbarInfo.ProgressState = TaskbarItemProgressState.Normal;
                                WindowTaskbarInfo.ProgressValue = (double)current / Math.Max(1, total);
                            }

                            StatusText.Text = string.Format(
                                "进度: {0} / {1} (成功: {2}, 失败: {3}) - 正在处理: {4}",
                                current, total, successCount, failCount, item.ScriptName);

                            if (ResultGrid.Items.Count > 0)
                            {
                                ResultGrid.ScrollIntoView(item);
                            }
                        });

                        System.Windows.Forms.Application.DoEvents();
                    },
                    () => _isCancelled
                );
            }
            finally
            {
                if (WindowTaskbarInfo != null)
                {
                    WindowTaskbarInfo.ProgressState = TaskbarItemProgressState.None;
                }
                sw.Stop();
                _isRunning = false;
                StartButton.IsEnabled = true;
                StopButton.IsEnabled = false;
                SourceDirBox.IsEnabled = true;
                OutputDirBox.IsEnabled = true;

                StatusText.Text = string.Format(
                    "测试完成！共处理: {0} 个脚本，成功: {1}，失败: {2}，总耗时: {3:F1} 秒",
                    _items.Count, successCount, failCount, sw.Elapsed.TotalSeconds);

                var reportPath = BatchReport.Write(outDir, folder, _items, sw.Elapsed, _isCancelled);
                if (!string.IsNullOrEmpty(reportPath))
                {
                    StatusText.Text += "  报告: " + Path.GetFileName(reportPath);
                    StatusText.ToolTip = reportPath;
                }
            }
        }

        private void StopBatch_Click(object sender, RoutedEventArgs e)
        {
            if (_isRunning)
            {
                _isCancelled = true;
                StatusText.Text = "正在停止测试...";
            }
        }

        private void ResultGrid_PreviewMouseRightButtonDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            var dep = e.OriginalSource as DependencyObject;
            while (dep != null && !(dep is DataGridRow))
            {
                dep = VisualTreeHelper.GetParent(dep);
            }
            if (dep is DataGridRow row)
            {
                row.IsSelected = true;
            }
        }

        private void ResultGrid_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item == null) return;

            if (item.HasImage && File.Exists(item.ImagePath))
            {
                try
                {
                    Process.Start(item.ImagePath);
                }
                catch (Exception ex)
                {
                    System.Windows.MessageBox.Show("打开截图失败: " + ex.Message, "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
                }
            }
            else if (!item.Success && !string.IsNullOrEmpty(item.ErrorMessage))
            {
                try
                {
                    System.Windows.Clipboard.SetText(item.ErrorMessage);
                }
                catch { }

                System.Windows.MessageBox.Show(
                    "测试失败原因 (已复制到剪贴板)：\n\n" + item.ErrorMessage,
                    "测试失败详情 - " + item.ScriptName,
                    MessageBoxButton.OK,
                    MessageBoxImage.Information);
            }
        }

        private void MenuOpenImage_Click(object sender, RoutedEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item != null && item.HasImage && File.Exists(item.ImagePath))
            {
                try
                {
                    Process.Start(item.ImagePath);
                }
                catch (Exception ex)
                {
                    System.Windows.MessageBox.Show("打开截图失败: " + ex.Message, "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
                }
            }
        }

        private void MenuLocateImage_Click(object sender, RoutedEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item != null && !string.IsNullOrEmpty(item.ImagePath) && File.Exists(item.ImagePath))
            {
                try
                {
                    Process.Start("explorer.exe", $"/select,\"{item.ImagePath}\"");
                }
                catch { }
            }
            else
            {
                OpenFolder_Click(sender, e);
            }
        }

        private void MenuCopyScriptPath_Click(object sender, RoutedEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item != null && !string.IsNullOrEmpty(item.ScriptPath))
            {
                try
                {
                    System.Windows.Clipboard.SetText(item.ScriptPath);
                }
                catch { }
            }
        }

        private void MenuCopyImagePath_Click(object sender, RoutedEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item != null && !string.IsNullOrEmpty(item.ImagePath))
            {
                try
                {
                    System.Windows.Clipboard.SetText(item.ImagePath);
                }
                catch { }
            }
        }

        private void MenuShowError_Click(object sender, RoutedEventArgs e)
        {
            var item = ResultGrid.SelectedItem as BatchItemResult;
            if (item != null && !string.IsNullOrEmpty(item.ErrorMessage))
            {
                try
                {
                    System.Windows.Clipboard.SetText(item.ErrorMessage);
                }
                catch { }

                System.Windows.MessageBox.Show(
                    item.ErrorMessage,
                    "测试失败原因 - " + item.ScriptName + " (已复制到剪贴板)",
                    MessageBoxButton.OK,
                    MessageBoxImage.Information);
            }
            else
            {
                System.Windows.MessageBox.Show("该项运行正常，无异常或错误信息。", "提示", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        private void OpenFolder_Click(object sender, RoutedEventArgs e)
        {
            var dir = OutputDirBox.Text.Trim();
            if (Directory.Exists(dir))
            {
                Process.Start("explorer.exe", dir);
            }
            else
            {
                var src = SourceDirBox.Text.Trim();
                if (Directory.Exists(src))
                {
                    Process.Start("explorer.exe", src);
                }
            }
        }

        protected override void OnClosing(CancelEventArgs e)
        {
            if (_isRunning)
            {
                _isCancelled = true;
            }
            base.OnClosing(e);
        }
    }
}
