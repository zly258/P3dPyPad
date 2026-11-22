# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"深冷保冷外包钢箍管道吊架",
    TooltipLong=u"化工低温乙烯/液氨/冷媒架空管线用高密度PIR隔冷吊架 (LH1 型，符合 HG/T 21629，含全圆高密度保冷瓦壳、防潮止水端环、外包上下对夹钢抱箍、顶部双耳吊板、花兰松紧螺套吊杆与生根顶板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"低温被吊管道外径 (mm)")
@param(T_INS=LENGTH, TooltipShort=u"保冷层厚度", TooltipLong=u"高密度PIR保冷管托瓦块厚度 (mm)")
@param(H=LENGTH, TooltipShort=u"吊点总高", TooltipLong=u"管道中心至顶部钢梁生根板顶面的总高 (mm)")
@param(L=LENGTH, TooltipShort=u"保冷瓦长度", TooltipLong=u"保冷瓦块轴向总长度 (mm)")
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"螺纹吊杆与花兰螺套公称直径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支吊架编号", TooltipLong=u"深冷保冷管道吊架型号编码")
def SUPPORT_INSULATED_HANGER(s, D=168.3, T_INS=80.0, H=620.0, L=300.0, ROD_D=20.0, ID=u"LH1-DN150-80", **kw):
    D = max(25.0, float(D))
    T_INS = max(40.0, float(T_INS))
    r_pipe = D / 2.0
    r_ins = r_pipe + T_INS
    H = max(r_ins + 240.0, float(H))
    L = max(180.0, float(L))
    ROD_D = max(12.0, float(ROD_D))

    r_rod = ROD_D / 2.0
    t_band = 10.0
    r_band = r_ins + t_band

    # 1. 高密度 PIR 保冷瓦筒 + 两端防潮止水台阶环 + 外包对夹钢护箍与两侧紧固螺栓耳
    o_m = CYLINDER(s, R=r_ins, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    for sx in (-1.0, 1.0):
        vb = CYLINDER(s, R=r_ins + 4.0, H=16.0, O=0.0).rotateY(90.0).translate((sx * (L * 0.5 - 12.0) - 8.0, 0.0, 0.0))
        o_m.uniteWith(vb); vb.erase()

    l_band = L * 0.72
    o_band = CYLINDER(s, R=r_band, H=l_band, O=0.0).rotateY(90.0).translate((-l_band * 0.5, 0.0, 0.0))
    o_ears = BOX(s, L=r_band * 2.35, W=32.0, H=l_band).translate((0.0, 0.0, 0.0))
    o_m.uniteWith(o_band); o_band.erase()
    o_m.uniteWith(o_ears); o_ears.erase()

    # 2. 钢护箍顶部双耳吊环 + 销轴 + 竖直吊杆 + 花兰调节螺套 + 顶部四孔生根底板
    z_pin = r_band + 38.0
    o_lug = BOX(s, L=ROD_D * 2.5, W=65.0, H=l_band * 0.48).translate((0.0, 0.0, r_band + 22.0))
    o_pin = CYLINDER(s, R=r_rod, H=l_band * 0.62, O=0.0).rotateY(90.0).translate((-l_band * 0.31, 0.0, z_pin))
    h_rod = H - z_pin
    o_rod = CYLINDER(s, R=r_rod, H=h_rod, O=0.0).translate((0.0, 0.0, z_pin))
    o_tb = CYLINDER(s, R=r_rod * 1.75, H=min(100.0, h_rod * 0.36), O=0.0).translate((0.0, 0.0, z_pin + h_rod * 0.35))
    o_top_pl = BOX(s, L=140.0, W=14.0, H=140.0).translate((0.0, 0.0, H - 7.0))
    o_top_gus = BOX(s, L=50.0, W=55.0, H=14.0).translate((0.0, 0.0, H - 34.0))
    for p in (o_lug, o_pin, o_rod, o_tb, o_top_pl, o_top_gus):
        o_m.uniteWith(p); p.erase()

    # 切除管道通孔
    o_cut = CYLINDER(s, R=r_pipe, H=L + 30.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("L", (-L / 2.0, 0.0, 0.0), (L / 2.0, 0.0, 0.0))
