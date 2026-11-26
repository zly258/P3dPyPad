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

@activate(Group="Flange",
          TooltipShort=u"绝缘法兰总成 (Insulating Flange Kit)",
          TooltipLong=u"管道阴极保护绝缘法兰总成，由对称双带颈对焊法兰、中间突出绝缘密封垫盘与双侧绝缘套管视觉台阶组成",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"绝缘法兰总成主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"两端对焊管道外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"双法兰盘外径 D (mm)")
@param(K_PCD=LENGTH, TooltipShort=u"绝缘套分布圆", TooltipLong=u"绝缘套管/垫圈视觉台阶分布圆直径 K (mm)")
@param(C_THK=LENGTH, TooltipShort=u"单盘厚度", TooltipLong=u"单个法兰盘厚度 C (mm)")
@param(H_FL=LENGTH, TooltipShort=u"单法兰高", TooltipLong=u"单侧带颈法兰长度 H (mm)", Ask4Dist=True)
@param(T_INS=LENGTH, TooltipShort=u"绝缘垫盘厚", TooltipLong=u"中间突出绝缘垫盘厚度 (mm)")
@param(D_INS=LENGTH, TooltipShort=u"绝缘垫盘外径", TooltipLong=u"中间突出绝缘垫盘外径 (大于法兰外径以清晰示警)")
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"锥形焊颈根部外径 N (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"贯通内孔直径 B (mm)")
def FLANGE_INSULATING_KIT(
    s,
    D=114.3,
    D_FL=220.0,
    K_PCD=180.0,
    C_THK=20.0,
    H_FL=52.0,
    T_INS=8.0,
    D_INS=236.0,
    N_HUB=131.0,
    B_ID=106.3,
    ID=u"FLANGE_INSULATING_KIT",
    **kw
):
    u"""绝缘法兰总成 (Port 1 在 X=0 左焊端, Port 2 在 X=2*H_FL+T_INS 右焊端)。"""
    D = max(20.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    K_PCD = max(D + 22.0, min(D_FL - 18.0, float(K_PCD)))
    C_THK = max(10.0, float(C_THK))
    H_FL = float(H_FL)
    if H_FL < 1.0:
        H_FL = 1.0
    T_INS = max(4.0, float(T_INS))
    D_INS = max(D_FL + 8.0, float(D_INS))
    N_HUB = max(D + 4.0, min(K_PCD - 14.0, float(N_HUB)))
    B_ID = max(6.0, min(D - 2.0, float(B_ID)))

    l_tot = 2.0 * H_FL + T_INS
    r_in = B_ID / 2.0
    neck_span = H_FL - C_THK
    lip_h = min(6.0, neck_span * 0.25)
    cone_h = max(4.0, neck_span - lip_h)

    # 1. 中间突出绝缘垫盘 (X: H_FL -> H_FL + T_INS)
    o_main = CYLINDER(s, R=D_INS / 2.0, H=T_INS + 0.4, O=0.0).rotateY(90.0).translate((H_FL - 0.2, 0.0, 0.0))

    # 2. 左侧对焊法兰 (X: 0 -> H_FL)
    o_l_lip = CYLINDER(s, R=D / 2.0, H=lip_h + 0.2, O=0.0).rotateY(90.0)
    o_l_cone = CONE(s, R1=D / 2.0, R2=N_HUB / 2.0, H=cone_h + 0.3, E=0.0).rotateY(90.0).translate((lip_h - 0.1, 0.0, 0.0))
    o_l_disc = CYLINDER(s, R=D_FL / 2.0, H=C_THK + 0.3, O=0.0).rotateY(90.0).translate((H_FL - C_THK - 0.1, 0.0, 0.0))
    o_main.uniteWith(o_l_disc)
    o_l_disc.erase()
    o_main.uniteWith(o_l_cone)
    o_l_cone.erase()
    o_main.uniteWith(o_l_lip)
    o_l_lip.erase()

    # 3. 右侧对焊法兰 (X: H_FL + T_INS -> l_tot)
    rx0 = H_FL + T_INS
    o_r_disc = CYLINDER(s, R=D_FL / 2.0, H=C_THK + 0.3, O=0.0).rotateY(90.0).translate((rx0 - 0.2, 0.0, 0.0))
    o_r_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.3, E=0.0).rotateY(90.0).translate((rx0 + C_THK - 0.2, 0.0, 0.0))
    o_r_lip = CYLINDER(s, R=D / 2.0, H=lip_h + 0.2, O=0.0).rotateY(90.0).translate((l_tot - lip_h - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_r_disc)
    o_r_disc.erase()
    o_main.uniteWith(o_r_cone)
    o_r_cone.erase()
    o_main.uniteWith(o_r_lip)
    o_r_lip.erase()

    # 4. 双侧绝缘套管与绝缘垫圈视觉台阶 (6 处均布，LOD300 清晰表达绝缘组件)
    r_pcd = K_PCD / 2.0
    r_slv = max(6.0, min(12.0, (D_FL - K_PCD) * 0.30))
    slv_protrude = max(5.0, C_THK * 0.32)
    slv_x0 = H_FL - C_THK - slv_protrude
    slv_len = 2.0 * C_THK + T_INS + 2.0 * slv_protrude
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0) + math.pi / 6.0
        py = r_pcd * math.cos(ang)
        pz = r_pcd * math.sin(ang)
        o_slv = CYLINDER(s, R=r_slv, H=slv_len, O=0.0).rotateY(90.0).translate((slv_x0, py, pz))
        o_main.uniteWith(o_slv)
        o_slv.erase()

    # 5. 贯通内通孔
    o_bore = CYLINDER(s, R=r_in, H=l_tot + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((l_tot, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_FL', (0.0, 0.0, 0.0), (H_FL, 0.0, 0.0))
