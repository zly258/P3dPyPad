# -*- coding: utf-8 -*-
# CD-ZD2010 114 单径向限位支座（水平管外包上下对称门框/双滑托限位架 + 双螺栓管夹）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="114单径向限位支座", TooltipLong="CD-ZD2010 114 单径向限位支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="总跨高", TooltipLong="上下限位滑面总高 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="支座长", TooltipLong="沿管轴方向长度 B")
@param(SW=LENGTH, TooltipShort="滑板宽", TooltipLong="上下限位滑板宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="主体钢板厚度")
@param(LW=LENGTH, TooltipShort="翼缘厚", TooltipLong="上下滑板带减摩层厚度")
@param(LH=LENGTH, TooltipShort="立柱宽", TooltipLong="门框立板宽度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_114(s, D=219.0, SH=380.0, SL=240.0, SW=180.0, ST=10.0, LW=14.0, LH=80.0, ID=u"ZD_114", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); LW = float(LW); LH = float(LH)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if LW < 6.0: LW = 6.0
    if SL < 80.0: SL = 80.0
    if SW < 60.0: SW = 60.0
    if SW > D * 2.5 + 160.0: SW = D * 1.1 + 60.0
    R1 = D / 2.0
    half_h = SH / 2.0
    if half_h <= R1 + LW + 20.0: half_h = R1 + LW + 45.0

    # 1. 水平管抱箍 + 左右两侧水平夹耳与紧固螺栓
    clamp_b = min(SL * 0.75, max(50.0, D * 0.45))
    o1 = CYLINDER(s, R=R1 + ST, H=clamp_b, O=0.0).rotateY(90.0).translate((-(clamp_b / 2.0), 0.0, 0.0))
    ear_ext = max(26.0, ST * 3.0)
    for sy in (-1.0, 1.0):
        yc = sy * (R1 + ear_ext / 2.0)
        for sz in (-1.0, 1.0):
            o_e = BOX(s, L=ear_ext, W=ST, H=clamp_b).translate((0.0, yc, sz * ST * 0.85))
            o1.uniteWith(o_e); o_e.erase()
        o_b = CYLINDER(s, R=ST * 0.55, H=ST * 4.5, O=0.0).translate((0.0, sy * (R1 + ear_ext * 0.55), -(ST * 2.25)))
        o1.uniteWith(o_b); o_b.erase()

    # 2. 上下对称箱形门框立板与顶底双滑板 (严格还原图集 114 上下双滑面单径向限位结构)
    web_y = min(R1 * 0.62, SW * 0.36)
    for sz in (-1.0, 1.0):
        # 顶/底水平限位滑板 + 减摩滑片台阶
        z_plate = sz * (half_h - LW / 2.0)
        o_pl = BOX(s, L=SW, W=LW, H=SL).translate((0.0, 0.0, z_plate))
        o1.uniteWith(o_pl); o_pl.erase()
        # 连接管夹与顶/底滑板的双侧平行箱形立腹板
        col_h = half_h - LW
        for sy in (-1.0, 1.0):
            o_col = BOX(s, L=ST, W=col_h, H=SL * 0.88).translate((0.0, sy * web_y, sz * (col_h / 2.0)))
            o1.uniteWith(o_col); o_col.erase()
        # 中央横向加劲隔板
        o_rib = BOX(s, L=web_y * 2.0, W=col_h, H=ST).translate((0.0, 0.0, sz * (col_h / 2.0)))
        o1.uniteWith(o_rib); o_rib.erase()

    # 3. 切除中心水平管道通孔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, half_h), (0.0, 0.0, -half_h))
