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
import math

@activate(Group="Valve", Ports=1, TooltipShort=u"储罐防爆阻火呼吸阀 (ZFQ-1 / SY/T 0511.1)", TooltipLong=u"化工行业标准 SY/T 0511.1 / HG/T 20570 储罐顶装全天候防爆阻火呼吸阀 (Tank Flame-Arresting Breather Valve)，含罐顶安装法兰、波纹阻火芯盘腔及左右正负压双腔防雨帽", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阻火呼吸阀主要结构尺寸：接管口径、总高与正负压双罩跨距")
@param(D=LENGTH, TooltipShort=u"接管外径 D", Ask4Dist=True, TooltipLong=u"底部接管公称外径 OD")
@param(H=LENGTH, TooltipShort=u"呼吸阀总高 H", Ask4Dist=True, TooltipLong=u"底部法兰面至顶部防雨帽总高 H")
@param(SPAN_HOOD=LENGTH, TooltipShort=u"双腔总宽", Ask4Dist=True, TooltipLong=u"正压呼出腔与负压吸入腔总跨宽")
@param(D_HOOD=LENGTH, TooltipShort=u"单罩外径", TooltipLong=u"防雨帽伞罩外径")
@param(FL_OD=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"底部安装法兰外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"底部安装法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"底部法兰螺栓孔数量")
@param(ID=STRING, TooltipShort=u"呼吸阀位号", TooltipLong=u"安装位号，如 PVV-101")
def VALVE_BREATHER(s, D=114.3, H=380.0, SPAN_HOOD=360.0, D_HOOD=175.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"ZFQ-1-DN100", **kw):
    D = max(40.0, float(D))
    H = max(240.0, float(H))
    SPAN_HOOD = max(D * 2.4, float(SPAN_HOOD))
    D_HOOD = max(D * 1.25, float(D_HOOD))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_fl = FL_OD / 2.0
    r_hood = D_HOOD / 2.0

    # 1. 底部安装法兰 (位于 z=0，法向朝下 (0,0,-1)) + 竖直主立管 + 波纹阻火盘夹持大法兰环
    o_v = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    h_trunk = H * 0.58
    o_trunk = CYLINDER(s, R=r_pipe, H=h_trunk, O=0.0)
    o_v.uniteWith(o_trunk); o_trunk.erase()

    z_arr = H * 0.28
    o_arr = CYLINDER(s, R=r_pipe * 1.48, H=42.0, O=0.0).translate((0.0, 0.0, z_arr))
    o_v.uniteWith(o_arr); o_arr.erase()

    # 2. 横向分流扁箱 + 左右不对称高度的正压呼出筒与负压吸入筒 + 伞形防雨帽
    w_span = SPAN_HOOD - D_HOOD
    z_manifold = H * 0.52
    o_man = BOX(s, L=D_HOOD * 0.72, W=r_pipe * 1.35, H=w_span + D_HOOD * 0.5).translate((0.0, 0.0, z_manifold))
    o_v.uniteWith(o_man); o_man.erase()

    for sx, z_top_c in ((-1.0, H - 10.0), (1.0, H * 0.84)):
        xc = sx * (w_span * 0.5)
        h_ch = z_top_c - (z_manifold - r_pipe * 0.5)
        ch = CYLINDER(s, R=r_hood * 0.78, H=h_ch, O=0.0).translate((xc, 0.0, z_manifold - r_pipe * 0.5))
        cap = CONE(s, R1=r_hood, R2=r_hood * 0.22, H=28.0, E=0.0).translate((xc, 0.0, z_top_c - 18.0))
        o_v.uniteWith(ch); ch.erase()
        o_v.uniteWith(cap); cap.erase()

    # 3. 底部接管内孔与法兰螺栓孔
    o_bore = CYLINDER(s, R=r_pipe * 0.85, H=h_trunk * 0.85, O=0.0).translate((0.0, 0.0, -2.0))
    o_v.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(12.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=r_hole, H=FL_T + 6.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_v.subtractFrom(bh); bh.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (-SPAN_HOOD * 0.5, 0.0, 0.0), (-SPAN_HOOD * 0.5, 0.0, H))
    s.setLinearDimension("SPAN_HOOD", (-SPAN_HOOD * 0.5, 0.0, H), (SPAN_HOOD * 0.5, 0.0, H))
