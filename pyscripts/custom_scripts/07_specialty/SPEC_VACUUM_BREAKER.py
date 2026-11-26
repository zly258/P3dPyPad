# -*- coding: utf-8 -*-
import math
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

@activate(Group="Valve",
          TooltipShort=u"罐顶真空破坏阀",
          TooltipLong=u"化工储罐顶用真空破坏阀，含底部HG/T 20592 PN16法兰、阀座、四柱导向罩与配重阀盖",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"罐顶真空破坏阀底法兰、导向罩、配重阀盖及总高尺寸参数")
@param(D=LENGTH, TooltipShort=u"接管外径", TooltipLong=u"底部接管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"底部安装法兰外径 D_FL (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"底部安装法兰厚度 C_FL (mm)")
@param(D_CAGE=LENGTH, TooltipShort=u"导向罩外径", TooltipLong=u"上部导向罩环外径 D_CAGE (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"阀门总高", TooltipLong=u"底法兰面至顶部阀盖顶面总高 H_TOTAL (mm)", Ask4Dist=True)
@param(D_WEIGHT=LENGTH, TooltipShort=u"配重阀盖外径", TooltipLong=u"配重阀盖/重锤盘外径 D_WEIGHT (mm)")
def SPEC_VACUUM_BREAKER(
    s,
    D=114.3,
    D_FL=220.0,
    C_FL=20.0,
    D_CAGE=210.0,
    H_TOTAL=390.0,
    D_WEIGHT=175.0,
    ID=u"SPEC_VACUUM_BREAKER",
    **kw
):
    u"""罐顶真空破坏阀 (底法兰面在 Z=0, Port 1 在原点朝向 -Z)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_CAGE = max(D * 1.4, float(D_CAGE))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    D_WEIGHT = max(D * 1.15, float(D_WEIGHT))

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_cage = D_CAGE / 2.0
    r_wt = D_WEIGHT / 2.0

    # 1. 底部单法兰与阀体短节
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    h_spool = max(45.0, H_TOTAL * 0.24)
    o_spool = CYLINDER(s, R=r_pipe * 1.06, H=h_spool + 6.0, O=0.0).translate((0.0, 0.0, C_FL - 3.0))
    o_main.uniteWith(o_spool)
    o_spool.erase()

    # 2. 阀座密封环 (座台)
    z_seat = C_FL + h_spool
    h_seat = max(16.0, C_FL * 0.85)
    r_seat = max(r_cage, r_pipe * 1.32)
    o_seat = CYLINDER(s, R=r_seat, H=h_seat, O=0.0).translate((0.0, 0.0, z_seat - 2.0))
    o_main.uniteWith(o_seat)
    o_seat.erase()

    # 3. 四柱导向罩 (4 根立柱 + 顶部导向环)
    z_cage_bot = z_seat + h_seat - 3.0
    h_cage = max(90.0, H_TOTAL * 0.42)
    z_cage_top = z_cage_bot + h_cage
    r_post = max(8.0, r_cage * 0.09)
    r_pcd = r_cage - r_post * 1.25
    for i in range(4):
        ang = math.radians(45.0 + i * 90.0)
        px = r_pcd * math.cos(ang)
        py = r_pcd * math.sin(ang)
        o_post = CYLINDER(s, R=r_post, H=h_cage + 6.0, O=0.0).translate((px, py, z_cage_bot))
        o_main.uniteWith(o_post)
        o_post.erase()

    h_ring = max(14.0, C_FL * 0.75)
    o_ring = CYLINDER(s, R=r_cage, H=h_ring, O=r_cage * 0.68).translate((0.0, 0.0, z_cage_top - h_ring))
    o_main.uniteWith(o_ring)
    o_ring.erase()

    # 4. 中心导向阀杆与配重阀盖 (重锤盘 + 顶帽)
    z_disc = z_seat + h_seat + max(18.0, h_cage * 0.22)
    o_stem = CYLINDER(s, R=max(10.0, r_pipe * 0.20), H=H_TOTAL - z_seat - 10.0, O=0.0).translate((0.0, 0.0, z_seat))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    h_disc = max(18.0, C_FL * 0.9)
    o_disc = CYLINDER(s, R=r_wt * 0.92, H=h_disc, O=0.0).translate((0.0, 0.0, z_disc))
    o_main.uniteWith(o_disc)
    o_disc.erase()

    # 顶部配重盘与防雨罩
    z_wt = z_cage_top - 2.0
    h_wt = max(24.0, (H_TOTAL - z_wt) * 0.55)
    o_wt = CYLINDER(s, R=r_wt, H=h_wt, O=0.0).translate((0.0, 0.0, z_wt))
    o_main.uniteWith(o_wt)
    o_wt.erase()

    h_hood = max(18.0, H_TOTAL - (z_wt + h_wt))
    o_hood = CONE(s, R1=r_wt * 1.05, R2=r_wt * 0.28, H=h_hood, E=0.0).translate((0.0, 0.0, z_wt + h_wt - 1.0))
    o_main.uniteWith(o_hood)
    o_hood.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
