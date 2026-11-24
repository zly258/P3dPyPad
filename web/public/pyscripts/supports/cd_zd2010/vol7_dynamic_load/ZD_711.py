# -*- coding: utf-8 -*-
# CD-ZD2010 711 液压阻尼器辅助加长件（空心无缝钢管拉杆 + 一端 U 形双耳叉头带销轴 + 另一端多螺栓法兰/螺纹连接箍套）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="711阻尼器加长件", TooltipLong="CD-ZD2010 711 液压阻尼器辅助加长件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_pipe=LENGTH, TooltipShort="钢管径D", TooltipLong="加长无缝钢管外径 D")
@param(L_ext=LENGTH, TooltipShort="加长长B", TooltipLong="接长有效长度 B", Ask4Dist=True)
@param(T_wall=LENGTH, TooltipShort="壁厚T", TooltipLong="管壁厚度 T")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_711(s, D_pipe=70.0, L_ext=800.0, T_wall=6.5, ID=u"ZD_711", Load_kN=45.0, Weight_kg=11.2, **kw):
    D_pipe = float(D_pipe); L_ext = float(L_ext); T_wall = float(T_wall)
    if D_pipe < 30.0: D_pipe = 30.0
    if L_ext < 150.0: L_ext = 150.0
    if T_wall < 2.5: T_wall = 2.5
    if T_wall >= D_pipe * 0.4: T_wall = D_pipe * 0.2

    # 对照图集 p.261 / p.272：一端 (Z=0) 为扁平圆头铰接耳头/U形叉头 + 可调螺纹杆与锁紧螺母 + 中部空心无缝钢管 + 另一端 (Z=-L_ext) 为阻尼器尾部连接法兰盘与箍套
    R_pipe = D_pipe / 2.0
    ear_r = R_pipe * 0.72
    ear_t = max(12.0, R_pipe * 0.42)
    pin_r = ear_r * 0.46
    shank_l = max(60.0, D_pipe * 1.4)
    flange_h = max(36.0, D_pipe * 0.65)
    pipe_l = max(60.0, L_ext - shank_l - flange_h)
    z_pipe_top = -shank_l
    z_pipe_btm = -(shank_l + pipe_l)

    # 1. 中段空心无缝钢管 (由 T_wall 驱动真实内壁空腔)
    o1 = CYLINDER(s, R=R_pipe, H=pipe_l, O=0.0).translate((0.0, 0.0, z_pipe_btm))
    o_in = CYLINDER(s, R=R_pipe - T_wall, H=max(20.0, pipe_l - T_wall * 2.0), O=0.0).translate((0.0, 0.0, z_pipe_btm + T_wall))
    o1.subtractFrom(o_in); o_in.erase()

    # 2. 上端 (Z=0) U形双耳叉头/球铰扁耳头 + 可调螺杆段 + 锥形收口端盖与锁紧螺母
    o_cone = CONE(s, R1=R_pipe, R2=R_pipe * 0.55, H=shank_l * 0.35, E=0.0).translate((0.0, 0.0, z_pipe_top))
    o_shank = CYLINDER(s, R=R_pipe * 0.45, H=shank_l * 0.85, O=0.0).translate((0.0, 0.0, z_pipe_top + shank_l * 0.15))
    o_nut = CYLINDER(s, R=R_pipe * 0.68, H=shank_l * 0.22, O=0.0).translate((0.0, 0.0, z_pipe_top + shank_l * 0.38))
    o1.uniteWith(o_cone); o_cone.erase()
    o1.uniteWith(o_shank); o_shank.erase()
    o1.uniteWith(o_nut); o_nut.erase()

    # 上端双耳叉头与销孔 (位于 Z = 0.0)
    clevis_gap = ear_t * 0.9
    clevis_h = ear_r * 2.2
    o_cbase = BOX(s, L=ear_r * 1.4, W=ear_t, H=clevis_gap + ear_t * 1.6).translate((0.0, 0.0, -(clevis_h * 0.65)))
    o1.uniteWith(o_cbase); o_cbase.erase()

    for sx in (-1.0, 1.0):
        xc = sx * (clevis_gap / 2.0 + ear_t * 0.4)
        o_plate = BOX(s, L=ear_r * 1.8, W=clevis_h * 0.65, H=ear_t * 0.8).translate((xc, 0.0, -(clevis_h * 0.325)))
        o_disc = CYLINDER(s, R=ear_r, H=ear_t * 0.8, O=0.0).rotateY(90.0).translate((xc - ear_t * 0.4, 0.0, 0.0))
        o_plate.uniteWith(o_disc); o_disc.erase()
        o_ph = CYLINDER(s, R=pin_r, H=ear_t * 2.0, O=0.0).rotateY(90.0).translate((xc - ear_t, 0.0, 0.0))
        o_plate.subtractFrom(o_ph); o_ph.erase()
        o1.uniteWith(o_plate); o_plate.erase()

    # 3. 下端 (Z = -L_ext) 阻尼器尾部螺纹/法兰连接箍套 (带 6~8 个法兰紧固螺栓凸缘，对照图集 p.272)
    flange_r = R_pipe * 1.45
    o_collar = CYLINDER(s, R=R_pipe * 1.18, H=flange_h, O=0.0).translate((0.0, 0.0, -L_ext))
    o_flange = CYLINDER(s, R=flange_r, H=flange_h * 0.42, O=0.0).translate((0.0, 0.0, -L_ext))
    o_sock = CYLINDER(s, R=R_pipe * 0.72, H=flange_h * 0.6, O=0.0).translate((0.0, 0.0, -L_ext - 2.0))
    o_collar.uniteWith(o_flange); o_flange.erase()
    o_collar.subtractFrom(o_sock); o_sock.erase()
    o1.uniteWith(o_collar); o_collar.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_ext', (0.0, 0.0, 0.0), (0.0, 0.0, -L_ext))
