using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using Autodesk.AutoCAD.DatabaseServices;

namespace P3dPyPad
{
    public enum EquipmentDialogMode
    {
        Create = 0,
        Edit = 1
    }

    /// <summary>
    /// 设备库中单个 .peqx 模板的元数据与预览图信息。
    /// </summary>
    public sealed class EquipmentTemplateItem
    {
        public string FilePath { get; set; }
        public string FileName { get; set; }
        public string Name { get; set; }
        public string DisplayName { get; set; }
        public string Type { get; set; }
        public string SubType { get; set; }
        public string PartType { get; set; }
        public string PartSubType { get; set; }
        public string CategoryKey { get; set; }
        public string CategoryDisplayName { get; set; }
        public string Guid { get; set; }
        public string LengthUnit { get; set; }
        public bool IsCustom { get; set; }
        public bool IsInternalTemplate { get; set; }
        public string ScriptPath { get; set; }
        public string HighResPreviewPath { get; set; }
        public byte[] EmbeddedPreviewBytes { get; set; }
        public List<EquipmentParamItem> DefaultParameters { get; set; } = new List<EquipmentParamItem>();
        public List<EquipmentNozzleItem> DefaultNozzles { get; set; } = new List<EquipmentNozzleItem>();

        private ImageSource _thumbnail;
        private ImageSource _fullPreview;

        public string SourceBadge => IsCustom
            ? LocalizationManager.T("EqSourceCustom", "自定义", "Custom")
            : LocalizationManager.T("EqSourceBuiltIn", "原厂", "Built-in");

        public string Subtitle => string.IsNullOrEmpty(CategoryDisplayName)
            ? Name
            : CategoryDisplayName + " · " + Name;

        public ImageSource Thumbnail
        {
            get
            {
                if (_thumbnail == null)
                {
                    _thumbnail = LoadImage(decodePixelWidth: 96);
                }
                return _thumbnail;
            }
        }

        public ImageSource FullPreview
        {
            get
            {
                if (_fullPreview == null)
                {
                    _fullPreview = LoadImage(decodePixelWidth: 0);
                }
                return _fullPreview;
            }
        }

        public void ResetImageCache()
        {
            _thumbnail = null;
            _fullPreview = null;
        }

        private ImageSource LoadImage(int decodePixelWidth)
        {
            try
            {
                if (!string.IsNullOrEmpty(HighResPreviewPath) && File.Exists(HighResPreviewPath))
                {
                    var bytes = File.ReadAllBytes(HighResPreviewPath);
                    return CreateBitmapFromBytes(bytes, decodePixelWidth);
                }

                if (EmbeddedPreviewBytes != null && EmbeddedPreviewBytes.Length > 0)
                {
                    return CreateBitmapFromBytes(EmbeddedPreviewBytes, decodePixelWidth);
                }
            }
            catch
            {
            }
            return null;
        }

        private static BitmapImage CreateBitmapFromBytes(byte[] bytes, int decodePixelWidth)
        {
            using (var ms = new MemoryStream(bytes))
            {
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                if (decodePixelWidth > 0)
                {
                    bmp.DecodePixelWidth = decodePixelWidth;
                }
                bmp.StreamSource = ms;
                bmp.EndInit();
                bmp.Freeze();
                return bmp;
            }
        }
    }

    /// <summary>
    /// 单个可编辑的设备尺寸参数项（支持主参数与分类参数）。
    /// </summary>
    public sealed class EquipmentParamItem : INotifyPropertyChanged
    {
        private string _value;

        public string GroupName { get; set; }
        public int CategoryIndex { get; set; } = -1;
        public string Name { get; set; }
        public string DisplayName { get; set; }
        public string Tooltip { get; set; }
        public string DefaultValue { get; set; }
        public string ParamType { get; set; }
        public string Unit { get; set; }

        public string Value
        {
            get => _value;
            set
            {
                if (!string.Equals(_value, value, StringComparison.Ordinal))
                {
                    _value = value;
                    OnPropertyChanged();
                    OnPropertyChanged(nameof(IsModified));
                }
            }
        }

        public bool IsModified => !string.Equals((_value ?? string.Empty).Trim(), (DefaultValue ?? string.Empty).Trim(), StringComparison.Ordinal);

        public string DescriptionText
        {
            get
            {
                if (!string.IsNullOrWhiteSpace(Tooltip)) return Tooltip;
                if (!string.IsNullOrWhiteSpace(DisplayName) && !string.Equals(DisplayName, Name, StringComparison.OrdinalIgnoreCase))
                {
                    return DisplayName;
                }
                return string.Empty;
            }
        }

        public EquipmentParamItem Clone()
        {
            return new EquipmentParamItem
            {
                GroupName = GroupName,
                CategoryIndex = CategoryIndex,
                Name = Name,
                DisplayName = DisplayName,
                Tooltip = Tooltip,
                DefaultValue = DefaultValue,
                ParamType = ParamType,
                Unit = Unit,
                _value = _value
            };
        }

        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }

    /// <summary>
    /// 单个设备工程特性（DataManager 属性）。
    /// </summary>
    public sealed class EquipmentPropertyItem : INotifyPropertyChanged
    {
        private string _value;

        public string Name { get; set; }
        public string DisplayName { get; set; }
        public string DefaultValue { get; set; }
        public bool IsCommon { get; set; }
        public bool IsReadOnly { get; set; }

        public string Value
        {
            get => _value;
            set
            {
                if (!string.Equals(_value, value, StringComparison.Ordinal))
                {
                    _value = value;
                    OnPropertyChanged();
                }
            }
        }

        public string LabelText => !string.IsNullOrWhiteSpace(DisplayName) ? DisplayName : Name;

        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }

    /// <summary>
    /// 设备管嘴条目（独立显示在管嘴 Tab）。
    /// </summary>
    public sealed class EquipmentNozzleItem : INotifyPropertyChanged
    {
        private string _nozzleTag;

        public int PortIndex { get; set; }
        public string PortName { get; set; }
        public string Name { get; set; }
        public string NominalSize { get; set; }
        public string PressureClass { get; set; }
        public string Facing { get; set; }
        public string EndType { get; set; }
        public string LongDescription { get; set; }

        public string NozzleTag
        {
            get => _nozzleTag;
            set
            {
                if (!string.Equals(_nozzleTag, value, StringComparison.Ordinal))
                {
                    _nozzleTag = value;
                    OnPropertyChanged();
                }
            }
        }

        public EquipmentNozzleItem Clone()
        {
            return new EquipmentNozzleItem
            {
                PortIndex = PortIndex,
                PortName = PortName,
                Name = Name,
                NominalSize = NominalSize,
                PressureClass = PressureClass,
                Facing = Facing,
                EndType = EndType,
                LongDescription = LongDescription,
                _nozzleTag = _nozzleTag
            };
        }

        public event PropertyChangedEventHandler PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string name = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        }
    }

    /// <summary>
    /// 当前正在创建或编辑的设备会话状态。
    /// </summary>
    public sealed class EquipmentEditSession
    {
        public EquipmentDialogMode Mode { get; set; }
        public ObjectId TargetObjectId { get; set; } = ObjectId.Null;
        public object NativeEquipmentType { get; set; }
        public EquipmentTemplateItem Template { get; set; }
        public string EquipmentName { get; set; }
        public string DisplayName { get; set; }
        public string CategoryDisplayName { get; set; }
        public string LengthUnit { get; set; } = "mm";
        public string EquipmentTag { get; set; } = string.Empty;
        public double Elevation { get; set; }
        public double RotationDegrees { get; set; }
        public List<EquipmentParamItem> Parameters { get; set; } = new List<EquipmentParamItem>();
        public List<EquipmentPropertyItem> Properties { get; set; } = new List<EquipmentPropertyItem>();
        public List<EquipmentNozzleItem> Nozzles { get; set; } = new List<EquipmentNozzleItem>();
    }
}
