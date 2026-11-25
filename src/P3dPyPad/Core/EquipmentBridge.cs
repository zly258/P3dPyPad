using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Geometry;

namespace P3dPyPad
{
    /// <summary>
    /// AutoCAD Plant 3D 2019–2026 跨版本设备原生 API 反射桥接层。
    /// 不在编译期强绑定特定年份的 PnP3dPipeUI.dll / PnP3dObjectsMgd.dll，
    /// 运行时动态加载当前宿主 Plant 3D 的原生设备服务，确保 .NET 4.7.2 与 .NET 8 全版本通用。
    /// </summary>
    internal static class EquipmentBridge
    {
        private static readonly HashSet<string> CommonPropertyNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "Tag",
            "LongDescription",
            "LongDescriptionSize",
            "LongDescriptionFamily",
            "ShortDescription",
            "Material",
            "MaterialCode",
            "Manufacturer",
            "DesignStandard",
            "DesignPressure",
            "DesignTemp",
            "OperatingPressure",
            "OperatingTemp",
            "Weight",
            "WeightUnit",
            "Comment",
            "Description",
            "PartCategory"
        };

        private static Assembly _pipeUiAsm;
        private static Assembly _objectsAsm;
        private static Type _equipmentHelperType;
        private static Type _equipmentType;
        private static Type _equipmentEntityType;
        private static bool _probed;

        public static bool IsAvailable
        {
            get
            {
                EnsureLoaded();
                return _equipmentHelperType != null && _equipmentType != null;
            }
        }

        private static void EnsureLoaded()
        {
            if (_probed) return;
            _probed = true;

            try
            {
                _pipeUiAsm = FindOrLoadPlantAssembly("PnP3dPipeUI");
                _objectsAsm = FindOrLoadPlantAssembly("PnP3dObjectsMgd");

                if (_pipeUiAsm != null)
                {
                    _equipmentHelperType = _pipeUiAsm.GetType("Autodesk.ProcessPower.PnP3dEquipment.EquipmentHelper", false);
                    _equipmentType = _pipeUiAsm.GetType("Autodesk.ProcessPower.PnP3dEquipment.EquipmentType", false);
                }

                if (_objectsAsm != null)
                {
                    _equipmentEntityType = _objectsAsm.GetType("Autodesk.ProcessPower.PnP3dObjects.Equipment", false);
                }
            }
            catch
            {
            }
        }

        private static Assembly FindOrLoadPlantAssembly(string simpleName)
        {
            foreach (var loaded in AppDomain.CurrentDomain.GetAssemblies())
            {
                try
                {
                    if (string.Equals(loaded.GetName().Name, simpleName, StringComparison.OrdinalIgnoreCase))
                    {
                        return loaded;
                    }
                }
                catch
                {
                }
            }

            var plntDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory ?? string.Empty, "PLNT3D");
            var path = Path.Combine(plntDir, simpleName + ".dll");
            if (File.Exists(path))
            {
                try
                {
                    return Assembly.LoadFrom(path);
                }
                catch
                {
                }
            }

            return null;
        }

        private static IDisposable CreateHelperInstance(out object helper)
        {
            helper = null;
            EnsureLoaded();
            if (_equipmentHelperType == null) return null;

            try
            {
                helper = Activator.CreateInstance(_equipmentHelperType);
                return helper as IDisposable;
            }
            catch
            {
                return null;
            }
        }

        public static string TryGetEquipmentPackageFolder()
        {
            try
            {
                using (CreateHelperInstance(out var helper))
                {
                    if (helper == null) return null;
                    var prop = _equipmentHelperType.GetProperty("EquipmentPackageFolder");
                    var val = prop?.GetValue(helper, null) as string;
                    if (!string.IsNullOrEmpty(val) && Directory.Exists(val))
                    {
                        return val;
                    }
                }
            }
            catch
            {
            }
            return null;
        }

        /// <summary>
        /// 基于选定的 .peqx 模板构建“创建设备”会话，并尽可能结合当前 Plant 3D 项目上下文初始化位号与工程特性。
        /// </summary>
        public static EquipmentEditSession CreateSessionFromTemplate(EquipmentTemplateItem template)
        {
            if (template == null) return null;

            var session = new EquipmentEditSession
            {
                Mode = EquipmentDialogMode.Create,
                Template = template,
                EquipmentName = template.Name,
                DisplayName = template.DisplayName,
                CategoryDisplayName = template.CategoryDisplayName,
                LengthUnit = string.IsNullOrEmpty(template.LengthUnit) ? "mm" : template.LengthUnit
            };

            object nativeEq = null;
            try
            {
                using (CreateHelperInstance(out var helper))
                {
                    if (helper != null && _equipmentType != null)
                    {
                        var getFromPkg = _equipmentType.GetMethod("GetFromPackage", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(string) }, null);
                        if (getFromPkg != null)
                        {
                            nativeEq = getFromPkg.Invoke(null, new object[] { template.FilePath });
                        }

                        if (nativeEq != null)
                        {
                            var makeForProj = _equipmentHelperType.GetMethod("MakeEquipmentForProject", new[] { _equipmentType });
                            if (makeForProj != null)
                            {
                                var projEq = makeForProj.Invoke(helper, new[] { nativeEq });
                                if (projEq != null) nativeEq = projEq;
                            }

                            var initTag = _equipmentHelperType.GetMethod("InitTagRelatedProperties", new[] { _equipmentType });
                            initTag?.Invoke(helper, new[] { nativeEq });
                        }
                    }
                }
            }
            catch
            {
                nativeEq = null;
            }

            if (nativeEq != null)
            {
                session.NativeEquipmentType = nativeEq;
                PopulateSessionFromNativeEquipment(session, nativeEq, template);
            }
            else
            {
                // 离线/兜底模式：直接使用 .peqx XML 解析出的默认参数与管嘴
                session.Parameters = template.DefaultParameters.Select(p => p.Clone()).ToList();
                session.Nozzles = template.DefaultNozzles.Select(n => n.Clone()).ToList();
                session.Properties = BuildFallbackProperties(template);
            }

            return session;
        }

        /// <summary>
        /// 从图面选取（或使用预选的）Plant 3D Equipment 实体并读取其完整参数、位号、工程特性与管嘴。
        /// </summary>
        public static bool TrySelectAndLoadEquipmentForEdit(
            Document doc,
            IEnumerable<EquipmentTemplateItem> templateCache,
            out EquipmentEditSession session,
            out string errorMessage)
        {
            session = null;
            errorMessage = null;

            if (doc == null)
            {
                errorMessage = LocalizationManager.T("EqErrNoDoc", "没有打开的图形文档。", "No active drawing document.");
                return false;
            }

            EnsureLoaded();
            if (!IsAvailable)
            {
                errorMessage = LocalizationManager.T("EqErrNoPlantApi", "当前环境未加载 Plant 3D 设备模块 (PnP3dPipeUI.dll)。", "Plant 3D equipment API is not available.");
                return false;
            }

            var targetId = FindPreselectedEquipmentId(doc);
            if (targetId.IsNull)
            {
                var peo = new PromptEntityOptions("\n" + LocalizationManager.T("EqPromptSelect", "请选择要编辑的 Plant 3D 设备: ", "Select a Plant 3D equipment to edit: "));
                peo.SetRejectMessage("\n" + LocalizationManager.T("EqPromptReject", "所选图元不是 Plant 3D 设备，请重新选择。", "Selected entity is not a Plant 3D equipment."));
                var per = doc.Editor.GetEntity(peo);
                if (per.Status != PromptStatus.OK)
                {
                    return false;
                }
                targetId = per.ObjectId;
            }

            if (!IsEquipmentEntity(doc.Database, targetId))
            {
                errorMessage = LocalizationManager.T("EqErrNotEquipment", "所选对象不是 Plant 3D 设备实体。", "Selected object is not a Plant 3D equipment entity.");
                return false;
            }

            return TryLoadEquipmentById(doc, targetId, templateCache, out session, out errorMessage);
        }

        public static bool TryLoadEquipmentById(
            Document doc,
            ObjectId targetId,
            IEnumerable<EquipmentTemplateItem> templateCache,
            out EquipmentEditSession session,
            out string errorMessage)
        {
            session = null;
            errorMessage = null;

            try
            {
                object nativeEq = null;
                using (CreateHelperInstance(out var helper))
                {
                    if (helper == null)
                    {
                        errorMessage = LocalizationManager.T("EqErrHelperFail", "无法初始化 Plant 3D EquipmentHelper。", "Failed to initialize EquipmentHelper.");
                        return false;
                    }

                    var retrieve = _equipmentHelperType.GetMethod("RetrieveEquipmentFromInstance", new[] { typeof(ObjectId) });
                    if (retrieve == null)
                    {
                        errorMessage = "RetrieveEquipmentFromInstance API not found.";
                        return false;
                    }

                    using (doc.LockDocument())
                    {
                        nativeEq = retrieve.Invoke(helper, new object[] { targetId });
                    }
                }

                if (nativeEq == null)
                {
                    errorMessage = LocalizationManager.T("EqErrRetrieveNull", "无法读取该设备的参数化定义（可能是纯块转换或损坏的设备实体）。", "Failed to retrieve equipment definition from selected instance.");
                    return false;
                }

                var eqName = GetStringProp(nativeEq, "Name");
                var eqDisp = GetStringProp(nativeEq, "DisplayName");
                var partType = GetStringProp(nativeEq, "PartType");
                var lengthUnit = GetStringProp(nativeEq, "LengthUnit");
                var template = EquipmentCatalogService.FindTemplateByName(eqName, templateCache);

                session = new EquipmentEditSession
                {
                    Mode = EquipmentDialogMode.Edit,
                    TargetObjectId = targetId,
                    NativeEquipmentType = nativeEq,
                    Template = template,
                    EquipmentName = eqName,
                    DisplayName = !string.IsNullOrWhiteSpace(eqDisp) ? eqDisp : (template?.DisplayName ?? eqName),
                    CategoryDisplayName = template?.CategoryDisplayName ?? EquipmentCatalogService.GetCategoryDisplayName(partType),
                    LengthUnit = string.IsNullOrEmpty(lengthUnit) ? "mm" : lengthUnit
                };

                PopulateSessionFromNativeEquipment(session, nativeEq, template);
                return true;
            }
            catch (TargetInvocationException tex)
            {
                errorMessage = tex.InnerException?.Message ?? tex.Message;
                return false;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 在图面上交互式定位并创建原生 Plant 3D 设备实体。
        /// </summary>
        public static bool PlaceNewEquipment(Document doc, EquipmentEditSession session, out ObjectId createdId, out string errorMessage)
        {
            createdId = ObjectId.Null;
            errorMessage = null;

            if (doc == null || session == null)
            {
                errorMessage = LocalizationManager.T("EqErrNoDoc", "没有打开的图形文档。", "No active drawing document.");
                return false;
            }

            if (session.NativeEquipmentType == null)
            {
                errorMessage = LocalizationManager.T("EqErrNoNative", "当前设备模板未成功加载原生 EquipmentType，无法在 Plant 3D 中创建。", "Native EquipmentType is not loaded.");
                return false;
            }

            // 1. 图面指定插入基点
            var ppo = new PromptPointOptions("\n" + LocalizationManager.T("EqPromptBasePoint", "指定设备放置点: ", "Specify equipment insertion point: "));
            var ppr = doc.Editor.GetPoint(ppo);
            if (ppr.Status != PromptStatus.OK)
            {
                return false;
            }

            var insertPt = new Point3d(ppr.Value.X, ppr.Value.Y, ppr.Value.Z + session.Elevation);

            // 2. 可选旋转角（直接回车使用界面设定角度）
            var defaultRad = session.RotationDegrees * Math.PI / 180.0;
            var pao = new PromptAngleOptions(
                "\n" + string.Format(LocalizationManager.T("EqPromptAngle", "指定旋转角度 <{0:0.##}°>: ", "Specify rotation angle <{0:0.##}°>: "), session.RotationDegrees))
            {
                BasePoint = insertPt,
                UseBasePoint = true,
                AllowNone = true,
                DefaultValue = defaultRad
            };
            var par = doc.Editor.GetAngle(pao);
            if (par.Status == PromptStatus.Cancel)
            {
                return false;
            }
            var finalRad = par.Status == PromptStatus.OK ? par.Value : defaultRad;

            try
            {
                // 回写 UI 修改到原生 EquipmentType
                WriteSessionBackToNativeEquipment(session);

                using (doc.LockDocument())
                using (CreateHelperInstance(out var helper))
                {
                    if (helper == null)
                    {
                        errorMessage = "EquipmentHelper unavailable.";
                        return false;
                    }

                    // 查找 6 参重载: CreateEquipmentEntity(EquipmentType eq, String dwgName, Double dwgScale, Database db, ref PartSizeProperties equipPart, ref PartSizePropertiesCollection nozzleParts)
                    var createMethod = _equipmentHelperType.GetMethods(BindingFlags.Public | BindingFlags.Instance)
                        .FirstOrDefault(m => m.Name == "CreateEquipmentEntity" && m.GetParameters().Length == 6);
                    if (createMethod == null)
                    {
                        errorMessage = "CreateEquipmentEntity API not found.";
                        return false;
                    }

                    var dwgName = doc.Name ?? string.Empty;
                    var dwgScale = 1.0;
                    var invokeArgs = new object[]
                    {
                        session.NativeEquipmentType,
                        dwgName,
                        dwgScale,
                        doc.Database,
                        null,
                        null
                    };

                    var eqEntity = createMethod.Invoke(helper, invokeArgs) as Entity;
                    if (eqEntity == null)
                    {
                        errorMessage = LocalizationManager.T("EqErrCreateNull", "Plant 3D 未能生成设备实体，请检查脚本是否已注册 (PLANTREGISTERCUSTOMSCRIPTS) 且参数合法。", "Failed to create equipment entity. Ensure the custom script is registered.");
                        return false;
                    }

                    var equipPart = invokeArgs[4];
                    var nozzleParts = invokeArgs[5];

                    // 应用平移与旋转
                    var matrix = Matrix3d.Displacement(insertPt - Point3d.Origin)
                        * Matrix3d.Rotation(finalRad, Vector3d.ZAxis, Point3d.Origin);
                    eqEntity.TransformBy(matrix);

                    using (var tr = doc.Database.TransactionManager.StartTransaction())
                    {
                        var bt = (BlockTable)tr.GetObject(doc.Database.BlockTableId, OpenMode.ForRead);
                        var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                        createdId = ms.AppendEntity(eqEntity);
                        tr.AddNewlyCreatedDBObject(eqEntity, true);
                        tr.Commit();
                    }

                    // 关联 Plant 3D DataLinksManager（确保位号/特性/管嘴进入 DataManager 并支持原生修改）
                    TryLinkNewEquipmentToDataManager(helper, doc.Database, createdId, session.NativeEquipmentType, equipPart, nozzleParts);

                    doc.Editor.Regen();
                    return true;
                }
            }
            catch (TargetInvocationException tex)
            {
                errorMessage = tex.InnerException?.Message ?? tex.Message;
                return false;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        /// <summary>
        /// 原地更新图面中已有设备的尺寸参数、位号与工程特性（保留 ObjectId 与管嘴连接）。
        /// </summary>
        public static bool ApplyEditToEquipment(Document doc, EquipmentEditSession session, out string errorMessage)
        {
            errorMessage = null;
            if (doc == null || session == null || session.TargetObjectId.IsNull || session.NativeEquipmentType == null)
            {
                errorMessage = LocalizationManager.T("EqErrInvalidSession", "当前编辑会话无效。", "Invalid equipment edit session.");
                return false;
            }

            try
            {
                WriteSessionBackToNativeEquipment(session);

                using (doc.LockDocument())
                using (CreateHelperInstance(out var helper))
                {
                    if (helper == null)
                    {
                        errorMessage = "EquipmentHelper unavailable.";
                        return false;
                    }

                    var updateMethod = _equipmentHelperType.GetMethod(
                        "UpdateEquipmentEntity",
                        new[] { typeof(ObjectId), _equipmentType, typeof(string), typeof(double) });
                    if (updateMethod == null)
                    {
                        errorMessage = "UpdateEquipmentEntity API not found.";
                        return false;
                    }

                    var ok = (bool)updateMethod.Invoke(helper, new object[]
                    {
                        session.TargetObjectId,
                        session.NativeEquipmentType,
                        doc.Name ?? string.Empty,
                        1.0
                    });

                    if (!ok)
                    {
                        errorMessage = LocalizationManager.T("EqErrUpdateFail", "设备更新未生效，请检查参数值是否合法。", "Equipment update returned false.");
                        return false;
                    }

                    doc.Editor.Regen();
                    return true;
                }
            }
            catch (TargetInvocationException tex)
            {
                errorMessage = tex.InnerException?.Message ?? tex.Message;
                return false;
            }
            catch (Exception ex)
            {
                errorMessage = ex.Message;
                return false;
            }
        }

        private static void TryLinkNewEquipmentToDataManager(
            object helper,
            Database db,
            ObjectId equipId,
            object nativeEq,
            object equipPart,
            object nozzleParts)
        {
            try
            {
                // 优先调用 saveBlob / UpdateEquipmentEntity 让 Plant 3D 完成内部数据链接与标高/属性落盘
                var updateMethod = _equipmentHelperType.GetMethod(
                    "UpdateEquipmentEntity",
                    new[] { typeof(ObjectId), _equipmentType, typeof(string), typeof(double) });
                if (updateMethod != null && !equipId.IsNull)
                {
                    var dlm = _equipmentHelperType.GetProperty("DLManager")?.GetValue(helper, null);
                    if (dlm != null && equipPart != null)
                    {
                        // 尝试 AddToDatabase(ObjectId, PartSizeProperties) 或 AcceptChanges
                        var addToDb = dlm.GetType().GetMethods(BindingFlags.Public | BindingFlags.Instance)
                            .FirstOrDefault(m => m.Name == "AcceptChanges" && m.GetParameters().Length == 0);
                        addToDb?.Invoke(dlm, null);
                    }
                    updateMethod.Invoke(helper, new object[] { equipId, nativeEq, db?.Filename ?? string.Empty, 1.0 });
                }
            }
            catch
            {
            }
        }

        private static ObjectId FindPreselectedEquipmentId(Document doc)
        {
            try
            {
                var implied = doc.Editor.SelectImplied();
                if (implied.Status == PromptStatus.OK && implied.Value != null && implied.Value.Count > 0)
                {
                    foreach (SelectedObject so in implied.Value)
                    {
                        if (so != null && IsEquipmentEntity(doc.Database, so.ObjectId))
                        {
                            return so.ObjectId;
                        }
                    }
                }
            }
            catch
            {
            }
            return ObjectId.Null;
        }

        private static bool IsEquipmentEntity(Database db, ObjectId id)
        {
            if (db == null || id.IsNull || !id.IsValid || id.IsErased) return false;
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var obj = tr.GetObject(id, OpenMode.ForRead);
                    if (obj == null) return false;
                    if (_equipmentEntityType != null && _equipmentEntityType.IsInstanceOfType(obj))
                    {
                        return true;
                    }
                    var typeName = obj.GetType().FullName ?? string.Empty;
                    return typeName.IndexOf("Equipment", StringComparison.OrdinalIgnoreCase) >= 0;
                }
            }
            catch
            {
                return false;
            }
        }

        private static void PopulateSessionFromNativeEquipment(EquipmentEditSession session, object nativeEq, EquipmentTemplateItem template)
        {
            session.EquipmentTag = GetStringProp(nativeEq, "EquipmentTag");
            session.Elevation = GetDoubleProp(nativeEq, "Elevation");

            var pyTooltips = template != null
                ? EquipmentCatalogService.LoadScriptParamTooltips(template.ScriptPath)
                : new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            var unit = string.IsNullOrEmpty(session.LengthUnit) ? "mm" : session.LengthUnit;

            // 1. 主参数
            var paramsList = new List<EquipmentParamItem>();
            var nativeParams = GetProp(nativeEq, "Parameters") as IEnumerable;
            if (nativeParams != null)
            {
                foreach (var p in nativeParams)
                {
                    var item = ConvertNativeParam(p, string.Empty, -1, unit, pyTooltips);
                    if (item != null) paramsList.Add(item);
                }
            }

            // 2. 分组参数 (Categories)
            var nativeCats = GetProp(nativeEq, "Categories") as IEnumerable;
            if (nativeCats != null)
            {
                var catIdx = 0;
                foreach (var cat in nativeCats)
                {
                    var catDisp = GetStringProp(cat, "DisplayName");
                    var catName = !string.IsNullOrWhiteSpace(catDisp) ? catDisp : GetStringProp(cat, "Name");
                    var cParams = GetProp(cat, "Parameters") as IEnumerable;
                    if (cParams != null)
                    {
                        foreach (var p in cParams)
                        {
                            var item = ConvertNativeParam(p, catName, catIdx, unit, pyTooltips);
                            if (item != null) paramsList.Add(item);
                        }
                    }
                    catIdx++;
                }
            }

            session.Parameters = paramsList;

            // 3. 工程特性 (PartProperties)
            var propList = new List<EquipmentPropertyItem>();
            var nativeProps = GetProp(nativeEq, "PartProperties") as IEnumerable;
            if (nativeProps != null)
            {
                foreach (var pr in nativeProps)
                {
                    var pname = GetStringProp(pr, "Name");
                    if (string.IsNullOrWhiteSpace(pname)) continue;
                    if (pname.StartsWith(".", StringComparison.Ordinal)) continue;

                    var disp = GetStringProp(pr, "DisplayName");
                    var val = GetStringProp(pr, "Value");
                    var defVal = GetStringProp(pr, "DefaultValue");

                    propList.Add(new EquipmentPropertyItem
                    {
                        Name = pname,
                        DisplayName = string.IsNullOrWhiteSpace(disp) ? pname : disp,
                        Value = val,
                        DefaultValue = defVal,
                        IsCommon = CommonPropertyNames.Contains(pname),
                        IsReadOnly = string.Equals(pname, "PartType", StringComparison.OrdinalIgnoreCase)
                            || string.Equals(pname, "PartSubType", StringComparison.OrdinalIgnoreCase)
                    });
                }
            }

            // 常用工程特性置顶排序
            propList.Sort((a, b) =>
            {
                var c = b.IsCommon.CompareTo(a.IsCommon);
                if (c != 0) return c;
                return string.Compare(a.LabelText, b.LabelText, StringComparison.CurrentCultureIgnoreCase);
            });
            session.Properties = propList;

            // 4. 管嘴 (Nozzles)
            var nozzleList = new List<EquipmentNozzleItem>();
            var nativeNozzles = GetProp(nativeEq, "Nozzles") as IEnumerable;
            if (nativeNozzles != null)
            {
                var idx = 1;
                foreach (var nz in nativeNozzles)
                {
                    var nTag = GetStringProp(nz, "NozzleTag");
                    var nName = GetStringProp(nz, "Name");
                    var pName = GetStringProp(nz, "PortName");
                    var pIdx = GetIntProp(nz, "PortIndex");
                    var ndObj = GetProp(nz, "NozzleSize");
                    var ndStr = ndObj != null ? ndObj.ToString() : string.Empty;

                    nozzleList.Add(new EquipmentNozzleItem
                    {
                        PortIndex = pIdx > 0 ? pIdx : idx,
                        PortName = string.IsNullOrEmpty(pName) ? ("S" + idx) : pName,
                        Name = string.IsNullOrEmpty(nName) ? ("Nozzle " + idx) : nName,
                        NozzleTag = !string.IsNullOrWhiteSpace(nTag) ? nTag : (string.IsNullOrEmpty(nName) ? ("Nozzle " + idx) : nName),
                        NominalSize = ndStr,
                        PressureClass = GetStringProp(nz, "PressureClass"),
                        Facing = GetStringProp(nz, "Facing"),
                        EndType = !string.IsNullOrEmpty(GetStringProp(nz, "NozzleEndType"))
                            ? GetStringProp(nz, "NozzleEndType")
                            : GetStringProp(nz, "EndType"),
                        LongDescription = GetStringProp(nz, "LongDescription")
                    });
                    idx++;
                }
            }
            session.Nozzles = nozzleList;
        }

        private static void WriteSessionBackToNativeEquipment(EquipmentEditSession session)
        {
            var nativeEq = session.NativeEquipmentType;
            if (nativeEq == null) return;

            SetProp(nativeEq, "EquipmentTag", session.EquipmentTag ?? string.Empty);
            SetProp(nativeEq, "Elevation", session.Elevation);

            // 回写主参数
            var mainMap = session.Parameters
                .Where(p => p.CategoryIndex < 0)
                .ToDictionary(p => p.Name, p => p.Value ?? string.Empty, StringComparer.OrdinalIgnoreCase);
            var nativeParams = GetProp(nativeEq, "Parameters") as IEnumerable;
            if (nativeParams != null)
            {
                foreach (var p in nativeParams)
                {
                    var pname = GetStringProp(p, "Name");
                    if (!string.IsNullOrEmpty(pname) && mainMap.TryGetValue(pname, out var newVal))
                    {
                        SetProp(p, "Value", newVal);
                    }
                }
            }

            // 回写分组参数
            var nativeCats = GetProp(nativeEq, "Categories") as IEnumerable;
            if (nativeCats != null)
            {
                var catIdx = 0;
                foreach (var cat in nativeCats)
                {
                    var catMap = session.Parameters
                        .Where(p => p.CategoryIndex == catIdx)
                        .ToDictionary(p => p.Name, p => p.Value ?? string.Empty, StringComparer.OrdinalIgnoreCase);
                    var cParams = GetProp(cat, "Parameters") as IEnumerable;
                    if (cParams != null)
                    {
                        foreach (var p in cParams)
                        {
                            var pname = GetStringProp(p, "Name");
                            if (!string.IsNullOrEmpty(pname) && catMap.TryGetValue(pname, out var newVal))
                            {
                                SetProp(p, "Value", newVal);
                            }
                        }
                    }
                    catIdx++;
                }
            }

            // 回写工程特性
            var propMap = session.Properties
                .Where(p => !p.IsReadOnly)
                .ToDictionary(p => p.Name, p => p.Value ?? string.Empty, StringComparer.OrdinalIgnoreCase);
            var nativeProps = GetProp(nativeEq, "PartProperties") as IEnumerable;
            if (nativeProps != null)
            {
                foreach (var pr in nativeProps)
                {
                    var pname = GetStringProp(pr, "Name");
                    if (!string.IsNullOrEmpty(pname) && propMap.TryGetValue(pname, out var newVal))
                    {
                        SetProp(pr, "Value", newVal);
                    }
                }
            }

            // 回写管嘴位号
            var nativeNozzles = GetProp(nativeEq, "Nozzles") as IEnumerable;
            if (nativeNozzles != null)
            {
                var idx = 0;
                foreach (var nz in nativeNozzles)
                {
                    if (idx < session.Nozzles.Count)
                    {
                        SetProp(nz, "NozzleTag", session.Nozzles[idx].NozzleTag ?? string.Empty);
                    }
                    idx++;
                }
            }
        }

        private static EquipmentParamItem ConvertNativeParam(
            object p,
            string groupName,
            int categoryIndex,
            string lengthUnit,
            Dictionary<string, string> pyTooltips)
        {
            var pname = GetStringProp(p, "Name");
            if (string.IsNullOrWhiteSpace(pname)) return null;

            var disp = GetStringProp(p, "DisplayName");
            var tip = GetStringProp(p, "Tooltip");
            if (string.IsNullOrWhiteSpace(tip) && pyTooltips.TryGetValue(pname, out var pyTip))
            {
                tip = pyTip;
            }

            var ptype = GetStringProp(p, "Type");
            var defVal = GetStringProp(p, "DefaultValue");
            var val = GetStringProp(p, "Value");
            if (string.IsNullOrEmpty(val)) val = defVal;

            var unit = string.Empty;
            if (string.Equals(ptype, "d", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(ptype, "d0", StringComparison.OrdinalIgnoreCase))
            {
                unit = lengthUnit;
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
                DisplayName = string.IsNullOrWhiteSpace(disp) ? pname : disp,
                Tooltip = tip,
                DefaultValue = defVal,
                Value = val,
                ParamType = ptype,
                Unit = unit
            };
        }

        private static List<EquipmentPropertyItem> BuildFallbackProperties(EquipmentTemplateItem template)
        {
            return new List<EquipmentPropertyItem>
            {
                new EquipmentPropertyItem { Name = "LongDescriptionSize", DisplayName = LocalizationManager.T("EqPropDesc", "详细描述(尺寸)", "Long Description (Size)"), Value = template.DisplayName, IsCommon = true },
                new EquipmentPropertyItem { Name = "ShortDescription", DisplayName = LocalizationManager.T("EqPropShortDesc", "简短描述", "Short Description"), Value = template.CategoryDisplayName, IsCommon = true },
                new EquipmentPropertyItem { Name = "Material", DisplayName = LocalizationManager.T("EqPropMaterial", "材质", "Material"), Value = string.Empty, IsCommon = true },
                new EquipmentPropertyItem { Name = "Manufacturer", DisplayName = LocalizationManager.T("EqPropManufacturer", "制造商", "Manufacturer"), Value = string.Empty, IsCommon = true },
                new EquipmentPropertyItem { Name = "DesignStandard", DisplayName = LocalizationManager.T("EqPropStd", "设计标准", "Design Standard"), Value = string.Empty, IsCommon = true },
                new EquipmentPropertyItem { Name = "Weight", DisplayName = LocalizationManager.T("EqPropWeight", "重量", "Weight"), Value = string.Empty, IsCommon = true },
            };
        }

        private static object GetProp(object obj, string propName)
        {
            if (obj == null) return null;
            return obj.GetType().GetProperty(propName, BindingFlags.Public | BindingFlags.Instance)?.GetValue(obj, null);
        }

        private static string GetStringProp(object obj, string propName)
        {
            var val = GetProp(obj, propName);
            return val != null ? Convert.ToString(val, CultureInfo.InvariantCulture) : string.Empty;
        }

        private static double GetDoubleProp(object obj, string propName)
        {
            var val = GetProp(obj, propName);
            if (val is double d) return d;
            if (val != null && double.TryParse(val.ToString(), NumberStyles.Float, CultureInfo.InvariantCulture, out var parsed))
            {
                return parsed;
            }
            return 0.0;
        }

        private static int GetIntProp(object obj, string propName)
        {
            var val = GetProp(obj, propName);
            if (val is int i) return i;
            if (val != null && int.TryParse(val.ToString(), NumberStyles.Integer, CultureInfo.InvariantCulture, out var parsed))
            {
                return parsed;
            }
            return 0;
        }

        private static void SetProp(object obj, string propName, object value)
        {
            if (obj == null) return;
            var prop = obj.GetType().GetProperty(propName, BindingFlags.Public | BindingFlags.Instance);
            if (prop != null && prop.CanWrite)
            {
                prop.SetValue(obj, value, null);
            }
        }
    }
}
