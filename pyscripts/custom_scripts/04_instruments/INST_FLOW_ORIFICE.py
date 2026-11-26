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
          TooltipShort=u"孔板流量计法兰组 (GB/T 2624 / ASME B16.36)",
          TooltipLong=u"化工对焊孔板流量计法兰组，含一对重型带取压嘴孔板法兰、夹持节流孔板及顶出位号标识手柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BW")
@group("MainDimensions", TooltipLong=u"孔板法兰组总长、法兰外径、厚度及手柄高度")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"法兰组总长", TooltipLong=u"对焊端面总长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"重型孔板法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"单法兰厚", TooltipLong=u"单片重型孔板法兰厚度 (mm)")
@param(H_HANDLE=LENGTH, TooltipShort=u"手柄总高", TooltipLong=u"管道中心至孔板标识手柄顶高 (mm)", Ask4Dist=True)
def INST_FLOW_ORIFICE(
    s,
    D=114.3,
    L_TOTAL=224.0,
    D_FL=254.0,
    C_FL=38.0,
    H_HANDLE=255.0,
    ID=u"INST_FLOW_ORIFICE",
    **kw
):
    u"""孔板流量计法兰组 (Port 1: X=-L/2, Port 2: X=+L/2, 孔板手柄在 +Z, 取压嘴在 -Y)。"""
    D = max(32.0, float(D))
    L_TOTAL = float(L_TOTAL)
    if L_TOTAL < 1.0:
        L_TOTAL = 1.0
    D_FL = max(D + 75.0, float(D_FL))
    C_FL = max(28.0, float(C_FL))
    H_HANDLE = float(H_HANDLE)
    if H_HANDLE < 1.0:
        H_HANDLE = 1.0

    half_l = L_TOTAL / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    t_plate = 10.0

    # 1. 中央夹持节流孔板圆片 + 突出位号手柄 (+Z)
    o_main = CYLINDER(s, R=r_fl * 0.82, H=t_plate, O=0.0).rotateY(90.0).translate((-t_plate / 2.0, 0.0, 0.0))
    w_tab = max(36.0, D * 0.34)
    o_tab = CORNERBOX(s, L=t_plate, W=w_tab, H=H_HANDLE).translate((-t_plate / 2.0, -w_tab / 2.0, 0.0))
    o_main.uniteWith(o_tab)
    o_tab.erase()
    # 手柄顶部圆角铭牌头
    o_tip = CYLINDER(s, R=w_tab * 0.5, H=t_plate, O=0.0).rotateY(90.0).translate((-t_plate / 2.0, 0.0, H_HANDLE - w_tab * 0.5))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    # 2. 左右重型孔板法兰盘 + 对焊锥颈 + 径向取压嘴 (-Y)
    gap = t_plate / 2.0 + 1.5
    l_neck = max(24.0, half_l - gap - C_FL)
    for sx in (-1.0, 1.0):
        x_fl_start = gap if sx > 0 else -(gap + C_FL)
        o_fl = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((x_fl_start, 0.0, 0.0))
        o_main.uniteWith(o_fl)
        o_fl.erase()
        # 对焊锥颈
        if sx > 0:
            o_nk = CONE(s, R1=r_pipe * 1.28, R2=r_pipe, H=l_neck + 2.0).rotateY(90.0).translate((gap + C_FL - 2.0, 0.0, 0.0))
        else:
            o_nk = CONE(s, R1=r_pipe, R2=r_pipe * 1.28, H=l_neck + 2.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
        o_main.uniteWith(o_nk)
        o_nk.erase()
        # 径向取压短节与六角丝堵/取压嘴 (-Y)
        x_tap = sx * (gap + C_FL * 0.52)
        o_tap = CYLINDER(s, R=15.0, H=52.0, O=0.0).rotateX(90.0).translate((x_tap, -(r_fl - 10.0), 0.0))
        o_main.uniteWith(o_tap)
        o_tap.erase()
        o_tnut = CORNERBOX(s, L=24.0, W=22.0, H=24.0).translate((x_tap - 12.0, -(r_fl + 54.0), -12.0))
        o_main.uniteWith(o_tnut)
        o_tnut.erase()

    # 3. 中央贯通内径连接柱 (确保两法兰与孔板刚性一体)
    o_core = CYLINDER(s, R=r_pipe * 0.96, H=L_TOTAL - 4.0, O=0.0).rotateY(90.0).translate((-(half_l - 2.0), 0.0, 0.0))
    o_main.uniteWith(o_core)
    o_core.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_TOTAL', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_HANDLE', (0.0, 0.0, 0.0), (0.0, 0.0, H_HANDLE))
