# -*- coding: utf-8 -*-
# CD-ZD2010 102 三孔管夹（水平管 X 轴抱箍 + 上下夹耳 + 顶部吊销与上下夹紧螺栓螺母）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="102三孔管夹", TooltipLong="CD-ZD2010 102 三孔管夹（水平管三孔承重抱箍）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(H1=LENGTH, TooltipShort="吊孔高", TooltipLong="管道中心至顶吊孔中心高", Ask4Dist=True)
@param(H2=LENGTH, TooltipShort="紧固高", TooltipLong="管道中心至上下紧固螺栓高")
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢板宽")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹板厚")
@param(d1=LENGTH, TooltipShort="吊孔径", TooltipLong="上部吊杆销孔径")
@param(d2=LENGTH, TooltipShort="紧固孔径", TooltipLong="上下夹紧螺栓孔径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_102(s, D=133.0, H1=150.0, H2=95.0, B=60.0, T=8.0, d1=20.0, d2=16.0, ID=u"ZD_102", **kw):
    D = float(D); H1 = float(H1); H2 = float(H2); B = float(B); T = float(T); d1 = float(d1); d2 = float(d2)
    if D < 15.0: D = 15.0
    if T < 3.0: T = 3.0
    if B < 22.0: B = 22.0
    if d1 < 8.0: d1 = 8.0
    if d2 < 8.0: d2 = 8.0
    if d1 > B * 0.65: d1 = B * 0.5
    if d2 > B * 0.65: d2 = B * 0.45
    R1 = D / 2.0
    R2 = R1 + T
    if H2 <= R1 + d2 * 1.1: H2 = R1 + d2 * 1.3 + 8.0
    if H2 > R1 * 3.5 + 100.0: H2 = R1 + d2 * 1.6 + 12.0
    if H1 <= H2 + d1 * 1.5: H1 = H2 + d1 * 2.0 + 15.0
    if H1 > H2 + 300.0: H1 = H2 + d1 * 2.5 + 30.0
    gap = max(8.0, T * 1.4)

    # 1. 左右两瓣圆弧抱箍 (沿 X 轴宽 B)
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_slot = BOX(s, L=gap, W=R2 * 3.0, H=B + 6.0)
    o1.subtractFrom(o_slot); o_slot.erase()

    # 2. 上长耳板 (延伸至 +H1 + 1.4*d1) 与下短耳板 (延伸至 -H2 - 1.4*d2)
    z_top = H1 + d1 * 1.4
    z_bot = -(H2 + d2 * 1.4)
    tot_h = z_top - z_bot
    zc_ear = (z_top + z_bot) / 2.0
    for sy in (-1.0, 1.0):
        yc = sy * (gap / 2.0 + T / 2.0)
        o_ear = BOX(s, L=T, W=tot_h, H=B).translate((0.0, yc, zc_ear))
        o1.uniteWith(o_ear); o_ear.erase()
    o_in2 = CYLINDER(s, R=R1, H=B + 6.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 3.0), 0.0, 0.0))
    o1.subtractFrom(o_in2); o_in2.erase()

    # 3. 三孔贯穿 (Z = -H2, +H2, +H1) + 上下紧固螺栓螺母与顶部穿销
    span_y = gap + T * 2.0
    for zc, dh, is_pin in ((-H2, d2, False), (H2, d2, False), (H1, d1, True)):
        o_hole = CYLINDER(s, R=dh / 2.0, H=span_y + 10.0, O=0.0).rotateX(90.0).translate((0.0, (span_y + 10.0) / 2.0, zc))
        o1.subtractFrom(o_hole); o_hole.erase()
        r_sh = (dh / 2.0) * 0.85
        blen = span_y + dh * 2.2
        o_sh = CYLINDER(s, R=r_sh, H=blen, O=0.0).rotateX(90.0).translate((0.0, blen / 2.0, zc))
        o1.uniteWith(o_sh); o_sh.erase()
        if is_pin:
            # 顶部销轴两侧圆盘挡圈（贴合耳板外侧）
            for sy_n in (-1.0, 1.0):
                yn = sy_n * (span_y / 2.0) + (dh * 0.4 if sy_n > 0 else 0.0)
                o_col = CYLINDER(s, R=dh * 0.72, H=dh * 0.4, O=0.0).rotateX(90.0).translate((0.0, yn, zc))
                o1.uniteWith(o_col); o_col.erase()
        else:
            hex_s = dh * 1.5
            nut_h = dh * 0.75
            for sy_n in (-1.0, 1.0):
                yn = sy_n * (span_y / 2.0 + nut_h / 2.0)
                o_n1 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).translate((0.0, yn, zc))
                o_n2 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).rotateY(60.0).translate((0.0, yn, zc))
                o_n3 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).rotateY(120.0).translate((0.0, yn, zc))
                o_n1.intersectWith(o_n2); o_n2.erase()
                o_n1.intersectWith(o_n3); o_n3.erase()
                o1.uniteWith(o_n1); o_n1.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, 0.0), (0.0, 0.0, H1))
