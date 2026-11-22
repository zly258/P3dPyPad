# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Equipment", Ports=3, TooltipShort=u"化工立式夹套搅拌反应釜 (HG/T 20569)", TooltipLong=u"化工行业标准 HG/T 20569 / JB/T 4712.3 立式夹套搅拌反应釜 (Agitated Jacketed Reactor)，含内筒与上下椭圆封头、外导热夹套筒体与锥形封口环、4座耳式支座、顶部双立柱机架、行星减速机、立式防爆电机及进出料管口", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"设备主要结构尺寸：筒体、封头、接管与支承高度")
@param(D_VESSEL=LENGTH, TooltipShort=u"内筒外径 D", Ask4Dist=True, TooltipLong=u"内筒外径 D")
@param(D_JACKET=LENGTH, TooltipShort=u"外夹套外径 D_J", Ask4Dist=True, TooltipLong=u"外夹套外径 D_J")
@param(H_SHELL=LENGTH, TooltipShort=u"内筒切线高 H", Ask4Dist=True, TooltipLong=u"内筒切线高 H")
@param(H_DRIVE=LENGTH, TooltipShort=u"顶部搅拌传动总高", TooltipLong=u"顶部搅拌传动总高")
@param(DN_NOZZLE=LENGTH, TooltipShort=u"工艺管口外径", TooltipLong=u"工艺管口外径")
@param(ID=STRING, TooltipShort=u"反应釜位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def EQUIPMENT_JACKETED_REACTOR(s, D_VESSEL=1200.0, D_JACKET=1320.0, H_SHELL=1600.0, H_DRIVE=1150.0, DN_NOZZLE=114.3, ID="R-101", **kw):
    D_VESSEL = max(500.0, float(D_VESSEL))
    D_JACKET = max(D_VESSEL + 80.0, float(D_JACKET))
    H_SHELL = max(800.0, float(H_SHELL))
    H_DRIVE = max(650.0, float(H_DRIVE))
    DN_NOZZLE = max(40.0, float(DN_NOZZLE))

    r_in = D_VESSEL / 2.0
    r_jk = D_JACKET / 2.0
    r_noz = DN_NOZZLE / 2.0
    head_h = r_in * 0.5

    # 1. 内筒 + 顶部与底部 2:1 标准椭圆封头 (底切线在 z = 0，顶切线在 z = H_SHELL)
    o_rx = CYLINDER(s, R=r_in, H=H_SHELL, O=0.0)
    o_top_h = ELLIPSOIDHEAD(s, R=r_in, H=head_h).translate((0.0, 0.0, H_SHELL))
    o_bot_h = ELLIPSOIDHEAD(s, R=r_in, H=head_h).rotateX(180.0)
    o_rx.uniteWith(o_top_h); o_top_h.erase()
    o_rx.uniteWith(o_bot_h); o_bot_h.erase()

    # 2. 外部换热夹套 (Jacket Shell + Bottom Head + Top Tapered Closure Ring)
    h_jk = H_SHELL * 0.72
    o_jk = CYLINDER(s, R=r_jk, H=h_jk, O=0.0)
    o_jk_bot = ELLIPSOIDHEAD(s, R=r_jk, H=r_jk * 0.5).rotateX(180.0)
    o_jk_cone = CONE(s, R1=r_jk, R2=r_in, H=75.0, E=0.0).translate((0.0, 0.0, h_jk))
    o_rx.uniteWith(o_jk); o_jk.erase()
    o_rx.uniteWith(o_jk_bot); o_jk_bot.erase()
    o_rx.uniteWith(o_jk_cone); o_jk_cone.erase()

    # 3. 上部壳体四周 4 个 JB/T 4712.3 B型耳式支座 (位于 z_ear = h_jk + 60)
    z_ear = h_jk + 60.0
    h_ear = 240.0
    l_ear = 190.0
    w_ear = 150.0
    for ang_deg in (0.0, 90.0, 180.0, 270.0):
        ang_rad = math.radians(ang_deg)
        rm = r_in + l_ear * 0.45
        base = BOX(s, L=w_ear, W=20.0, H=l_ear).rotateZ(ang_deg).translate((rm * math.cos(ang_rad), rm * math.sin(ang_rad), z_ear + 10.0))
        gus1 = BOX(s, L=16.0, W=h_ear, H=l_ear * 0.85).rotateZ(ang_deg).translate((rm * math.cos(ang_rad) - 45.0 * math.sin(ang_rad), rm * math.sin(ang_rad) + 45.0 * math.cos(ang_rad), z_ear + h_ear * 0.5))
        gus2 = BOX(s, L=16.0, W=h_ear, H=l_ear * 0.85).rotateZ(ang_deg).translate((rm * math.cos(ang_rad) + 45.0 * math.sin(ang_rad), rm * math.sin(ang_rad) - 45.0 * math.cos(ang_rad), z_ear + h_ear * 0.5))
        o_rx.uniteWith(base); base.erase()
        o_rx.uniteWith(gus1); gus1.erase()
        o_rx.uniteWith(gus2); gus2.erase()

    # 4. 顶部机械密封座 + 双立柱机架 + 行星减速机 + 立式防爆电机 (Agitator Drive Assembly)
    z_top_crown = H_SHELL + head_h
    h_lantern = H_DRIVE * 0.36
    h_gear = H_DRIVE * 0.24
    h_motor = H_DRIVE * 0.40

    # 机架底座法兰与机械密封筒
    o_seal_fl = CYLINDER(s, R=r_in * 0.36, H=36.0, O=0.0).translate((0.0, 0.0, z_top_crown - 25.0))
    o_seal = CYLINDER(s, R=r_in * 0.18, H=h_lantern, O=0.0).translate((0.0, 0.0, z_top_crown))
    o_rx.uniteWith(o_seal_fl); o_seal_fl.erase()
    o_rx.uniteWith(o_seal); o_seal.erase()

    for sy in (-1.0, 1.0):
        leg = BOX(s, L=32.0, W=h_lantern, H=75.0).translate((0.0, sy * r_in * 0.24, z_top_crown + h_lantern * 0.5))
        o_rx.uniteWith(leg); leg.erase()

    # 行星减速机筒体
    z_gear = z_top_crown + h_lantern
    r_gear = r_in * 0.30
    o_gear_fl = CYLINDER(s, R=r_gear * 1.18, H=28.0, O=0.0).translate((0.0, 0.0, z_gear))
    o_gear = CYLINDER(s, R=r_gear, H=h_gear, O=0.0).translate((0.0, 0.0, z_gear))
    o_rx.uniteWith(o_gear_fl); o_gear_fl.erase()
    o_rx.uniteWith(o_gear); o_gear.erase()

    # 立式防爆电机 + 侧面防爆接线盒 + 顶部风扇罩
    z_mot = z_gear + h_gear
    r_mot = r_in * 0.25
    o_mot = CYLINDER(s, R=r_mot, H=h_motor * 0.82, O=0.0).translate((0.0, 0.0, z_mot))
    o_fan_cap = CONE(s, R1=r_mot * 1.04, R2=r_mot * 0.72, H=h_motor * 0.18, E=0.0).translate((0.0, 0.0, z_mot + h_motor * 0.82))
    o_jbox = BOX(s, L=90.0, W=110.0, H=85.0).translate((r_mot + 35.0, 0.0, z_mot + h_motor * 0.45))
    o_rx.uniteWith(o_mot); o_mot.erase()
    o_rx.uniteWith(o_fan_cap); o_fan_cap.erase()
    o_rx.uniteWith(o_jbox); o_jbox.erase()

    # 5. 顶封头左右工艺管嘴 (Port 1, Port 2) 与底封头中心放料口 (Port 3)
    z_top_noz = z_top_crown + 110.0
    x_noz = r_in * 0.56
    r_fl = r_noz + 48.0
    for sx in (-1.0, 1.0):
        xn = sx * x_noz
        nc = CYLINDER(s, R=r_noz, H=220.0, O=0.0).translate((xn, 0.0, z_top_noz - 220.0))
        nf = CYLINDER(s, R=r_fl, H=22.0, O=0.0).translate((xn, 0.0, z_top_noz - 22.0))
        nb = CYLINDER(s, R=r_noz * 0.85, H=140.0, O=0.0).translate((xn, 0.0, z_top_noz - 135.0))
        o_rx.uniteWith(nc); nc.erase()
        o_rx.uniteWith(nf); nf.erase()
        o_rx.subtractFrom(nb); nb.erase()

    z_bot_noz = -(head_h + r_jk - r_in + 160.0)
    b_nc = CYLINDER(s, R=r_noz, H=220.0, O=0.0).translate((0.0, 0.0, z_bot_noz))
    b_nf = CYLINDER(s, R=r_fl, H=22.0, O=0.0).translate((0.0, 0.0, z_bot_noz))
    b_nb = CYLINDER(s, R=r_noz * 0.85, H=140.0, O=0.0).translate((0.0, 0.0, z_bot_noz - 5.0))
    o_rx.uniteWith(b_nc); b_nc.erase()
    o_rx.uniteWith(b_nf); b_nf.erase()
    o_rx.subtractFrom(b_nb); b_nb.erase()

    s.setPoint((-x_noz, 0.0, z_top_noz), (0.0, 0.0, 1.0))
    s.setPoint((x_noz, 0.0, z_top_noz), (0.0, 0.0, 1.0))
    s.setPoint((0.0, 0.0, z_bot_noz), (0.0, 0.0, -1.0))

    s.setLinearDimension("H_SHELL", (-r_jk - l_ear, 0.0, 0.0), (-r_jk - l_ear, 0.0, H_SHELL))
    s.setLinearDimension("H_DRIVE", (-r_jk - l_ear, 0.0, z_top_crown), (-r_jk - l_ear, 0.0, z_top_crown + H_DRIVE))
    s.setLinearDimension("D_JACKET", (-r_jk, 0.0, z_bot_noz), (r_jk, 0.0, z_bot_noz))
