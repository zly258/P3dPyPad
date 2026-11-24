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

@activate(Group="Reducer", Ports=2, TooltipShort=u"同心对焊大小头 (GB/T 12459)", TooltipLong=u"化工标准 GB/T 12459 同心对焊异径管 (Concentric Reducer)，带两端直管段、锥形过渡段与中空内腔", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"管件主要结构尺寸：口径、中心距与壁厚")
@param(D1=LENGTH, TooltipShort=u"大端外径 OD1", Ask4Dist=True, TooltipLong=u"大端外径 OD1")
@param(D2=LENGTH, TooltipShort=u"小端外径 OD2", Ask4Dist=True, TooltipLong=u"小端外径 OD2")
@param(H=LENGTH, TooltipShort=u"异径管总长 H", Ask4Dist=True, TooltipLong=u"异径管总长 H")
@param(THK=LENGTH0, TooltipShort=u"壁厚 T", TooltipLong=u"壁厚 T")
@param(ID=STRING, TooltipShort=u"件号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def REDUCER_CONCENTRIC(s, D1=168.3, D2=114.3, H=140.0, THK=7.1, ID="RED-150x100", **kw):
    D1 = max(25.0, float(D1))
    D2 = max(15.0, min(D1 * 0.92, float(D2)))
    H = max(40.0, float(H))
    THK = max(2.5, min(D2 * 0.25, float(THK)))

    r1 = D1 / 2.0
    r2 = D2 / 2.0
    tl1 = H * 0.18
    tl2 = H * 0.16
    h_cone = H - tl1 - tl2

    # 沿 +X 轴从 x=0 (大端 D1) 到 x=H (小端 D2)
    o_body = CYLINDER(s, R=r1, H=tl1, O=0.0).rotateY(90.0)
    o_cone = CONE(s, R1=r1, R2=r2, H=h_cone, E=0.0).rotateY(90.0).translate((tl1, 0.0, 0.0))
    o_body.uniteWith(o_cone); o_cone.erase()
    o_s = CYLINDER(s, R=r2, H=tl2, O=0.0).rotateY(90.0).translate((tl1 + h_cone, 0.0, 0.0))
    o_body.uniteWith(o_s); o_s.erase()

    # 贯通内流道
    ri1 = max(4.0, r1 - THK)
    ri2 = max(3.0, r2 - THK * 0.85)
    o_bore = CYLINDER(s, R=ri1, H=tl1 + 4.0, O=0.0).rotateY(90.0).translate((-3.0, 0.0, 0.0))
    o_bcone = CONE(s, R1=ri1, R2=ri2, H=h_cone, E=0.0).rotateY(90.0).translate((tl1, 0.0, 0.0))
    o_bore.uniteWith(o_bcone); o_bcone.erase()
    o_bs = CYLINDER(s, R=ri2, H=tl2 + 4.0, O=0.0).rotateY(90.0).translate((tl1 + h_cone - 1.0, 0.0, 0.0))
    o_bore.uniteWith(o_bs); o_bs.erase()

    o_body.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("H", (0.0, 0.0, -r1), (H, 0.0, -r1))
    s.setLinearDimension("D1", (0.0, -r1, 0.0), (0.0, r1, 0.0))
    s.setLinearDimension("D2", (H, -r2, 0.0), (H, r2, 0.0))
