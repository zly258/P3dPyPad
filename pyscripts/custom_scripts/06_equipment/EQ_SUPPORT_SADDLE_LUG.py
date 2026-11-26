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

@activate(Group="Equipment",
          TooltipShort=u"容器标准鞍式支座组件 (NB/T 47065.1)",
          TooltipLong=u"NB/T 47065.1 卧式容器标准重型/轻型 120°包角鞍式支座参数化模型，含 120°弧形包角垫板、主腹板、5道立筋板及底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"NB/T 47065.1 标准鞍式支座主要尺寸参数")
@param(DN=LENGTH, TooltipShort=u"适配容器公称直径", TooltipLong=u"所支承卧式容器公称直径 DN (mm)")
@param(H_CL=LENGTH, TooltipShort=u"支座中心高", TooltipLong=u"底板底面至容器中心线高度 H (mm)", Ask4Dist=True)
@param(B_BASE=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"鞍座底板沿容器轴向宽度 b (mm)", Ask4Dist=True)
@param(L_BASE=LENGTH, TooltipShort=u"底板长度", TooltipLong=u"鞍座底板横向跨度长度 l (mm)", Ask4Dist=True)
@param(T_BASE=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"底板钢板厚度 (mm)")
@param(T_WEB=LENGTH, TooltipShort=u"腹板与筋板厚", TooltipLong=u"主腹板与立筋板厚度 (mm)")
@param(T_PAD=LENGTH, TooltipShort=u"垫板厚度", TooltipLong=u"120°弧形包角垫板厚度 (mm)")
def EQ_SUPPORT_SADDLE_LUG(
    s,
    DN=1200.0,
    H_CL=900.0,
    B_BASE=260.0,
    L_BASE=1040.0,
    T_BASE=20.0,
    T_WEB=14.0,
    T_PAD=12.0,
    ID=u"EQ_SUPPORT_SADDLE_LUG",
    **kw
):
    u"""NB/T 47065.1 120°包角标准鞍式支座 (底板底面 Z=0，容器轴向沿 X 轴，容器底部切点 Z=H_CL-DN/2 为端口 1)。"""
    DN = max(400.0, float(DN))
    R_V = DN / 2.0
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0
    B_BASE = float(B_BASE)
    if B_BASE < 1.0:
        B_BASE = 1.0
    L_BASE = float(L_BASE)
    if L_BASE < 1.0:
        L_BASE = 1.0
    T_BASE = max(12.0, float(T_BASE))
    T_WEB = max(8.0, float(T_WEB))
    T_PAD = max(8.0, float(T_PAD))

    # 120度包角弦宽与顶边高度
    arc_half_y = R_V * math.sin(math.radians(60.0))  # R_V * 0.866
    z_arc_top = H_CL - R_V * math.cos(math.radians(60.0))  # H_CL - 0.5 * R_V
    z_bot_tan = H_CL - R_V
    pad_b = B_BASE + 80.0

    # 1. 鞍座底板 (Z: 0 -> T_BASE)
    o_main = CORNERBOX(s, L=B_BASE, W=L_BASE, H=T_BASE).translate(
        (-B_BASE / 2.0, -L_BASE / 2.0, 0.0)
    )

    # 2. 主腹板 (居中于 X=0, 从底板直达 120° 弧面)
    web_w = min(L_BASE * 0.96, arc_half_y * 2.0)
    o_web = CORNERBOX(s, L=T_WEB, W=web_w, H=z_arc_top - T_BASE + 10.0).translate(
        (-T_WEB / 2.0, -web_w / 2.0, T_BASE - 4.0)
    )
    o_main.uniteWith(o_web)
    o_web.erase()

    # 3. 5 道横向立筋板 (对称布置于 Y = 0, ±0.24*web_w, ±0.46*web_w)
    rib_l = B_BASE * 0.92
    for frac in (-0.45, -0.23, 0.0, 0.23, 0.45):
        ry = frac * web_w
        z_r_top = H_CL - math.sqrt(max(1.0, R_V * R_V - ry * ry)) + 15.0
        rib_h = max(40.0, z_r_top - T_BASE + 4.0)
        o_rib = CORNERBOX(s, L=rib_l, W=T_WEB, H=rib_h).translate(
            (-rib_l / 2.0, ry - T_WEB / 2.0, T_BASE - 4.0)
        )
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 4. 用容器外圆柱减去主腹板与筋板上部，形成精确弧形鞍座面
    o_cut = CYLINDER(s, R=R_V + T_PAD * 0.4, H=pad_b + 120.0, O=0.0).rotateY(90.0).translate(
        (-(pad_b + 120.0) / 2.0, 0.0, H_CL)
    )
    o_main.subtractFrom(o_cut)
    o_cut.erase()

    # 5. 120° 弧形包角垫板 (圆柱环与 120° 矩形框求交后并入主体)
    o_pad_ring = CYLINDER(s, R=R_V + T_PAD, H=pad_b, O=R_V).rotateY(90.0).translate(
        (-pad_b / 2.0, 0.0, H_CL)
    )
    o_pad_clip = CORNERBOX(s, L=pad_b + 20.0, W=arc_half_y * 2.0, H=R_V * 0.52 + T_PAD + 10.0).translate(
        (-pad_b / 2.0 - 10.0, -arc_half_y, H_CL - R_V - T_PAD - 5.0)
    )
    o_pad_ring.intersectWith(o_pad_clip)
    o_pad_clip.erase()
    o_main.uniteWith(o_pad_ring)
    o_pad_ring.erase()

    # 6. 注册 1 个装配端口 (位于 120° 弧形垫板最低切点，严格落在实体包围盒内)
    s.setPoint((0.0, 0.0, z_bot_tan), (0.0, 0.0, 1.0))

    # 7. 注册线性标注
    s.setLinearDimension('B_BASE', (-B_BASE / 2.0, -L_BASE / 2.0, 0.0), (B_BASE / 2.0, -L_BASE / 2.0, 0.0))
    s.setLinearDimension('L_BASE', (-B_BASE / 2.0, -L_BASE / 2.0, 0.0), (-B_BASE / 2.0, L_BASE / 2.0, 0.0))
    s.setLinearDimension('H_CL', (0.0, 0.0, 0.0), (0.0, 0.0, H_CL))
