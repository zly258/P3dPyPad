# -*- coding: utf-8 -*-
# CD-ZD2010 208 焊接管座（水平管底部弧形鞍板 + 纵向主腹板 + 横向加劲肋 + 底板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="208焊接管座", TooltipLong="CD-ZD2010 208 焊接管座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="管座长", TooltipLong="管座沿管道方向长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="腹板及底板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_208(s, D=159.0, SH=190.0, SL=180.0, SW=120.0, ST=10.0, ID=u"ZD_208", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if ST > 24.0: ST = 12.0
    if SL < 60.0: SL = 60.0
    if SW < 50.0: SW = 50.0
    R1 = D / 2.0
    if SH <= R1 + ST * 2.5: SH = R1 + ST * 3.5 + 25.0

    # 1. 水平管底部 120° 弧形马鞍垫板 (长 SL 沿 X，贴合管底 Z <= -R1*0.35)
    R_pad = R1 + ST
    o1 = CYLINDER(s, R=R_pad, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    cut_h = R_pad * 2.0
    o_cut_top = BOX(s, L=R_pad * 3.0, W=cut_h, H=SL + 10.0).translate((0.0, 0.0, -(R1 * 0.35) + cut_h / 2.0))
    o1.subtractFrom(o_cut_top); o_cut_top.erase()

    # 2. 纵向主腹板 + 中央横向加劲肋板 + 底部水平基板
    web_h = SH - ST
    o_web = BOX(s, L=ST, W=web_h, H=SL).translate((0.0, 0.0, -(web_h / 2.0)))
    o_rib = BOX(s, L=SW * 0.88, W=web_h - R1 * 0.45, H=ST).translate((0.0, 0.0, -(SH - ST - (web_h - R1 * 0.45) / 2.0)))
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o1.uniteWith(o_web); o_web.erase()
    o1.uniteWith(o_rib); o_rib.erase()
    o1.uniteWith(o_base); o_base.erase()

    # 3. 切除管道外径圆弧
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
