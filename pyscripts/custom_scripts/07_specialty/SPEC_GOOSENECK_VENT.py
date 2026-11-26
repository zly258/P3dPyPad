# -*- coding: utf-8 -*-
import math
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Cap",
          TooltipShort=u"鹅颈放空管 (HG/T 21574)",
          TooltipLong=u"带底法兰与防雨防虫网口的 180 度回弯鹅颈放空管，含安装底法兰、竖直立管、180 度回弯段及喇叭防雨网口",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"鹅颈放空管管径、底法兰、总高及弯曲半径")
@param(D=LENGTH, TooltipShort=u"放空管外径", TooltipLong=u"放空立管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"安装底法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"安装底法兰厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"放空管总高", TooltipLong=u"底法兰面至 180 度回弯外背顶端总高 H (mm)", Ask4Dist=True)
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"180 度回弯中心线弯曲半径 R (mm)", Ask4Dist=True)
def SPEC_GOOSENECK_VENT(
    s,
    D=114.3,
    D_FL=220.0,
    C_FL=20.0,
    H_TOTAL=650.0,
    R_BEND=152.0,
    ID=u"SPEC_GOOSENECK_VENT",
    **kw
):
    u"""鹅颈放空管 (底法兰面在 Z=0, Port 1 朝向 -Z, 回弯朝 +X 向下开口)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    z_bend = H_TOTAL - R_BEND - r_pipe

    # 1. 安装底法兰与竖直立管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    o_riser = CYLINDER(s, R=r_pipe, H=z_bend - C_FL + 8.0, O=0.0).translate((0.0, 0.0, C_FL - 4.0))
    o_main.uniteWith(o_riser)
    o_riser.erase()

    # 2. 顶部 180 度回弯 (使用 12 段光滑管节拟合 180 度圆弧, 绝对无接缝/旋转歧义)
    n_seg = 12
    for i in range(n_seg):
        a0 = math.pi * float(i) / float(n_seg)
        a1 = math.pi * float(i + 1) / float(n_seg)
        am = 0.5 * (a0 + a1)
        x0 = R_BEND * (1.0 - math.cos(a0))
        z0 = z_bend + R_BEND * math.sin(a0)
        x1 = R_BEND * (1.0 - math.cos(a1))
        z1 = z_bend + R_BEND * math.sin(a1)
        seg_l = math.hypot(x1 - x0, z1 - z0) + 4.0
        o_seg = CYLINDER(s, R=r_pipe, H=seg_l, O=0.0).translate((0.0, 0.0, -2.0))
        o_seg.rotateY(math.degrees(am)).translate((x0, 0.0, z0))
        o_main.uniteWith(o_seg)
        o_seg.erase()
        if i > 0:
            o_jt = SPHERE(s, R=r_pipe).translate((x0, 0.0, z0))
            o_main.uniteWith(o_jt)
            o_jt.erase()

    # 3. 向下短管与喇叭防雨防虫网口
    x_out = 2.0 * R_BEND
    l_stub = max(55.0, D * 0.65)
    z_mouth = z_bend - l_stub
    o_stub = CYLINDER(s, R=r_pipe, H=l_stub + 6.0, O=0.0).translate((x_out, 0.0, z_mouth))
    o_main.uniteWith(o_stub)
    o_stub.erase()

    o_collar = CYLINDER(s, R=r_pipe * 1.24, H=max(16.0, D * 0.16), O=0.0).translate((x_out, 0.0, z_mouth - 4.0))
    o_main.uniteWith(o_collar)
    o_collar.erase()

    o_mesh_rim = CONE(s, R1=r_pipe * 1.30, R2=r_pipe * 1.05, H=max(18.0, D * 0.18), E=0.0).translate((x_out, 0.0, z_mouth - max(18.0, D * 0.18)))
    o_main.uniteWith(o_mesh_rim)
    o_mesh_rim.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('R_BEND', (0.0, 0.0, z_bend), (x_out, 0.0, z_bend))
