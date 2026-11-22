# -*- coding: utf-8 -*-
# FLANGE_WN: 带颈对焊法兰（WN 法兰，突面 RF）
# 几何特征：法兰盘 + 突面密封台 + 锥形高颈过渡段 + 全贯通内孔。
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *


@activate(Group="Flange", TooltipShort=u"带颈对焊法兰 WN", TooltipLong=u"带颈对焊法兰（WN/RF，突面密封，锥形高颈过渡，全贯通内孔）", LengthUnit="mm", Ports=2)
@group("MainDimensions", TooltipLong=u"法兰主要几何尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"与法兰对焊的管道外径 OD")
@param(L=LENGTH, TooltipShort=u"法兰总长", TooltipLong=u"密封面到对焊端的轴向总长度", Ask4Dist=True)
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(THK=LENGTH0, TooltipShort=u"管道壁厚", TooltipLong=u"对焊端管道壁厚，决定贯通内孔")
@param(ID=STRING, TooltipShort=u"构件位号", TooltipLong=u"法兰规格标识，如 WN-DN100")
def FLANGE_WN(s, D=114.3, L=100.0, FL_OD=220.0, FL_T=20.0, THK=6.0, ID=u"FLANGE-WN-DN100", **kw):
    D = float(D)
    L = float(L)
    FL_OD = float(FL_OD)
    FL_T = float(FL_T)
    THK = float(THK)

    r_pipe = D / 2.0
    if FL_OD <= D * 1.25:
        FL_OD = D * 1.9
    if FL_T <= 4.0:
        FL_T = max(12.0, D * 0.18)
    if THK <= 0.0 or THK >= r_pipe * 0.7:
        THK = max(3.0, r_pipe * 0.11)
    if L <= FL_T + 10.0:
        L = FL_T + max(25.0, D * 0.5)

    r_flange = FL_OD / 2.0
    r_bore = max(2.0, r_pipe - THK)
    rf_t = max(2.0, FL_T * 0.12)
    rf_r = min(r_flange * 0.82, r_flange - max(6.0, FL_T * 0.45))
    hub_r = max(r_pipe + THK, r_flange * 0.46)
    hub_len = max(10.0, L - FL_T)

    # 1. 法兰盘（密封面位于 X=0，向 +X 延伸 FL_T）
    o_disc = CYLINDER(s, R=r_flange, H=FL_T, O=0.0).rotateY(90.0)

    # 2. 突面密封台（向 -X 突出 rf_t）
    o_rf = CYLINDER(s, R=rf_r, H=rf_t, O=0.0).rotateY(90.0).translate((-rf_t, 0.0, 0.0))
    o_disc.uniteWith(o_rf)
    o_rf.erase()

    # 3. 锥形高颈：根部 hub_r 过渡到对焊端管道外径 r_pipe
    o_hub = CONE(s, R1=hub_r, R2=r_pipe, H=hub_len, E=0.0).rotateY(90.0).translate((FL_T, 0.0, 0.0))
    o_disc.uniteWith(o_hub)
    o_hub.erase()

    # 4. 全贯通内孔
    o_bore = CYLINDER(s, R=r_bore, H=L + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(rf_t + 3.0), 0.0, 0.0))
    o_disc.subtractFrom(o_bore)
    o_bore.erase()

    # 5. 端口：密封面中心 + 对焊端中心
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("L", (0.0, 0.0, -r_flange), (L, 0.0, -r_flange))
    s.setLinearDimension("FL_OD", (L, 0.0, -r_flange), (L, 0.0, r_flange))
    s.setLinearDimension("D", (L, 0.0, 0.0), (L, 0.0, r_pipe))
