# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="THD",
    Ports="1",
    TooltipShort=u"化工隔膜耐震压力表",
    TooltipLong=u"化工工艺管线径向直接安装耐震压力表总成 (Y-100BF / HG/T 20507，含下部过程连接螺纹接头、六角隔膜连接座、针型截止考克阀与手柄、散热缓冲颈、阶梯压盖表圈、凹入玻璃度盘与倾斜指针)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_DIAL=LENGTH, TooltipShort=u"表盘外径", TooltipLong=u"压力表圆形表壳外径 (mm)")
@param(T_CASE=LENGTH, TooltipShort=u"表壳厚度", TooltipLong=u"压力表圆盘表壳前后厚度 (mm)")
@param(H_STEM=LENGTH, TooltipShort=u"连接杆长", TooltipLong=u"过程接口端面至表壳底部的高度 (mm)")
@param(D_STEM=LENGTH, TooltipShort=u"街头外径", TooltipLong=u"下部螺纹接头与考克杆外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"工业压力表型号规格编码")
def INSTRUMENT_PRESSURE_GAUGE(s, D_DIAL=104.0, T_CASE=38.0, H_STEM=65.0, D_STEM=22.0, ID=u"PI-101-Y100", **kw):
    D_DIAL = max(60.0, float(D_DIAL))
    T_CASE = max(24.0, float(T_CASE))
    H_STEM = max(42.0, float(H_STEM))
    D_STEM = max(14.0, float(D_STEM))

    r_dial = D_DIAL / 2.0
    r_stem = D_STEM / 2.0
    z_c = H_STEM + r_dial

    # 1. 下部螺纹接头 + 六角扳手座 + 截止考克阀体与红色一字手柄 + 上部连接颈
    o_m = CYLINDER(s, R=r_stem * 0.72, H=H_STEM + 12.0, O=0.0)
    o_hex1 = BOX(s, L=D_STEM * 1.45, W=14.0, H=D_STEM * 1.45).translate((0.0, 0.0, 14.0))
    o_cock = BOX(s, L=D_STEM * 1.55, W=22.0, H=D_STEM * 1.55).translate((0.0, 0.0, H_STEM * 0.52))
    o_hndl = BOX(s, L=12.0, W=10.0, H=48.0).translate((26.0, 0.0, H_STEM * 0.52))
    o_hex2 = BOX(s, L=D_STEM * 1.35, W=12.0, H=D_STEM * 1.35).translate((0.0, 0.0, H_STEM - 8.0))
    for p in (o_hex1, o_cock, o_hndl, o_hex2):
        o_m.uniteWith(p); p.erase()

    # 2. 圆形不锈钢表壳 + 前侧卡口压盖表圈 + 凹入表盘视窗 + 倾斜指针 + 背部防爆泄压塞
    o_case = CYLINDER(s, R=r_dial * 0.95, H=T_CASE * 0.75, O=0.0).rotateX(90.0).translate((0.0, T_CASE * 0.5, z_c))
    o_bezel = CYLINDER(s, R=r_dial, H=T_CASE * 0.35, O=0.0).rotateX(90.0).translate((0.0, -T_CASE * 0.15, z_c))
    o_m.uniteWith(o_case); o_case.erase()
    o_m.uniteWith(o_bezel); o_bezel.erase()

    rec_d = T_CASE * 0.16
    o_rec = CYLINDER(s, R=r_dial * 0.84, H=rec_d + 2.0, O=0.0).rotateX(90.0).translate((0.0, -T_CASE * 0.5 + rec_d, z_c))
    o_m.subtractFrom(o_rec); o_rec.erase()

    o_pin = CYLINDER(s, R=6.5, H=6.0, O=0.0).rotateX(90.0).translate((0.0, -T_CASE * 0.5 + rec_d + 2.0, z_c))
    o_ptr = BOX(s, L=5.0, W=r_dial * 0.68, H=4.0).translate((0.0, 0.0, r_dial * 0.24)).rotateY(-38.0).translate((0.0, -T_CASE * 0.5 + rec_d - 1.0, z_c))
    o_back = CYLINDER(s, R=12.0, H=8.0, O=0.0).rotateX(-90.0).translate((0.0, T_CASE * 0.5 - 2.0, z_c + r_dial * 0.35))
    for p in (o_pin, o_ptr, o_back):
        o_m.uniteWith(p); p.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("D_DIAL", (-r_dial, 0.0, z_c), (r_dial, 0.0, z_c))
    s.setLinearDimension("H_STEM", (0.0, 0.0, 0.0), (0.0, 0.0, H_STEM))
