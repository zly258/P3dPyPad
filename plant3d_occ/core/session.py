# -*- coding: utf-8 -*-
"""Plant 3D 脚本全局上下文会话管理器 (s对象)
负责追踪脚本内生成的所有实体、连接端口 (Port) 与参数化尺寸夹点/标注 (Grip / LinearDimension)。
"""


class OccSession:
    """模拟 AutoCAD Plant 3D 传递给脚本入口函数的第一个参数 `s`"""

    def __init__(self):
        self.bodies = []
        self.ports = []
        self.grips = []
        self.linear_dimensions = self.grips
        self._call_depth = 0

    def add_body(self, body):
        self.bodies.append(body)

    def register_body(self, body):
        self.bodies.append(body)

    def setPoint(self, pt, vec=None, angle=0.0, *extra):
        """注册管道连接端口 (Port)：包含三维坐标点与外法向方向向量"""
        if vec is not None and not hasattr(pt, "__len__") and len(extra) >= 3:
            # 6-scalar call: s.setPoint(x, y, z, dx, dy, dz)
            p_coord = (float(pt), float(vec), float(angle))
            d_coord = (float(extra[0]), float(extra[1]), float(extra[2]))
            ang = float(extra[3]) if len(extra) > 3 else 0.0
        else:
            p_coord = (float(pt[0]), float(pt[1]), float(pt[2]))
            d_coord = (float(vec[0]), float(vec[1]), float(vec[2])) if vec is not None else (1.0, 0.0, 0.0)
            ang = float(angle)
        self.ports.append({
            "point": p_coord,
            "dir": d_coord,
            "angle": ang,
        })

    def setEndpoints(self, *args, **kw):
        return self

    def setColor(self, *args, **kw):
        return self

    def setLinearDimension(self, name, pt1, pt2, ext_dir=None, style=None):
        """注册线性尺寸动态拉伸夹点与轴测尺寸标注点 (Grip & Isometric Dimension)。

        兼容 AutoCAD Plant 3D 原生三参数调用 `s.setLinearDimension(name, pt1, pt2)`，
        同时可选支持 `ext_dir` (三维引出线方向) 与 `style` ("linear" | "leader_ext")。
        """
        if not name or str(name).strip().startswith("#"):
            return
        entry = {
            "name": str(name).strip(),
            "pt1": (float(pt1[0]), float(pt1[1]), float(pt1[2])),
            "pt2": (float(pt2[0]), float(pt2[1]), float(pt2[2])),
        }
        if ext_dir is not None and len(ext_dir) >= 3:
            entry["ext_dir"] = (float(ext_dir[0]), float(ext_dir[1]), float(ext_dir[2]))
        if style is not None:
            entry["style"] = str(style)
        for idx, existing in enumerate(self.grips):
            if existing["name"] == entry["name"]:
                self.grips[idx] = entry
                return
        self.grips.append(entry)

    def get_final_shapes(self):
        """提取所有未被 .erase() 销毁的最终保留三维实体，并自动统一共面与共线几何，消除多余内部棱线。

        注意：ShapeUpgrade_UnifySameDomain 会把"接缝"合并掉，但它本身不保证结果仍然有效。
        在同时存在贴合面 / 相切圆角的装配体上（典型如阀门阀体），合并会产出
        BRepCheck_Analyzer 判定无效的壳，后续渲染、包围盒、布尔都会跟着出问题——
        表现为"模型外形莫名其妙不对"。因此这里必须校验合并结果：
        无效就退回合并前的原始实体，宁可多几条内部棱线，也不能交付坏几何。
        """
        valid_shapes = [b.shape for b in self.bodies if not b.erased and b.shape is not None and (not hasattr(b.shape, "IsNull") or not b.shape.IsNull())]
        cleaned = []
        for sh in valid_shapes:
            cleaned.append(self._unify_if_valid(sh))
        return cleaned

    @staticmethod
    def _unify_if_valid(shape):
        """共面合并；合并结果无效时退回原实体。

        ShapeUpgrade_UnifySameDomain 会**原地改写**传入实体的底层拓扑，
        所以必须在副本上合并：否则一旦合并失败，原件也已经被改坏，
        再"退回原实体"已经来不及（同一对象前后 IsValid 结果会由 True 变 False）。
        """
        try:
            from OCC.Core.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
            from OCC.Core.BRepCheck import BRepCheck_Analyzer
            from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Copy

            work = BRepBuilderAPI_Copy(shape).Shape()
            if work is None or (hasattr(work, "IsNull") and work.IsNull()):
                return shape

            unif = ShapeUpgrade_UnifySameDomain(work, True, True, True)
            unif.Build()
            merged = unif.Shape()
            if merged is None or (hasattr(merged, "IsNull") and merged.IsNull()):
                return shape
            if not BRepCheck_Analyzer(merged).IsValid():
                return shape
            return merged
        except Exception:
            return shape

    def add(self, body):
        return self.register_body(body)
