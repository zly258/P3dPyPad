# -*- coding: utf-8 -*-
# CD-ZD2010 115 双径向限位支座（水平管外包十字四向放射滑托限位框 + 45°分型抱箍）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="115双径向限位支座", TooltipLong="CD-ZD2010 115 双径向限位支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(SH=LENGTH, TooltipShort="限位跨高", TooltipLong="四向限位滑面总跨距 H", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="支座长", TooltipLong="沿管轴方向长度 B")
@param(SW=LENGTH, TooltipShort="滑板宽", TooltipLong="四向滑板宽度 A")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="主体钢板厚度")
@param(LW=LENGTH, TooltipShort="滑板厚", TooltipLong="外端限位滑板厚度")
@param(LH=LENGTH, TooltipShort="支臂宽", TooltipLong="径向支臂宽度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_115(s, D=273.0, SH=460.0, SL=260.0, SW=160.0, ST=12.0, LW=14.0, LH=80.0, ID=u"ZD_115", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); LW = float(LW); LH = float(LH)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 4.0
    if LW < 6.0: LW = 6.0
    if SL < 80.0: SL = 80.0
    if SW < 50.0: SW = 50.0
    if SW > D * 1.5 + 80.0: SW = D * 0.75 + 40.0
    R1 = D / 2.0
    half_h = SH / 2.0
    if half_h <= R1 + LW + 35.0: half_h = R1 + LW + 65.0

    # 1. 中心管夹抱箍环 + 45° 斜向分型夹耳 (与图集 115 完全一致)
    clamp_b = min(SL * 0.65, max(50.0, D * 0.4))
    o1 = CYLINDER(s, R=R1 + ST, H=clamp_b, O=0.0).rotateY(90.0).translate((-(clamp_b / 2.0), 0.0, 0.0))
    ear_r = R1 + ST * 3.2
    for ang in (45.0, -135.0):
        o_ear = BOX(s, L=ST * 3.5, W=ST * 2.4, H=clamp_b).translate((0.0, ear_r * 0.85, 0.0)).rotateX(ang)
        o1.uniteWith(o_ear); o_ear.erase()

    # 2. 上、下、左、右 4 组正交十字径向限位支臂与外端滑板 (0°, 90°, 180°, 270°)
    arm_h = half_h - LW
    web_span = min(R1 * 0.48, SW * 0.32)
    for deg in (0.0, 90.0, 180.0, 270.0):
        # 端头滑板 (在 +Z 处构建后绕 X 轴旋转 deg)
        o_shoe = BOX(s, L=SW, W=LW, H=SL).translate((0.0, 0.0, half_h - LW / 2.0)).rotateX(deg)
        o1.uniteWith(o_shoe); o_shoe.erase()
        # 双平行径向支臂腹板
        for sy in (-1.0, 1.0):
            o_arm = BOX(s, L=ST, W=arm_h, H=SL * 0.82).translate((0.0, sy * web_span, arm_h / 2.0)).rotateX(deg)
            o1.uniteWith(o_arm); o_arm.erase()
        # 径向支臂中肋
        o_rib = BOX(s, L=web_span * 2.0, W=arm_h, H=ST).translate((0.0, 0.0, arm_h / 2.0)).rotateX(deg)
        o1.uniteWith(o_rib); o_rib.erase()

    # 3. 切除中心水平管道通孔
    o_pipe = CYLINDER(s, R=R1, H=SL + 20.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, half_h), (0.0, 0.0, -half_h))
