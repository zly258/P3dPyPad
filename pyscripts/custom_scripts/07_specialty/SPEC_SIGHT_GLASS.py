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
          TooltipShort=u"直通法兰管道视镜 (HG/T 21619)",
          TooltipLong=u"HG/T 21619 PN16 直通法兰连接管道视镜，含双端法兰、方形/圆筒观察窗体与双侧玻璃压盖环",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"直通管道视镜结构长度与双侧压盖尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_WIN=LENGTH, TooltipShort=u"压盖环外径", TooltipLong=u"双侧视镜玻璃压盖环外径 (mm)")
@param(W_BODY=LENGTH, TooltipShort=u"视镜总宽", TooltipLong=u"双侧玻璃压盖外端面总宽度 (mm)", Ask4Dist=True)
def SPEC_SIGHT_GLASS(
    s,
    D=114.3,
    L_FACE=250.0,
    D_FL=220.0,
    C_FL=20.0,
    D_WIN=140.0,
    W_BODY=210.0,
    ID=u"SPEC_SIGHT_GLASS",
    **kw
):
    u"""直通法兰管道视镜 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 双侧视窗沿 +/-Y)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_WIN = max(D * 0.9, float(D_WIN))
    W_BODY = float(W_BODY)
    if W_BODY < 1.0:
        W_BODY = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_win = D_WIN / 2.0
    half_w = W_BODY / 2.0
    ring_t = max(14.0, C_FL * 0.85)

    # 1. 双端法兰与直通短管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_pipe = CYLINDER(s, R=r_pipe * 1.12, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    # 2. 中央方形观察窗主体
    box_x = min(L_FACE - 2.0 * C_FL - 16.0, D_WIN * 1.05)
    box_x = max(40.0, box_x)
    box_y = max(D * 1.1, W_BODY - 2.0 * ring_t + 6.0)
    box_z = max(D * 1.2, D_WIN * 1.05)
    o_box = BOX(s, L=box_y, W=box_z, H=box_x)
    o_main.uniteWith(o_box)
    o_box.erase()

    # 3. 双侧 (+Y / -Y) 玻璃压盖环与内凹视窗玻璃面
    # CYLINDER 沿 +Z，rotateX(90) 后 +Z -> -Y，rotateX(-90) 后 +Z -> +Y
    o_ring_pos = CYLINDER(s, R=r_win, H=ring_t, O=r_win * 0.62).rotateX(-90.0).translate((0.0, half_w - ring_t, 0.0))
    o_main.uniteWith(o_ring_pos)
    o_ring_pos.erase()

    o_ring_neg = CYLINDER(s, R=r_win, H=ring_t, O=r_win * 0.62).rotateX(90.0).translate((0.0, -(half_w - ring_t), 0.0))
    o_main.uniteWith(o_ring_neg)
    o_ring_neg.erase()

    # 玻璃盘实体（微凹于压盖端面 6mm，保持实体完整）
    o_glass = CYLINDER(s, R=r_win * 0.68, H=W_BODY - 12.0, O=0.0).rotateX(-90.0).translate((0.0, -(half_w - 6.0), 0.0))
    o_main.uniteWith(o_glass)
    o_glass.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('W_BODY', (0.0, -half_w, 0.0), (0.0, half_w, 0.0))
