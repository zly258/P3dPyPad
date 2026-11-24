# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *

@activate(Group="Tee", Ports=3, TooltipShort=u"对焊等径/异径三通 (GB/T 12459)", TooltipLong=u"化工标准 GB/T 12459 / ASME B16.9 锻制对焊三通，带三端坡口、拔制过渡圆领与T形贯通内腔", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"管件主要结构尺寸：口径、中心距与壁厚")
@param(D=LENGTH, TooltipShort=u"主管外径 OD", Ask4Dist=True, TooltipLong=u"主管外径 OD")
@param(D_B=LENGTH, TooltipShort=u"支管外径 OD_B", TooltipLong=u"支管外径 OD_B")
@param(C=LENGTH, TooltipShort=u"主管中心至端面距 C", TooltipLong=u"主管中心至端面距 C")
@param(M=LENGTH, TooltipShort=u"主管中心至支管端面距 M", TooltipLong=u"主管中心至支管端面距 M")
@param(THK=LENGTH0, TooltipShort=u"壁厚 T", TooltipLong=u"壁厚 T")
@param(ID=STRING, TooltipShort=u"件号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def TEE_EQUAL(s, D=114.3, D_B=114.3, C=105.0, M=105.0, THK=6.0, ID="TEE-DN100", **kw):
    D = max(20.0, float(D))
    D_B = max(15.0, min(D, float(D_B) if float(D_B) > 0 else D))
    C = max(D * 0.65, float(C))
    M = max(D * 0.65, float(M))
    THK = max(2.5, min(D * 0.25, float(THK)))

    r_main = D / 2.0
    r_br = D_B / 2.0
    r_in_main = max(4.0, r_main - THK)
    r_in_br = max(3.0, r_br - THK * 0.9)
    bev = min(3.0, THK * 0.45)

    # 1. 主管筒体 (沿 X 轴 [-C, +C])
    L_main = 2.0 * (C - bev)
    o_body = CYLINDER(s, R=r_main, H=L_main, O=0.0).rotateY(90.0).translate((-L_main / 2.0, 0.0, 0.0))
    b_l = CONE(s, R1=r_main, R2=r_main - bev * 0.6, H=bev, E=0.0).rotateY(-90.0).translate((-(C - bev), 0.0, 0.0))
    o_body.uniteWith(b_l); b_l.erase()
    b_r = CONE(s, R1=r_main, R2=r_main - bev * 0.6, H=bev, E=0.0).rotateY(90.0).translate((C - bev, 0.0, 0.0))
    o_body.uniteWith(b_r); b_r.erase()

    # 2. 中部锻造三通拔制过渡肩圈 + 支管筒体 (沿 +Z 轴 [0, M])
    o_collar = CONE(s, R1=r_br + THK * 1.3, R2=r_br, H=r_main * 0.45, E=0.0).translate((0.0, 0.0, r_main * 0.65))
    o_body.uniteWith(o_collar); o_collar.erase()

    o_br = CYLINDER(s, R=r_br, H=M - bev, O=0.0).translate((0.0, 0.0, 0.0))
    o_body.uniteWith(o_br); o_br.erase()
    b_t = CONE(s, R1=r_br, R2=r_br - bev * 0.6, H=bev, E=0.0).translate((0.0, 0.0, M - bev))
    o_body.uniteWith(b_t); b_t.erase()

    # 3. T 形贯通内流道
    o_bore = CYLINDER(s, R=r_in_main, H=2.0 * C + 10.0, O=0.0).rotateY(90.0).translate((-(C + 5.0), 0.0, 0.0))
    o_bore_br = CYLINDER(s, R=r_in_br, H=M + 6.0, O=0.0).translate((0.0, 0.0, 0.0))
    o_bore.uniteWith(o_bore_br); o_bore_br.erase()
    o_body.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-C, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, M), (0.0, 0.0, 1.0))

    s.setLinearDimension("C", (-C, 0.0, -r_main), (0.0, 0.0, -r_main))
    s.setLinearDimension("M", (-r_main, 0.0, 0.0), (-r_main, 0.0, M))
    s.setLinearDimension("D", (C, -r_main, 0.0), (C, r_main, 0.0))
