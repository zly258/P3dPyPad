# -*- coding: utf-8 -*-
# CD-ZD2010 109 夹式管座（水平管双耳管夹 + 底部倒T形/双肋焊接支座腹板与底板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="109夹式管座", TooltipLong="CD-ZD2010 109 夹式管座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至管座底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="管座长", TooltipLong="管座沿管轴方向长度 B")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板横向宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="立板及底板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_109(s, D=159.0, SH=200.0, SL=180.0, SW=160.0, ST=10.0, ID=u"ZD_109", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if SL < 60.0: SL = 60.0
    if SW < 60.0: SW = 60.0
    R1 = D / 2.0
    if SH <= R1 + ST * 2.5: SH = R1 + ST * 3.0 + 30.0

    # 1. 水平管双螺栓抱箍 (宽 clamp_b 沿 X，两侧带水平夹耳与竖向紧固螺栓)
    clamp_b = min(SL * 0.55, max(40.0, D * 0.35))
    o1 = CYLINDER(s, R=R1 + ST, H=clamp_b, O=0.0).rotateY(90.0).translate((-(clamp_b / 2.0), 0.0, 0.0))
    ear_ext = max(28.0, ST * 3.2)
    gap = max(6.0, ST * 0.8)
    for sy in (-1.0, 1.0):
        yc = sy * (R1 + ear_ext / 2.0)
        for sz in (-1.0, 1.0):
            zc = sz * (gap / 2.0 + ST / 2.0)
            o_ear = BOX(s, L=ear_ext, W=ST, H=clamp_b).translate((0.0, yc, zc))
            o1.uniteWith(o_ear); o_ear.erase()
        o_bolt = CYLINDER(s, R=ST * 0.65, H=gap + ST * 4.0, O=0.0).translate((0.0, sy * (R1 + ear_ext * 0.55), -(gap / 2.0 + ST * 2.0)))
        o1.uniteWith(o_bolt); o_bolt.erase()

    # 2. 下部倒 T 形焊接支座 (纵向主腹板 + 中央横向加劲肋 + 水平底板)
    web_h = SH - ST
    o_web = BOX(s, L=ST, W=web_h, H=SL).translate((0.0, 0.0, -(web_h / 2.0)))
    o_rib = BOX(s, L=SW * 0.82, W=web_h - R1 * 0.4, H=ST).translate((0.0, 0.0, -(SH - ST - (web_h - R1 * 0.4) / 2.0)))
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o1.uniteWith(o_web); o_web.erase()
    o1.uniteWith(o_rib); o_rib.erase()
    o1.uniteWith(o_base); o_base.erase()

    # 3. 切除中心水平管道通孔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
