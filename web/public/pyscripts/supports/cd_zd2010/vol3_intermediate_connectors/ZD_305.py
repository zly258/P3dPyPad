# -*- coding: utf-8 -*-
# CD-ZD2010 305 拉杆（已合并 305~308：两端带锥面倒角与螺纹段退刀槽特征的圆柱拉杆）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="305拉杆", TooltipLong="CD-ZD2010 305~308 螺纹拉杆", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(Thread_d=LENGTH, TooltipShort="杆径", TooltipLong="拉杆公称螺纹外径 D")
@param(L_total=LENGTH, TooltipShort="总长", TooltipLong="拉杆总长度 L", Ask4Dist=True)
@param(Thread_L=LENGTH, TooltipShort="丝长", TooltipLong="两端螺纹加工段长度 L0")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_305(s, Thread_d=20.0, L_total=750.0, Thread_L=100.0, ID=u"ZD_305", **kw):
    Thread_d = float(Thread_d); L_total = float(L_total); Thread_L = float(Thread_L)
    if Thread_d < 8.0: Thread_d = 8.0
    if L_total < Thread_d * 5.0: L_total = Thread_d * 10.0
    th_l = min(max(Thread_d * 1.5, Thread_L), L_total * 0.38)
    r_rod = Thread_d / 2.0
    r_th = r_rod * 0.86
    cham = max(2.0, r_rod * 0.25)
    groove_h = max(3.0, r_rod * 0.35)

    # 1. 两端螺纹小径段 + 端头圆锥倒角 (CONE)
    o1 = CYLINDER(s, R=r_th, H=L_total - 2.0 * cham, O=0.0).translate((0.0, 0.0, -(L_total - cham)))
    o_c_top = CONE(s, R1=r_th, R2=r_th * 0.65, H=cham, E=0.0).translate((0.0, 0.0, -cham))
    o_c_bot = CONE(s, R1=r_th * 0.65, R2=r_th, H=cham, E=0.0).translate((0.0, 0.0, -L_total))
    o1.uniteWith(o_c_top); o_c_top.erase()
    o1.uniteWith(o_c_bot); o_c_bot.erase()

    # 2. 中部大径光杆段 (两端在 Z = -th_l 与 Z = -(L_total - th_l) 处留出退刀槽台阶)
    mid_h = L_total - 2.0 * (th_l + groove_h)
    if mid_h > 4.0:
        o_mid = CYLINDER(s, R=r_rod, H=mid_h, O=0.0).translate((0.0, 0.0, -(L_total - th_l - groove_h)))
        o1.uniteWith(o_mid); o_mid.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_total', (0.0, 0.0, 0.0), (0.0, 0.0, -L_total))
