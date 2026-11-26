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

@activate(Group="Coupling",
          TooltipShort=u"锻钢承插焊活接头 Union (GB/T 14383)",
          TooltipLong=u"GB/T 14383-2021 锻钢承插焊活接头 (Class 3000)，含两端承插体、中间大直径六角锁紧螺母环与贯通流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="SW")
@group("MainDimensions", TooltipLong=u"锻钢承插焊活接头主要几何参数")
@param(D_HUB=LENGTH, TooltipShort=u"承插端外径", TooltipLong=u"活接头两端承插肩外径 D_HUB (mm)")
@param(D_BORE=LENGTH, TooltipShort=u"承插孔径", TooltipLong=u"承插口内径 B (mm)")
@param(D_IN=LENGTH, TooltipShort=u"通流内径", TooltipLong=u"活接头中心通流孔径 D_IN (mm)")
@param(W_NUT=LENGTH, TooltipShort=u"螺母对边宽", TooltipLong=u"中间六角锁紧螺母对边宽度 W_NUT (mm)")
@param(L_LEN=LENGTH, TooltipShort=u"活接头总长", TooltipLong=u"活接头端面至端面总长 L (mm)", Ask4Dist=True)
@param(J_DEP=LENGTH, TooltipShort=u"承插深度", TooltipLong=u"承插口深度 J (mm)")
def UNION_SW_GBT14383(
    s,
    D_HUB=48.0,
    D_BORE=33.9,
    D_IN=26.6,
    W_NUT=64.0,
    L_LEN=62.0,
    J_DEP=12.5,
    ID=u"UNION_SW_GBT14383",
    **kw
):
    u"""锻钢承插焊活接头 Union (两端承插体 + 中间大六角锁紧螺母)。"""
    D_HUB = max(20.0, float(D_HUB))
    D_BORE = max(12.0, min(D_HUB - 4.0, float(D_BORE)))
    D_IN = max(8.0, min(D_BORE - 2.0, float(D_IN)))
    W_NUT = max(D_HUB + 6.0, float(W_NUT))
    L_LEN = float(L_LEN)
    if L_LEN < 1.0:
        L_LEN = 1.0
    J_DEP = max(6.0, min(L_LEN * 0.32, float(J_DEP)))

    r_hub = D_HUB / 2.0
    r_collar = min(W_NUT * 0.46, r_hub + 3.5)
    r_bore = D_BORE / 2.0
    r_in = D_IN / 2.0
    half_l = L_LEN / 2.0
    l_nut = L_LEN * 0.36
    l_col = L_LEN * 0.56

    # 外形：主体承插体 + 中间阶梯过渡环 + 大直径六角锁紧螺母环
    o_body = CYLINDER(s, R=r_hub, H=L_LEN, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_col = CYLINDER(s, R=r_collar, H=l_col, O=0.0).rotateY(90.0).translate((-l_col / 2.0, 0.0, 0.0))
    o_nut = NUT_BOLT_HEAD_6_001(s, W=W_NUT, H=l_nut).translate((-l_nut / 2.0, 0.0, 0.0))
    o_body.uniteWith(o_col)
    o_col.erase()
    o_body.uniteWith(o_nut)
    o_nut.erase()

    # 内部通流孔 + 两端承插台阶孔
    o_cut = CYLINDER(s, R=r_in, H=L_LEN + 4.0, O=0.0).rotateY(90.0).translate((-half_l - 2.0, 0.0, 0.0))
    o_sk1 = CYLINDER(s, R=r_bore, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((-half_l - 2.0, 0.0, 0.0))
    o_sk2 = CYLINDER(s, R=r_bore, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((half_l - J_DEP, 0.0, 0.0))
    o_cut.uniteWith(o_sk1)
    o_sk1.erase()
    o_cut.uniteWith(o_sk2)
    o_sk2.erase()

    o_body.subtractFrom(o_cut)
    o_cut.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_LEN', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
