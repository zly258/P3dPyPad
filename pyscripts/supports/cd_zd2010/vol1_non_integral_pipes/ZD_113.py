# -*- coding: utf-8 -*-
# CD-ZD2010 113 夹式导向支座（在 ZD_111 基础上，底板左右两侧增加带外斜肋的导向限位轨）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="113夹式导向支座", TooltipLong="CD-ZD2010 113 夹式导向支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至支座底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="管托长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底宽 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托板厚")
@param(GW=LENGTH, TooltipShort="导向座宽", TooltipLong="导向底板总宽 A1")
@param(GH=LENGTH, TooltipShort="导向高", TooltipLong="两侧导向挡板高度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_113(s, D=219.0, SH=250.0, SL=300.0, SW=180.0, ST=10.0, GW=240.0, GH=55.0, ID=u"ZD_113", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW); GH = float(GH)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if SL < 80.0: SL = 80.0
    if SW < 60.0: SW = 60.0
    if GH < 25.0: GH = 25.0
    R1 = D / 2.0
    if SH <= R1 + ST * 3.0 + GH * 0.6: SH = R1 + ST * 3.0 + GH + 20.0
    if GW <= SW + ST * 2.5: GW = SW + ST * 4.5

    # 1. 下部双腹板箱形鞍座 + 管托滑板
    shoe_h = SH - ST * 1.3
    web_y = min(R1 * 0.65, SW * 0.34)
    o1 = BOX(s, L=SW, W=ST, H=SL * 0.85).translate((0.0, 0.0, -(shoe_h - ST / 2.0)))
    for sy in (-1.0, 1.0):
        o_w = BOX(s, L=ST, W=shoe_h - ST, H=SL * 0.84).translate((0.0, sy * web_y, -((shoe_h - ST) / 2.0)))
        o1.uniteWith(o_w); o_w.erase()

    # 2. 前后两道双耳管夹
    clamp_w = min(40.0, SL * 0.22)
    x_off = max(clamp_w * 0.75, SL * 0.30)
    ear_ext = max(24.0, ST * 2.8)
    for sx in (-1.0, 1.0):
        xc = sx * x_off
        o_c = CYLINDER(s, R=R1 + ST, H=clamp_w, O=0.0).rotateY(90.0).translate((xc - clamp_w / 2.0, 0.0, 0.0))
        o1.uniteWith(o_c); o_c.erase()
        for sy in (-1.0, 1.0):
            yc = sy * (R1 + ear_ext / 2.0)
            for sz in (-1.0, 1.0):
                o_e = BOX(s, L=ear_ext, W=ST * 0.85, H=clamp_w).translate((xc, yc, sz * (ST * 0.75)))
                o1.uniteWith(o_e); o_e.erase()

    # 3. 切除水平管道内腔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 4. 底部 416/417 型导向底板 + 左右两侧 L 形卡槽导向轨与外侧加劲肋
    base_t = ST * 1.3
    tot_gw = GW + ST * 3.0
    o_gbase = BOX(s, L=tot_gw, W=base_t, H=SL).translate((0.0, 0.0, -(SH - base_t / 2.0)))
    o1.uniteWith(o_gbase); o_gbase.erase()
    gy = SW / 2.0 + ST * 0.7
    for sy in (-1.0, 1.0):
        # 竖向导向轨立板
        o_rail = BOX(s, L=ST * 1.1, W=GH, H=SL * 0.92).translate((0.0, sy * gy, -(SH - base_t - GH / 2.0)))
        # L形向内抗拔折边
        o_lip = BOX(s, L=ST * 2.0, W=ST * 0.9, H=SL * 0.92).translate((0.0, sy * (gy - ST * 0.45), -(SH - base_t - GH + ST * 0.45)))
        o1.uniteWith(o_rail); o_rail.erase()
        o1.uniteWith(o_lip); o_lip.erase()
        # 外侧两道三角形加劲肋
        for sx in (-1.0, 1.0):
            o_rib = BOX(s, L=ST * 1.8, W=GH * 0.75, H=ST).translate((sx * (SL * 0.28), sy * (gy + ST * 1.3), -(SH - base_t - GH * 0.375)))
            o1.uniteWith(o_rib); o_rib.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
