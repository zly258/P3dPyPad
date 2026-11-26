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
          TooltipShort=u"防爆紫外/红外火焰探测器 (GB/T 50493)",
          TooltipLong=u"化工防爆 UV/IR 火焰探测器，含重型安装背板、万向节调节支架、倾斜式防爆圆柱主壳、双侧电缆格兰及斜切光学视窗遮阳罩",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"防爆圆柱壳外径与长度、光学视窗罩长度及安装背板尺寸")
@param(D_CASE=LENGTH, TooltipShort=u"防爆壳直径", TooltipLong=u"防爆圆柱主壳外径 (mm)")
@param(L_CASE=LENGTH, TooltipShort=u"防爆壳长度", TooltipLong=u"防爆圆柱主壳轴向长度 (mm)", Ask4Dist=True)
@param(L_HOOD=LENGTH, TooltipShort=u"视窗罩长度", TooltipLong=u"前端倾斜光学视窗遮阳罩长度 (mm)")
@param(W_PLATE=LENGTH, TooltipShort=u"安装板宽", TooltipLong=u"背部固定安装底板宽度 (mm)")
@param(H_PLATE=LENGTH, TooltipShort=u"安装板高", TooltipLong=u"背部固定安装底板高度 (mm)")
def INST_FLAME_DETECTOR(
    s,
    D_CASE=126.0,
    L_CASE=168.0,
    L_HOOD=85.0,
    W_PLATE=150.0,
    H_PLATE=150.0,
    ID=u"INST_FLAME_DETECTOR",
    **kw
):
    u"""防爆紫外/红外火焰探测器 (Port 1 在背部安装板中心 (0, y_back, 0)，探头朝 -Y 并向下倾斜 25°)。"""
    D_CASE = max(90.0, float(D_CASE))
    L_CASE = float(L_CASE)
    if L_CASE < 1.0:
        L_CASE = 1.0
    L_HOOD = max(55.0, float(L_HOOD))
    W_PLATE = float(W_PLATE)
    if W_PLATE < 1.0:
        W_PLATE = 1.0
    H_PLATE = max(110.0, float(H_PLATE))

    r_case = D_CASE / 2.0
    y_back = L_CASE * 0.55 + 68.0
    tilt_deg = -25.0

    # 1. 防爆圆柱主壳 + 后端防爆端盖 + 前端光学窗口基座 (绕 X 轴向下倾斜 25°)
    o_body = CYLINDER(s, R=r_case, H=L_CASE, O=0.0).rotateX(-90.0).translate((0.0, -L_CASE * 0.5, 0.0))
    o_rcap = CYLINDER(s, R=r_case + 6.0, H=20.0, O=0.0).rotateX(-90.0).translate((0.0, L_CASE * 0.5 - 6.0, 0.0))
    o_body.uniteWith(o_rcap)
    o_rcap.erase()

    # 前端光学窗口环 + 倾斜遮阳/防雨罩 + 双通道 UV/IR 光学透镜凸台
    o_fcollar = CYLINDER(s, R=r_case + 7.0, H=22.0, O=0.0).rotateX(-90.0).translate((0.0, -L_CASE * 0.5 - 16.0, 0.0))
    o_body.uniteWith(o_fcollar)
    o_fcollar.erase()

    o_hood = CONE(s, R1=r_case + 4.0, R2=r_case + 14.0, H=L_HOOD).rotateX(-90.0).translate((0.0, -L_CASE * 0.5 - 16.0, 0.0))
    o_body.uniteWith(o_hood)
    o_hood.erase()

    for sx in (-r_case * 0.34, r_case * 0.34):
        o_lens = CYLINDER(s, R=r_case * 0.24, H=18.0, O=0.0).rotateX(-90.0).translate((sx, -L_CASE * 0.5 - 26.0, 0.0))
        o_body.uniteWith(o_lens)
        o_lens.erase()

    # 两侧 M20/M25 防爆电缆格兰接头
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=14.0, H=32.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_case - 4.0), L_CASE * 0.18, 0.0))
        o_body.uniteWith(o_gl)
        o_gl.erase()

    # 顶部万向节连接耳座 (随壳体倾斜前保留在顶部，或先倾斜主壳再与万向节相连)
    o_body.rotateX(tilt_deg)
    o_main = o_body

    # 2. 万向节安装支架 (垂直/水平双轴关节 + 悬臂 + 背部安装底板)
    o_saddle = CORNERBOX(s, L=44.0, W=44.0, H=38.0).translate((-22.0, -22.0, r_case - 12.0))
    o_main.uniteWith(o_saddle)
    o_saddle.erase()

    o_knuckle = CYLINDER(s, R=24.0, H=48.0, O=0.0).rotateY(90.0).translate((-24.0, 0.0, r_case + 26.0))
    o_main.uniteWith(o_knuckle)
    o_knuckle.erase()

    arm_len = y_back - 12.0
    o_arm = CORNERBOX(s, L=32.0, W=arm_len, H=32.0).translate((-16.0, 0.0, r_case + 10.0))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    o_stem = CORNERBOX(s, L=36.0, W=28.0, H=r_case + 26.0).translate((-18.0, y_back - 34.0, 0.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    # 背部重型安装底板 (+Y 侧，Port 1 落在底板背面中心 (0, y_back, 0))
    o_plate = CORNERBOX(s, L=W_PLATE, W=12.0, H=H_PLATE).translate((-W_PLATE / 2.0, y_back - 12.0, -H_PLATE / 2.0))
    o_main.uniteWith(o_plate)
    o_plate.erase()

    s.setPoint((0.0, y_back, 0.0), (0.0, 1.0, 0.0))
    s.setLinearDimension('L_CASE', (0.0, L_CASE * 0.5, 0.0), (0.0, -L_CASE * 0.5, 0.0))
    s.setLinearDimension('W_PLATE', (-W_PLATE / 2.0, y_back, 0.0), (W_PLATE / 2.0, y_back, 0.0))
