# -*- coding: utf-8 -*-
# CD-ZD2010 212 循环水管道支座（大管径宽幅弧形鞍板 + 3道纵向承重肋 + 横向肋板 + 宽底板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="212循环水管道支座", TooltipLong="CD-ZD2010 212 循环水管道支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="大口径管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至支承底面高度 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="支座长", TooltipLong="支座轴向长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板宽度 A")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_212(s, D=820.0, SH=550.0, SL=420.0, SW=420.0, ID=u"ZD_212", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW)
    if D < 200.0: D = 200.0
    if SL < 150.0: SL = 250.0
    if SW < 200.0: SW = 350.0
    R1 = D / 2.0
    ST = max(14.0, min(28.0, D * 0.022))
    if SH <= R1 + ST * 3.0: SH = R1 + ST * 4.5 + 50.0

    # 1. 大口径管道底部 120° 宽幅弧形马鞍补强板 (沿 X 轴宽 SL * 1.05)
    R_pad = R1 + ST
    pad_l = SL * 1.05
    o1 = CYLINDER(s, R=R_pad, H=pad_l, O=0.0).rotateY(90.0).translate((-(pad_l / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=pad_l + 4.0, O=0.0).rotateY(90.0).translate((-(pad_l / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    cut_h = R_pad * 2.0
    o_cut_top = BOX(s, L=R_pad * 3.0, W=cut_h, H=pad_l + 10.0).translate((0.0, 0.0, -(R1 * 0.35) + cut_h / 2.0))
    o1.subtractFrom(o_cut_top); o_cut_top.erase()

    # 2. 宽幅水平基板 (SL x SW x ST)
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o1.uniteWith(o_base); o_base.erase()

    # 3. 3 道纵向承重主肋 (中央垂直纵肋 + 左右两侧略向内倾的八字斜纵肋，严格对齐图集 212)
    web_h = SH - ST
    o_w_mid = BOX(s, L=ST, W=web_h, H=SL * 0.96).translate((0.0, 0.0, -(web_h / 2.0)))
    o1.uniteWith(o_w_mid); o_w_mid.erase()

    side_y = SW * 0.40
    for sy in (-1.0, 1.0):
        o_ws = BOX(s, L=ST, W=web_h, H=SL * 0.96).rotateX(-sy * 8.0).translate((0.0, sy * side_y, -(web_h / 2.0)))
        o1.uniteWith(o_ws); o_ws.erase()

    # 4. 中央横向贯通加劲肋板
    o_xrib = BOX(s, L=SW * 0.90, W=web_h, H=ST).translate((0.0, 0.0, -(web_h / 2.0)))
    o1.uniteWith(o_xrib); o_xrib.erase()

    # 5. 切除大口径管道外圆马鞍口与底面以下多余突出部分
    o_pipe = CYLINDER(s, R=R1, H=pad_l + 40.0, O=0.0).rotateY(90.0).translate((-(pad_l / 2.0 + 20.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()
    o_bot_trim = BOX(s, L=SW * 3.0, W=SH, H=SL * 3.0).translate((0.0, 0.0, -(SH * 1.5)))
    o1.subtractFrom(o_bot_trim); o_bot_trim.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
