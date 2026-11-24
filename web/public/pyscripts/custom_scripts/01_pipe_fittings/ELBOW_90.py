# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
# ELBOW_90: AutoCAD Plant 3D 90度长半径无缝对焊弯头 (ASME B16.9 / GB/T 12459)
# 几何特征：90°空间圆环平滑弯曲段 + 两端切线直段 + 标准 37.5° 对焊坡口倒角 + 全贯通平滑内流道
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *


@activate(Group="Elbow", TooltipShort=u"90度对焊弯头", TooltipLong=u"90度长半径无缝对焊弯头（带标准对焊坡口与全贯通内流道）", LengthUnit="mm", Ports=2)
@group("MainDimensions", TooltipLong=u"弯头主要几何尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"弯头公称管道外径 OD")
@param(R=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"中心线弯曲半径 (长半径 1.5D)")
@param(THK=LENGTH0, TooltipShort=u"管道壁厚", TooltipLong=u"公称壁厚，大于0时贯通内流道")
@param(TL=LENGTH0, TooltipShort=u"切线直段", TooltipLong=u"端口对焊切线直段延伸长度")
@param(BW=LENGTH0, TooltipShort=u"坡口长度", TooltipLong=u"端口 37.5° 对焊坡口倒角轴向长度，0为平端")
@param(ID=STRING, TooltipShort=u"构件位号", TooltipLong=u"弯头规格标识，如 E90-DN100")
def ELBOW_90(s, D=114.3, R=152.4, THK=6.0, TL=25.0, BW=3.0, ID=u"ELBOW_90-DN100", **kw):
    D = float(D)
    R = float(R)
    THK = float(THK)
    TL = float(TL)
    BW = float(BW)

    r_outer = D / 2.0
    if R <= r_outer + 5.0:
        R = r_outer * 1.5
    if TL < 0.0:
        TL = 0.0
    if BW < 0.0:
        BW = 0.0
    if THK <= 0.0 or THK >= r_outer * 0.8:
        THK = max(3.0, r_outer * 0.11)

    r_inner = r_outer - THK
    bevel_len = min(max(0.0, BW), TL * 0.45) if TL > 2.0 else 0.0
    r_bevel_tip = r_inner + min(1.6, THK * 0.25)

    # 1. 主弯曲段：ARC3D 在 XY 平面内，两端中心线切线交点在 (0, 0, 0)
    # 端口 1 截面中心位于 (0.0, R, 0.0)，端口 2 截面中心位于 (R, 0.0, 0.0)
    o_main = ARC3D(s, D=r_outer, R=R, A=90.0)

    # 2. 两端切线直段 + 标准 37.5° 对焊坡口锥台 (消除旧版突兀的外凸台阶环)
    if TL > 0.0:
        cyl_len = max(1.0, TL - bevel_len)
        # 端口 1 (沿 +Y 延伸)
        o_ext1 = CYLINDER(s, R=r_outer, H=cyl_len, O=0.0).rotateX(-90.0).translate((0.0, R, 0.0))
        o_main.uniteWith(o_ext1); o_ext1.erase()
        if bevel_len > 0.5:
            o_bev1 = CONE(s, R1=r_outer, R2=r_bevel_tip, H=bevel_len).rotateX(-90.0).translate((0.0, R + cyl_len, 0.0))
            o_main.uniteWith(o_bev1); o_bev1.erase()

        # 端口 2 (沿 +X 延伸)
        o_ext2 = CYLINDER(s, R=r_outer, H=cyl_len, O=0.0).rotateY(90.0).translate((R, 0.0, 0.0))
        o_main.uniteWith(o_ext2); o_ext2.erase()
        if bevel_len > 0.5:
            o_bev2 = CONE(s, R1=r_outer, R2=r_bevel_tip, H=bevel_len).rotateY(90.0).translate((R + cyl_len, 0.0, 0.0))
            o_main.uniteWith(o_bev2); o_bev2.erase()

    # 3. 贯通内流道：先将内弯流道与两端切线段流道芯体融合，再一次性 subtractFrom
    o_core = ARC3D(s, D=r_inner, R=R, A=90.0)
    core_ext = TL + 5.0
    o_c1 = CYLINDER(s, R=r_inner, H=core_ext, O=0.0).rotateX(-90.0).translate((0.0, R, 0.0))
    o_core.uniteWith(o_c1); o_c1.erase()
    o_c2 = CYLINDER(s, R=r_inner, H=core_ext, O=0.0).rotateY(90.0).translate((R, 0.0, 0.0))
    o_core.uniteWith(o_c2); o_c2.erase()

    o_main.subtractFrom(o_core)
    o_core.erase()

    # 4. 端口设置与轴测尺寸标注锚点
    p1_y = R + TL
    p2_x = R + TL
    s.setPoint((0.0, p1_y, 0.0), (0.0, 1.0, 0.0))
    s.setPoint((p2_x, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("R", (0.0, 0.0, -r_outer), (R, 0.0, -r_outer))
    s.setLinearDimension("D", (p2_x, 0.0, -r_outer), (p2_x, 0.0, r_outer))
    if TL > 0.0:
        s.setLinearDimension("TL", (R, 0.0, r_outer), (R + TL, 0.0, r_outer))
