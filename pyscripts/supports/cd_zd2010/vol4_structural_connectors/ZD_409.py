# -*- coding: utf-8 -*-
# CD-ZD2010 409 双耳吊板（顶部水平底板 + 下部两片平行圆头吊耳板 + 横向穿销 + 两侧加强小肋）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="409双耳吊板", TooltipLong="CD-ZD2010 409 双耳吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="梁底长", TooltipLong="底座焊板长 B", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="下垂高", TooltipLong="梁底至销轴中心高度 H")
@param(B=LENGTH, TooltipShort="双耳距", TooltipLong="双耳板间距 A")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="穿销孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_409(s, L=110.0, H=90.0, B=50.0, T=12.0, d=24.0, ID=u"ZD_409", **kw):
    L = float(L); H = float(H); B = float(B); T = float(T); d = float(d)
    if d < 10.0: d = 12.0
    if T < 6.0: T = 8.0
    if B < d * 1.1: B = d * 1.6
    if L < d * 2.2: L = d * 3.0
    if H < d * 1.8: H = d * 2.6
    ear_w = min(L * 0.85, max(d * 2.1, 48.0))
    r_ear = ear_w / 2.0

    # 1. 顶部水平矩形安装底板 (宽 base_w 沿 Y，长 L 沿 X，厚 base_t 沿 Z)
    base_t = T * 1.25
    base_w = B + T * 4.2
    o1 = BOX(s, L=base_w, W=base_t, H=L).translate((0.0, 0.0, -(base_t / 2.0)))

    # 2. 下部两片平行圆头吊耳板 (位于 Y = ±(B/2 + T/2)) + 外侧加强小肋板
    for sy in (-1.0, 1.0):
        yc = sy * (B / 2.0 + T / 2.0)
        o_rect = BOX(s, L=T, W=H, H=ear_w).translate((0.0, yc, -(H / 2.0)))
        o_round = CYLINDER(s, R=r_ear, H=T, O=0.0).rotateX(90.0).translate((0.0, yc + T / 2.0, -H))
        o1.uniteWith(o_rect); o_rect.erase()
        o1.uniteWith(o_round); o_round.erase()
        # 外侧三角形加强小肋
        rib_w = T * 1.3
        o_rib = BOX(s, L=rib_w, W=H * 0.65, H=T * 0.85).translate((0.0, sy * (B / 2.0 + T + rib_w / 2.0), -(base_t + H * 0.325)))
        o1.uniteWith(o_rib); o_rib.erase()

    # 3. 横向销孔切除 + 带挡圈与开口销的横向穿销轴 (Z = -H)
    o_h = CYLINDER(s, R=d / 2.0, H=base_w + 20.0, O=0.0).rotateX(90.0).translate((0.0, (base_w + 20.0) / 2.0, -H))
    o1.subtractFrom(o_h); o_h.erase()

    pin_len = B + T * 2.0 + d * 1.4
    o_pin = CYLINDER(s, R=(d / 2.0) * 0.9, H=pin_len, O=0.0).rotateX(90.0).translate((0.0, pin_len / 2.0, -H))
    o_phead = CYLINDER(s, R=d * 0.78, H=d * 0.35, O=0.0).rotateX(90.0).translate((0.0, -(B / 2.0 + T + d * 0.1), -H))
    o_cot = CYLINDER(s, R=d * 0.15, H=d * 2.1, O=0.0).translate((0.0, B / 2.0 + T + d * 0.35, -(H + d * 1.05)))
    o1.uniteWith(o_pin); o_pin.erase()
    o1.uniteWith(o_phead); o_phead.erase()
    o1.uniteWith(o_cot); o_cot.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, -H))
