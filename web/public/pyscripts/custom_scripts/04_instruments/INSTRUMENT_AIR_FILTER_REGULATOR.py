# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"气动仪表风过滤减压阀组",
    TooltipLong=u"化工现场气动阀门/仪表供气支路双联空气过滤减压阀组站 (AFR-Set，符合 HG/T 20510，含进出气螺纹/法兰接头、入口球阀、带排污杯空气过滤减压器、顶部调压旋钮、压力表与安装背板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"供气管外径", TooltipLong=u"仪表空气进出气支管外径 (mm)")
@param(L=LENGTH, TooltipShort=u"阀组总长", TooltipLong=u"进出气端口间距 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"上部调压钮高", TooltipLong=u"管线中心至顶部调压手轮顶部的高度 (mm)")
@param(H_BOWL=LENGTH, TooltipShort=u"下部滤杯深", TooltipLong=u"管线中心至底部自动排水阀口的深度 (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"减压阀体宽", TooltipLong=u"过滤减压器圆柱腔体直径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"仪表风过滤减压阀组型号编码")
def INSTRUMENT_AIR_FILTER_REGULATOR(s, D=21.3, L=175.0, H_TOP=135.0, H_BOWL=145.0, D_BODY=72.0, ID=u"AFR-119-DN15", **kw):
    D = max(12.0, float(D))
    L = max(130.0, float(L))
    H_TOP = max(95.0, float(H_TOP))
    H_BOWL = max(100.0, float(H_BOWL))
    D_BODY = max(52.0, float(D_BODY))

    r_pipe = D / 2.0
    r_body = D_BODY / 2.0

    # 1. 水平仪表风连接管 + 入口球阀块 (-X 侧) + 中心过滤减压方体阀座 + 后部 L 型安装支架
    o_m = CYLINDER(s, R=r_pipe * 1.15, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_hex_l = BOX(s, L=34.0, W=34.0, H=24.0).translate((-L * 0.5 + 12.0, 0.0, 0.0))
    o_hex_r = BOX(s, L=34.0, W=34.0, H=24.0).translate((L * 0.5 - 12.0, 0.0, 0.0))
    o_bvalve = BOX(s, L=42.0, W=44.0, H=46.0).translate((-L * 0.24, 0.0, 0.0))
    o_blever = BOX(s, L=12.0, W=8.0, H=65.0).translate((-L * 0.24 + 22.0, 0.0, 32.0))
    o_main_blk = BOX(s, L=D_BODY, W=54.0, H=D_BODY).translate((L * 0.10, 0.0, 0.0))
    o_brk = BOX(s, L=12.0, W=110.0, H=D_BODY * 1.25).translate((L * 0.10, D_BODY * 0.56, 20.0))
    for p in (o_hex_l, o_hex_r, o_bvalve, o_blever, o_main_blk, o_brk):
        o_m.uniteWith(p); p.erase()

    # 2. 上部调压弹簧钟罩 + 顶部调压旋钮 (+Z) + 下部金属带视窗储水滤杯与排污考克 (-Z)
    xc = L * 0.10
    o_bon = CONE(s, R1=r_body * 0.88, R2=r_body * 0.58, H=H_TOP - 45.0, E=0.0).translate((xc, 0.0, 22.0))
    o_knob = CYLINDER(s, R=r_body * 0.65, H=28.0, O=0.0).translate((xc, 0.0, H_TOP - 28.0))
    o_bowl = CYLINDER(s, R=r_body * 0.84, H=H_BOWL - 42.0, O=0.0).translate((xc, 0.0, -(H_BOWL - 22.0)))
    o_drain = CONE(s, R1=12.0, R2=22.0, H=26.0, E=0.0).translate((xc, 0.0, -H_BOWL))
    for p in (o_bon, o_knob, o_bowl, o_drain):
        o_m.uniteWith(p); p.erase()

    # 3. 前侧输出压力表小圆盘 (-Y 侧)
    o_gn = CYLINDER(s, R=8.0, H=28.0, O=0.0).rotateX(90.0).translate((xc, -r_body * 0.5, 0.0))
    o_gdial = CYLINDER(s, R=30.0, H=22.0, O=0.0).rotateX(90.0).translate((xc, -(r_body * 0.5 + 18.0), 0.0))
    o_m.uniteWith(o_gn); o_gn.erase()
    o_m.uniteWith(o_gdial); o_gdial.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -H_BOWL), (L / 2.0, 0.0, -H_BOWL))
    s.setLinearDimension("H_TOP", (xc, 0.0, 0.0), (xc, 0.0, H_TOP))
    s.setLinearDimension("H_BOWL", (xc, 0.0, -H_BOWL), (xc, 0.0, 0.0))
