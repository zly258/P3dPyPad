using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using Autodesk.AutoCAD.ApplicationServices;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Geometry;
using AcadApp = Autodesk.AutoCAD.ApplicationServices.Application;

namespace P3dPyPad
{
    public enum CadViewDirection
    {
        IsoSE,  // 东南等轴测
        Front,  // 正视 (XZ)
        Top,    // 俯视 (XY)
        Right   // 右视 (YZ)
    }

    internal static class ViewportHelper
    {
        public static void ConfigureViewport(Document doc, CadViewDirection dir, Extents3d? bounds, string visualStyle = "Shaded with edges", double targetAspect = 1.0)
        {
            if (doc == null) return;
            var db = doc.Database;
            var ed = doc.Editor;

            // 1. 关闭网格与坐标系图标
            try
            {
                AcadApp.SetSystemVariable("GRIDMODE", 0);
                AcadApp.SetSystemVariable("UCSICON", 0);
            }
            catch (Exception)
            {
                // 部分环境下只读保护容错
            }

            // 2. 获取着色带边框视觉样式 ID (优先 Shaded with edges / 带边框着色)
            var vsId = GetVisualStyleId(db, visualStyle);

            // 3. 构造视口记录并应用
            using (var view = ed.GetCurrentView())
            {
                view.ViewDirection = GetDirectionVector(dir);
                view.ViewTwist = 0.0;
                view.PerspectiveEnabled = false; // 正交视图，无透视畸变

                if (vsId != ObjectId.Null)
                {
                    view.VisualStyleId = vsId;
                }

                // 4. 聚焦到模型三维包围盒（严格按目标视口宽高比对齐，消除各向异性拉伸变形）
                if (bounds.HasValue)
                {
                    FitViewToExtents(view, bounds.Value, targetAspect);
                }

                ed.SetCurrentView(view);
            }

            ed.UpdateScreen();
            System.Windows.Forms.Application.DoEvents();
        }

        private static Vector3d GetDirectionVector(CadViewDirection dir)
        {
            switch (dir)
            {
                case CadViewDirection.IsoSE:
                    return new Vector3d(1.0, -1.0, 1.0).GetNormal();
                case CadViewDirection.Front:
                    return new Vector3d(0.0, -1.0, 0.0);
                case CadViewDirection.Top:
                    return new Vector3d(0.0, 0.0, 1.0);
                case CadViewDirection.Right:
                    return new Vector3d(1.0, 0.0, 0.0);
                default:
                    return new Vector3d(1.0, -1.0, 1.0).GetNormal();
            }
        }

        /// <summary>
        /// 正交视图的投影上下文：把世界坐标映射到画面像素所需的全部参数。
        /// 视图定位 (FitViewToExtents) 与尺寸标注必须共用同一份计算，
        /// 否则标注点会整体偏离模型。
        /// </summary>
        private struct ViewProjection
        {
            public Point3d Center;
            public Vector3d DcsX;
            public Vector3d DcsY;
            public double CenterX;
            public double CenterY;
            public double Width;
            public double Height;
        }

        /// <summary>画面四周留白比例，与呼吸边距一致。</summary>
        private const double ViewMarginFactor = 1.25;

        private static ViewProjection ComputeProjection(Extents3d extents, Vector3d viewDir, double targetAspect = 1.0)
        {
            var center = extents.MinPoint + (extents.MaxPoint - extents.MinPoint) * 0.5;

            // 构造显示坐标系 (DCS) 正交基底 (Screen X, Screen Y)
            Vector3d dcsX, dcsY;
            if (Math.Abs(viewDir.Z) > 0.99999)
            {
                dcsX = Vector3d.XAxis;
                dcsY = viewDir.Z > 0 ? Vector3d.YAxis : -Vector3d.YAxis;
            }
            else
            {
                dcsX = Vector3d.ZAxis.CrossProduct(viewDir).GetNormal();
                dcsY = viewDir.CrossProduct(dcsX).GetNormal();
            }

            // 投影 8 个角点到 DCS 平面
            var pts = new[]
            {
                new Point3d(extents.MinPoint.X, extents.MinPoint.Y, extents.MinPoint.Z),
                new Point3d(extents.MinPoint.X, extents.MinPoint.Y, extents.MaxPoint.Z),
                new Point3d(extents.MinPoint.X, extents.MaxPoint.Y, extents.MinPoint.Z),
                new Point3d(extents.MinPoint.X, extents.MaxPoint.Y, extents.MaxPoint.Z),
                new Point3d(extents.MaxPoint.X, extents.MinPoint.Y, extents.MinPoint.Z),
                new Point3d(extents.MaxPoint.X, extents.MinPoint.Y, extents.MaxPoint.Z),
                new Point3d(extents.MaxPoint.X, extents.MaxPoint.Y, extents.MinPoint.Z),
                new Point3d(extents.MaxPoint.X, extents.MaxPoint.Y, extents.MaxPoint.Z)
            };

            double minX = double.MaxValue, maxX = double.MinValue;
            double minY = double.MaxValue, maxY = double.MinValue;

            for (var i = 0; i < pts.Length; i++)
            {
                var v = pts[i] - center;
                var x = v.DotProduct(dcsX);
                var y = v.DotProduct(dcsY);
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            }

            var spanX = Math.Max((maxX - minX) * ViewMarginFactor, 20.0);
            var spanY = Math.Max((maxY - minY) * ViewMarginFactor, 20.0);

            // 核心：相机的视域范围必须与渲染画面的物理宽高比严格保持一致！
            // 否则 AutoCAD 离屏渲染器会将视口拉伸填充到画面中，导致圆变扁、正方形变长方形！
            double viewW, viewH;
            if (targetAspect > 0.001)
            {
                var boxAspect = spanX / Math.Max(1e-6, spanY);
                if (boxAspect > targetAspect)
                {
                    viewW = spanX;
                    viewH = spanX / targetAspect;
                }
                else
                {
                    viewH = spanY;
                    viewW = spanY * targetAspect;
                }
            }
            else
            {
                viewW = spanX;
                viewH = spanY;
            }

            return new ViewProjection
            {
                Center = center,
                DcsX = dcsX,
                DcsY = dcsY,
                CenterX = (minX + maxX) * 0.5,
                CenterY = (minY + maxY) * 0.5,
                Width = viewW,
                Height = viewH
            };
        }

        /// <summary>世界点 → 画面像素。画面尺寸必须与投影宽高比一致，否则映射不成立。</summary>
        private static PointF ProjectToPixel(ViewProjection p, Point3d pt, int imgW, int imgH)
        {
            var v = pt - p.Center;
            var u = v.DotProduct(p.DcsX);
            var w = v.DotProduct(p.DcsY);
            var nx = (u - p.CenterX) / p.Width;
            var ny = (w - p.CenterY) / p.Height;
            return new PointF((float)((nx + 0.5) * imgW), (float)((0.5 - ny) * imgH));
        }

        private static void FitViewToExtents(ViewTableRecord view, Extents3d extents, double targetAspect = 1.0)
        {
            var p = ComputeProjection(extents, view.ViewDirection.GetNormal(), targetAspect);

            view.Target = p.Center;
            view.CenterPoint = new Point2d(p.CenterX, p.CenterY);
            view.Width = p.Width;
            view.Height = p.Height;
        }

        public static ObjectId GetVisualStyleId(Database db, string styleName = "Shaded with edges")
        {
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var dict = (DBDictionary)tr.GetObject(db.VisualStyleDictionaryId, OpenMode.ForRead);
                    string[] candidates = {
                        styleName,
                        "Shaded with edges",
                        "带边框着色",
                        "ShadedWithEdges",
                        "Realistic",
                        "真实",
                        "Shaded",
                        "着色",
                        "Conceptual",
                        "概念"
                    };
                    foreach (var s in candidates)
                    {
                        if (!string.IsNullOrEmpty(s) && dict.Contains(s))
                        {
                            return dict.GetAt(s);
                        }
                    }
                    tr.Commit();
                }
            }
            catch (Exception)
            {
                // ignored
            }

            return ObjectId.Null;
        }

        public static bool CaptureIsometricOnly(Document doc, Extents3d? bounds, string outputPngPath, string title)
        {
            double screenAspect = 1.3333;
            try
            {
                using (var curV = doc.Editor.GetCurrentView())
                {
                    if (curV.Height > 1e-4)
                    {
                        screenAspect = curV.Width / curV.Height;
                    }
                }
            }
            catch { }

            const int width = 1024;
            const int headerH = 40;
            var bodyH = (int)Math.Round(width / Math.Max(0.5, Math.Min(3.0, screenAspect)));
            var height = bodyH + headerH;

            try
            {
                ConfigureViewport(doc, CadViewDirection.IsoSE, bounds, "Shaded with edges", screenAspect);
                doc.Editor.UpdateScreen();
                System.Windows.Forms.Application.DoEvents();

                var preview = doc.CapturePreviewImage((uint)width, (uint)bodyH);
                using (var canvas = new Bitmap(width, height))
                using (var g = Graphics.FromImage(canvas))
                {
                    g.Clear(Color.FromArgb(245, 247, 250));

                    // 顶部标题条
                    using (var headBrush = new SolidBrush(Color.FromArgb(38, 50, 56)))
                    {
                        g.FillRectangle(headBrush, 0, 0, width, headerH);
                    }
                    using (var titleFont = new System.Drawing.Font("Microsoft YaHei", 12, System.Drawing.FontStyle.Bold))
                    using (var textBrush = new SolidBrush(Color.White))
                    {
                        g.DrawString((title ?? "P3D_COMPONENT") + " [AutoCAD Plant 3D 东南等轴测图]", titleFont, textBrush, 14, 10);
                    }

                    if (preview != null)
                    {
                        g.DrawImage(preview, 0, headerH, width, bodyH);
                        preview.Dispose();
                    }

                    var outDir = Path.GetDirectoryName(outputPngPath);
                    if (!string.IsNullOrEmpty(outDir)) Directory.CreateDirectory(outDir);
                    canvas.Save(outputPngPath, ImageFormat.Png);
                    return true;
                }
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
