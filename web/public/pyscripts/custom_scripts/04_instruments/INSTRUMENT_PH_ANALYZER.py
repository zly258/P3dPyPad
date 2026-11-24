# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="1",
    TooltipShort=u"在线pH电导率水质分析仪",
    TooltipLong=u"化工酸碱中和池/循环水/反应釜沉入式在线 pH/ORP/电导率分析电极护套与智能变送器总成 (符合 HG/T 20507，含安装法兰、顶部方形数字分析仪、冲洗接线腔、浸入护管与底部电极防撞保护笼)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(FL_OD=LENGTH, TooltipShort=u"安装法兰径", TooltipLong=u"分析仪浸入护套安装法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"安装法兰厚度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"分析仪高度", TooltipLong=u"法兰底面至顶部四线制智能分析仪顶部的高度 (mm)")
@param(L_IMM=LENGTH, TooltipShort=u"护套插入深", TooltipLong=u"法兰底面以下电极护管及底部防护笼插入深度 (mm)")
@param(W_XMTR=LENGTH, TooltipShort=u"变送器箱宽", TooltipLong=u"上部方形智能分析仪外壳边宽 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"安装法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"在线pH水质分析仪位号编码")
def INSTRUMENT_PH_ANALYZER(s, FL_OD=165.0, FL_T=20.0, H_TOP=285.0, L_IMM=320.0, W_XMTR=144.0, NBOLTS=4, ID=u"AT-118-PH", **kw):
    FL_OD = max(100.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H_TOP = max(200.0, float(H_TOP))
    L_IMM = max(160.0, float(L_IMM))
    W_XMTR = max(105.0, float(W_XMTR))
    NBOLTS = max(4, int(NBOLTS))

    r_fl = FL_OD / 2.0

    # 1. 安装法兰 (底面 Z=0, Port 1 朝向 -Z) + 螺栓孔
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    r_bcd = r_fl * 0.74
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=8.0, H=FL_T + 4.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 上部电极提拉锁紧卡箍 + 立柱 + 方形大屏数字 pH 变送器表箱與遮阳帽
    z_box_c = H_TOP - W_XMTR * 0.52
    o_clamp = CYLINDER(s, R=36.0, H=48.0, O=0.0).translate((0.0, 0.0, FL_T))
    o_post = CYLINDER(s, R=20.0, H=z_box_c - FL_T, O=0.0).translate((0.0, 0.0, FL_T))
    o_box = BOX(s, L=110.0, W=W_XMTR, H=W_XMTR).translate((0.0, 0.0, z_box_c))
    o_win = BOX(s, L=14.0, W=W_XMTR * 0.58, H=W_XMTR * 0.72).translate((0.0, -58.0, z_box_c + 12.0))
    o_hood = BOX(s, L=135.0, W=10.0, H=W_XMTR * 1.12).translate((0.0, -8.0, H_TOP - 5.0))
    for p in (o_clamp, o_post, o_box, o_win, o_hood):
        o_m.uniteWith(p); p.erase()

    # 3. 下部耐腐蚀 PVDF/316L 电极浸入护管 + 底部开窗防撞电极保护笼 (Z: [-L_IMM, 0])
    o_tube = CYLINDER(s, R=24.0, H=L_IMM - 55.0, O=0.0).translate((0.0, 0.0, -(L_IMM - 55.0) + 4.0))
    o_cage_top = CYLINDER(s, R=30.0, H=16.0, O=0.0).translate((0.0, 0.0, -(L_IMM - 45.0)))
    o_cage_bot = CYLINDER(s, R=30.0, H=14.0, O=0.0).translate((0.0, 0.0, -L_IMM))
    o_probe = CYLINDER(s, R=10.0, H=48.0, O=0.0).translate((0.0, 0.0, -(L_IMM - 10.0)))
    for p in (o_tube, o_cage_top, o_cage_bot, o_probe):
        o_m.uniteWith(p); p.erase()

    for k in range(4):
        ang = math.radians(90.0 * k + 45.0)
        bar = CYLINDER(s, R=4.5, H=50.0, O=0.0).translate((23.0 * math.cos(ang), 23.0 * math.sin(ang), -L_IMM + 6.0))
        o_m.uniteWith(bar); bar.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension("L_IMM", (0.0, 0.0, -L_IMM), (0.0, 0.0, 0.0))
    s.setLinearDimension("W_XMTR", (-W_XMTR / 2.0, 0.0, z_box_c), (W_XMTR / 2.0, 0.0, z_box_c))
