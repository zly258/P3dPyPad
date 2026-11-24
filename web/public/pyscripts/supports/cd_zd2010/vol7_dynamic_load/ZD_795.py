# -*- coding: utf-8 -*-
# CD-ZD2010 795 轴向动载管夹（抱紧管道的重型分体管夹 + 管壁防滑抗剪卡块 + 左右两侧水平伸出的双层平行梯形抗剪耳板 + 多排紧固螺栓与两端铰销）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="795轴向动载管夹", TooltipLong="CD-ZD2010 795 轴向动载管夹（防轴向水击冲击）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径OD", TooltipLong="管道外径 OD")
@param(L_clamp=LENGTH, TooltipShort="管夹总长B", TooltipLong="管夹沿管道轴向总长 B", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="跨宽C", TooltipLong="两侧销孔中心跨距 C")
@param(T=LENGTH, TooltipShort="耳板厚", TooltipLong="双层重型耳板厚度")
@param(Pin_d=LENGTH, TooltipShort="铰销径d", TooltipLong="阻尼器推力铰销孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Axial_Load_kN=LENGTH0, TooltipShort="轴向荷载", TooltipLong="许用轴向荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_795(s, D=273.0, L_clamp=440.0, B=850.0, T=18.0, Pin_d=35.0, ID=u"ZD_795", Axial_Load_kN=174.0, Weight_kg=104.82, **kw):
    D = float(D); L_clamp = float(L_clamp); B = float(B); T = float(T); Pin_d = float(Pin_d)
    if D < 50.0: D = 50.0
    if L_clamp < 160.0: L_clamp = 160.0
    if T < 8.0: T = 8.0
    if Pin_d < 15.0: Pin_d = 15.0
    if B <= D + Pin_d * 3.0 + 80.0: B = D + Pin_d * 4.0 + 160.0
    R1 = D / 2.0
    R2 = R1 + T

    # 对照图集 ZD_795_atlas.png (p.342)：
    # 1. 抱紧管道的重型分体半圆筒管夹 (沿管道 X 轴长 clamp_body_l = L_clamp * 0.55) + 管壁四周 8 块轴向抗剪卡块 (shear lugs)
    body_l = L_clamp * 0.55
    o1 = CYLINDER(s, R=R2, H=body_l, O=0.0).rotateY(90.0).translate((-(body_l / 2.0), 0.0, 0.0))

    # 管壁两端共 8 块轴向限位抗剪卡块 (45° 分布，对照 p.342 俯视图与卡块详图)
    lug_l = L_clamp * 0.22
    lug_h = T * 1.4
    lug_w = max(14.0, T * 0.8)
    for sx in (-1.0, 1.0):
        xl = sx * (body_l / 2.0 + lug_l / 2.0 - 4.0)
        for ang in (45.0, 135.0, 225.0, 315.0):
            o_klug = BOX(s, L=lug_w, W=lug_h, H=lug_l).translate((xl, 0.0, R1 + lug_h / 2.0 - 2.0)).rotateX(ang)
            o1.uniteWith(o_klug); o_klug.erase()

    # 2. 左右两侧水平伸出的双层平行梯形抗剪耳板 (Z = +wing_gap/2 与 Z = -wing_gap/2 两层平行大翼板，中间夹紧腹板与多排螺栓，对照 p.342 轴测图)
    wing_gap = max(50.0, Pin_d * 1.6)
    tot_span = B + Pin_d * 3.2
    for sz in (-1.0, 1.0):
        zw = sz * (wing_gap / 2.0 + T / 2.0)
        o_wing = BOX(s, L=tot_span, W=T, H=body_l).translate((0.0, 0.0, zw))
        # 切削四个外角形成图集标志性的梯形收口双层翼板
        cut_x = body_l * 0.35
        cut_y = (tot_span - D) * 0.35
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                o_wcut = BOX(s, L=cut_y, W=T * 3.0, H=cut_x).rotateZ(sx * sy * 24.0).translate((sx * (body_l * 0.48), sy * (tot_span * 0.42), zw))
                o_wing.subtractFrom(o_wcut); o_wcut.erase()
        o1.uniteWith(o_wing); o_wing.erase()

    # 双层翼板之间的纵向加强肋板与多排紧固螺栓群
    for sy in (-1.0, 1.0):
        y_mid = sy * (R2 + (B / 2.0 - R2) * 0.48)
        o_web = BOX(s, L=(B / 2.0 - R2) * 0.75, W=wing_gap, H=T).translate((0.0, y_mid, 0.0))
        o1.uniteWith(o_web); o_web.erase()
        # 内侧与外侧紧固螺栓排
        bolt_r = max(6.0, T * 0.38)
        bolt_h = wing_gap + T * 3.6
        for yb in (sy * (R2 + T * 1.8), sy * (B / 2.0 - Pin_d * 1.8)):
            for xb in (-body_l * 0.25, body_l * 0.25):
                o_b = CYLINDER(s, R=bolt_r, H=bolt_h, O=0.0).translate((xb, yb, -(bolt_h / 2.0)))
                o1.uniteWith(o_b); o_b.erase()

    # 3. 左右两端 (Y = ±B/2) 阻尼器铰接穿销与销孔
    pin_h = wing_gap + T * 4.2
    for sy in (-1.0, 1.0):
        yp = sy * (B / 2.0)
        o_pin = CYLINDER(s, R=Pin_d / 2.0, H=pin_h, O=0.0).translate((0.0, yp, -(pin_h / 2.0)))
        o_phead = CYLINDER(s, R=Pin_d * 0.78, H=T * 0.6, O=0.0).translate((0.0, yp, wing_gap / 2.0 + T))
        o1.uniteWith(o_pin); o_pin.erase()
        o1.uniteWith(o_phead); o_phead.erase()

    # 4. 切除中心管道通孔 ØD
    o_pipe = CYLINDER(s, R=R1, H=L_clamp * 1.5, O=0.0).rotateY(90.0).translate((-(L_clamp * 0.75), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_clamp', (-(L_clamp / 2.0), 0.0, 0.0), ((L_clamp / 2.0), 0.0, 0.0))
