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

@activate(Group="Support", Ports=1, TooltipShort=u"化工焊接式滑动管托 (HG/T 21629 J1)", TooltipLong=u"化工行业标准 HG/T 21629-2021 J1 焊接式滑动管托 (Welded Saddle Pipe Shoe)，含底板、纵向立板、前后横向加劲肋板与120度弧形承重鞍板", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"支吊架主要结构尺寸：管道口径、结构与型钢规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(H=LENGTH, TooltipShort=u"管中心至底板高 H", Ask4Dist=True, TooltipLong=u"管中心至底板高 H")
@param(L_SHOE=LENGTH, TooltipShort=u"管托总长 L", Ask4Dist=True, TooltipLong=u"管托总长 L")
@param(W_BASE=LENGTH, TooltipShort=u"底板宽度 B", TooltipLong=u"底板宽度 B")
@param(T_PLATE=LENGTH0, TooltipShort=u"板厚 T", TooltipLong=u"板厚 T")
@param(ID=STRING, TooltipShort=u"管托代号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def SUPPORT_SLIDING_SHOE(s, D=168.3, H=180.0, L_SHOE=300.0, W_BASE=180.0, T_PLATE=12.0, ID="J1-DN150", **kw):
    D = max(25.0, float(D))
    r_pipe = D / 2.0
    H = max(r_pipe + 45.0, float(H))
    L_SHOE = max(140.0, float(L_SHOE))
    W_BASE = max(D * 0.9, float(W_BASE))
    t = max(6.0, float(T_PLATE))

    # 1. 底板
    o_shoe = BOX(s, L=W_BASE, W=t, H=L_SHOE).translate((0.0, 0.0, -H + t * 0.5))

    # 2. 纵向中心腹板
    h_web = H - t - r_pipe * 0.5
    o_web = BOX(s, L=t, W=h_web, H=L_SHOE).translate((0.0, 0.0, -H + t + h_web * 0.5))
    o_shoe.uniteWith(o_web); o_web.erase()

    # 3. 120° 弧形承重鞍板 (Full-length 120 deg curved saddle cradle)
    r_sad = r_pipe + t
    w_sad = 2.0 * r_sad * math.sin(math.radians(60.0))
    o_sad = CYLINDER(s, R=r_sad, H=L_SHOE, O=0.0).rotateY(90.0).translate((-L_SHOE * 0.5, 0.0, 0.0))
    # 切掉 z > -r_pipe * 0.5 的上半部分，只保留底部 120° 弧形托鞍
    h_cut = r_sad + r_pipe * 0.5 + 10.0
    o_cut_top = BOX(s, L=2.0 * r_sad + 20.0, W=h_cut, H=L_SHOE + 10.0).translate((0.0, 0.0, -r_pipe * 0.5 + h_cut * 0.5))
    o_sad.subtractFrom(o_cut_top); o_cut_top.erase()
    o_shoe.uniteWith(o_sad); o_sad.erase()

    # 4. 前后两道横向梯形加劲肋板 (连接底板、腹板与弧形鞍板下缘)
    h_rib = H - t - r_pipe * 0.55
    w_rib = min(W_BASE * 0.88, w_sad)
    for sx in (-1.0, 1.0):
        xr = sx * (L_SHOE * 0.34)
        rib = BOX(s, L=w_rib, W=h_rib, H=t).translate((xr, 0.0, -H + t + h_rib * 0.5))
        o_shoe.uniteWith(rib); rib.erase()

    # 5. 挖除管道外径通道 D
    o_pipe_cut = CYLINDER(s, R=r_pipe, H=L_SHOE + 20.0, O=0.0).rotateY(90.0).translate((-(L_SHOE * 0.5 + 10.0), 0.0, 0.0))
    o_shoe.subtractFrom(o_pipe_cut); o_pipe_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))

    s.setLinearDimension("H", (-L_SHOE * 0.5, -W_BASE * 0.5, -H), (-L_SHOE * 0.5, -W_BASE * 0.5, 0.0))
    s.setLinearDimension("L_SHOE", (-L_SHOE * 0.5, -W_BASE * 0.5, -H), (L_SHOE * 0.5, -W_BASE * 0.5, -H))
    s.setLinearDimension("W_BASE", (L_SHOE * 0.5, -W_BASE * 0.5, -H), (L_SHOE * 0.5, W_BASE * 0.5, -H))
    s.setLinearDimension("D", (0.0, 0.0, -r_pipe), (0.0, 0.0, r_pipe))
