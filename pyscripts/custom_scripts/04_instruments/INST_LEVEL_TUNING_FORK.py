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
          TooltipShort=u"侧装法兰音叉液位开关 (GB/T 34041)",
          TooltipLong=u"化工侧装法兰式音叉液位开关，含过程连接法兰、特征双叉齿振动探头及外部防爆圆柱接线表头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"音叉液位开关法兰、插入深度及外部表头尺寸")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"侧装过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
@param(L_PROBE=LENGTH, TooltipShort=u"探头插入深", TooltipLong=u"法兰密封面至双叉齿端头总长 (mm)", Ask4Dist=True)
@param(L_EXT=LENGTH, TooltipShort=u"外部表头长", TooltipLong=u"法兰密封面至外部表头端面长度 (mm)", Ask4Dist=True)
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"外部防爆接线表头外径 (mm)")
def INST_LEVEL_TUNING_FORK(
    s,
    D_FL=165.0,
    C_FL=18.0,
    L_PROBE=195.0,
    L_EXT=210.0,
    D_HEAD=102.0,
    ID=u"INST_LEVEL_TUNING_FORK",
    **kw
):
    u"""侧装法兰音叉液位开关 (Port 1 在 X=0 法兰密封面，双叉齿向 -X 伸入容器，表头在 +X)。"""
    D_FL = max(115.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    L_PROBE = float(L_PROBE)
    if L_PROBE < 1.0:
        L_PROBE = 1.0
    L_EXT = float(L_EXT)
    if L_EXT < 1.0:
        L_EXT = 1.0
    D_HEAD = max(78.0, float(D_HEAD))

    r_fl = D_FL / 2.0
    r_head = D_HEAD / 2.0

    # 1. 过程连接法兰 (X=[0, C_FL])
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0)

    # 2. 容器侧音叉底座短管 + 特征双叉齿振动叶片 (-X)
    l_base = L_PROBE * 0.42
    l_tine = L_PROBE - l_base
    o_base = CYLINDER(s, R=24.0, H=l_base + 6.0, O=0.0).rotateY(90.0).translate((-l_base, 0.0, 0.0))
    o_main.uniteWith(o_base)
    o_base.erase()
    # 双叉齿连接肩块
    o_sh = CORNERBOX(s, L=24.0, W=36.0, H=52.0).translate((-l_base - 14.0, -18.0, -26.0))
    o_main.uniteWith(o_sh)
    o_sh.erase()
    # 上下两片清晰饱满的音叉齿 (沿 Z 轴分开，宽在 Y，长在 -X)
    for sz in (-1.0, 1.0):
        z_tine = 11.0 if sz > 0 else -25.0
        o_tine = CORNERBOX(s, L=l_tine + 8.0, W=26.0, H=14.0).translate((-L_PROBE, -13.0, z_tine))
        o_main.uniteWith(o_tine)
        o_tine.erase()

    # 3. 外部隔离颈 + 六角接头 + 防爆圆柱接线表头 (+X)
    l_head = 118.0
    x_head_start = L_EXT - l_head
    o_neck = CYLINDER(s, R=22.0, H=max(40.0, x_head_start - C_FL + 14.0), O=0.0).rotateY(90.0).translate((C_FL - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_hex = CORNERBOX(s, L=26.0, W=46.0, H=46.0).translate((x_head_start - 22.0, -23.0, -23.0))
    o_main.uniteWith(o_hex)
    o_hex.erase()
    o_head = CYLINDER(s, R=r_head, H=l_head - 18.0, O=0.0).rotateY(90.0).translate((x_head_start, 0.0, 0.0))
    o_main.uniteWith(o_head)
    o_head.erase()
    o_cap = CYLINDER(s, R=r_head + 5.0, H=22.0, O=0.0).rotateY(90.0).translate((L_EXT - 22.0, 0.0, 0.0))
    o_main.uniteWith(o_cap)
    o_cap.erase()
    # 底部防爆电缆格兰 (-Z)
    o_gl = CYLINDER(s, R=14.0, H=34.0, O=0.0).translate((x_head_start + l_head * 0.42, 0.0, -r_head - 24.0))
    o_main.uniteWith(o_gl)
    o_gl.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_PROBE', (0.0, 0.0, 0.0), (-L_PROBE, 0.0, 0.0))
    s.setLinearDimension('L_EXT', (0.0, 0.0, 0.0), (L_EXT, 0.0, 0.0))
