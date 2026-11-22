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

@activate(Group="Support", Ports=1, TooltipShort=u"化工耳轴柱脚支撑架 (HG/T 21629 F1)", TooltipLong=u"化工行业标准 HG/T 21629-2021 F1/J9 管道耳轴柱脚支承架 (Pipe Trunnion Base Support)，含鞍形补强板、竖向耳轴支承圆管、十字四块柱脚三角形加劲肋板与四孔地脚底板", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"支吊架主要结构尺寸：管道口径、结构与型钢规格")
@param(D=LENGTH, TooltipShort=u"主管外径 OD", Ask4Dist=True, TooltipLong=u"主管外径 OD")
@param(D_TRUN=LENGTH, TooltipShort=u"耳轴支管外径", Ask4Dist=True, TooltipLong=u"耳轴支管外径")
@param(H=LENGTH, TooltipShort=u"主管中心至底板高 H", Ask4Dist=True, TooltipLong=u"主管中心至底板高 H")
@param(W_BASE=LENGTH, TooltipShort=u"方形底板边长 B", TooltipLong=u"方形底板边长 B")
@param(T_BASE=LENGTH0, TooltipShort=u"底板与肋板厚 T", TooltipLong=u"底板与肋板厚 T")
@param(ID=STRING, TooltipShort=u"支架代号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def SUPPORT_TRUNNION_BASE(s, D=168.3, D_TRUN=114.3, H=450.0, W_BASE=240.0, T_BASE=14.0, ID="F1-DN150", **kw):
    D = max(40.0, float(D))
    r_pipe = D / 2.0
    D_TRUN = max(32.0, min(D * 0.92, float(D_TRUN)))
    r_trun = D_TRUN / 2.0
    H = max(r_pipe + 140.0, float(H))
    W_BASE = max(D_TRUN + 90.0, float(W_BASE))
    t = max(8.0, float(T_BASE))

    # 1. 底部四孔方形地脚底板 (z in [-H, -H + t])
    o_sup = BOX(s, L=W_BASE, W=t, H=W_BASE).translate((0.0, 0.0, -H + t * 0.5))
    hole_off = W_BASE * 0.35
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            hc = CYLINDER(s, R=10.0, H=t + 6.0, O=0.0).translate((sx * hole_off, sy * hole_off, -H - 2.0))
            o_sup.subtractFrom(hc); hc.erase()

    # 2. 竖向耳轴支承圆管 (从底板向上延伸至主管底部马鞍口) + 主管底部弧形补强板
    h_trun = H - t - r_pipe * 0.35
    o_trun = CYLINDER(s, R=r_trun, H=h_trun, O=0.0).translate((0.0, 0.0, -H + t))
    o_sup.uniteWith(o_trun); o_trun.erase()

    # 鞍形补强板 (Reinforcing Pad wrapping bottom 120 deg of main pipe)
    l_pad = D_TRUN + 80.0
    r_pad = r_pipe + t * 0.85
    o_pad = CYLINDER(s, R=r_pad, H=l_pad, O=0.0).rotateY(90.0).translate((-l_pad * 0.5, 0.0, 0.0))
    o_cut_up = BOX(s, L=2.0 * r_pad + 20.0, W=2.0 * r_pad, H=l_pad + 10.0).translate((0.0, 0.0, r_pad * 0.65))
    o_pad.subtractFrom(o_cut_up); o_cut_up.erase()
    o_sup.uniteWith(o_pad); o_pad.erase()

    # 3. 柱脚十字对称四块加劲肋板 (Cruciform Base Gusset Ribs)
    h_gus = min(140.0, (H - r_pipe - t) * 0.52)
    w_gus = W_BASE * 0.86
    g_x = BOX(s, L=t, W=h_gus, H=w_gus).translate((0.0, 0.0, -H + t + h_gus * 0.5))
    g_y = BOX(s, L=w_gus, W=h_gus, H=t).translate((0.0, 0.0, -H + t + h_gus * 0.5))
    o_sup.uniteWith(g_x); g_x.erase()
    o_sup.uniteWith(g_y); g_y.erase()

    # 4. 挖除主管外径通道 D 与耳轴管内孔
    o_pipe_cut = CYLINDER(s, R=r_pipe, H=W_BASE + 60.0, O=0.0).rotateY(90.0).translate((-(W_BASE * 0.5 + 30.0), 0.0, 0.0))
    o_sup.subtractFrom(o_pipe_cut); o_pipe_cut.erase()
    o_trun_bore = CYLINDER(s, R=r_trun - t * 0.65, H=h_trun - 10.0, O=0.0).translate((0.0, 0.0, -H + t + 5.0))
    o_sup.subtractFrom(o_trun_bore); o_trun_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))

    s.setLinearDimension("H", (-W_BASE * 0.5, 0.0, -H), (-W_BASE * 0.5, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (-W_BASE * 0.5, -W_BASE * 0.5, -H), (W_BASE * 0.5, -W_BASE * 0.5, -H))
    s.setLinearDimension("D_TRUN", (-r_trun, 0.0, -H * 0.5), (r_trun, 0.0, -H * 0.5))
    s.setLinearDimension("D", (0.0, -r_pipe, -r_pipe), (0.0, -r_pipe, r_pipe))
