using System.Windows;
using System.Windows.Input;

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

        private void OkButton_Click(object sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
