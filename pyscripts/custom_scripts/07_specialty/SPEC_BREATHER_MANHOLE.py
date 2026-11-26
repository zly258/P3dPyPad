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

@activate(Group="Valve",
          TooltipShort=u"紧急泄压呼吸人孔 (SY/T 0511)",
          TooltipLong=u"SY/T 0511 储罐顶紧急泄压呼吸人孔，含大直径筒节、安装底法兰、密封法兰与加厚铰接配重盖",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"紧急泄压呼吸人孔公称筒径、法兰及总高尺寸")
@param(D=LENGTH, TooltipShort=u"筒节外径", TooltipLong=u"人孔大直径接管筒节外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"安装底法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"安装底法兰厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"人孔总高", TooltipLong=u"底法兰面至配重盖顶总高 H (mm)", Ask4Dist=True)
@param(D_COVER=LENGTH, TooltipShort=u"泄压盖外径", TooltipLong=u"加厚铰接配重盖外径 (mm)")
@param(H_COVER=LENGTH, TooltipShort=u"配重盖厚度", TooltipLong=u"铰接配重泄压盖总厚度 (mm)")
def SPEC_BREATHER_MANHOLE(
    s,
    D=508.0,
    D_FL=670.0,
    C_FL=24.0,
    H_TOTAL=320.0,
    D_COVER=620.0,
    H_COVER=65.0,
    ID=u"SPEC_BREATHER_MANHOLE",
    **kw
):
    u"""紧急泄压呼吸人孔 (底法兰面在 Z=0, Port 1 朝向 -Z, 铰链位于 -X 侧)。"""
    D = max(200.0, float(D))
    D_FL = float(D_FL)
    if D_FL < 1.0:
        D_FL = 1.0
    C_FL = max(16.0, float(C_FL))
    D_COVER = max(D + 50.0, float(D_COVER))
    H_COVER = max(35.0, float(H_COVER))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_cov = D_COVER / 2.0

    # 1. 底部大法兰与筒节
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)

    z_seat_top = H_TOTAL - H_COVER
    c_seat = max(18.0, C_FL * 0.90)
    o_shell = CYLINDER(s, R=r_pipe, H=z_seat_top - C_FL + 8.0, O=0.0).translate((0.0, 0.0, C_FL - 4.0))
    o_main.uniteWith(o_shell)
    o_shell.erase()

    # 2. 上部密封座法兰
    o_seat = CYLINDER(s, R=r_fl * 0.95, H=c_seat, O=0.0).translate((0.0, 0.0, z_seat_top - c_seat))
    o_main.uniteWith(o_seat)
    o_seat.erase()

    # 3. 加厚泄压顶盖与中央叠层配重块
    h_plate = H_COVER * 0.48
    h_wt = H_COVER - h_plate
    o_cov = CYLINDER(s, R=r_cov, H=h_plate + 4.0, O=0.0).translate((0.0, 0.0, z_seat_top - 2.0))
    o_main.uniteWith(o_cov)
    o_cov.erase()

    o_wt = CYLINDER(s, R=r_cov * 0.62, H=h_wt + 4.0, O=0.0).translate((0.0, 0.0, z_seat_top + h_plate - 2.0))
    o_main.uniteWith(o_wt)
    o_wt.erase()

    # 4. -X 侧重型铰链支座与连臂
    hx = -(r_fl * 0.96)
    h_arm = H_TOTAL - C_FL - h_wt * 0.5
    o_hpost = BOX(s, L=max(70.0, D * 0.16), W=h_arm, H=max(42.0, D * 0.09)).translate((hx, 0.0, C_FL + h_arm / 2.0 - 4.0))
    o_main.uniteWith(o_hpost)
    o_hpost.erase()

    o_hpin = CYLINDER(s, R=max(18.0, D * 0.04), H=max(110.0, D * 0.24), O=0.0).rotateX(90.0).translate((hx, max(55.0, D * 0.12), z_seat_top + h_plate * 0.5))
    o_main.uniteWith(o_hpin)
    o_hpin.erase()

    o_harm = BOX(s, L=max(60.0, D * 0.14), W=max(24.0, h_plate * 0.8), H=r_fl * 0.65).translate((hx + r_fl * 0.30, 0.0, z_seat_top + h_plate * 0.55))
    o_main.uniteWith(o_harm)
    o_harm.erase()

    # 5. +X 侧限位导向柱与开启提手
    o_guide = CYLINDER(s, R=max(14.0, D * 0.03), H=h_arm * 0.92, O=0.0).translate((r_fl * 0.90, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_guide)
    o_guide.erase()

    o_lug = BOX(s, L=max(80.0, D * 0.16), W=max(22.0, h_plate * 0.6), H=max(55.0, D * 0.12)).translate((r_cov * 0.92, 0.0, z_seat_top + h_plate * 0.5))
    o_main.uniteWith(o_lug)
    o_lug.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('D_FL', (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
