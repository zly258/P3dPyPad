using System;
using System.Globalization;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Media;

namespace P3dPyPad
{
    /// <summary>
    /// ComboBox 下拉弹层自适应辅助。
    ///
    /// 主题模板里的 Popup 固定 <c>Placement="Bottom"</c>，弹层又是一级顶层窗口，
    /// 所以当 ComboBox 靠近屏幕（或窗口）底边时，展开的列表会一直往下长，
    /// 超出可见区域的部分直接被屏幕边缘裁掉——这就是"下拉列表被挡住"的根因。
    ///
    /// 这里在 DropDownOpened 时按 ComboBox 在屏幕上的实际位置做两件事：
    ///   1. 下方空间不足且上方更宽裕时，把弹层翻到控件上方；
    ///   2. 按可用空间收紧弹层最大高度，超出部分由弹层内部滚动条承接。
    /// </summary>
    public static class ComboBoxAssist
    {
        /// <summary>弹层与屏幕边缘之间保留的安全间隙。</summary>
        private const double ScreenGap = 8.0;

        /// <summary>弹层允许收缩到的最小高度，低于这个值就没法用了。</summary>
        private const double MinPopupHeight = 120.0;

        public static readonly DependencyProperty AutoFlipDropDownProperty =
            DependencyProperty.RegisterAttached(
                "AutoFlipDropDown",
                typeof(bool),
                typeof(ComboBoxAssist),
                new PropertyMetadata(false, OnAutoFlipDropDownChanged));

        public static bool GetAutoFlipDropDown(DependencyObject obj)
        {
            return (bool)obj.GetValue(AutoFlipDropDownProperty);
        }

        public static void SetAutoFlipDropDown(DependencyObject obj, bool value)
        {
            obj.SetValue(AutoFlipDropDownProperty, value);
        }

        private static void OnAutoFlipDropDownChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
        {
            var combo = d as ComboBox;
            if (combo == null) return;

            combo.DropDownOpened -= OnDropDownOpened;
            combo.DropDownClosed -= OnDropDownClosed;

            if ((bool)e.NewValue)
            {
                combo.DropDownOpened += OnDropDownOpened;
                combo.DropDownClosed += OnDropDownClosed;
            }
        }

        private static void OnDropDownOpened(object sender, EventArgs e)
        {
            var combo = sender as ComboBox;
            if (combo == null) return;

            // 首次展开时模板可能刚应用完，视觉树里的 Popup 还取不到；
            // 用 Dispatcher 排到当前布局之后，确保 PART_Popup 已就绪。
            combo.Dispatcher.BeginInvoke(
                new Action(() => ApplyFlip(combo)),
                System.Windows.Threading.DispatcherPriority.Loaded);
        }

        /// <summary>
        /// 最近一次翻转判定的诊断信息，仅供渲染工具与现场排查读取；
        /// 不参与任何业务逻辑，正式使用时可忽略。
        /// </summary>
        public static string LastDiagnostics = "";

        private static void ApplyFlip(ComboBox combo)
        {
            LastDiagnostics = "no-popup";
            var popup = FindPopup(combo);
            if (popup == null) return;

            var dropDown = popup.Child as FrameworkElement;
            if (dropDown == null) { LastDiagnostics = "no-child"; return; }

            Rect comboRect;
            try
            {
                var topLeft = combo.PointToScreen(new Point(0.0, 0.0));
                comboRect = new Rect(topLeft.X, topLeft.Y, combo.ActualWidth, combo.ActualHeight);
            }
            catch (InvalidOperationException)
            {
                // 控件还没进可视化树，保持模板默认行为。
                return;
            }

            var workArea = GetWorkingArea(comboRect.TopLeft, combo);

            // 下方/上方各自还能放多高（扣掉安全间隙）
            var spaceBelow = workArea.Bottom - comboRect.Bottom - ScreenGap;
            var spaceAbove = comboRect.Top - workArea.Top - ScreenGap;

            // 下方放得下就向下展开（符合直觉）；下方不够且上方更宽裕时才翻到上方。
            var preferBelow = spaceBelow >= MinPopupHeight || spaceBelow >= spaceAbove;
            popup.Placement = preferBelow ? PlacementMode.Bottom : PlacementMode.Top;

            // 弹层向上时，原来的 3px 下边距要挪到上边，避免贴住控件。
            dropDown.Margin = preferBelow ? new Thickness(0.0, 3.0, 0.0, 0.0) : new Thickness(0.0, 0.0, 0.0, 3.0);

            // 按实际可用空间收紧弹层高度：放不下就在弹层内部滚动，绝不越出屏幕。
            var available = preferBelow ? spaceBelow : spaceAbove;
            var limit = combo.MaxDropDownHeight > 0.0 ? combo.MaxDropDownHeight : double.PositiveInfinity;
            dropDown.MaxHeight = Math.Max(MinPopupHeight, Math.Min(available, limit));

            LastDiagnostics = string.Format(CultureInfo.InvariantCulture,
                "combo={0:0.#},{1:0.#},{2:0.#}x{3:0.#} wa={4:0.#},{5:0.#},{6:0.#}x{7:0.#} below={8:0.#} above={9:0.#} -> {10}",
                comboRect.X, comboRect.Y, comboRect.Width, comboRect.Height,
                workArea.X, workArea.Y, workArea.Width, workArea.Height,
                spaceBelow, spaceAbove, popup.Placement);
        }

        private static void OnDropDownClosed(object sender, EventArgs e)
        {
            var combo = sender as ComboBox;
            if (combo == null) return;

            var popup = FindPopup(combo);
            if (popup == null) return;

            // 还原模板里声明的定位与间距，下一次展开会重新计算。
            popup.Placement = PlacementMode.Bottom;
            if (popup.Child is FrameworkElement dropDown)
            {
                dropDown.Margin = new Thickness(0.0, 3.0, 0.0, 0.0);
                dropDown.ClearValue(FrameworkElement.MaxHeightProperty);
            }
        }

        /// <summary>
        /// 取 ComboBox 所在显示器的可用工作区，统一换算成 WPF 的 DIP 坐标。
        ///
        /// 注意：<c>PointToScreen</c> 返回的是**设备像素**，而 <c>SystemParameters.WorkArea</c>
        /// 是 **DIP**。两者在 125%/150% DPI 下不能直接相减，否则算出来的可用空间是错的，
        /// 翻转判断会一直失败。这里用同一套变换把工作区也换成设备像素再比较。
        /// </summary>
        private static Rect GetWorkingArea(Point screenPointDip, Visual reference)
        {
            try
            {
                var source = PresentationSource.FromVisual(reference);
                var m = source != null ? source.CompositionTarget.TransformToDevice : Matrix.Identity;

                var device = m.Transform(screenPointDip);
                var screen = System.Windows.Forms.Screen.FromPoint(
                    new System.Drawing.Point((int)device.X, (int)device.Y));
                var area = screen.WorkingArea;

                // 把设备像素的工作区换回 DIP，保证后续比较全在 DIP 空间里进行
                var inv = m;
                if (inv.HasInverse) inv.Invert();
                var tl = inv.Transform(new Point(area.Left, area.Top));
                var br = inv.Transform(new Point(area.Right, area.Bottom));
                return new Rect(tl, br);
            }
            catch (Exception)
            {
                var wa = SystemParameters.WorkArea;
                return new Rect(wa.Left, wa.Top, wa.Width, wa.Height);
            }
        }

        private static Popup FindPopup(DependencyObject root)
        {
            if (root == null) return null;

            var count = VisualTreeHelper.GetChildrenCount(root);
            for (var i = 0; i < count; i++)
            {
                var child = VisualTreeHelper.GetChild(root, i);
                if (child is Popup popup) return popup;

                var nested = FindPopup(child);
                if (nested != null) return nested;
            }
            return null;
        }
    }
}
