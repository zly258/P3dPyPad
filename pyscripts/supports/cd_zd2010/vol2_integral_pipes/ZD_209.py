# -*- coding: utf-8 -*-
# CD-ZD2010 209 加强焊接管座（水平管底部弧形鞍板 + 双平行纵向腹板 + 横向封板 + 底板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="209加强焊接管座", TooltipLong="CD-ZD2010 209 加强焊接管座（U形双腹板箱式管座）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底面高度 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="管座长", TooltipLong="管座沿管轴方向长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="立板及底板厚度")
@param(Rib_T=LENGTH, TooltipShort="筋厚", TooltipLong="横向加强封板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_209(s, D=273.0, SH=295.0, SL=240.0, SW=180.0, ST=12.0, Rib_T=10.0, ID=u"ZD_209", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); Rib_T = float(Rib_T)
    if D < 30.0: D = 30.0
    if ST < 5.0: ST = 5.0
    if ST > 24.0: ST = 12.0
    if Rib_T < 5.0: Rib_T = 8.0
    if SL < 68.0: SL = 120.0
    if SL > 1200.0: SL = 240.0
    if SW < 68.0: SW = 120.0
    R1 = D / 2.0
    if SH <= R1 + ST * 2.5: SH = R1 + ST * 3.5 + 35.0

    # 1. 水平管底部弧形鞍板 (长 SL 沿 X，外径 R1+ST)
    R_pad = R1 + ST
    o1 = CYLINDER(s, R=R_pad, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    cut_h = R_pad * 2.0
    o_cut_top = BOX(s, L=R_pad * 3.0, W=cut_h, H=SL + 10.0).translate((0.0, 0.0, -(R1 * 0.25) + cut_h / 2.0))
    o1.subtractFrom(o_cut_top); o_cut_top.erase()

    # 2. 双平行纵向腹板 (位于 Y = ±web_y，构成图集 209 典型 U 形槽式双腹板座) + 底部水平基板
    web_y = min(R1 * 0.72, (SW - ST) / 2.0)
    web_h = SH - ST
    for sy in (-1.0, 1.0):
        o_w = BOX(s, L=ST, W=web_h, H=SL).translate((0.0, sy * web_y, -(web_h / 2.0)))
        o1.uniteWith(o_w); o_w.erase()
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o1.uniteWith(o_base); o_base.erase()

    # 3. 内部横向加劲隔板 (Rib_T)
    o_rib = BOX(s, L=web_y * 2.0, W=web_h, H=Rib_T).translate((0.0, 0.0, -(web_h / 2.0)))
    o1.uniteWith(o_rib); o_rib.erase()

    # 4. 切除水平管道圆弧内腔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
