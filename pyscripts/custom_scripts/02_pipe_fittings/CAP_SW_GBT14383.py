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

@activate(Group="Cap",
          TooltipShort=u"锻钢承插焊管帽 (GB/T 14383)",
          TooltipLong=u"GB/T 14383-2021 锻钢承插焊管帽 (Class 3000)，加厚圆筒本体+平顶倒角+内部承插盲孔",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="SW")
@group("MainDimensions", TooltipLong=u"锻钢承插焊管帽主要几何参数")
@param(D_HUB=LENGTH, TooltipShort=u"管帽外径", TooltipLong=u"承插焊管帽加厚筒体外径 D_HUB (mm)")
@param(D_BORE=LENGTH, TooltipShort=u"承插孔径", TooltipLong=u"承插口内径 B (mm)")
@param(L_LEN=LENGTH, TooltipShort=u"管帽总长", TooltipLong=u"管帽端面至平顶总长度 L (mm)", Ask4Dist=True)
@param(J_DEP=LENGTH, TooltipShort=u"承插深度", TooltipLong=u"承插口深度 J (mm)")
def CAP_SW_GBT14383(
    s,
    D_HUB=48.0,
    D_BORE=33.9,
    L_LEN=38.0,
    J_DEP=12.5,
    ID=u"CAP_SW_GBT14383",
    **kw
):
    u"""锻钢承插焊管帽 (开口在 X=0, 沿 +X 轴封闭)。"""
    D_HUB = max(20.0, float(D_HUB))
    D_BORE = max(12.0, min(D_HUB - 4.0, float(D_BORE)))
    L_LEN = float(L_LEN)
    if L_LEN < 1.0:
        L_LEN = 1.0
    J_DEP = max(6.0, min(L_LEN - 6.0, float(J_DEP)))

    r_hub = D_HUB / 2.0
    r_bore = D_BORE / 2.0
    ch = min(4.5, L_LEN * 0.14)
    r_top = max(r_bore * 0.65, r_hub - ch)

    # 加厚圆筒 + 平顶倒角锥台
    o_body = CYLINDER(s, R=r_hub, H=L_LEN - ch, O=0.0).rotateY(90.0)
    o_top = CONE(s, R1=r_hub, R2=r_top, H=ch, E=0.0).rotateY(90.0).translate((L_LEN - ch, 0.0, 0.0))
    o_body.uniteWith(o_top)
    o_top.erase()

    # 承插盲孔
    o_sk = CYLINDER(s, R=r_bore, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    o_body.subtractFrom(o_sk)
    o_sk.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_LEN', (0.0, 0.0, 0.0), (L_LEN, 0.0, 0.0))
