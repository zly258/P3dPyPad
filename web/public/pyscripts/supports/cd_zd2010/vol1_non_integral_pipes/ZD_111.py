# -*- coding: utf-8 -*-
# CD-ZD2010 111 夹式滑动支座（水平管双耳管夹 + 下部箱形双腹板鞍座 + 带四氟滑片的滑动基板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="111夹式滑动支座", TooltipLong="CD-ZD2010 111 夹式滑动支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至支座底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="管托沿管道方向长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托板厚")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部415滑动基板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_111(s, D=219.0, SH=250.0, SL=300.0, SW=180.0, ST=10.0, HH=14.0, ID=u"ZD_111", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if SL < 80.0: SL = 80.0
    if SW < 60.0: SW = 60.0
    R1 = D / 2.0
    pad_h = max(10.0, HH if HH > 0.0 else 12.0)
    if SH <= R1 + pad_h + ST * 2.0: SH = R1 + pad_h + ST * 3.0 + 25.0

    # 1. 下部双腹板 U 形箱式鞍座 (位于 Y = ±web_y) + 管托底板
    shoe_h = SH - pad_h
    web_y = min(R1 * 0.65, SW * 0.34)
    o1 = BOX(s, L=SW, W=ST, H=SL * 0.86).translate((0.0, 0.0, -(shoe_h - ST / 2.0)))
    for sy in (-1.0, 1.0):
        o_w = BOX(s, L=ST, W=shoe_h - ST, H=SL * 0.84).translate((0.0, sy * web_y, -((shoe_h - ST) / 2.0)))
        o1.uniteWith(o_w); o_w.erase()
    # 中央横向隔板
    o_mid = BOX(s, L=web_y * 2.0, W=shoe_h - R1 * 0.5, H=ST).translate((0.0, 0.0, -(shoe_h - (shoe_h - R1 * 0.5) / 2.0)))
    o1.uniteWith(o_mid); o_mid.erase()

    # 2. 前后两道双耳抱箍 (带左右水平螺栓耳及紧固螺栓)
    clamp_w = min(42.0, SL * 0.22)
    x_off = max(clamp_w * 0.75, SL * 0.32)
    ear_ext = max(26.0, ST * 3.0)
    for sx in (-1.0, 1.0):
        xc = sx * x_off
        o_c = CYLINDER(s, R=R1 + ST, H=clamp_w, O=0.0).rotateY(90.0).translate((xc - clamp_w / 2.0, 0.0, 0.0))
        o1.uniteWith(o_c); o_c.erase()
        for sy in (-1.0, 1.0):
            yc = sy * (R1 + ear_ext / 2.0)
            for sz in (-1.0, 1.0):
                o_e = BOX(s, L=ear_ext, W=ST * 0.9, H=clamp_w).translate((xc, yc, sz * (ST * 0.8)))
                o1.uniteWith(o_e); o_e.erase()
            o_b = CYLINDER(s, R=ST * 0.55, H=ST * 4.5, O=0.0).translate((xc, sy * (R1 + ear_ext * 0.55), -(ST * 2.25)))
            o1.uniteWith(o_b); o_b.erase()

    # 3. 切除水平管道内腔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 4. 底部 415 型宽幅滑动基板 (A1 x B1 台阶底板)
    o_sub = BOX(s, L=SW * 1.22, W=pad_h * 0.7, H=SL).translate((0.0, 0.0, -(SH - pad_h * 0.35)))
    o_ptfe = BOX(s, L=SW * 1.08, W=pad_h * 0.4, H=SL * 0.92).translate((0.0, 0.0, -(SH - pad_h * 0.8)))
    o1.uniteWith(o_sub); o_sub.erase()
    o1.uniteWith(o_ptfe); o_ptfe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
