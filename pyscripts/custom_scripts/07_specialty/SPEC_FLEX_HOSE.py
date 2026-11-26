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
          TooltipShort=u"法兰金属软管总成 (GB/T 14525)",
          TooltipLong=u"GB/T 14525 PN16 法兰连接不锈钢金属软管总成，含双端法兰、扣压护套环与波纹网套直管段",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"金属软管总成长度、网套外径及护套环尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"软管总长", TooltipLong=u"法兰端面至端面总长 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_HOSE=LENGTH, TooltipShort=u"网套外径", TooltipLong=u"波纹网套直管段外径 (mm)")
@param(L_COLLAR=LENGTH, TooltipShort=u"护套环长", TooltipLong=u"两端金属扣压护套环长度 (mm)")
def SPEC_FLEX_HOSE(
    s,
    D=114.3,
    L_FACE=600.0,
    D_FL=220.0,
    C_FL=20.0,
    D_HOSE=138.0,
    L_COLLAR=55.0,
    ID=u"SPEC_FLEX_HOSE",
    **kw
):
    u"""法兰金属软管总成 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_HOSE = float(D_HOSE)
    if D_HOSE < 1.0:
        D_HOSE = 1.0
    L_COLLAR = max(25.0, min(L_FACE * 0.2, float(L_COLLAR)))

    half_l = L_FACE / 2.0
    r_fl = D_FL / 2.0
    r_hose = D_HOSE / 2.0
    r_collar = r_hose * 1.12

    # 1. 双端法兰
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 两端扣压护套环
    o_col1 = CYLINDER(s, R=r_collar, H=L_COLLAR + 4.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 2.0), 0.0, 0.0))
    o_main.uniteWith(o_col1)
    o_col1.erase()

    o_col2 = CYLINDER(s, R=r_collar, H=L_COLLAR + 4.0, O=0.0).rotateY(90.0).translate((half_l - C_FL - L_COLLAR - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_col2)
    o_col2.erase()

    # 3. 波纹网套直管段（核心网套管 + 均匀细环肋表现编织波纹质感）
    flex_span = max(40.0, L_FACE - 2.0 * (C_FL + L_COLLAR))
    o_tube = CYLINDER(s, R=r_hose * 0.94, H=flex_span + 12.0, O=0.0).rotateY(90.0).translate((-(flex_span / 2.0 + 6.0), 0.0, 0.0))
    o_main.uniteWith(o_tube)
    o_tube.erase()

    n_ribs = 12
    pitch = flex_span / float(n_ribs)
    r_rib = min(pitch * 0.28, r_hose * 0.08)
    r_rib = max(3.0, r_rib)
    x0 = -flex_span / 2.0 + pitch / 2.0
    for i in range(n_ribs):
        rx = x0 + i * pitch
        o_rib = TORUS(s, R1=r_hose - r_rib, R2=r_rib).rotateY(90.0).translate((rx, 0.0, 0.0))
        o_main.uniteWith(o_rib)
        o_rib.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('D_HOSE', (0.0, 0.0, -r_hose), (0.0, 0.0, r_hose))
