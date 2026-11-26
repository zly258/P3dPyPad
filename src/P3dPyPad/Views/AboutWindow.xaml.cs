using System.Diagnostics;
using System.Windows;
using System.Windows.Input;
using System.Windows.Navigation;

namespace P3dPyPad
{
    public partial class AboutWindow : Window
    {
        public AboutWindow()
        {
            LocalizationManager.EnsureInitialized(this);
            InitializeComponent();
            KeyDown += (s, e) =>
            {
                if (e.Key == Key.Escape || e.Key == Key.Enter) Close();
            };
        }

        private void Hyperlink_RequestNavigate(object sender, RequestNavigateEventArgs e)
        {
            try
            {
                Process.Start(new ProcessStartInfo(e.Uri.AbsoluteUri) { UseShellExecute = true });
            }
            catch
            {
                // 忽略系统未配置默认浏览器或邮件客户端时的异常
            }
            e.Handled = true;
        }

        private void OkButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
