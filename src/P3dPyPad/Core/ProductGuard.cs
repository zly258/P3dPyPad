using System;
using System.Diagnostics;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    /// <summary>
    /// 运行产品门禁：P3dPyPad 只在 AutoCAD Plant 3D 中启用。
    /// Plant 3D 本身基于 AutoCAD，所以普通 AutoCAD 也会加载本程序集，
    /// 必须通过产品标识、已加载程序集和已加载模块三重判断。
    /// </summary>
    internal static class ProductGuard
    {
        private static readonly object SyncRoot = new object();
        private static bool? _isPlant3D;

        public static bool IsPlant3D
        {
            get
            {
                if (_isPlant3D.HasValue)
                {
                    return _isPlant3D.Value;
                }

                lock (SyncRoot)
                {
                    if (!_isPlant3D.HasValue)
                    {
                        // 只缓存肯定结果；否定结果每次重新探测，
                        // 避免 Plant 3D 模块延迟加载时被永久误判为普通 AutoCAD。
                        var detected = Detect();
                        if (detected)
                        {
                            _isPlant3D = true;
                        }
                        return detected;
                    }
                    return _isPlant3D.Value;
                }
            }
        }

        /// <summary>
        /// 校验当前宿主是否为 Plant 3D；不是时在命令行给出一次明确提示。
        /// </summary>
        public static bool EnsurePlant3D()
        {
            if (IsPlant3D)
            {
                return true;
            }

            try
            {
                var doc = AcadApp.DocumentManager.MdiActiveDocument;
                if (doc != null)
                {
                    doc.Editor.WriteMessage("\nP3dPyPad 仅支持 Autodesk AutoCAD Plant 3D，当前 AutoCAD 中已禁用该插件。\n");
                }
            }
            catch
            {
            }

            return false;
        }

        private static bool Detect()
        {
            if (HasPlantProductName())
            {
                return true;
            }

            if (HasPlantAssemblyLoaded())
            {
                return true;
            }

            return HasPlantModuleLoaded();
        }

        private static bool HasPlantProductName()
        {
            try
            {
                var product = AcadApp.GetSystemVariable("PRODUCT") as string;
                if (!string.IsNullOrEmpty(product) &&
                    product.IndexOf("Plant", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    return true;
                }
            }
            catch
            {
            }

            return false;
        }

        private static bool HasPlantAssemblyLoaded()
        {
            try
            {
                foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies())
                {
                    var name = assembly.GetName().Name;
                    if (string.IsNullOrEmpty(name))
                    {
                        continue;
                    }

                    if (name.StartsWith("PnP3d", StringComparison.OrdinalIgnoreCase) ||
                        name.StartsWith("PnPProject", StringComparison.OrdinalIgnoreCase) ||
                        name.StartsWith("Autodesk.ProcessPower", StringComparison.OrdinalIgnoreCase))
                    {
                        return true;
                    }
                }
            }
            catch
            {
            }

            return false;
        }

        private static bool HasPlantModuleLoaded()
        {
            try
            {
                using (var process = Process.GetCurrentProcess())
                {
                    foreach (ProcessModule module in process.Modules)
                    {
                        string moduleName;
                        string modulePath;
                        try
                        {
                            moduleName = module.ModuleName;
                            modulePath = module.FileName;
                        }
                        catch
                        {
                            continue;
                        }

                        if (string.IsNullOrEmpty(moduleName))
                        {
                            continue;
                        }

                        if (moduleName.StartsWith("PnP3d", StringComparison.OrdinalIgnoreCase) ||
                            moduleName.StartsWith("PnPProject", StringComparison.OrdinalIgnoreCase) ||
                            string.Equals(moduleName, "ProcessPower.arx", StringComparison.OrdinalIgnoreCase))
                        {
                            return true;
                        }

                        if (!string.IsNullOrEmpty(modulePath) &&
                            modulePath.IndexOf("\\PLNT3D\\", StringComparison.OrdinalIgnoreCase) >= 0)
                        {
                            return true;
                        }
                    }
                }
            }
            catch
            {
            }

            return false;
        }
    }
}
