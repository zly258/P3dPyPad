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

@activate(Group="Elbow",
          TooltipShort=u"衬氟/衬胶防腐 90°法兰弯头",
          TooltipLong=u"HG/T 20592 PN16 衬氟(PTFE)/衬胶防腐 90度法兰弯头，含双端法兰、加厚衬里法兰翻边与贯通防腐内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"衬氟/衬胶90度法兰弯头主要几何参数")
@param(D=LENGTH, TooltipShort=u"钢管外径", TooltipLong=u"基体弯管公称外径 D (mm)")
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"弯头中心弯曲半径 R (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"配套法兰外径 D_FL (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"配套法兰盘厚度 C_FL (mm)")
@param(D_RF=LENGTH, TooltipShort=u"翻边外径", TooltipLong=u"衬里法兰翻边密封面外径 D_RF (mm)")
@param(T_LIN=LENGTH, TooltipShort=u"衬里厚度", TooltipLong=u"PTFE/橡胶防腐内衬壁厚 T_LIN (mm)")
@param(WT=LENGTH, TooltipShort=u"钢管壁厚", TooltipLong=u"碳钢基体壁厚 WT (mm)")
def FITTING_LINED_PTFE_ELBOW(
    s,
    D=114.3,
    R_BEND=152.0,
    D_FL=220.0,
    C_FL=20.0,
    D_RF=158.0,
    T_LIN=3.5,
    WT=6.0,
    ID=u"FITTING_LINED_PTFE_ELBOW",
    **kw
):
    u"""衬氟/衬胶防腐 90度法兰弯头 (双法兰 + 加厚衬里法兰翻边 + 弯管)。"""
    D = max(25.0, float(D))
    r_out = D / 2.0
    WT = max(2.0, min(r_out * 0.25, float(WT)))
    T_LIN = max(2.0, min(r_out * 0.25, float(T_LIN)))
    r_in = max(5.0, r_out - WT - T_LIN)
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0
    D_FL = max(D + 20.0, float(D_FL))
    C_FL = max(10.0, float(C_FL))
    D_RF = max(D + 4.0, min(D_FL - 4.0, float(D_RF)))
    f_flare = max(3.0, T_LIN + 1.0)

    o_body = ARC3D(s, D=r_out, R=R_BEND, A=90.0)
    p0 = o_body.pointAt(0)
    v0 = o_body.directionAt(0)
    p1 = o_body.pointAt(1)
    v1 = o_body.directionAt(1)

    # 双端法兰盘 (沿各自端面朝弯头内侧)
    o_fl0 = CYLINDER(s, R=D_FL / 2.0, H=C_FL, O=0.0).rotateY(90.0).translate((p0.x(), p0.y(), p0.z()))
    o_fl1 = CYLINDER(s, R=D_FL / 2.0, H=C_FL, O=0.0).rotateX(90.0).translate((p1.x(), p1.y(), p1.z()))
    o_body.uniteWith(o_fl0)
    o_fl0.erase()
    o_body.uniteWith(o_fl1)
    o_fl1.erase()

    # 加厚衬里法兰翻边 (向外突面)
    o_lr0 = CYLINDER(s, R=D_RF / 2.0, H=f_flare, O=0.0).rotateY(90.0).translate((p0.x() - f_flare, p0.y(), p0.z()))
    o_lr1 = CYLINDER(s, R=D_RF / 2.0, H=f_flare, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y(), p1.z()))
    o_body.uniteWith(o_lr0)
    o_lr0.erase()
    o_body.uniteWith(o_lr1)
    o_lr1.erase()

    # 贯通防腐内流道一次差集
    o_in = ARC3D(s, D=r_in, R=R_BEND, A=90.0)
    o_ext0 = CYLINDER(s, R=r_in, H=f_flare + 6.0, O=0.0).rotateY(90.0).translate((p0.x() - f_flare - 3.0, p0.y(), p0.z()))
    o_ext1 = CYLINDER(s, R=r_in, H=f_flare + 6.0, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y() - 3.0, p1.z()))
    o_in.uniteWith(o_ext0)
    o_ext0.erase()
    o_in.uniteWith(o_ext1)
    o_ext1.erase()

    o_body.subtractFrom(o_in)
    o_in.erase()

    pt0 = (p0.x() - f_flare, p0.y(), p0.z())
    pt1 = (p1.x(), p1.y() + f_flare, p1.z())
    s.setPoint(pt0, v0)
    s.setPoint(pt1, v1)
    s.setLinearDimension('R_BEND', (0.0, 0.0, 0.0), (p0.x(), p0.y(), p0.z()))
