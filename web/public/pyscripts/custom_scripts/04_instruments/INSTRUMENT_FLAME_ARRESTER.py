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

@activate(Group="Instrument", Ports=2, TooltipShort=u"管道波纹板爆轰阻火器 (GZW-I / GB/T 13347)", TooltipLong=u"化工安全标准 GB/T 13347 / HG/T 20570 管道爆轰型波纹板法兰阻火器 (In-Line Deflagration/Detonation Flame Arrester)，含两端连接法兰、对称渐扩圆锥壳、中部大直径双法兰夹持波纹阻火芯盘与环周长拉杆螺柱", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"管道阻火器主要结构尺寸：总装长度、中部阻火芯盘外径与芯盘厚")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"总装长度 L", Ask4Dist=True, TooltipLong=u"两端连接法兰端面总长 L")
@param(D_CORE=LENGTH, TooltipShort=u"阻火盘外径", Ask4Dist=True, TooltipLong=u"中部波纹阻火芯盘夹持大法兰外径")
@param(L_CORE=LENGTH, TooltipShort=u"阻火芯总厚", TooltipLong=u"中部双夹持法兰与阻火芯盘总长")
@param(FL_OD=LENGTH, TooltipShort=u"连接法兰径", TooltipLong=u"两端管道连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端连接法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"两端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"阻火器位号", TooltipLong=u"安装位号，如 FA-101")
def INSTRUMENT_FLAME_ARRESTER(s, D=114.3, L=380.0, D_CORE=340.0, L_CORE=130.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"GZW-I-DN100", **kw):
    D = max(25.0, float(D))
    L = max(240.0, float(L))
    D_CORE = max(D * 2.3, float(D_CORE))
    L_CORE = max(85.0, min(L * 0.45, float(L_CORE)))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_core = D_CORE / 2.0
    r_fl = FL_OD / 2.0

    # 1. 两端连接法兰 + 对称渐扩圆锥过渡壳 + 中部波纹阻火芯盘双大法兰
    o_m = CYLINDER(s, R=r_pipe * 1.08, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    len_cone = (L - L_CORE) * 0.5 - FL_T
    r_cbody = r_core * 0.76
    c_l = CONE(s, R1=r_pipe * 1.12, R2=r_cbody, H=len_cone + 6.0, E=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    c_r = CONE(s, R1=r_cbody, R2=r_pipe * 1.12, H=len_cone + 6.0, E=0.0).rotateY(90.0).translate((L_CORE * 0.5 - 6.0, 0.0, 0.0))
    o_m.uniteWith(c_l); c_l.erase()
    o_m.uniteWith(c_r); c_r.erase()

    # 中部阻火芯环与两侧夹持大法兰 + 8根周向长穿心螺柱与顶部起吊耳
    t_cfl = L_CORE * 0.30
    o_elem = CYLINDER(s, R=r_cbody * 1.04, H=L_CORE, O=0.0).rotateY(90.0).translate((-L_CORE * 0.5, 0.0, 0.0))
    cfl_1 = CYLINDER(s, R=r_core, H=t_cfl, O=0.0).rotateY(90.0).translate((-L_CORE * 0.5, 0.0, 0.0))
    cfl_2 = CYLINDER(s, R=r_core, H=t_cfl, O=0.0).rotateY(90.0).translate((L_CORE * 0.5 - t_cfl, 0.0, 0.0))
    for p in (o_elem, cfl_1, cfl_2):
        o_m.uniteWith(p); p.erase()

    r_cbcd = (r_cbody + r_core) * 0.52
    for k in range(8):
        ang = math.radians(k * 45.0 + 22.5)
        st = CYLINDER(s, R=max(6.5, D * 0.06), H=L_CORE + 24.0, O=0.0).rotateY(90.0).translate((-(L_CORE * 0.5 + 12.0), r_cbcd * math.cos(ang), r_cbcd * math.sin(ang)))
        o_m.uniteWith(st); st.erase()

    o_lug = BOX(s, L=16.0, W=48.0, H=55.0).translate((0.0, 0.0, r_core + 18.0))
    o_m.uniteWith(o_lug); o_lug.erase()

    # 2. 两端接管流道孔与法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()
    # 重新并入中心阻火盘芯网格圆柱
    o_mesh = CYLINDER(s, R=r_bore * 1.05, H=L_CORE * 0.36, O=0.0).rotateY(90.0).translate((-L_CORE * 0.18, 0.0, 0.0))
    o_m.uniteWith(o_mesh); o_mesh.erase()

    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_m.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - 4.0, by, bz))
        o_m.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_core), (L / 2.0, 0.0, -r_core))
    s.setLinearDimension("D_CORE", (0.0, -r_core, -r_core), (0.0, r_core, -r_core))
