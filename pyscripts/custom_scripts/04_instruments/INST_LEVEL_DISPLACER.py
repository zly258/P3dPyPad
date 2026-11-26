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
          TooltipShort=u"外浮筒液位变送器 (JB/T 9242)",
          TooltipLong=u"化工侧装外浮筒液位/界位变送器，含加粗外浮筒承压腔、上下侧向双法兰、顶法兰、特征水平扭力管臂及智能变送器表头",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"外浮筒中心距、浮筒外径、接管伸出及顶表头尺寸")
@param(L_C2C=LENGTH, TooltipShort=u"法兰中心距", TooltipLong=u"上下侧向过程法兰中心距 C-C (mm)", Ask4Dist=True)
@param(D_CHAMBER=LENGTH, TooltipShort=u"外浮筒外径", TooltipLong=u"外浮筒承压筒体外径 (mm)")
@param(L_NOZ=LENGTH, TooltipShort=u"接管伸出距", TooltipLong=u"浮筒中心至侧向法兰密封面距离 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"侧向过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
def INST_LEVEL_DISPLACER(
    s,
    L_C2C=800.0,
    D_CHAMBER=140.0,
    L_NOZ=195.0,
    D_FL=165.0,
    C_FL=20.0,
    ID=u"INST_LEVEL_DISPLACER",
    **kw
):
    u"""外浮筒液位变送器 (Port 1 在 (-L_NOZ, 0, -L_C2C/2), Port 2 在 (-L_NOZ, 0, +L_C2C/2))。"""
    L_C2C = float(L_C2C)
    if L_C2C < 1.0:
        L_C2C = 1.0
    D_CHAMBER = max(110.0, float(D_CHAMBER))
    L_NOZ = float(L_NOZ)
    if L_NOZ < 1.0:
        L_NOZ = 1.0
    D_FL = max(115.0, float(D_FL))
    C_FL = max(16.0, float(C_FL))

    half_c = L_C2C / 2.0
    r_ch = D_CHAMBER / 2.0
    r_fl = D_FL / 2.0
    ext_top = 130.0
    ext_bot = 135.0
    h_ch = L_C2C + ext_top + ext_bot

    # 1. 加粗外浮筒承压主体 + 上下重型端盖法兰
    o_main = CYLINDER(s, R=r_ch, H=h_ch, O=0.0).translate((0.0, 0.0, -half_c - ext_bot))
    z_top_fl = half_c + ext_top
    o_tfl = CYLINDER(s, R=r_ch + 36.0, H=44.0, O=0.0).translate((0.0, 0.0, z_top_fl - 14.0))
    o_main.uniteWith(o_tfl)
    o_tfl.erase()
    # 底部封头与排污法兰
    o_bcap = HALFSPHERE(s, R=r_ch).rotateX(180.0).translate((0.0, 0.0, -half_c - ext_bot + 4.0))
    o_main.uniteWith(o_bcap)
    o_bcap.erase()
    o_drain = CYLINDER(s, R=20.0, H=55.0, O=0.0).translate((0.0, 0.0, -half_c - ext_bot - r_ch - 38.0))
    o_main.uniteWith(o_drain)
    o_drain.erase()
    o_dfl = CYLINDER(s, R=38.0, H=16.0, O=0.0).translate((0.0, 0.0, -half_c - ext_bot - r_ch - 46.0))
    o_main.uniteWith(o_dfl)
    o_dfl.erase()

    # 2. 上下侧向连接支管与过程法兰 (-X)
    for sz in (-1.0, 1.0):
        zz = sz * half_c
        o_noz = CYLINDER(s, R=32.0, H=L_NOZ, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_noz)
        o_noz.erase()
        o_fl = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_fl)
        o_fl.erase()

    # 3. 顶部扭力管立柱 + 特征水平扭力管臂 (+X) + 智能变送器表头
    z_arm = z_top_fl + 92.0
    o_tcol = CYLINDER(s, R=42.0, H=96.0, O=0.0).translate((0.0, 0.0, z_top_fl + 24.0))
    o_main.uniteWith(o_tcol)
    o_tcol.erase()
    o_tcap = CYLINDER(s, R=48.0, H=24.0, O=0.0).translate((0.0, 0.0, z_arm + 16.0))
    o_main.uniteWith(o_tcap)
    o_tcap.erase()
    # 水平扭力管套臂 (+X)
    o_arm = CYLINDER(s, R=26.0, H=145.0, O=0.0).rotateY(90.0).translate((20.0, 0.0, z_arm))
    o_main.uniteWith(o_arm)
    o_arm.erase()
    # 智能液位变送器表头箱体 (装在扭力管臂端部)
    o_tx = CORNERBOX(s, L=118.0, W=148.0, H=168.0).translate((145.0, -74.0, z_arm - 64.0))
    o_main.uniteWith(o_tx)
    o_tx.erase()
    # 表头前视窗圆盘 (-Y) + 底部双格兰头
    o_win = CYLINDER(s, R=46.0, H=18.0, O=0.0).rotateX(-90.0).translate((204.0, -86.0, z_arm + 16.0))
    o_main.uniteWith(o_win)
    o_win.erase()
    for sy in (-24.0, 24.0):
        o_gl = CYLINDER(s, R=12.0, H=28.0, O=0.0).translate((204.0, sy, z_arm - 88.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((-L_NOZ, 0.0, -half_c), (-1.0, 0.0, 0.0))
    s.setPoint((-L_NOZ, 0.0, half_c), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_C2C', (-L_NOZ, 0.0, -half_c), (-L_NOZ, 0.0, half_c))
    s.setLinearDimension('L_NOZ', (-L_NOZ, 0.0, 0.0), (0.0, 0.0, 0.0))
