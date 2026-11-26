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
          TooltipShort=u"锻钢六角丝堵 Hex Plug",
          TooltipLong=u"GB/T 14383 / ASME B16.11 锻钢六角头管塞丝堵，含外螺纹柱体与六角扳手头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="THM")
@group("MainDimensions", TooltipLong=u"六角丝堵主要几何参数")
@param(D_OUT=LENGTH, TooltipShort=u"外螺纹大径", TooltipLong=u"丝堵外螺纹柱体直径 D_OUT (mm)")
@param(W_HEX=LENGTH, TooltipShort=u"六角对边宽", TooltipLong=u"六角头对边宽度 W_HEX (mm)")
@param(L_BODY=LENGTH, TooltipShort=u"柱体长度", TooltipLong=u"外螺纹柱体长度 L_BODY (mm)", Ask4Dist=True)
@param(H_HEX=LENGTH, TooltipShort=u"六角头厚度", TooltipLong=u"六角扳手头厚度 H_HEX (mm)")
def PLUG_HEX_TH(
    s,
    D_OUT=33.4,
    W_HEX=36.0,
    L_BODY=20.0,
    H_HEX=11.0,
    ID=u"PLUG_HEX_TH",
    **kw
):
    u"""锻钢六角丝堵 (柱体沿 [0, L_BODY], 六角头沿 [L_BODY, L_BODY+H_HEX])。"""
    D_OUT = max(12.0, float(D_OUT))
    W_HEX = max(D_OUT + 1.5, float(W_HEX))
    L_BODY = float(L_BODY)
    if L_BODY < 1.0:
        L_BODY = 1.0
    H_HEX = float(H_HEX)
    if H_HEX < 1.0:
        H_HEX = 1.0

    r_out = D_OUT / 2.0
    ch = min(2.0, L_BODY * 0.12)
    l_tot = L_BODY + H_HEX

    o_ch = CONE(s, R1=max(3.0, r_out - 1.8), R2=r_out, H=ch, E=0.0).rotateY(90.0)
    o_cyl = CYLINDER(s, R=r_out, H=L_BODY - ch + 1.0, O=0.0).rotateY(90.0).translate((ch, 0.0, 0.0))
    o_hex = NUT_BOLT_HEAD_6_001(s, W=W_HEX, H=H_HEX).translate((L_BODY, 0.0, 0.0))
    o_ch.uniteWith(o_cyl)
    o_cyl.erase()
    o_ch.uniteWith(o_hex)
    o_hex.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_BODY', (0.0, 0.0, 0.0), (L_BODY, 0.0, 0.0))
    s.setLinearDimension('H_HEX', (L_BODY, 0.0, 0.0), (l_tot, 0.0, 0.0))
