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
          TooltipShort=u"经典文丘里流量计 (GB/T 2624.4 / ISO 5167)",
          TooltipLong=u"化工经典文丘里管流量计，含双端法兰、入口圆筒段、收缩锥、喉管段、长扩散恢复锥及上下游环形取压室与取压嘴",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"文丘里流量计面距、喉径、法兰及取压尺寸")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"入口/出口连接管道外径 D (mm)")
@param(D_THROAT=LENGTH, TooltipShort=u"喉管外径", TooltipLong=u"文丘里喉管段外径 d (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"总结构长", TooltipLong=u"进出口法兰端面总距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"进出口端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
def INST_FLOW_VENTURI(
    s,
    D=168.3,
    D_THROAT=106.0,
    L_FACE=920.0,
    D_FL=285.0,
    C_FL=22.0,
    ID=u"INST_FLOW_VENTURI",
    **kw
):
    u"""经典文丘里流量计 (Port 1 入口在 X=-L/2, Port 2 出口在 X=+L/2, 上下游取压嘴在 +Z)。"""
    D = max(50.0, float(D))
    D_THROAT = max(28.0, min(D * 0.78, float(D_THROAT)))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 60.0, float(D_FL))
    C_FL = max(16.0, float(C_FL))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_th = D_THROAT / 2.0
    r_fl = D_FL / 2.0
    l_net = L_FACE - 2.0 * C_FL

    # 轴向分段比例: 入口段 16%, 收缩锥 16%, 喉管段 14%, 长扩散锥 54%
    l_in = l_net * 0.16
    l_conv = l_net * 0.16
    l_th = l_net * 0.14
    l_diff = l_net - l_in - l_conv - l_th

    x0 = -half_l
    x1 = x0 + C_FL
    x2 = x1 + l_in
    x3 = x2 + l_conv
    x4 = x3 + l_th
    x5 = half_l - C_FL

    # 1. 双端法兰
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((x0, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((x5, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 入口圆柱段 + 收缩锥 + 喉管圆柱段 + 长扩散恢复锥
    o_in = CYLINDER(s, R=r_pipe, H=l_in + 6.0, O=0.0).rotateY(90.0).translate((x1 - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_in)
    o_in.erase()
    o_conv = CONE(s, R1=r_pipe, R2=r_th, H=l_conv + 4.0).rotateY(90.0).translate((x2 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_conv)
    o_conv.erase()
    o_th = CYLINDER(s, R=r_th, H=l_th + 4.0, O=0.0).rotateY(90.0).translate((x3 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_th)
    o_th.erase()
    o_diff = CONE(s, R1=r_th, R2=r_pipe, H=l_diff + 6.0).rotateY(90.0).translate((x4 - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_diff)
    o_diff.erase()

    # 3. 入口段与喉管段均压环 + 上(+Z)下(-Z)取压嘴
    x_tap1 = x1 + l_in * 0.52
    x_tap2 = x3 + l_th * 0.50
    for xt, rr in ((x_tap1, r_pipe), (x_tap2, r_th)):
        o_pr = CYLINDER(s, R=rr + 18.0, H=42.0, O=0.0).rotateY(90.0).translate((xt - 21.0, 0.0, 0.0))
        o_main.uniteWith(o_pr)
        o_pr.erase()
        # 顶部取压嘴 (+Z) 与 底部排污/取压嘴 (-Z)
        o_tup = CYLINDER(s, R=15.0, H=62.0, O=0.0).translate((xt, 0.0, rr + 8.0))
        o_main.uniteWith(o_tup)
        o_tup.erase()
        o_tfl = CYLINDER(s, R=26.0, H=14.0, O=0.0).translate((xt, 0.0, rr + 62.0))
        o_main.uniteWith(o_tfl)
        o_tfl.erase()
        o_tdn = CYLINDER(s, R=14.0, H=46.0, O=0.0).translate((xt, 0.0, -(rr + 50.0)))
        o_main.uniteWith(o_tdn)
        o_tdn.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('D_THROAT', (x_tap2, 0.0, -r_th), (x_tap2, 0.0, r_th))
