# -*- coding: utf-8 -*-
# CD-ZD2010 750 销座（矩形厚钢底板 + 两片平行圆头梯形双耳立板 + 横向穿销与轴端挡圈/开口销）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="750动载销座", TooltipLong="CD-ZD2010 750 销座（动载铰接座）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(Base_L=LENGTH, TooltipShort="底板长A", TooltipLong="底板长度 A", Ask4Dist=True)
@param(Base_W=LENGTH, TooltipShort="底板宽B", TooltipLong="底板宽度 B")
@param(H=LENGTH, TooltipShort="销心高F", TooltipLong="底板底面至销轴中心高度 F")
@param(Pin_d=LENGTH, TooltipShort="销轴孔径d", TooltipLong="铰接销孔孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_750(s, Base_L=112.0, Base_W=96.0, H=62.0, Pin_d=35.0, ID=u"ZD_750", Load_kN=80.0, Weight_kg=2.94, **kw):
    Base_L = float(Base_L); Base_W = float(Base_W); H = float(H); Pin_d = float(Pin_d)
    if Pin_d < 12.0: Pin_d = 12.0
    if H < Pin_d * 1.5: H = Pin_d * 1.75
    if Base_L < H * 1.4: Base_L = H * 1.75
    if Base_W < Pin_d * 2.2: Base_W = Pin_d * 2.6

    # 对照图集 p.282 图 1：矩形厚钢底板 + 两片平行梯形收腰圆头双耳立板 + 两侧斜向加劲肋 + 横向铰接销轴与两端圆盘挡圈
    base_t = max(12.0, H * 0.22)
    ear_r = max(Pin_d * 0.95, H * 0.42)
    ear_t = max(10.0, Pin_d * 0.42)
    ear_gap = min(Base_W * 0.45, max(16.0, Pin_d * 0.95))
    h_web = H - base_t

    # 1. 矩形厚钢底板 (底面位于 Z = -H)
    o1 = BOX(s, L=Base_W, W=base_t, H=Base_L).translate((0.0, 0.0, -(H - base_t / 2.0)))

    # 2. 两片平行圆头梯形双耳立板 + 外侧三角形加劲肋 (对照 p.282 图 1 的 25° 梯形轮廓与圆头顶)
    for sy in (-1.0, 1.0):
        yc = sy * (ear_gap / 2.0 + ear_t / 2.0)
        # 梯形立板下部 + 顶部半圆柱圆头 (圆心在 Z = 0.0)
        o_plate = BOX(s, L=ear_t, W=h_web + 2.0, H=Base_L * 0.86).translate((0.0, yc, -(h_web / 2.0)))
        # 两侧 25° 斜切形成上窄下宽梯形耳板
        cut_w = Base_L * 0.55
        for sx in (-1.0, 1.0):
            o_cut = BOX(s, L=ear_t * 3.0, W=h_web * 1.6, H=cut_w).rotateY(sx * 25.0).translate((sx * (ear_r + cut_w * 0.45), yc, 0.0))
            o_plate.subtractFrom(o_cut); o_cut.erase()
        o_top_cyl = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, yc + ear_t / 2.0, 0.0))
        o_plate.uniteWith(o_top_cyl); o_top_cyl.erase()

        # 外侧斜向三角形加劲肋板
        rib_w = max(10.0, (Base_W - ear_gap - ear_t * 2.0) * 0.42)
        o_rib = BOX(s, L=rib_w, W=h_web * 0.65, H=ear_t * 0.85).translate((0.0, sy * (ear_gap / 2.0 + ear_t + rib_w / 2.0 - 1.0), -(H - base_t - h_web * 0.325)))
        o_plate.uniteWith(o_rib); o_rib.erase()
        o1.uniteWith(o_plate); o_plate.erase()

    # 3. 横向穿销与两端限位圆头挡圈/开口销孔 (位于 Z = 0.0)
    pin_l = ear_gap + ear_t * 2.0 + Pin_d * 0.8
    o_pin = CYLINDER(s, R=Pin_d / 2.0, H=pin_l, O=0.0).rotateX(90.0).translate((0.0, pin_l / 2.0, 0.0))
    o_col1 = CYLINDER(s, R=Pin_d * 0.72, H=Pin_d * 0.25, O=0.0).rotateX(90.0).translate((0.0, -(ear_gap / 2.0 + ear_t), 0.0))
    o_col2 = CYLINDER(s, R=Pin_d * 0.72, H=Pin_d * 0.25, O=0.0).rotateX(90.0).translate((0.0, (ear_gap / 2.0 + ear_t + Pin_d * 0.25), 0.0))
    o1.uniteWith(o_pin); o_pin.erase()
    o1.uniteWith(o_col1); o_col1.erase()
    o1.uniteWith(o_col2); o_col2.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('Base_L', (-(Base_L / 2.0), 0.0, -H), ((Base_L / 2.0), 0.0, -H))
