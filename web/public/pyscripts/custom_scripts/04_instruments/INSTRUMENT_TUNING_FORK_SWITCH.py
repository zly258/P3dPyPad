# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="1",
    TooltipShort=u"防爆音叉液位开关",
    TooltipLong=u"化工储罐与缓冲罐高/低液位联锁报警用防爆音叉液位开关 (LSH/LSL，符合 HG/T 21584，含过程安装法兰、六角隔热延长颈、斜置双腔防爆铝壳体与下部双平行不锈钢音叉谐振叉体)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(FL_OD=LENGTH, TooltipShort=u"过程法兰径", TooltipLong=u"音叉液位开关安装法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程法兰厚度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"表头高度", TooltipLong=u"法兰底面至上部防爆壳体顶部的高度 (mm)")
@param(L_FORK=LENGTH, TooltipShort=u"音叉插入深", TooltipLong=u"法兰底面以下不锈钢延伸管与音叉叉体总深 (mm)")
@param(D_HEAD=LENGTH, TooltipShort=u"防爆壳直径", TooltipLong=u"上部压铸铝防爆转换壳体直径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"过程法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"防爆音叉液位开关位号编码")
def INSTRUMENT_TUNING_FORK_SWITCH(s, FL_OD=165.0, FL_T=20.0, H_TOP=215.0, L_FORK=195.0, D_HEAD=112.0, NBOLTS=4, ID=u"LSH-116-DN50", **kw):
    FL_OD = max(100.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H_TOP = max(150.0, float(H_TOP))
    L_FORK = max(100.0, float(L_FORK))
    D_HEAD = max(85.0, float(D_HEAD))
    NBOLTS = max(4, int(NBOLTS))

    r_fl = FL_OD / 2.0
    r_head = D_HEAD / 2.0

    # 1. 过程连接法兰 (底面位于 Z=0, Port 1 朝向 -Z) + 法兰螺栓孔
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    r_bcd = r_fl * 0.75
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=8.0, H=FL_T + 4.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 上部六角锁紧座 + 散热颈 + 防爆双腔圆柱表头与侧面防爆格兰头
    z_head_c = H_TOP - r_head
    o_hex = BOX(s, L=44.0, W=26.0, H=44.0).translate((0.0, 0.0, FL_T + 11.0))
    o_neck = CYLINDER(s, R=18.0, H=z_head_c - FL_T, O=0.0).translate((0.0, 0.0, FL_T))
    o_head = CYLINDER(s, R=r_head, H=115.0, O=0.0).rotateX(90.0).translate((0.0, 57.5, z_head_c))
    o_cap = CYLINDER(s, R=r_head * 1.06, H=18.0, O=0.0).rotateX(90.0).translate((0.0, -45.0, z_head_c))
    o_gland = CYLINDER(s, R=15.0, H=42.0, O=0.0).rotateY(90.0).translate((r_head - 5.0, 0.0, z_head_c - 12.0))
    for p in (o_hex, o_neck, o_head, o_cap, o_gland):
        o_m.uniteWith(p); p.erase()

    # 3. 法兰下方不锈钢延伸套管 + 音叉基座圆锥 + 双平行扁平音叉谐振叉翼 (Z: [-L_FORK, 0])
    l_tube = L_FORK * 0.52
    l_tine = L_FORK * 0.48
    o_ext = CYLINDER(s, R=16.0, H=l_tube + 10.0, O=0.0).translate((0.0, 0.0, -l_tube))
    o_root = BOX(s, L=38.0, W=20.0, H=18.0).translate((0.0, 0.0, -l_tube - 6.0))
    o_m.uniteWith(o_ext); o_ext.erase()
    o_m.uniteWith(o_root); o_root.erase()

    for sy in (-1.0, 1.0):
        tine = BOX(s, L=6.0, W=l_tine, H=18.0).translate((0.0, sy * 12.0, -l_tube - l_tine * 0.5))
        o_m.uniteWith(tine); tine.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension("L_FORK", (0.0, 0.0, -L_FORK), (0.0, 0.0, 0.0))
    s.setLinearDimension("FL_OD", (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
