# -*- coding: utf-8 -*-
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
          TooltipShort=u"钢制回转盖人孔组件 (HG/T 21515)",
          TooltipLong=u"HG/T 21515 常压/带颈平焊回转盖人孔组件参数化模型，含人孔筒节、法兰、回转盲盖、侧铰链轴支耳及盖顶吊耳",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"HG/T 21515 钢制回转盖人孔主要尺寸参数")
@param(DN=LENGTH, TooltipShort=u"人孔公称通径", TooltipLong=u"人孔公称通径 DN (mm)")
@param(H_NECK=LENGTH, TooltipShort=u"筒节高度", TooltipLong=u"人孔焊接端面至法兰密封面高度 H (mm)", Ask4Dist=True)
@param(D_FLANGE=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"人孔法兰及盲盖外径 D (mm)")
@param(T_FLANGE=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"人孔法兰厚度 (mm)")
@param(T_COVER=LENGTH, TooltipShort=u"盲盖厚度", TooltipLong=u"回转盲盖板厚度 (mm)")
def EQ_MANHOLE_HGT21515(
    s,
    DN=450.0,
    H_NECK=220.0,
    D_FLANGE=585.0,
    T_FLANGE=26.0,
    T_COVER=24.0,
    ID=u"EQ_MANHOLE_HGT21515",
    **kw
):
    u"""HG/T 21515 钢制回转盖人孔组件 (焊接端面 Z=0 为端口 1，法向 -Z，筒节与盲盖沿 +Z)。"""
    DN = max(300.0, float(DN))
    H_NECK = float(H_NECK)
    if H_NECK < 1.0:
        H_NECK = 1.0
    D_FLANGE = float(D_FLANGE)
    if D_FLANGE < 1.0:
        D_FLANGE = 1.0
    T_FLANGE = max(16.0, float(T_FLANGE))
    T_COVER = max(14.0, float(T_COVER))

    r_neck = (DN + 14.0) / 2.0
    r_fl = D_FLANGE / 2.0

    # 1. 人孔筒节 (Z: 0 -> H_NECK)
    o_main = CYLINDER(s, R=r_neck, H=H_NECK, O=0.0)

    # 2. 人孔法兰 (顶面齐平 Z=H_NECK)
    o_fl = CYLINDER(s, R=r_fl, H=T_FLANGE, O=0.0).translate((0.0, 0.0, H_NECK - T_FLANGE))
    o_main.uniteWith(o_fl)
    o_fl.erase()

    # 3. 垫片槽间隙与回转盲盖 (Z: H_NECK -> H_NECK + T_COVER)
    o_gsk = CYLINDER(s, R=r_neck + 28.0, H=6.0, O=0.0).translate((0.0, 0.0, H_NECK - 2.0))
    o_main.uniteWith(o_gsk)
    o_gsk.erase()

    z_cov0 = H_NECK + 3.0
    o_cov = CYLINDER(s, R=r_fl, H=T_COVER, O=0.0).translate((0.0, 0.0, z_cov0))
    o_main.uniteWith(o_cov)
    o_cov.erase()

    # 4. 侧回转铰链机构 (+X 侧: 法兰支耳 + 盲盖转臂 + 竖直铰链转轴)
    x_pin = r_fl + 42.0
    lug_l = 75.0
    lug_w = 54.0
    # 法兰侧支耳
    o_hlug1 = CORNERBOX(s, L=lug_l, W=lug_w, H=T_FLANGE).translate(
        (r_fl - 25.0, -lug_w / 2.0, H_NECK - T_FLANGE)
    )
    # 盲盖侧支耳
    o_hlug2 = CORNERBOX(s, L=lug_l, W=lug_w, H=T_COVER).translate(
        (r_fl - 25.0, -lug_w / 2.0, z_cov0)
    )
    # 竖直铰链转轴 (贯穿上下支耳)
    pin_h = T_FLANGE + T_COVER + 68.0
    o_pin = CYLINDER(s, R=18.0, H=pin_h, O=0.0).translate(
        (x_pin, 0.0, H_NECK - T_FLANGE - 24.0)
    )
    o_main.uniteWith(o_hlug1)
    o_hlug1.erase()
    o_main.uniteWith(o_hlug2)
    o_hlug2.erase()
    o_main.uniteWith(o_pin)
    o_pin.erase()

    # 5. 盖顶中心吊耳 + 两侧把手 (-X/+Y 侧)
    z_top = z_cov0 + T_COVER
    o_eye = CORNERBOX(s, L=20.0, W=84.0, H=76.0).translate((-10.0, -42.0, z_top - 4.0))
    o_main.uniteWith(o_eye)
    o_eye.erase()

    # 盲盖边缘把手 (-X 侧)
    o_hleg1 = CYLINDER(s, R=10.0, H=58.0, O=0.0).translate((-r_fl * 0.72, -55.0, z_top - 4.0))
    o_hleg2 = CYLINDER(s, R=10.0, H=58.0, O=0.0).translate((-r_fl * 0.72, 55.0, z_top - 4.0))
    o_hbar = CYLINDER(s, R=10.0, H=124.0, O=0.0).rotateX(-90.0).translate((-r_fl * 0.72, -62.0, z_top + 46.0))
    o_main.uniteWith(o_hleg1)
    o_hleg1.erase()
    o_main.uniteWith(o_hleg2)
    o_hleg2.erase()
    o_main.uniteWith(o_hbar)
    o_hbar.erase()

    # 6. 注册 1 个焊接端口 (Z=0 中心，法向 -Z)
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))

    # 7. 注册线性标注
    s.setLinearDimension('D_FLANGE', (-r_fl, 0.0, H_NECK), (r_fl, 0.0, H_NECK))
    s.setLinearDimension('H_NECK', (-r_neck, 0.0, 0.0), (-r_neck, 0.0, H_NECK))
