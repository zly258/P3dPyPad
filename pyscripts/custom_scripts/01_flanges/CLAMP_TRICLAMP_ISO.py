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

@activate(Group="Flange",
          TooltipShort=u"卫生级 Tri-Clamp 快装卡箍法兰接头 (ISO 2852)",
          TooltipLong=u"医药/精细化工卫生级 Tri-Clamp 快装卡箍接头(ISO 2852 / DIN 32676)，含双卡箍法兰盘、中间密封垫片、快装卡箍环与蝶形螺母",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="TC")
@group("MainDimensions", TooltipLong=u"Tri-Clamp 快装卡箍接头主要几何尺寸参数")
@param(D_PIPE=LENGTH, TooltipShort=u"卫生管外径", TooltipLong=u"卡箍接管焊接端外径 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"卫生级贯通内孔直径 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"卡盘外径", TooltipLong=u"Tri-Clamp 卡箍法兰盘外径 C (mm)")
@param(L_FERRULE=LENGTH, TooltipShort=u"单侧卡盘长度", TooltipLong=u"单个焊接卡箍接头长度 L (mm)")
@param(T_GSK=LENGTH, TooltipShort=u"垫片厚度", TooltipLong=u"中间卫生垫片压缩厚度 (mm)")
@param(D_CLAMP=LENGTH, TooltipShort=u"卡箍环外径", TooltipLong=u"外部快装卡箍抱箍外径 (mm)")
@param(W_CLAMP=LENGTH, TooltipShort=u"卡箍环宽度", TooltipLong=u"外部快装卡箍抱箍轴向宽度 (mm)")
def CLAMP_TRICLAMP_ISO(
    s,
    D_PIPE=53.0,
    B_ID=50.0,
    D_FL=64.0,
    L_FERRULE=21.5,
    T_GSK=4.0,
    D_CLAMP=78.0,
    W_CLAMP=22.0,
    ID=u"CLAMP_TRICLAMP_ISO",
    **kw
):
    u"""卫生级 Tri-Clamp 快装卡箍法兰接头 (Port 1 在 X=0, Port 2 在 X=L_TOT)。"""
    D_PIPE = max(12.0, float(D_PIPE))
    B_ID = max(6.0, min(D_PIPE - 2.0, float(B_ID)))
    D_FL = max(D_PIPE + 8.0, float(D_FL))
    L_FERRULE = max(12.0, float(L_FERRULE))
    T_GSK = max(2.0, min(10.0, float(T_GSK)))
    D_CLAMP = max(D_FL + 8.0, float(D_CLAMP))
    W_CLAMP = max(T_GSK + 8.0, min(2.0 * L_FERRULE, float(W_CLAMP)))

    r_in = B_ID / 2.0
    l_tot = 2.0 * L_FERRULE + T_GSK
    x_mid = l_tot / 2.0
    disc_t = max(4.5, min(7.0, L_FERRULE * 0.28))
    cone_t = max(2.5, L_FERRULE * 0.16)
    neck_l = max(4.0, L_FERRULE - disc_t - cone_t)

    # 1. 左侧卡箍接头 (直管颈 + 锥形过渡 + 卡盘)
    o_main = CYLINDER(s, R=D_PIPE / 2.0, H=neck_l + 0.3, O=r_in).rotateY(90.0)
    o_c1 = CONE(s, R1=D_PIPE / 2.0, R2=D_FL / 2.0, H=cone_t + 0.3, E=0.0).rotateY(90.0).translate((neck_l - 0.1, 0.0, 0.0))
    o_d1 = CYLINDER(s, R=D_FL / 2.0, H=disc_t + 0.2, O=r_in).rotateY(90.0).translate((neck_l + cone_t - 0.1, 0.0, 0.0))
    o_main.uniteWith(o_c1); o_c1.erase()
    o_main.uniteWith(o_d1); o_d1.erase()

    # 2. 中间卫生垫片
    o_gsk = CYLINDER(s, R=(D_FL + 1.5) / 2.0, H=T_GSK + 0.4, O=r_in).rotateY(90.0).translate((L_FERRULE - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_gsk); o_gsk.erase()

    # 3. 右侧卡箍接头 (镜像对称)
    x_r0 = L_FERRULE + T_GSK
    o_d2 = CYLINDER(s, R=D_FL / 2.0, H=disc_t + 0.2, O=r_in).rotateY(90.0).translate((x_r0 - 0.1, 0.0, 0.0))
    o_c2 = CONE(s, R1=D_FL / 2.0, R2=D_PIPE / 2.0, H=cone_t + 0.3, E=0.0).rotateY(90.0).translate((x_r0 + disc_t - 0.1, 0.0, 0.0))
    o_p2 = CYLINDER(s, R=D_PIPE / 2.0, H=neck_l + 0.2, O=r_in).rotateY(90.0).translate((x_r0 + disc_t + cone_t - 0.1, 0.0, 0.0))
    o_main.uniteWith(o_d2); o_d2.erase()
    o_main.uniteWith(o_c2); o_c2.erase()
    o_main.uniteWith(o_p2); o_p2.erase()

    # 4. 外部快装卡箍抱箍环
    o_ring = CYLINDER(s, R=D_CLAMP / 2.0, H=W_CLAMP, O=D_FL / 2.0 - 1.0).rotateY(90.0).translate((x_mid - W_CLAMP / 2.0, 0.0, 0.0))
    o_main.uniteWith(o_ring); o_ring.erase()

    # 5. 铰链耳与蝶形螺母锁紧机构 (LOD 300)
    lug_w = max(12.0, W_CLAMP * 0.72)
    lug_h = max(14.0, (D_CLAMP - D_FL) * 1.1)
    # 下侧铰链耳
    o_hinge = BOX(s, L=lug_w, W=lug_h * 0.9, H=lug_w * 0.7).translate((x_mid, 0.0, -D_CLAMP / 2.0 - lug_h * 0.3))
    o_main.uniteWith(o_hinge); o_hinge.erase()

    # 上侧锁紧耳 + 螺杆 + 蝶形螺母
    z_top = D_CLAMP / 2.0 + lug_h * 0.35
    o_ear = BOX(s, L=lug_w, W=lug_h, H=lug_w * 0.75).translate((x_mid, 0.0, z_top))
    o_main.uniteWith(o_ear); o_ear.erase()

    bolt_r = max(3.5, D_FL * 0.055)
    bolt_len = max(18.0, lug_w * 1.35)
    o_bolt = CYLINDER(s, R=bolt_r, H=bolt_len, O=0.0).translate((x_mid, 0.0, z_top - bolt_len * 0.35))
    o_main.uniteWith(o_bolt); o_bolt.erase()

    # 蝶形螺母两翼
    wing_z = z_top + bolt_len * 0.55
    o_nut_hub = CYLINDER(s, R=bolt_r * 1.7, H=bolt_r * 2.2, O=0.0).translate((x_mid, 0.0, wing_z - bolt_r))
    o_wing = BOX(s, L=bolt_r * 6.5, W=bolt_r * 1.3, H=bolt_r * 2.4).translate((x_mid, 0.0, wing_z))
    o_main.uniteWith(o_nut_hub); o_nut_hub.erase()
    o_main.uniteWith(o_wing); o_wing.erase()

    # 6. 贯通卫生级内孔
    o_bore = CYLINDER(s, R=r_in, H=l_tot + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((l_tot, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_TOT', (0.0, 0.0, 0.0), (l_tot, 0.0, 0.0))
