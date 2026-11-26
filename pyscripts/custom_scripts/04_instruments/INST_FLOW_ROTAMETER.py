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
          TooltipShort=u"金属管浮子/转子流量计 (JB/T 6844)",
          TooltipLong=u"化工竖直安装金属管浮子/转子流量计，含上下双法兰、金属锥形测量管及侧装磁耦合方形指示表头",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"金属管转子流量计面距、法兰及侧装表头尺寸")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(H_FACE=LENGTH, TooltipShort=u"法兰面距", TooltipLong=u"上下法兰端面距 H (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"上下连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰厚度 (mm)")
@param(W_HEAD=LENGTH, TooltipShort=u"表头宽度", TooltipLong=u"侧装方形指示表头宽度 (mm)")
@param(H_HEAD=LENGTH, TooltipShort=u"表头高度", TooltipLong=u"侧装方形指示表头高度 (mm)")
def INST_FLOW_ROTAMETER(
    s,
    D=60.3,
    H_FACE=250.0,
    D_FL=165.0,
    C_FL=18.0,
    W_HEAD=138.0,
    H_HEAD=146.0,
    ID=u"INST_FLOW_ROTAMETER",
    **kw
):
    u"""金属管浮子/转子流量计 (Port 1 在 Z=-H/2, Port 2 在 Z=+H/2, 指示表头在 -Y)。"""
    D = max(20.0, float(D))
    H_FACE = float(H_FACE)
    if H_FACE < 1.0:
        H_FACE = 1.0
    D_FL = max(D + 45.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    W_HEAD = max(100.0, float(W_HEAD))
    H_HEAD = max(105.0, float(H_HEAD))

    half_h = H_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0

    # 1. 上下双法兰 (竖直沿 Z 轴)
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).translate((0.0, 0.0, -half_h))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).translate((0.0, 0.0, half_h - C_FL))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 竖直金属锥形测量管 (下小上大典型转子管轮廓)
    l_tube = H_FACE - 2.0 * C_FL + 8.0
    o_cone = CONE(s, R1=max(r_pipe * 1.05, 22.0), R2=max(r_pipe * 1.38, 32.0), H=l_tube).translate((0.0, 0.0, -(half_h - C_FL + 4.0)))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 磁耦合支架与侧装方形指示表头 (-Y)
    d_head = 82.0
    y_head_back = -(max(r_pipe * 1.45, 36.0) + 26.0)
    o_br = CORNERBOX(s, L=68.0, W=42.0, H=64.0).translate((-34.0, y_head_back - 6.0, -32.0))
    o_main.uniteWith(o_br)
    o_br.erase()
    o_head = CORNERBOX(s, L=W_HEAD, W=d_head, H=H_HEAD).translate((-W_HEAD / 2.0, y_head_back - d_head, -H_HEAD / 2.0))
    o_main.uniteWith(o_head)
    o_head.erase()
    # 表头前凸起表盘视窗框 (-Y)
    o_win = CORNERBOX(s, L=W_HEAD - 22.0, W=14.0, H=H_HEAD - 24.0).translate((-(W_HEAD - 22.0) / 2.0, y_head_back - d_head - 10.0, -(H_HEAD - 24.0) / 2.0))
    o_main.uniteWith(o_win)
    o_win.erase()
    # 侧向防爆接线格兰 (+X)
    o_gl = CYLINDER(s, R=12.0, H=28.0, O=0.0).rotateY(90.0).translate((W_HEAD / 2.0 - 4.0, y_head_back - d_head * 0.5, -H_HEAD * 0.22))
    o_main.uniteWith(o_gl)
    o_gl.erase()

    s.setPoint((0.0, 0.0, -half_h), (0.0, 0.0, -1.0))
    s.setPoint((0.0, 0.0, half_h), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_FACE', (0.0, 0.0, -half_h), (0.0, 0.0, half_h))
