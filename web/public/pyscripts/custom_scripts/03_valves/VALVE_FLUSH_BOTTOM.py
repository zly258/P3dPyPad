# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"反应釜底45度放料阀",
    TooltipLong=u"化工反应釜与结晶罐底无死角排料用 45° 斜Y型上展式/下展式法兰放料阀 (FL41H / HG5-89，含加大上法兰接釜底凸台、45°斜向出料法兰支管、柱塞阀瓣、开窗支架与下部操作手轮)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"出料口管径", TooltipLong=u"侧向出料管外径 (mm)")
@param(FL_TOP=LENGTH, TooltipShort=u"釜底法兰径", TooltipLong=u"顶部与反应釜底出料口连接的加大法兰外径 (mm)")
@param(FL_OUT=LENGTH, TooltipShort=u"出料法兰径", TooltipLong=u"45°侧向出料接管法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_BODY=LENGTH, TooltipShort=u"阀体高度", TooltipLong=u"顶部釜底法兰面至阀杆手轮底部的总高度 (mm)")
@param(W_DIA=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"下部操作手轮直径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"釜底放料阀图集型号编码")
def VALVE_FLUSH_BOTTOM(s, D=88.9, FL_TOP=220.0, FL_OUT=200.0, FL_T=22.0, H_BODY=420.0, W_DIA=220.0, ID=u"FL41H-DN100x80", **kw):
    D = max(25.0, float(D))
    FL_OUT = max(D + 55.0, float(FL_OUT))
    FL_TOP = max(FL_OUT + 15.0, float(FL_TOP))
    FL_T = max(14.0, float(FL_T))
    H_BODY = max(280.0, float(H_BODY))
    W_DIA = max(140.0, float(W_DIA))

    r_pipe = D / 2.0
    r_fl_t = FL_TOP / 2.0
    r_fl_o = FL_OUT / 2.0

    # 1. 顶部接反应釜底大法兰 (Port 1 at Z=0, 朝向 +Z) + 竖直放料腔与 45° 斜向下支架主轴
    o_m = CYLINDER(s, R=r_fl_t, H=FL_T, O=0.0).translate((0.0, 0.0, -FL_T))
    h_throat = H_BODY * 0.44
    o_throat = CYLINDER(s, R=r_pipe * 1.28, H=h_throat, O=0.0).translate((0.0, 0.0, -h_throat))
    o_hub = SPHERE(s, R=r_pipe * 1.48).translate((0.0, 0.0, -h_throat * 0.72))
    o_m.uniteWith(o_throat); o_throat.erase()
    o_m.uniteWith(o_hub); o_hub.erase()

    # 2. 45° 侧向下倾斜出料法兰支管 (朝向 +X, -Z, Port 2)
    z_branch = -h_throat * 0.72
    len_out = r_pipe * 1.8 + 85.0
    o_br = CYLINDER(s, R=r_pipe * 1.08, H=len_out - FL_T, O=0.0).rotateY(135.0).translate((0.0, 0.0, z_branch))
    c45 = math.sqrt(0.5)
    ox = (len_out - FL_T) * c45
    oz = z_branch - (len_out - FL_T) * c45
    o_fl_out = CYLINDER(s, R=r_fl_o, H=FL_T, O=0.0).rotateY(135.0).translate((ox, 0.0, oz))
    o_m.uniteWith(o_br); o_br.erase()
    o_m.uniteWith(o_fl_out); o_fl_out.erase()

    # 3. 下部填料函法兰 + 双柱支架 + 底部操作手轮 (位于 Z = -H_BODY)
    z_gland = -h_throat
    h_yoke = H_BODY - h_throat - 24.0
    o_gfl = CYLINDER(s, R=r_pipe * 1.45, H=22.0, O=0.0).translate((0.0, 0.0, z_gland - 16.0))
    o_stem = CYLINDER(s, R=14.0, H=H_BODY - h_throat, O=0.0).translate((0.0, 0.0, -H_BODY))
    o_ybot = CYLINDER(s, R=r_pipe * 0.85, H=24.0, O=0.0).translate((0.0, 0.0, -H_BODY + 18.0))
    for p in (o_gfl, o_stem, o_ybot):
        o_m.uniteWith(p); p.erase()

    for sy in (-1.0, 1.0):
        leg = BOX(s, L=16.0, W=h_yoke, H=26.0).translate((0.0, sy * r_pipe * 0.95, z_gland - h_yoke * 0.5))
        o_m.uniteWith(leg); leg.erase()

    r_w = W_DIA / 2.0
    w_thk = 16.0
    z_w = -H_BODY + 12.0
    o_rim = TORUS(s, R1=r_w - w_thk * 0.5, R2=w_thk * 0.5).translate((0.0, 0.0, z_w))
    o_m.uniteWith(o_rim); o_rim.erase()
    for k in range(4):
        spk = BOX(s, L=14.0, W=12.0, H=r_w * 1.85).rotateZ(k * 45.0).translate((0.0, 0.0, z_w))
        o_m.uniteWith(spk); spk.erase()

    px = len_out * c45
    pz = z_branch - len_out * c45
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setPoint((px, 0.0, pz), (c45, 0.0, -c45))
    s.setLinearDimension("H_BODY", (0.0, 0.0, -H_BODY), (0.0, 0.0, 0.0))
    s.setLinearDimension("FL_TOP", (-r_fl_t, 0.0, 0.0), (r_fl_t, 0.0, 0.0))
