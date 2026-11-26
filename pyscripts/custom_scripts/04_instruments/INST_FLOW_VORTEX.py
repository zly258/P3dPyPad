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
          TooltipShort=u"法兰式涡街流量计 (JB/T 9249)",
          TooltipLong=u"化工法兰式涡街流量计，含双端法兰测量管、旋涡发生体加强座、带散热片隔离颈及顶部防爆双腔圆筒表头",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"涡街流量计面距、法兰及表头总高尺寸")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至表头顶面高度 (mm)", Ask4Dist=True)
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"顶部防爆圆筒表头外径 (mm)")
def INST_FLOW_VORTEX(
    s,
    D=88.9,
    L_FACE=200.0,
    D_FL=200.0,
    C_FL=20.0,
    H_TOP=365.0,
    D_HEAD=118.0,
    ID=u"INST_FLOW_VORTEX",
    **kw
):
    u"""法兰式涡街流量计 (Port 1: X=-L/2, Port 2: X=+L/2, 散热颈与双腔表头在 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0
    D_HEAD = max(92.0, float(D_HEAD))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_head = D_HEAD / 2.0
    z_head_c = H_TOP - r_head

    # 1. 双端法兰与表体测量管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_tube = CYLINDER(s, R=r_pipe * 1.18, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_tube)
    o_tube.erase()

    # 2. 旋涡发生体顶部加强座 + 阶梯散热隔离颈
    o_boss = CYLINDER(s, R=max(34.0, r_pipe * 0.72), H=46.0, O=0.0).translate((0.0, 0.0, r_pipe * 0.75))
    o_main.uniteWith(o_boss)
    o_boss.erase()
    z_neck_bot = r_pipe * 0.75 + 36.0
    h_neck = max(80.0, z_head_c - z_neck_bot)
    o_neck = CYLINDER(s, R=22.0, H=h_neck, O=0.0).translate((0.0, 0.0, z_neck_bot))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    # 3片高温散热片环
    for i in range(3):
        zf = z_neck_bot + h_neck * (0.28 + i * 0.20)
        o_fin = CYLINDER(s, R=38.0, H=8.0, O=0.0).translate((0.0, 0.0, zf))
        o_main.uniteWith(o_fin)
        o_fin.erase()

    # 3. 顶部防爆双腔圆筒表头 + 前液晶窗盖 + 电缆接口
    l_head = D_HEAD * 1.32
    o_head = CYLINDER(s, R=r_head, H=l_head, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0, z_head_c))
    o_main.uniteWith(o_head)
    o_head.erase()
    o_fcap = CYLINDER(s, R=r_head + 6.0, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_fcap)
    o_fcap.erase()
    o_rcap = CYLINDER(s, R=r_head + 4.0, H=14.0, O=0.0).rotateX(-90.0).translate((0.0, l_head / 2.0 - 6.0, z_head_c))
    o_main.uniteWith(o_rcap)
    o_rcap.erase()
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=13.0, H=28.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_head - 6.0), 18.0, z_head_c - 6.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
