# -*- coding: utf-8 -*-
# CD-ZD2010 792 横担式动载管夹（中心重型管道抱箍与鞍式支承立板 + 下部横向重型双工字钢/槽钢横担大梁 + 横担梁左右两端顶面各焊一组双耳销座）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="792横担动载管夹", TooltipLong="CD-ZD2010 792 横担式动载管夹", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径OD", TooltipLong="管道外径 OD")
@param(L_beam=LENGTH, TooltipShort="横担长C", TooltipLong="横担梁总长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="截面高", TooltipLong="横担型钢高度")
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="横担型钢翼缘宽")
@param(Pin_d=LENGTH, TooltipShort="销孔径d", TooltipLong="两端阻尼器销座孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_792(s, D=219.0, L_beam=900.0, H=140.0, B=60.0, Pin_d=35.0, ID=u"ZD_792", Load_kN=80.0, Weight_kg=58.5, **kw):
    D = float(D); L_beam = float(L_beam); H = float(H); B = float(B); Pin_d = float(Pin_d)
    if D < 50.0: D = 50.0
    if H < 80.0: H = 80.0
    if B < 40.0: B = 40.0
    if Pin_d < 15.0: Pin_d = 15.0
    R1 = D / 2.0
    if L_beam <= D + 260.0: L_beam = D + 360.0

    # 对照图集 ZD_792_atlas.png (p.313)：
    # 1. 中心重型管道双抱箍 + 下部鞍式立板支座 (管道中心在 (0,0,0)，横担大梁顶面位于管道下方 z_beam_top = -(R1 + saddle_h))
    clamp_t = max(12.0, R1 * 0.12)
    clamp_w = B * 2.2
    saddle_h = max(45.0, R1 * 0.38)
    z_beam_top = -(R1 + saddle_h)
    z_beam_mid = z_beam_top - H / 2.0

    o1 = CYLINDER(s, R=R1 + clamp_t, H=clamp_w, O=0.0).rotateY(90.0).translate((-(clamp_w / 2.0), 0.0, 0.0))
    # 管夹水平紧固耳与鞍座支承立板
    o_cflange = BOX(s, L=(R1 + clamp_t * 3.5) * 2.0, W=clamp_t * 1.8, H=clamp_w).translate((0.0, 0.0, 0.0))
    o_saddle = BOX(s, L=R1 * 1.5, W=R1 + saddle_h, H=clamp_w * 0.85).translate((0.0, 0.0, -(R1 + saddle_h) / 2.0))
    o1.uniteWith(o_cflange); o_cflange.erase()
    o1.uniteWith(o_saddle); o_saddle.erase()
    o_pipe = CYLINDER(s, R=R1, H=clamp_w + 20.0, O=0.0).rotateY(90.0).translate((-(clamp_w / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 2. 下部横向重型双槽钢/工字钢横担大梁 (沿 Y 轴跨度 L_beam，前后两根并列型钢 + 端部封板与腹板加劲肋)
    beam_gap = max(24.0, B * 0.4)
    tf = max(8.0, H * 0.08)
    tw = max(6.0, B * 0.12)
    for sx in (-1.0, 1.0):
        xb = sx * (beam_gap / 2.0 + B / 2.0)
        o_bm = BOX(s, L=L_beam, W=H, H=B).translate((xb, 0.0, z_beam_mid))
        # 挖出槽钢凹槽形成真实型钢截面
        o_ch = BOX(s, L=L_beam - 24.0, W=H - tf * 2.0, H=B - tw).translate((xb + sx * tw / 2.0, 0.0, z_beam_mid))
        o_bm.subtractFrom(o_ch); o_ch.erase()
        o1.uniteWith(o_bm); o_bm.erase()

    # 横担梁顶底连接垫板与两端封头板
    tot_bx = B * 2.0 + beam_gap
    o_top_pad = BOX(s, L=L_beam, W=tf, H=tot_bx + 16.0).translate((0.0, 0.0, z_beam_top + tf / 2.0))
    o1.uniteWith(o_top_pad); o_top_pad.erase()

    # 3. 横担梁左右两端顶面各焊一组 750 型双耳动载销座 (带横向穿销，对照 p.313 轴测图)
    y_lug = L_beam / 2.0 - max(70.0, Pin_d * 2.2)
    ear_r = max(Pin_d * 1.05, 28.0)
    ear_h = max(55.0, Pin_d * 1.8)
    ear_t = max(10.0, Pin_d * 0.42)
    ear_gap = max(20.0, Pin_d * 1.05)
    for sy in (-1.0, 1.0):
        yl = sy * y_lug
        # 销座底垫板
        o_lpad = BOX(s, L=ear_gap + ear_t * 4.0, W=tf, H=tot_bx).translate((0.0, yl, z_beam_top + tf * 1.5))
        o1.uniteWith(o_lpad); o_lpad.erase()
        for s_ear in (-1.0, 1.0):
            ye = yl + s_ear * (ear_gap / 2.0 + ear_t / 2.0)
            o_ep = BOX(s, L=ear_t, W=ear_h, H=ear_r * 2.0).translate((0.0, ye, z_beam_top + tf * 2.0 + ear_h / 2.0))
            o_ec = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, ye + ear_t / 2.0, z_beam_top + tf * 2.0 + ear_h))
            o_ep.uniteWith(o_ec); o_ec.erase()
            o1.uniteWith(o_ep); o_ep.erase()
        # 销座横向穿销
        pin_len = ear_gap + ear_t * 3.4
        o_pin = CYLINDER(s, R=Pin_d / 2.0, H=pin_len, O=0.0).rotateX(90.0).translate((0.0, yl + pin_len / 2.0, z_beam_top + tf * 2.0 + ear_h))
        o1.uniteWith(o_pin); o_pin.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_beam', (0.0, -(L_beam / 2.0), z_beam_mid), (0.0, (L_beam / 2.0), z_beam_mid))
