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
          TooltipShort=u"对焊环松套法兰 (HG/T 20592 PJ/SE PN16)",
          TooltipLong=u"HG/T 20592-2009 PN16 对焊环松套法兰(PJ/SE)，由翻边对焊短节、翻边密封环与活套法兰盘组成，台阶层次清晰",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"对焊环松套法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"对焊短节管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"活套盘外径", TooltipLong=u"活套法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"活套盘厚度", TooltipLong=u"活套法兰盘厚度 C (mm)")
@param(D_LAP=LENGTH, TooltipShort=u"翻边环外径", TooltipLong=u"对焊环翻边密封面外径 d (mm)")
@param(T_LAP=LENGTH, TooltipShort=u"翻边环厚度", TooltipLong=u"翻边密封环厚度 F (mm)")
@param(H_STUB=LENGTH, TooltipShort=u"短节总长", TooltipLong=u"对焊环短节总长度 h (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"短节根径", TooltipLong=u"对焊环根部外径 N (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"贯通内孔直径 B (mm)")
def FLANGE_LJ_HGT20592(
    s,
    D=114.3,
    D_FL=220.0,
    C_THK=20.0,
    D_LAP=158.0,
    T_LAP=12.0,
    H_STUB=56.0,
    N_HUB=124.0,
    B_ID=106.3,
    ID=u"FLANGE_LJ_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 对焊环松套法兰 (Port 1 在 X=0 翻边密封面, Port 2 在 X=H_STUB 对焊端)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 36.0, float(D_FL))
    T_LAP = max(4.0, float(T_LAP))
    C_THK = max(8.0, float(C_THK))
    H_STUB = float(H_STUB)
    if H_STUB < 1.0:
        H_STUB = 1.0
    N_HUB = max(D + 2.0, min(D_FL - 20.0, float(N_HUB)))
    D_LAP = max(N_HUB + 8.0, min(D_FL - 12.0, float(D_LAP)))
    B_ID = max(4.0, min(D - 2.0, float(B_ID)))

    r_in = B_ID / 2.0
    # 1. 前端翻边密封环 (X: 0 -> T_LAP)
    o_main = CYLINDER(s, R=D_LAP / 2.0, H=T_LAP + 0.3, O=r_in).rotateY(90.0)

    # 2. 活套法兰盘 (X: T_LAP -> T_LAP + C_THK，在贴合面微搭接保证单实体，外径明显大于翻边环)
    o_ring = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=N_HUB / 2.0 - 0.3).rotateY(90.0).translate((T_LAP, 0.0, 0.0))
    o_main.uniteWith(o_ring)
    o_ring.erase()

    # 3. 翻边短节直段 + 锥形过渡至对焊管端 (X: T_LAP -> H_STUB)
    straight_len = C_THK
    o_st = CYLINDER(s, R=N_HUB / 2.0, H=straight_len + 0.4, O=r_in).rotateY(90.0).translate((T_LAP - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_st)
    o_st.erase()

    tail_x0 = T_LAP + straight_len
    tail_span = max(6.0, H_STUB - tail_x0)
    lip_h = min(6.0, tail_span * 0.35)
    cone_h = max(3.0, tail_span - lip_h)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.2, E=0.0).rotateY(90.0).translate((tail_x0 - 0.2, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D / 2.0, H=lip_h + 0.2, O=0.0).rotateY(90.0).translate((tail_x0 + cone_h - 0.2, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 4. 贯通内孔
    o_bore = CYLINDER(s, R=r_in, H=H_STUB + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_STUB, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_STUB', (0.0, 0.0, 0.0), (H_STUB, 0.0, 0.0))
