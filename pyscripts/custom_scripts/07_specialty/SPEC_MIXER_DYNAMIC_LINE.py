# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Instrument",
          TooltipShort=u"管道在线动态混合器",
          TooltipLong=u"化工管道在线动态混合器，含双端HG/T 20592 PN16法兰、扩径混料腔、排净口与径向驱动电机减速机",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"在线动态混合器结构长度、端法兰及径向驱动电机减速机尺寸参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"主管道接管外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰面至法兰面结构长度 L_FACE (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"端法兰外径", TooltipLong=u"端法兰外径 D_FL (mm)")
@param(C_FL=LENGTH, TooltipShort=u"端法兰厚度", TooltipLong=u"端法兰厚度 C_FL (mm)")
@param(D_CHAMBER=LENGTH, TooltipShort=u"混料腔外径", TooltipLong=u"扩径混料腔筒体外径 D_CHAMBER (mm)")
@param(H_DRIVE=LENGTH, TooltipShort=u"驱动总高", TooltipLong=u"管道中心至电机顶部风罩总高 H_DRIVE (mm)", Ask4Dist=True)
@param(D_MOTOR=LENGTH, TooltipShort=u"电机外径", TooltipLong=u"驱动电机机座外径 D_MOTOR (mm)")
def SPEC_MIXER_DYNAMIC_LINE(
    s,
    D=114.3,
    L_FACE=650.0,
    D_FL=220.0,
    C_FL=20.0,
    D_CHAMBER=273.0,
    H_DRIVE=540.0,
    D_MOTOR=200.0,
    ID=u"SPEC_MIXER_DYNAMIC_LINE",
    **kw
):
    u"""管道在线动态混合器 (中心在原点, Port 1 在 X=-L_FACE/2, Port 2 在 X=+L_FACE/2, 电机减速机沿 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_CHAMBER = max(D * 1.35, float(D_CHAMBER))
    D_MOTOR = max(80.0, float(D_MOTOR))
    H_DRIVE = float(H_DRIVE)
    if H_DRIVE < 1.0:
        H_DRIVE = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_ch = D_CHAMBER / 2.0
    r_mot = D_MOTOR / 2.0

    # 1. 双端法兰 (Port 1 @ -half_l, Port 2 @ +half_l)
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 接管段 + 变径过渡锥 + 中央混料腔
    l_ch = L_FACE * 0.44
    l_cone = max(35.0, (L_FACE - 2.0 * C_FL - l_ch) * 0.28)
    l_neck = max(20.0, (L_FACE - l_ch - 2.0 * l_cone) / 2.0 - C_FL)

    o_n1 = CYLINDER(s, R=r_pipe, H=l_neck + 6.0, O=0.0).rotateY(90.0).translate((-half_l + C_FL - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_n1)
    o_n1.erase()

    o_n2 = CYLINDER(s, R=r_pipe, H=l_neck + 6.0, O=0.0).rotateY(90.0).translate((half_l - C_FL - l_neck - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_n2)
    o_n2.erase()

    x_c1 = -l_ch / 2.0 - l_cone
    o_c1 = CONE(s, R1=r_pipe, R2=r_ch, H=l_cone + 4.0, E=0.0).rotateY(90.0).translate((x_c1 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_c1)
    o_c1.erase()

    x_c2 = l_ch / 2.0
    o_c2 = CONE(s, R1=r_ch, R2=r_pipe, H=l_cone + 4.0, E=0.0).rotateY(90.0).translate((x_c2 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_c2)
    o_c2.erase()

    o_ch = CYLINDER(s, R=r_ch, H=l_ch + 4.0, O=0.0).rotateY(90.0).translate((-l_ch / 2.0 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_ch)
    o_ch.erase()

    # 3. 混料腔两端加强法兰环与底部排净短节
    ring_w = max(14.0, C_FL * 0.8)
    for rx in (-l_ch / 2.0, l_ch / 2.0 - ring_w):
        o_ring = CYLINDER(s, R=r_ch * 1.07, H=ring_w, O=0.0).rotateY(90.0).translate((rx, 0.0, 0.0))
        o_main.uniteWith(o_ring)
        o_ring.erase()

    o_drain = CYLINDER(s, R=max(14.0, r_pipe * 0.28), H=45.0, O=0.0).translate((0.0, 0.0, -r_ch - 38.0))
    o_main.uniteWith(o_drain)
    o_drain.erase()

    # 4. 径向(+Z)驱动安装颈、联轴器护罩、减速机箱体与立式电机
    z_mnt = r_ch + max(25.0, D_CHAMBER * 0.14)
    r_mnt = max(r_mot * 0.85, r_ch * 0.55)
    o_ped = CYLINDER(s, R=r_mnt * 0.78, H=z_mnt - r_ch * 0.5 + 8.0, O=0.0).translate((0.0, 0.0, r_ch * 0.5))
    o_main.uniteWith(o_ped)
    o_ped.erase()

    c_mnt = max(14.0, C_FL * 0.8)
    o_mfl = CYLINDER(s, R=r_mnt, H=c_mnt, O=0.0).translate((0.0, 0.0, z_mnt - c_mnt * 0.5))
    o_main.uniteWith(o_mfl)
    o_mfl.erase()

    z_gb_bot = z_mnt + c_mnt * 0.5 - 2.0
    h_gb = max(65.0, (H_DRIVE - z_gb_bot) * 0.34)
    o_gb = CYLINDER(s, R=r_mot * 0.88, H=h_gb + 4.0, O=0.0).translate((0.0, 0.0, z_gb_bot))
    o_main.uniteWith(o_gb)
    o_gb.erase()

    z_mot_bot = z_gb_bot + h_gb
    h_mot_tot = max(100.0, H_DRIVE - z_mot_bot)
    h_cowl = max(28.0, h_mot_tot * 0.18)
    h_mot_body = h_mot_tot - h_cowl

    o_mot = CYLINDER(s, R=r_mot, H=h_mot_body + 3.0, O=0.0).translate((0.0, 0.0, z_mot_bot - 1.0))
    o_main.uniteWith(o_mot)
    o_mot.erase()

    # 电机散热筋环与侧向接线盒
    for fz in (0.25, 0.50, 0.75):
        o_fin = CYLINDER(s, R=r_mot * 1.06, H=max(8.0, h_mot_body * 0.06), O=0.0).translate((0.0, 0.0, z_mot_bot + h_mot_body * fz))
        o_main.uniteWith(o_fin)
        o_fin.erase()

    jb_w = max(36.0, r_mot * 0.55)
    o_jb = BOX(s, L=jb_w, W=jb_w * 0.9, H=jb_w * 0.85).translate((0.0, r_mot + jb_w * 0.28, z_mot_bot + h_mot_body * 0.52))
    o_main.uniteWith(o_jb)
    o_jb.erase()

    o_cowl = CONE(s, R1=r_mot * 1.02, R2=r_mot * 0.72, H=h_cowl, E=0.0).translate((0.0, 0.0, z_mot_bot + h_mot_body))
    o_main.uniteWith(o_cowl)
    o_cowl.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_DRIVE', (0.0, 0.0, 0.0), (0.0, 0.0, H_DRIVE))
