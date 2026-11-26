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

@activate(Group="Valve",
          TooltipShort=u"夹持式爆破片安全装置 (GB/T 567)",
          TooltipLong=u"GB/T 567 对夹式爆破片安全装置，含进口/出口夹持器双环与侧向标牌手柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"夹持式爆破片总厚、夹持器外径与标牌手柄尺寸参数")
@param(D=LENGTH, TooltipShort=u"公称管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"夹持器总厚", TooltipLong=u"对夹式夹持器双环总厚度 L (mm)", Ask4Dist=True)
@param(D_HOLDER=LENGTH, TooltipShort=u"夹持器外径", TooltipLong=u"夹持器外圆直径 (mm)")
@param(H_TAG=LENGTH, TooltipShort=u"标牌顶高", TooltipLong=u"管道中心至侧向标牌手柄顶端高度 (mm)", Ask4Dist=True)
@param(W_TAG=LENGTH, TooltipShort=u"标牌宽度", TooltipLong=u"侧向铭牌标牌宽度 (mm)")
def SPEC_RUPTURE_DISC(
    s,
    D=114.3,
    L_FACE=58.0,
    D_HOLDER=162.0,
    H_TAG=175.0,
    W_TAG=40.0,
    ID=u"SPEC_RUPTURE_DISC",
    **kw
):
    u"""夹持式爆破片安全装置 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 标牌手柄在 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_HOLDER = max(D + 24.0, float(D_HOLDER))
    H_TAG = float(H_TAG)
    if H_TAG < 1.0:
        H_TAG = 1.0
    W_TAG = max(20.0, float(W_TAG))

    half_l = L_FACE / 2.0
    r_hold = D_HOLDER / 2.0
    r_mid = r_hold * 0.90
    ring_t = (L_FACE - 8.0) / 2.0

    # 1. 夹持器双环（进口环 + 出口环）与中间爆破片夹持槽颈
    o_main = CYLINDER(s, R=r_hold, H=ring_t, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_ring2 = CYLINDER(s, R=r_hold, H=ring_t, O=0.0).rotateY(90.0).translate((half_l - ring_t, 0.0, 0.0))
    o_main.uniteWith(o_ring2)
    o_ring2.erase()

    o_mid = CYLINDER(s, R=r_mid, H=14.0, O=0.0).rotateY(90.0).translate((-7.0, 0.0, 0.0))
    o_main.uniteWith(o_mid)
    o_mid.erase()

    # 2. 侧向 (+Z) 标牌手柄与矩形爆破参数铭牌
    tag_h = max(28.0, (H_TAG - r_hold) * 0.48)
    stem_h = max(20.0, H_TAG - r_hold - tag_h + 12.0)
    o_stem = CYLINDER(s, R=max(5.0, L_FACE * 0.11), H=stem_h, O=0.0).translate((0.0, 0.0, r_hold - 8.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    o_plate = BOX(s, L=W_TAG, W=tag_h, H=max(8.0, L_FACE * 0.22)).translate((0.0, 0.0, H_TAG - tag_h / 2.0))
    o_main.uniteWith(o_plate)
    o_plate.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TAG', (0.0, 0.0, 0.0), (0.0, 0.0, H_TAG))
