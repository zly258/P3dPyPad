using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shell;
using Microsoft.Win32;
using ICSharpCode.AvalonEdit.Highlighting;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    public partial class ScriptPadWindow : Window
    {
        private static readonly string StateDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "P3dPyPad");

        private readonly List<ParamRow> _rows = new List<ParamRow>();
        private ParsedScript _parsed = new ParsedScript();
        private List<PresetRow> _presets = new List<PresetRow>();
        private string _currentScriptPath = null;
        private bool _presetEventSuppressed;

        public ScriptPadWindow()
        {
            LocalizationManager.EnsureInitialized(this);
            InitializeComponent();
            ApplyEditor();
            CodeEditor.TextChanged += CodeEditor_TextChanged;
            PresetBox.DropDownOpened += PresetBox_DropDownOpened;
            KeyDown += ScriptPadWindow_KeyDown;

            LocalizationManager.LanguageChanged += OnLanguageChanged;
            OnLanguageChanged();

            LoadState();
            ShowParsed(ScriptParser.Parse(CodeEditor.Text));
        }

        private void OnLanguageChanged()
        {
            Title = LocalizationManager.T("PadWindowTitle");
            if (string.IsNullOrEmpty(_currentScriptPath))
            {
                ScriptPathText.Text = LocalizationManager.T("NoScriptSelected");
            }
            if (StatusInfoText.Text == "就绪" || StatusInfoText.Text == "Ready")
            {
                StatusInfoText.Text = LocalizationManager.T("Ready");
            }
            if (_parsed != null)
            {
                ShowParsed(_parsed);
            }
        }

        public void OpenScriptPath(string path)
        {
            if (string.IsNullOrEmpty(path) || !File.Exists(path))
            {
                return;
            }

            // 切换脚本时立即删除上次显示的 3D 模型
            var doc = AcadApp.DocumentManager.MdiActiveDocument;
            if (doc != null)
            {
                try
                {
                    using (doc.LockDocument())
                    {
                        ScriptRunner.EraseLast(doc.Database);
                    }
                }
                catch
                {
                }
            }

            BeginLoading("正在加载脚本: " + Path.GetFileName(path) + " ...");
            try
            {
                LoadScriptFile(path);
            }
            finally
            {
                EndLoading(StatusInfoText.Text);
            }
        }

        private void BeginLoading(string message)
        {
            StatusInfoText.Text = message;
            if (LoadingBar != null)
            {
                LoadingBar.Visibility = Visibility.Visible;
            }
            if (WindowTaskbarInfo != null)
            {
                WindowTaskbarInfo.ProgressState = TaskbarItemProgressState.Indeterminate;
                WindowTaskbarInfo.Description = message;
            }
            Mouse.OverrideCursor = Cursors.Wait;
            System.Windows.Forms.Application.DoEvents();
        }

        private void EndLoading(string message = "就绪")
        {
            if (LoadingBar != null)
            {
                LoadingBar.Visibility = Visibility.Collapsed;
            }
            StatusInfoText.Text = message;
            if (WindowTaskbarInfo != null)
            {
                WindowTaskbarInfo.ProgressState = TaskbarItemProgressState.None;
                WindowTaskbarInfo.Description = message;
            }
            Mouse.OverrideCursor = null;
            System.Windows.Forms.Application.DoEvents();
        }

        private void ScriptPadWindow_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.F5)
            {
                Run_Click(RunButton, new RoutedEventArgs());
                e.Handled = true;
            }
            else if (e.Key == Key.S && (Keyboard.Modifiers & ModifierKeys.Control) == ModifierKeys.Control)
            {
                SaveScript_Click(SaveScriptButton, new RoutedEventArgs());
                e.Handled = true;
            }
        }

        private void CodeEditor_TextChanged(object sender, EventArgs e)
        {
            ShowParsed(ScriptParser.Parse(CodeEditor.Text));
        }

        #region 文件选择、同目录翻页与预设管理

        private void SelectScript_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Title = "选择 Python 脚本",
                Filter = "Python 脚本 (*.py)|*.py|所有文件 (*.*)|*.*",
                Multiselect = false
            };

            if (dialog.ShowDialog(this) != true)
            {
                return;
            }

            OpenScriptPath(dialog.FileName);
        }

        private void LoadScriptFile(string path)
        {
            if (string.IsNullOrEmpty(path) || !File.Exists(path))
            {
                return;
            }

            try
            {
                var text = File.ReadAllText(path, Encoding.UTF8);
                _currentScriptPath = path;
                ScriptPathText.Text = Path.GetFileName(path);
                ScriptPathText.ToolTip = path;

                CodeEditor.Text = text;
                StatusInfoText.Text = "已载入脚本：" + Path.GetFileName(path);
                LoadMatchingCsvForScript(path);
            }
            catch (Exception ex)
            {
                LogBox.Text = "读取脚本失败：" + ex.Message;
            }
        }

        private void LoadMatchingCsvForScript(string scriptPath)
        {
            _presetEventSuppressed = true;
            try
            {
                PresetBox.Items.Clear();
                PresetBox.Text = string.Empty;
            }
            finally
            {
                _presetEventSuppressed = false;
            }

            _presets.Clear();

            var csvPath = string.IsNullOrEmpty(scriptPath) ? null : Path.ChangeExtension(scriptPath, ".csv");
            if (string.IsNullOrEmpty(csvPath) || !File.Exists(csvPath))
            {
                PresetBar.Visibility = Visibility.Collapsed;
                return;
            }

            try
            {
                var rows = PresetReader.ReadAll(csvPath);
                if (rows.Count == 0)
                {
                    PresetBar.Visibility = Visibility.Collapsed;
                    return;
                }

                _presets = rows;
                PresetBar.Visibility = Visibility.Visible;

                _presetEventSuppressed = true;
                try
                {
                    for (var i = 0; i < rows.Count; i++)
                    {
                        PresetBox.Items.Add(rows[i]);
                    }
                    PresetBox.SelectedIndex = 0;
                }
                finally
                {
                    _presetEventSuppressed = false;
                }

                ApplyPresetToControls(_presets[0]);
                SyncPresetText(_presets[0]);
                StatusInfoText.Text = string.Format("已载入脚本与同名规格表：{0} (共 {1} 组规格)", Path.GetFileName(csvPath), rows.Count);
            }
            catch
            {
                PresetBar.Visibility = Visibility.Collapsed;
            }
        }

        private void PresetBox_DropDownOpened(object sender, EventArgs e)
        {
            if (PresetBox.Items.Count > 0)
            {
                return;
            }
            PresetBox.IsDropDownOpen = false;
        }

        private void PresetBox_KeyUp(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Up || e.Key == Key.Down || e.Key == Key.Enter || e.Key == Key.Escape || e.Key == Key.Tab)
            {
                return;
            }

            var query = PresetBox.Text ?? string.Empty;
            FilterPresets(query);
            if (PresetBox.Items.Count > 0)
            {
                PresetBox.IsDropDownOpen = true;
            }
        }

        private void FilterPresets(string query)
        {
            _presetEventSuppressed = true;
            try
            {
                PresetBox.Items.Clear();

                var q = query.Trim().ToLowerInvariant();
                for (var i = 0; i < _presets.Count; i++)
                {
                    var p = _presets[i];
                    if (string.IsNullOrEmpty(q) ||
                        (p.Name != null && p.Name.ToLowerInvariant().Contains(q)) ||
                        (p.DisplayName != null && p.DisplayName.ToLowerInvariant().Contains(q)))
                    {
                        PresetBox.Items.Add(p);
                    }
                }

                if (!string.Equals(PresetBox.Text, query, StringComparison.Ordinal))
                {
                    PresetBox.Text = query;
                    var host = PresetBox.Template == null
                        ? null
                        : PresetBox.Template.FindName("PART_EditableTextBox", PresetBox) as TextBox;
                    if (host != null)
                    {
                        host.CaretIndex = host.Text == null ? 0 : host.Text.Length;
                    }
                }
            }
            finally
            {
                _presetEventSuppressed = false;
            }
        }

        private void PresetBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_presetEventSuppressed)
            {
                return;
            }

            var selection = PresetBox.SelectedItem as PresetRow;
            if (selection == null)
            {
                return;
            }

            ApplyPresetToControls(selection);
            SyncPresetText(selection);
            StatusInfoText.Text = "已应用规格：" + selection.Name;
        }

        private void SyncPresetText(PresetRow preset)
        {
            if (preset == null)
            {
                return;
            }

            var text = preset.ToString();
            if (string.Equals(PresetBox.Text, text, StringComparison.Ordinal))
            {
                return;
            }

            _presetEventSuppressed = true;
            try
            {
                PresetBox.Text = text;
                var host = PresetBox.Template == null
                    ? null
                    : PresetBox.Template.FindName("PART_EditableTextBox", PresetBox) as TextBox;
                if (host != null)
                {
                    host.CaretIndex = host.Text == null ? 0 : host.Text.Length;
                }
            }
            finally
            {
                _presetEventSuppressed = false;
            }
        }

        private void ApplyPresetToControls(PresetRow preset)
        {
            if (preset == null)
            {
                return;
            }

            for (var i = 0; i < _rows.Count; i++)
            {
                string value;
                if (preset.TryGetValue(_rows[i].Name, out value))
                {
                    _rows[i].Box.Text = value;
                }
            }
        }

        private void ResetDefaults_Click(object sender, RoutedEventArgs e)
        {
            for (var i = 0; i < _rows.Count; i++)
            {
                _rows[i].Box.Text = _rows[i].ScriptDefault;
            }
            StatusInfoText.Text = "已重置为 Python 脚本签名默认参数";
        }

        #endregion

        #region 保存与运行建模

        private void SaveScript_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var target = _currentScriptPath;
                if (string.IsNullOrEmpty(target))
                {
                    var dialog = new SaveFileDialog
                    {
                        Title = "保存 Python 脚本",
                        Filter = "Python 脚本 (*.py)|*.py|所有文件 (*.*)|*.*",
                        FileName = (!string.IsNullOrEmpty(_parsed.EntryName) ? _parsed.EntryName : "NEW_SUPPORT") + ".py"
                    };
                    if (dialog.ShowDialog(this) != true)
                    {
                        return;
                    }
                    target = dialog.FileName;
                    _currentScriptPath = target;
                    ScriptPathText.Text = Path.GetFileName(target);
                    ScriptPathText.ToolTip = target;
                }

                File.WriteAllText(target, CodeEditor.Text ?? string.Empty, new UTF8Encoding(false));
                SaveState();
                StatusInfoText.Text = "已保存脚本：" + Path.GetFileName(target);
            }
            catch (Exception ex)
            {
                LogBox.Text = "保存脚本失败：" + ex.Message;
                StatusInfoText.Text = "保存失败";
            }
        }

        private void Run_Click(object sender, RoutedEventArgs e)
        {
            RunButton.IsEnabled = false;
            BeginLoading("正在运行脚本并在 AutoCAD 中生成 3D 模型...");
            try
            {
                SaveState();
                if (string.IsNullOrEmpty(_parsed.EntryName))
                {
                    LogBox.Text = "没有找到 def 函数。请粘贴完整脚本。";
                    EndLoading("执行失败：无入口函数");
                    return;
                }

                var values = new Dictionary<string, string>(StringComparer.Ordinal);
                for (var i = 0; i < _rows.Count; i++)
                {
                    values[_rows[i].Name] = _rows[i].Box.Text;
                }

                var result = ScriptRunner.Run(new ScriptRunRequest
                {
                    ScriptPath = _currentScriptPath,
                    PresetName = PresetBox.Text,
                    Code = CodeEditor.Text,
                    Values = values
                });

                LogBox.Text = result.Message;
                EndLoading(result.Ok ? "生成成功" : "执行出错");
            }
            catch (Exception ex)
            {
                LogBox.Text = ex.Message;
                EndLoading("运行时异常：" + ex.Message);
            }
            finally
            {
                RunButton.IsEnabled = true;
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            try
            {
                SaveState();
            }
            catch (Exception)
            {
            }

            base.OnClosed(e);
        }

        #endregion

        #region 参数解析与控件生成

        private void ShowParsed(ParsedScript parsed)
        {
            var edited = new Dictionary<string, ParamRow>(StringComparer.Ordinal);
            for (var i = 0; i < _rows.Count; i++)
            {
                edited[_rows[i].Name] = _rows[i];
            }

            _parsed = parsed ?? new ParsedScript();
            _rows.Clear();
            ParamList.Children.Clear();

            ParamHeaderEntry.Text = string.IsNullOrEmpty(_parsed.EntryName) ? "def" : "def " + _parsed.EntryName;
            CodeGroupTitle.Text = string.IsNullOrEmpty(_parsed.EntryName) ? "Python 脚本源码 (Plant 3D 内核)" : string.Format("Python 脚本源码 ({0})", _parsed.EntryName);

            if (_parsed.Parameters.Count == 0)
            {
                ParamList.Children.Add(new TextBlock
                {
                    Style = (Style)FindResource("Text.Caption"),
                    Text = string.IsNullOrEmpty(_parsed.EntryName) ? "脚本需要包含 def 函数与 @param 装饰器。" : "这个函数没有定义参数。",
                    TextWrapping = TextWrapping.Wrap,
                    Margin = new Thickness(8, 12, 8, 12)
                });
                return;
            }

            for (var i = 0; i < _parsed.Parameters.Count; i++)
            {
                var param = _parsed.Parameters[i];
                var value = param.DefaultText ?? string.Empty;
                ParamRow previous;
                if (edited.TryGetValue(param.Name, out previous) && previous.Box.Text != previous.ScriptDefault)
                {
                    value = previous.Box.Text;
                }

                var rowBorder = new Border
                {
                    BorderBrush = (Brush)FindResource("Brush.Border"),
                    BorderThickness = new Thickness(0, 0, 0, 1),
                    MinHeight = (double)FindResource("Layout.RowHeight"),
                    ClipToBounds = true
                };

                var rowGrid = new Grid();
                rowGrid.ColumnDefinitions.Add(new ColumnDefinition
                {
                    Width = (GridLength)FindResource("Layout.PropertyGridNameColumn")
                });
                rowGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1) });
                rowGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });

                var description = string.IsNullOrEmpty(param.Tooltip) ? param.TooltipLong : param.Tooltip;
                var leftPanel = new DockPanel
                {
                    Background = (Brush)FindResource("Brush.SurfaceAlt"),
                    VerticalAlignment = VerticalAlignment.Stretch,
                    HorizontalAlignment = HorizontalAlignment.Stretch,
                    ClipToBounds = true,
                    ToolTip = string.IsNullOrEmpty(description)
                        ? param.TypeName
                        : string.Format("{0}\n类型: {1}\n{2}", param.Name, param.TypeName, param.TooltipLong)
                };

                var nameText = new TextBlock
                {
                    Text = param.Name,
                    FontWeight = FontWeights.SemiBold,
                    FontSize = (double)FindResource("FontSize.Caption"),
                    Foreground = (Brush)FindResource("Brush.Text.Primary"),
                    VerticalAlignment = VerticalAlignment.Center,
                    TextWrapping = TextWrapping.NoWrap,
                    TextTrimming = TextTrimming.CharacterEllipsis,
                    Margin = new Thickness(6, 0, 4, 0)
                };
                leftPanel.Children.Add(nameText);

                if (!string.IsNullOrEmpty(description))
                {
                    var descText = new TextBlock
                    {
                        Text = description,
                        FontSize = (double)FindResource("FontSize.Caption"),
                        Foreground = (Brush)FindResource("Brush.Text.Secondary"),
                        VerticalAlignment = VerticalAlignment.Center,
                        TextWrapping = TextWrapping.NoWrap,
                        TextTrimming = TextTrimming.CharacterEllipsis,
                        Margin = new Thickness(0, 0, 4, 0)
                    };
                    leftPanel.Children.Add(descText);
                }

                Grid.SetColumn(leftPanel, 0);
                rowGrid.Children.Add(leftPanel);

                var splitBorder = new Border
                {
                    Background = (Brush)FindResource("Brush.Border")
                };
                Grid.SetColumn(splitBorder, 1);
                rowGrid.Children.Add(splitBorder);

                var box = new TextBox
                {
                    Text = value,
                    Height = (double)FindResource("Layout.ControlHeight"),
                    MinHeight = 0,
                    FontSize = (double)FindResource("FontSize.Body"),
                    VerticalContentAlignment = VerticalAlignment.Center,
                    Padding = (Thickness)FindResource("Layout.InputPadding"),
                    Margin = new Thickness(4, 1, 4, 1),
                    BorderThickness = new Thickness(1),
                    BorderBrush = (Brush)FindResource("Brush.Border.Control"),
                    ToolTip = string.IsNullOrEmpty(param.TooltipLong) ? param.TypeName : param.TooltipLong
                };
                Grid.SetColumn(box, 2);
                rowGrid.Children.Add(box);

                rowBorder.Child = rowGrid;
                ParamList.Children.Add(rowBorder);

                _rows.Add(new ParamRow
                {
                    Name = param.Name,
                    ScriptDefault = param.DefaultText ?? string.Empty,
                    Box = box
                });
            }

            if (PresetBox.SelectedItem is PresetRow currentPreset)
            {
                ApplyPresetToControls(currentPreset);
            }
        }

        private void LoadState()
        {
            var scriptDraft = Path.Combine(StateDir, "draft.py");
            if (File.Exists(scriptDraft))
            {
                var text = File.ReadAllText(scriptDraft, Encoding.UTF8);
                if (!string.IsNullOrWhiteSpace(text))
                {
                    CodeEditor.Text = text;
                }
            }

            var lastScriptFile = Path.Combine(StateDir, "last_script.txt");
            if (File.Exists(lastScriptFile))
            {
                var savedPath = File.ReadAllText(lastScriptFile, Encoding.UTF8).Trim();
                if (File.Exists(savedPath))
                {
                    _currentScriptPath = savedPath;
                    ScriptPathText.Text = Path.GetFileName(savedPath);
                    ScriptPathText.ToolTip = savedPath;
                    LoadMatchingCsvForScript(savedPath);
                }
            }
        }

        private void SaveState()
        {
            Directory.CreateDirectory(StateDir);
            File.WriteAllText(Path.Combine(StateDir, "draft.py"), CodeEditor.Text ?? string.Empty, new UTF8Encoding(false));
            if (!string.IsNullOrEmpty(_currentScriptPath))
            {
                File.WriteAllText(Path.Combine(StateDir, "last_script.txt"), _currentScriptPath, new UTF8Encoding(false));
            }
        }

        private void ApplyEditor()
        {
            CodeEditor.FontFamily = new FontFamily("Consolas, Cascadia Mono, Microsoft YaHei");
            CodeEditor.Background = (Brush)FindResource("Brush.Surface");
            CodeEditor.Foreground = (Brush)FindResource("Brush.Text.Primary");
            CodeEditor.LineNumbersForeground = (Brush)FindResource("Brush.Text.Secondary");
            CodeEditor.ShowLineNumbers = true;
            CodeEditor.Options.HighlightCurrentLine = true;
            CodeEditor.Options.IndentationSize = 4;
            CodeEditor.TextArea.SelectionBrush = (Brush)FindResource("Brush.Selection");
            CodeEditor.TextArea.SelectionForeground = (Brush)FindResource("Brush.Text.Primary");
            CodeEditor.TextArea.TextView.CurrentLineBackground = (Brush)FindResource("Brush.SurfaceAlt");
            var highlighting = HighlightingManager.Instance.GetDefinition("Python");
            if (highlighting != null)
            {
                CodeEditor.SyntaxHighlighting = highlighting;
            }
        }

        #endregion

        private sealed class ParamRow
        {
            public string Name { get; set; }
            public string ScriptDefault { get; set; }
            public TextBox Box { get; set; }
        }
    }
}
