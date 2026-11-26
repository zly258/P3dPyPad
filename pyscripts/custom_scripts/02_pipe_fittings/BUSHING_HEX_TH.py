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
from varmain.divsub.cnut6_001 import *

@activate(Group="Reducer",
          TooltipShort=u"锻钢六角内外丝补芯 Hex Bushing",
          TooltipLong=u"GB/T 14383 / ASME B16.11 锻钢六角内外螺纹补芯，含外螺纹柱体、六角扳手头台阶与贯通内螺纹孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="THM")
@group("MainDimensions", TooltipLong=u"六角补芯主要几何参数")
@param(D1=LENGTH, TooltipShort=u"外螺纹大径", TooltipLong=u"外螺纹主体外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"内螺纹孔径", TooltipLong=u"内螺纹公称孔径 D2 (mm)")
@param(D_IN=LENGTH, TooltipShort=u"通流内径", TooltipLong=u"小端通流内径 D_IN (mm)")
@param(W_HEX=LENGTH, TooltipShort=u"六角对边宽", TooltipLong=u"六角扳手面对边宽度 W_HEX (mm)")
@param(L_BODY=LENGTH, TooltipShort=u"外丝柱体长", TooltipLong=u"外螺纹柱体段长度 L_BODY (mm)", Ask4Dist=True)
@param(H_HEX=LENGTH, TooltipShort=u"六角头厚度", TooltipLong=u"六角头台阶厚度 H_HEX (mm)")
def BUSHING_HEX_TH(
    s,
    D1=33.4,
    D2=21.3,
    D_IN=15.8,
    W_HEX=36.0,
    L_BODY=20.0,
    H_HEX=8.0,
    ID=u"BUSHING_HEX_TH",
    **kw
):
    u"""锻钢六角内外丝补芯 (外丝柱体沿 [0, L_BODY], 六角头沿 [L_BODY, L_BODY+H_HEX])。"""
    D1 = max(16.0, float(D1))
    D2 = max(10.0, min(D1 - 4.0, float(D2)))
    D_IN = max(6.0, min(D2 - 1.5, float(D_IN)))
    W_HEX = max(D1 + 2.0, float(W_HEX))
    L_BODY = float(L_BODY)
    if L_BODY < 1.0:
        L_BODY = 1.0
    H_HEX = float(H_HEX)
    if H_HEX < 1.0:
        H_HEX = 1.0

    r1 = D1 / 2.0
    r2 = D2 / 2.0
    r_in = D_IN / 2.0
    ch = min(2.0, L_BODY * 0.12)
    l_tot = L_BODY + H_HEX

    # 外螺纹柱体（带前端小倒角）+ 六角扳手头台阶
    o_ch = CONE(s, R1=max(r2 + 1.0, r1 - 1.5), R2=r1, H=ch, E=0.0).rotateY(90.0)
    o_cyl = CYLINDER(s, R=r1, H=L_BODY - ch + 1.0, O=0.0).rotateY(90.0).translate((ch, 0.0, 0.0))
    o_hex = NUT_BOLT_HEAD_6_001(s, W=W_HEX, H=H_HEX).translate((L_BODY, 0.0, 0.0))
    o_ch.uniteWith(o_cyl)
    o_cyl.erase()
    o_ch.uniteWith(o_hex)
    o_hex.erase()

    # 内部贯通流道 + 小端内螺纹台阶孔
    o_cut = CYLINDER(s, R=r_in, H=l_tot + 4.0, O=0.0).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    j_th = min(l_tot - 4.0, max(H_HEX + 4.0, l_tot * 0.62))
    o_th = CYLINDER(s, R=r2, H=j_th + 2.0, O=0.0).rotateY(90.0).translate((l_tot - j_th, 0.0, 0.0))
    o_cut.uniteWith(o_th)
    o_th.erase()

    o_ch.subtractFrom(o_cut)
    o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((l_tot, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_BODY', (0.0, 0.0, 0.0), (L_BODY, 0.0, 0.0))
    s.setLinearDimension('H_HEX', (L_BODY, 0.0, 0.0), (l_tot, 0.0, 0.0))
