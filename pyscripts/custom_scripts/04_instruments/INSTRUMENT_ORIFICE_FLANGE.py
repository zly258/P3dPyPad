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

@activate(Group="Instrument", Ports=2, TooltipShort=u"环室孔板流量计总成 (LG / HG/T 20507)", TooltipLong=u"化工行业标准 ISO 5167 / HG/T 20507 一体化环室标准孔板流量计配三阀组与智能差压变送器总成 (Orifice Plate Flowmeter with 3-Valve Manifold & DP Transmitter)，含对焊取压孔板法兰、节流孔板铭牌柄、双导压立管、三阀组与顶部差压变送器", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"孔板流量计主要结构尺寸：安装长、孔板法兰外径与顶部差压变送器高")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"被测管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"总装长度 L", Ask4Dist=True, TooltipLong=u"两端取压孔板法兰端面总长 L")
@param(FL_OD=LENGTH, TooltipShort=u"孔板法兰径", Ask4Dist=True, TooltipLong=u"加厚孔板法兰外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"单法兰厚", TooltipLong=u"单侧孔板法兰盘厚度")
@param(H_XMTR=LENGTH, TooltipShort=u"中心至变送器高", Ask4Dist=True, TooltipLong=u"管道中心至顶部差压变送器总高")
@param(W_XMTR=LENGTH, TooltipShort=u"变送器宽", TooltipLong=u"顶部差压变送器与三阀组总宽")
@param(NBOLTS=INT, TooltipShort=u"夹紧螺柱数", TooltipLong=u"孔板法兰圆周夹紧长螺柱数量")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 FE/FT-105")
def INSTRUMENT_ORIFICE_FLANGE(s, D=114.3, L=160.0, FL_OD=230.0, FL_T=32.0, H_XMTR=380.0, W_XMTR=145.0, NBOLTS=8, ID=u"FE-105-DN100", **kw):
    D = max(25.0, float(D))
    L = max(110.0, float(L))
    FL_OD = max(D + 65.0, float(FL_OD))
    FL_T = max(22.0, float(FL_T))
    H_XMTR = max(FL_OD * 0.5 + 160.0, float(H_XMTR))
    W_XMTR = max(110.0, float(W_XMTR))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0

    # 1. 左右高颈对焊孔板法兰 + 中央环室与孔板垫片环 + 斜向 45° 孔板信息铭牌手柄
    o_m = CYLINDER(s, R=r_pipe * 1.15, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    t_ring = 24.0
    o_ring = CYLINDER(s, R=r_fl * 0.76, H=t_ring + 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(t_ring * 0.5 + FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-(t_ring * 0.5 + FL_T), 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((t_ring * 0.5, 0.0, 0.0))
    for p in (o_ring, fl_l, fl_r):
        o_m.uniteWith(p); p.erase()

    # 孔板外伸标识手柄 (Paddle Handle at -Y)
    o_pad = BOX(s, L=110.0, W=32.0, H=6.0).translate((0.0, -(r_fl * 0.72 + 50.0), 0.0))
    o_m.uniteWith(o_pad); o_pad.erase()

    # 孔板法兰周向夹紧螺柱
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.68
    len_stud = t_ring + 2.0 * FL_T + 24.0
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        st = CYLINDER(s, R=max(6.0, D * 0.06), H=len_stud, O=0.0).rotateY(90.0).translate((-len_stud * 0.5, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
        o_m.uniteWith(st); st.erase()

    # 2. 正负压双引压导压立管 + 三阀组阀块 + 顶部智能差压变送器表头
    z_man = H_XMTR - 115.0
    for sx in (-1.0, 1.0):
        xt = sx * (t_ring * 0.5 + FL_T * 0.45)
        imp = CYLINDER(s, R=9.0, H=z_man - r_fl * 0.6, O=0.0).translate((xt, 0.0, r_fl * 0.6))
        o_m.uniteWith(imp); imp.erase()

    o_man = BOX(s, L=75.0, W=55.0, H=t_ring + 2.0 * FL_T + 30.0).translate((0.0, 0.0, z_man))
    o_m.uniteWith(o_man); o_man.erase()

    z_xmtr = H_XMTR - 52.0
    o_xneck = CYLINDER(s, R=24.0, H=65.0, O=0.0).translate((0.0, 0.0, z_man))
    o_xhead = CYLINDER(s, R=52.0, H=W_XMTR, O=0.0).rotateX(90.0).translate((0.0, W_XMTR * 0.5, z_xmtr))
    o_m.uniteWith(o_xneck); o_xneck.erase()
    o_m.uniteWith(o_xhead); o_xhead.erase()

    # 3. 切除管道流道并留出中心标准节流孔板环 (孔径 d = 0.62 * D)
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()
    o_orifice = CYLINDER(s, R=r_pipe * 1.02, H=5.0, O=r_bore * 0.62).rotateY(90.0).translate((-2.5, 0.0, 0.0))
    o_m.uniteWith(o_orifice); o_orifice.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H_XMTR", (-r_fl, 0.0, 0.0), (-r_fl, 0.0, H_XMTR))
    s.setLinearDimension("FL_OD", (0.0, -r_fl, -r_fl), (0.0, r_fl, -r_fl))
