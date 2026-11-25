using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Xml.Linq;

namespace P3dPyPad
{
    /// <summary>
    /// 直接扫描 Plant 3D 内容目录下的 CPak Common\equipment\*.peqx，
    /// 解析设备分类、尺寸参数、默认管嘴、高清预览图与脚本中文注释。
    /// 不依赖 Plant 3D 启动缓存，随时支持热刷新。
    /// </summary>
    internal static class EquipmentCatalogService
    {
        private static readonly Regex PyParamTooltipRegex = new Regex(
            @"@param\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*=[^)]*?TooltipShort\s*=\s*(?:u|U)?(?:""([^""]*)""|'([^']*)')",
            RegexOptions.Compiled);

        private static readonly Dictionary<string, (string Zh, string En)> BuiltInFriendlyNames =
            new Dictionary<string, (string Zh, string En)>(StringComparer.OrdinalIgnoreCase)
            {
                { "BoxTypeHeater", ("箱式加热炉", "Box Type Heater") },
                { "CylindricalHeater", ("圆筒加热炉", "Cylindrical Heater") },
                { "BreechLockHeatexchg", ("螺纹锁紧环换热器", "Breech Lock Heat Exchanger") },
                { "PlateFrameHeatexchg", ("板框式换热器", "Plate & Frame Heat Exchanger") },
                { "Reboiler", ("重沸器", "Reboiler") },
                { "VerticalDownHeatexchg", ("立式下进料换热器", "Vertical Down Heat Exchanger") },
                { "VerticalUpHeatexchg", ("立式上进料换热器", "Vertical Up Heat Exchanger") },
                { "CentrifugalPump", ("卧式离心泵", "Centrifugal Pump") },
                { "HorizontalSplitcasePump", ("卧式中开离心泵", "Horizontal Splitcase Pump") },
                { "HorizontalSplitcaseTurbinePump", ("卧式中开透平泵", "Horizontal Splitcase Turbine Pump") },
                { "TurbineCentrifugalPump", ("透平离心泵", "Turbine Centrifugal Pump") },
                { "HosePump", ("软管泵", "Hose Pump") },
                { "SumpPump", ("液下潜污泵", "Sump Pump") },
                { "VerticalInlinePump", ("立式管道泵", "Vertical Inline Pump") },
                { "VerticalInlinePumpDualArm", ("双臂立式管道泵", "Vertical Inline Pump (Dual Arm)") },
                { "HorizontalTank", ("卧式储罐", "Horizontal Tank") },
                { "VerticalTank", ("立式储罐", "Vertical Tank") },
                { "HorizontalVessel", ("卧式容器", "Horizontal Vessel") },
                { "VerticalVessel", ("立式容器", "Vertical Vessel") },
                { "Strainer", ("工艺过滤器", "Strainer") },
            };

        private static string ResolveFriendlyDisplayName(string rawDisplayName, string peqxPath, string scriptName)
        {
            var trimmed = (rawDisplayName ?? string.Empty).Trim();
            if (!string.IsNullOrEmpty(trimmed) && !trimmed.StartsWith("@", StringComparison.Ordinal))
            {
                return trimmed;
            }

            var stem = Path.GetFileNameWithoutExtension(peqxPath) ?? string.Empty;
            if (BuiltInFriendlyNames.TryGetValue(stem, out var pair))
            {
                return LocalizationManager.IsChinese ? pair.Zh : pair.En;
            }

            if (!string.IsNullOrEmpty(stem))
            {
                // 将 PascalCase 拆成易读词组，例如 HorizontalTank -> Horizontal Tank
                return Regex.Replace(stem, "([a-z])([A-Z])", "$1 $2");
            }

            return scriptName;
        }

        private static readonly Dictionary<string, (string Zh, string En)> CategoryNames =
            new Dictionary<string, (string Zh, string En)>(StringComparer.OrdinalIgnoreCase)
            {
                { "Pump", ("泵", "Pump") },
                { "Tank", ("储罐", "Tank") },
                { "Vessel", ("容器", "Vessel") },
                { "Column", ("柱形容器 / 塔器", "Column") },
                { "HeatExchanger", ("换热器", "Heat Exchanger") },
                { "Heater", ("加热器", "Heater") },
                { "Filter", ("过滤器", "Filter") },
                { "StrainerEquipment", ("过滤设备", "Strainer") },
                { "Cyclone", ("旋风分离器", "Cyclone") },
                { "Centrifuge", ("离心机", "Centrifuge") },
                { "Compressor", ("压缩机", "Compressor") },
                { "Blower", ("鼓风机", "Blower") },
                { "Conveyor", ("输送机", "Conveyor") },
                { "Dryer", ("干燥机", "Dryer") },
                { "Boiler", ("锅炉", "Boiler") },
                { "Furnace", ("工业炉", "Furnace") },
                { "Scrubber", ("洗涤器", "Scrubber") },
                { "Mixer", ("混合设备", "Mixer") },
                { "Motor", ("电动机", "Motor") },
                { "MechanicalDriver", ("机械驱动器", "Mechanical Driver") },
                { "GeneralEquipment", ("通用设备", "General Equipment") },
                { "GlobalEquipment", ("设备样板", "Template") },
                { "MiscEquipment", ("其他设备", "Misc Equipment") },
            };

        public static string ResolveEquipmentFolder()
        {
            var fromPlant = EquipmentBridge.TryGetEquipmentPackageFolder();
            if (!string.IsNullOrEmpty(fromPlant) && Directory.Exists(fromPlant))
            {
                return fromPlant;
            }

            var scriptsDir = ScriptRunner.ScriptsDir;
            if (!string.IsNullOrEmpty(scriptsDir))
            {
                var parent = Path.GetDirectoryName(scriptsDir.TrimEnd('\\', '/'));
                if (!string.IsNullOrEmpty(parent))
                {
                    var eqDir = Path.Combine(parent, "equipment");
                    if (Directory.Exists(eqDir))
                    {
                        return eqDir;
                    }
                }
            }

            return string.Empty;
        }

        public static string ResolveCustomScriptsFolder(string equipmentFolder)
        {
            if (!string.IsNullOrEmpty(equipmentFolder))
            {
                var parent = Path.GetDirectoryName(equipmentFolder.TrimEnd('\\', '/'));
                if (!string.IsNullOrEmpty(parent))
                {
                    var cs = Path.Combine(parent, "CustomScripts");
                    if (Directory.Exists(cs))
                    {
                        return cs;
                    }
                }
            }
            return ScriptRunner.ScriptsDir;
        }

        public static string GetCategoryDisplayName(string partType)
        {
            if (string.IsNullOrWhiteSpace(partType))
            {
                return LocalizationManager.IsChinese ? "其他设备" : "Other";
            }

            if (CategoryNames.TryGetValue(partType.Trim(), out var pair))
            {
                return LocalizationManager.IsChinese ? pair.Zh : pair.En;
            }

            return partType.Trim();
        }

        /// <summary>
        /// 扫描 equipment 目录下所有 .peqx 模板。
        /// </summary>
        public static List<EquipmentTemplateItem> LoadTemplates(out string equipmentFolder)
        {
            equipmentFolder = ResolveEquipmentFolder();
            var list = new List<EquipmentTemplateItem>();
            if (string.IsNullOrEmpty(equipmentFolder) || !Directory.Exists(equipmentFolder))
            {
                return list;
            }

            var customScriptsDir = ResolveCustomScriptsFolder(equipmentFolder);
            string[] files;
            try
            {
                files = Directory.GetFiles(equipmentFolder, "*.peqx", SearchOption.TopDirectoryOnly);
            }
            catch
            {
                return list;
            }

            foreach (var file in files)
            {
                var item = TryParsePeqx(file, customScriptsDir);
                if (item != null && !item.IsInternalTemplate)
                {
                    list.Add(item);
                }
            }

            // 自定义设备优先，其次按分类与显示名排序
            list.Sort((a, b) =>
            {
                var c = b.IsCustom.CompareTo(a.IsCustom);
                if (c != 0) return c;
                c = string.Compare(a.CategoryDisplayName, b.CategoryDisplayName, StringComparison.CurrentCultureIgnoreCase);
                if (c != 0) return c;
                return string.Compare(a.DisplayName, b.DisplayName, StringComparison.CurrentCultureIgnoreCase);
            });

            return list;
        }

        public static EquipmentTemplateItem FindTemplateByName(string equipmentName, IEnumerable<EquipmentTemplateItem> cache = null)
        {
            if (string.IsNullOrWhiteSpace(equipmentName)) return null;

            if (cache != null)
            {
                foreach (var item in cache)
                {
                    if (string.Equals(item.Name, equipmentName, StringComparison.OrdinalIgnoreCase))
                    {
                        return item;
                    }
                }
            }

            var folder = ResolveEquipmentFolder();
            if (string.IsNullOrEmpty(folder) || !Directory.Exists(folder)) return null;

            var customScriptsDir = ResolveCustomScriptsFolder(folder);
            var direct = Path.Combine(folder, equipmentName + ".peqx");
            if (File.Exists(direct))
            {
                return TryParsePeqx(direct, customScriptsDir);
            }

            foreach (var file in Directory.GetFiles(folder, "*.peqx", SearchOption.TopDirectoryOnly))
            {
                var item = TryParsePeqx(file, customScriptsDir);
                if (item != null && string.Equals(item.Name, equipmentName, StringComparison.OrdinalIgnoreCase))
                {
                    return item;
                }
            }

            return null;
        }

        private static EquipmentTemplateItem TryParsePeqx(string peqxPath, string customScriptsDir)
        {
            try
            {
                using (var archive = ZipFile.OpenRead(peqxPath))
                {
                    var xmlEntry = archive.GetEntry("content/EquipmentType.xml")
                        ?? archive.Entries.FirstOrDefault(e =>
                            e.FullName.EndsWith("EquipmentType.xml", StringComparison.OrdinalIgnoreCase));
                    if (xmlEntry == null) return null;

                    XDocument doc;
                    using (var stream = xmlEntry.Open())
                    {
                        doc = XDocument.Load(stream);
                    }

                    var root = doc.Root;
                    if (root == null) return null;

                    var name = (string)root.Attribute("Name") ?? Path.GetFileNameWithoutExtension(peqxPath);
                    var type = (string)root.Attribute("Type") ?? "C";
                    var subType = (string)root.Attribute("SubType") ?? string.Empty;
                    var partType = (string)root.Attribute("PartType") ?? "Vessel";
                    var partSubType = (string)root.Attribute("PartSubType") ?? string.Empty;
                    var guid = (string)root.Attribute("GUID") ?? string.Empty;
                    var lengthUnit = (string)root.Attribute("LengthUnit") ?? "mm";
                    var rawDisplayName = (root.Element("DisplayName")?.Value ?? string.Empty).Trim();
                    var displayName = ResolveFriendlyDisplayName(rawDisplayName, peqxPath, name);

                    // 排除 Plant 3D 内部 _TEMPLATE-H / _TEMPLATE-V 占位样板
                    var isInternal = name.StartsWith("_TEMPLATE", StringComparison.OrdinalIgnoreCase)
                        || string.Equals(partType, "GlobalEquipment", StringComparison.OrdinalIgnoreCase);

                    var scriptPath = FindCustomScriptPath(customScriptsDir, name);
                    var isCustom = !string.IsNullOrEmpty(scriptPath)
                        || name.StartsWith("EQUIPMENT_", StringComparison.OrdinalIgnoreCase);

                    // 读取脚本中的中文 Tooltip 补全
                    var pyTooltips = LoadScriptParamTooltips(scriptPath);

                    // 智能纠偏：对于早期误归到 Vessel 的专业设备，在插件分类视图里可按关键词辅助识别
                    var effectiveCategory = ResolveDisplayCategoryKey(partType, name, displayName);

                    var item = new EquipmentTemplateItem
                    {
                        FilePath = peqxPath,
                        FileName = Path.GetFileName(peqxPath),
                        Name = name,
                        DisplayName = displayName,
                        Type = type,
                        SubType = subType,
                        PartType = partType,
                        PartSubType = partSubType,
                        CategoryKey = effectiveCategory,
                        CategoryDisplayName = GetCategoryDisplayName(effectiveCategory),
                        Guid = guid,
                        LengthUnit = lengthUnit,
                        IsCustom = isCustom,
                        IsInternalTemplate = isInternal,
                        ScriptPath = scriptPath,
                        HighResPreviewPath = FindHighResPreviewPath(customScriptsDir, name),
                        EmbeddedPreviewBytes = ExtractPreviewBytes(archive, name)
                    };

                    // 解析主参数
                    var mainParamsEl = root.Element("Parameters");
                    if (mainParamsEl != null)
                    {
                        foreach (var p in mainParamsEl.Elements("ParameterInfo"))
                        {
                            var paramItem = ParseParameterElement(p, string.Empty, -1, lengthUnit, pyTooltips);
                            if (paramItem != null) item.DefaultParameters.Add(paramItem);
                        }
                    }

                    // 解析分组参数 (Categories)
                    var categoriesEl = root.Element("Categories");
                    if (categoriesEl != null)
                    {
                        var catIdx = 0;
                        foreach (var cat in categoriesEl.Elements("CategoryInfo"))
                        {
                            var catName = (cat.Element("DisplayName")?.Value ?? (string)cat.Attribute("Name") ?? ("Group " + (catIdx + 1))).Trim();
                            var cParams = cat.Element("Parameters");
                            if (cParams != null)
                            {
                                foreach (var p in cParams.Elements("ParameterInfo"))
                                {
                                    var paramItem = ParseParameterElement(p, catName, catIdx, lengthUnit, pyTooltips);
                                    if (paramItem != null) item.DefaultParameters.Add(paramItem);
                                }
                            }
                            catIdx++;
                        }
                    }

                    // 解析默认管嘴
                    var nozzlesEl = root.Element("Nozzles");
                    if (nozzlesEl != null)
                    {
                        var idx = 1;
                        foreach (var n in nozzlesEl.Elements("NozzleInfo"))
                        {
                            var nName = (string)n.Attribute("Name") ?? ("Nozzle " + idx);
                            var pName = (string)n.Attribute("PortName") ?? ("S" + idx);
                            int.TryParse((string)n.Attribute("PortIndex"), out var pIdx);
                            if (pIdx <= 0) pIdx = idx;

                            var nTypeEl = n.Element("NozzleTypes")?.Element("NozzleType");
                            var endType = (string)nTypeEl?.Attribute("EndType") ?? "FL";
                            var subT = (string)nTypeEl?.Attribute("PartSubType") ?? "StraightNozzle";

                            item.DefaultNozzles.Add(new EquipmentNozzleItem
                            {
                                PortIndex = pIdx,
                                PortName = pName,
                                Name = nName,
                                NozzleTag = nName,
                                EndType = endType,
                                LongDescription = subT
                            });
                            idx++;
                        }
                    }

                    return item;
                }
            }
            catch
            {
                return null;
            }
        }

        private static string ResolveDisplayCategoryKey(string partType, string name, string displayName)
        {
            if (!string.Equals(partType, "Vessel", StringComparison.OrdinalIgnoreCase))
            {
                return partType;
            }

            var probe = ((name ?? string.Empty) + " " + (displayName ?? string.Empty)).ToLowerInvariant();
            if (probe.Contains("filter") || probe.Contains("过滤")) return "Filter";
            if (probe.Contains("cyclone") || probe.Contains("旋风")) return "Cyclone";
            if (probe.Contains("centrifuge") || probe.Contains("离心机")) return "Centrifuge";
            if (probe.Contains("compressor") || probe.Contains("压缩机")) return "Compressor";
            if (probe.Contains("scrubber") || probe.Contains("洗涤")) return "Scrubber";
            if (probe.Contains("column") || probe.Contains("精馏塔")) return "Column";
            if (probe.Contains("mixer") || probe.Contains("混合")) return "Mixer";
            if (probe.Contains("evaporator") || probe.Contains("蒸发器")) return "HeatExchanger";
            return partType;
        }

        private static EquipmentParamItem ParseParameterElement(
            XElement el,
            string groupName,
            int categoryIndex,
            string lengthUnit,
            Dictionary<string, string> pyTooltips)
        {
            var pname = (string)el.Attribute("Name");
            if (string.IsNullOrWhiteSpace(pname)) return null;

            var ptype = (string)el.Attribute("Type") ?? "d";
            var defVal = (string)el.Attribute("DefaultValue") ?? "0";
            var tip = (el.Element("Tooltip")?.Value ?? string.Empty).Trim();
            if (string.IsNullOrEmpty(tip) && pyTooltips != null && pyTooltips.TryGetValue(pname, out var pyTip))
            {
                tip = pyTip;
            }

            var unit = string.Empty;
            if (string.Equals(ptype, "d", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(ptype, "d0", StringComparison.OrdinalIgnoreCase))
            {
                unit = string.IsNullOrEmpty(lengthUnit) ? "mm" : lengthUnit;
            }
            else if (string.Equals(ptype, "a", StringComparison.OrdinalIgnoreCase))
            {
                unit = "°";
            }

            return new EquipmentParamItem
            {
                GroupName = groupName,
                CategoryIndex = categoryIndex,
                Name = pname,
                DisplayName = pname,
                Tooltip = tip,
                DefaultValue = defVal,
                Value = defVal,
                ParamType = ptype,
                Unit = unit
            };
        }

        private static string FindCustomScriptPath(string customScriptsDir, string name)
        {
            if (string.IsNullOrEmpty(customScriptsDir) || string.IsNullOrEmpty(name)) return null;
            var candidate = Path.Combine(customScriptsDir, name + ".py");
            return File.Exists(candidate) ? candidate : null;
        }

        private static string FindHighResPreviewPath(string customScriptsDir, string name)
        {
            if (string.IsNullOrEmpty(customScriptsDir) || string.IsNullOrEmpty(name)) return null;
            var candidates = new[]
            {
                Path.Combine(customScriptsDir, name + "_640.png"),
                Path.Combine(customScriptsDir, name + "_dim.png"),
                Path.Combine(customScriptsDir, name + ".png"),
                Path.Combine(customScriptsDir, name + "_200.png"),
            };

            foreach (var c in candidates)
            {
                if (File.Exists(c)) return c;
            }
            return null;
        }

        private static byte[] ExtractPreviewBytes(ZipArchive archive, string name)
        {
            var entry = archive.Entries.FirstOrDefault(e =>
                e.FullName.StartsWith("preview/", StringComparison.OrdinalIgnoreCase) &&
                e.FullName.IndexOf(name, StringComparison.OrdinalIgnoreCase) >= 0 &&
                e.FullName.EndsWith(".png", StringComparison.OrdinalIgnoreCase));

            if (entry == null)
            {
                entry = archive.Entries.FirstOrDefault(e =>
                    e.FullName.StartsWith("preview/", StringComparison.OrdinalIgnoreCase) &&
                    e.FullName.EndsWith(".png", StringComparison.OrdinalIgnoreCase));
            }

            if (entry == null) return null;

            using (var s = entry.Open())
            using (var ms = new MemoryStream())
            {
                s.CopyTo(ms);
                return ms.ToArray();
            }
        }

        public static Dictionary<string, string> LoadScriptParamTooltips(string scriptPath)
        {
            var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            if (string.IsNullOrEmpty(scriptPath) || !File.Exists(scriptPath))
            {
                return map;
            }

            try
            {
                var text = File.ReadAllText(scriptPath, Encoding.UTF8);
                foreach (Match m in PyParamTooltipRegex.Matches(text))
                {
                    var key = m.Groups[1].Value.Trim();
                    var val = !string.IsNullOrEmpty(m.Groups[2].Value) ? m.Groups[2].Value : m.Groups[3].Value;
                    if (!string.IsNullOrEmpty(key) && !string.IsNullOrWhiteSpace(val) && !map.ContainsKey(key))
                    {
                        map[key] = val.Trim();
                    }
                }
            }
            catch
            {
            }

            return map;
        }
    }
}
