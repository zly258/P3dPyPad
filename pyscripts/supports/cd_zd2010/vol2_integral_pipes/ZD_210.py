# -*- coding: utf-8 -*-
# CD-ZD2010 210 焊接固定支座（水平管底部双腹板鞍座 + 前后斜向止推筋板 + 带地脚螺栓孔的底板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="210焊接固定支座", TooltipLong="CD-ZD2010 210 焊接固定支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="固定高", TooltipLong="管心至底面高度 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="支座长", TooltipLong="支座底板长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="底板宽度")
@param(ST=LENGTH, TooltipShort="底厚", TooltipLong="底板厚度")
@param(Fix_T=LENGTH, TooltipShort="肋板厚", TooltipLong="止推加劲肋板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_210(s, D=273.0, SH=320.0, SL=420.0, SW=320.0, ST=18.0, Fix_T=14.0, ID=u"ZD_210", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); Fix_T = float(Fix_T)
    if D < 25.0: D = 25.0
    if ST < 8.0: ST = 8.0
    if Fix_T < 6.0: Fix_T = 6.0
    R1 = D / 2.0
    if SH <= R1 + ST * 2.5: SH = R1 + ST * 3.5 + 45.0
    if SL < D * 1.2 + 80.0: SL = D * 1.3 + 100.0
    if SW < D * 0.9 + 60.0: SW = D * 1.1 + 80.0

    # 1. 底部厚重固定基板 (SL x SW x ST)
    o1 = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))

    # 2. 中部双腹板箱式立柱鞍座 + 圆管支腿内核
    core_l = SL * 0.48
    web_y = min(R1 * 0.68, SW * 0.28)
    web_h = SH - ST
    for sy in (-1.0, 1.0):
        o_w = BOX(s, L=Fix_T, W=web_h, H=core_l).translate((0.0, sy * web_y, -(web_h / 2.0)))
        o1.uniteWith(o_w); o_w.erase()
    # 顶部贴合弧形补强鞍板
    o_pad = CYLINDER(s, R=R1 + Fix_T, H=core_l * 1.15, O=0.0).rotateY(90.0).translate((-(core_l * 0.575), 0.0, 0.0))
    o_pad_cut = BOX(s, L=(R1 + Fix_T) * 3.0, W=(R1 + Fix_T) * 2.0, H=core_l * 1.3).translate((0.0, 0.0, R1 + Fix_T))
    o_pad.subtractFrom(o_pad_cut); o_pad_cut.erase()
    o1.uniteWith(o_pad); o_pad.erase()

    # 3. 前后 (±X) 与左右 (±Y) 斜向三角形止推筋板
    gus_h = web_h - R1 * 0.35
    for sx in (-1.0, 1.0):
        # 顺管向前后斜撑止推肋
        gus_l = (SL * 0.92 - core_l) / 2.0
        xc = sx * (core_l / 2.0 + gus_l / 2.0)
        o_gx = BOX(s, L=Fix_T, W=gus_h, H=gus_l).translate((xc, 0.0, -(SH - ST - gus_h / 2.0)))
        ang_x = degrees(atan2(gus_l * 0.85, gus_h))
        o_cx = BOX(s, L=Fix_T * 4.0, W=gus_h * 2.0, H=gus_l * 2.0).translate((sx * gus_l, 0.0, 0.0)).rotateY(-sx * ang_x).translate((xc, 0.0, -(SH - ST - gus_h * 0.5)))
        o_gx.subtractFrom(o_cx); o_cx.erase()
        o1.uniteWith(o_gx); o_gx.erase()

    for sy in (-1.0, 1.0):
        # 横向侧止推斜肋
        gus_w = (SW * 0.92 - web_y * 2.0) / 2.0
        yc = sy * (web_y + gus_w / 2.0)
        o_gy = BOX(s, L=gus_w, W=gus_h, H=Fix_T).translate((0.0, yc, -(SH - ST - gus_h / 2.0)))
        o1.uniteWith(o_gy); o_gy.erase()

    # 4. 切除水平管道圆弧马鞍口 + 底板四角地脚螺栓通孔
    o_pipe = CYLINDER(s, R=R1, H=SL + 40.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 20.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    bolt_r = max(9.0, min(18.0, ST * 0.65))
    hx = SL * 0.38
    hy = SW * 0.36
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_bh = CYLINDER(s, R=bolt_r, H=ST * 4.0, O=0.0).translate((sx * hx, sy * hy, -(SH + ST)))
            o1.subtractFrom(o_bh); o_bh.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
