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

@activate(Group="Valve",
          TooltipShort=u"多回转电动执行机构 (ISO 5210)",
          TooltipLong=u"ISO 5210 智能多回转电动执行机构 (如 AUMA/Rotork 型)，含标准底座法兰、蜗轮箱体、散热筋水平驱动电机、防爆电气控制箱、就地操作面板、手动离合辐条手轮与明杆保护套管",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"多回转电动执行机构外形尺寸")
@param(D_BASE=LENGTH, TooltipShort=u"ISO底座外径", TooltipLong=u"ISO 5210 底部安装法兰外径 (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"总长度", TooltipLong=u"电机端至控制箱端总宽度 L (mm)", Ask4Dist=True)
@param(H_BODY=LENGTH, TooltipShort=u"主体高度", TooltipLong=u"底座面至齿轮箱顶部高度 (mm)", Ask4Dist=True)
@param(H_STEM_TUBE=LENGTH, TooltipShort=u"阀杆套管高", TooltipLong=u"底座面至顶部阀杆护管顶面总高 (mm)", Ask4Dist=True)
@param(D_MOTOR=LENGTH, TooltipShort=u"电机外径", TooltipLong=u"水平驱动电机筒体外径 (mm)")
@param(D_HW=LENGTH, TooltipShort=u"应急手轮直径", TooltipLong=u"侧装/顶装手动离合手轮直径 (mm)")
def ACTUATOR_ELECTRIC_MULTI(
    s,
    D_BASE=175.0,
    L_TOTAL=520.0,
    H_BODY=245.0,
    H_STEM_TUBE=460.0,
    D_MOTOR=155.0,
    D_HW=280.0,
    ID=u"ACTUATOR_ELECTRIC_MULTI",
    **kw
):
    D_BASE = float(D_BASE)
    if D_BASE < 1.0:
        D_BASE = 1.0
    L_TOTAL = max(320.0, float(L_TOTAL))
    H_BODY = max(160.0, float(H_BODY))
    H_STEM_TUBE = float(H_STEM_TUBE)
    if H_STEM_TUBE < 1.0:
        H_STEM_TUBE = 1.0
    D_MOTOR = max(100.0, float(D_MOTOR))
    D_HW = max(160.0, float(D_HW))

    r_base = D_BASE / 2.0
    r_mot = D_MOTOR / 2.0
    z_ctr = H_BODY * 0.56

    # 1. ISO 5210 底部安装法兰 (Port 1 在原点 0,0,0 向下)
    o_main = CYLINDER(s, R=r_base, H=24.0, O=0.0)
    o_neck = CYLINDER(s, R=r_base * 0.72, H=z_ctr, O=0.0).translate((0.0, 0.0, 18.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    # 2. 中央蜗轮齿轮箱主体
    gb_l = max(130.0, D_BASE * 0.85)
    gb_w = max(145.0, D_BASE * 0.92)
    gb_h = H_BODY - 55.0
    o_gb = CORNERBOX(s, L=gb_l, W=gb_w, H=gb_h).translate((-gb_l / 2.0, -gb_w / 2.0, 50.0))
    o_main.uniteWith(o_gb)
    o_gb.erase()

    # 3. 顶部垂直明杆保护套管 (多回转执行器典型标志)
    r_tube = max(24.0, r_base * 0.34)
    o_tube = CYLINDER(s, R=r_tube, H=H_STEM_TUBE - H_BODY + 24.0, O=0.0).translate((0.0, 0.0, H_BODY - 16.0))
    o_main.uniteWith(o_tube)
    o_tube.erase()
    o_tcap = CYLINDER(s, R=r_tube * 1.18, H=16.0, O=0.0).translate((0.0, 0.0, H_STEM_TUBE - 16.0))
    o_main.uniteWith(o_tcap)
    o_tcap.erase()

    # 4. +X 侧水平圆柱形防爆驱动电机 (带 4 道散热筋环)
    mot_len = max(160.0, L_TOTAL * 0.42)
    x_mot_start = gb_l * 0.42
    o_mot = CYLINDER(s, R=r_mot, H=mot_len, O=0.0).rotateY(90.0).translate((x_mot_start, 0.0, z_ctr))
    o_main.uniteWith(o_mot)
    o_mot.erase()
    # 电机尾部风罩圆台
    o_mcap = CONE(s, R1=r_mot, R2=r_mot * 0.72, H=24.0, E=0.0).rotateY(90.0).translate((x_mot_start + mot_len - 2.0, 0.0, z_ctr))
    o_main.uniteWith(o_mcap)
    o_mcap.erase()
    # 4 道散热筋环
    for idx in range(4):
        fx = x_mot_start + mot_len * (0.18 + idx * 0.18)
        o_fin = CYLINDER(s, R=r_mot * 1.07, H=8.0, O=0.0).rotateY(90.0).translate((fx, 0.0, z_ctr))
        o_main.uniteWith(o_fin)
        o_fin.erase()

    # 5. -X 侧智能电气控制与接线腔 (带前倾显示操作面板)
    ctrl_l = max(130.0, L_TOTAL * 0.34)
    ctrl_w = max(140.0, D_MOTOR * 0.96)
    ctrl_h = max(145.0, D_MOTOR * 1.02)
    o_ctrl = CORNERBOX(s, L=ctrl_l, W=ctrl_w, H=ctrl_h).translate((-(gb_l * 0.42 + ctrl_l), -ctrl_w / 2.0, z_ctr - ctrl_h / 2.0))
    o_main.uniteWith(o_ctrl)
    o_ctrl.erase()

    # 接线端盖圆筒
    o_term = CYLINDER(s, R=ctrl_h * 0.38, H=48.0, O=0.0).rotateY(90.0).translate((-(gb_l * 0.42 + ctrl_l + 42.0), 0.0, z_ctr))
    o_main.uniteWith(o_term)
    o_term.erase()

    # 就地旋钮与显示屏凸台 (-Y 正面)
    o_disp = CORNERBOX(s, L=ctrl_l * 0.72, W=26.0, H=ctrl_h * 0.62).translate((-(gb_l * 0.42 + ctrl_l * 0.86), -(ctrl_w / 2.0 + 20.0), z_ctr - ctrl_h * 0.31))
    o_main.uniteWith(o_disp)
    o_disp.erase()

    # 6. 侧面手动离合应急辐条手轮 (+Y 侧)
    y_hw = gb_w / 2.0 + 68.0
    o_hw_shaft = CYLINDER(s, R=max(14.0, r_base * 0.18), H=78.0, O=0.0).rotateX(-90.0).translate((0.0, gb_w / 2.0 - 8.0, z_ctr))
    o_main.uniteWith(o_hw_shaft)
    o_hw_shaft.erase()

    r_hw = D_HW / 2.0
    r_rim = max(9.0, D_HW * 0.042)
    o_hw = TORUS(s, R1=r_hw - r_rim, R2=r_rim)
    o_hub = CYLINDER(s, R=max(20.0, r_base * 0.26), H=24.0, O=0.0).translate((0.0, 0.0, -12.0))
    o_hw.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, 0.0)).rotateZ(ang)
        o_hw.uniteWith(o_sp)
        o_sp.erase()
    o_hw.rotateX(90.0).translate((0.0, y_hw, z_ctr))
    o_main.uniteWith(o_hw)
    o_hw.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('D_BASE', (-r_base, 0.0, 0.0), (r_base, 0.0, 0.0))
    s.setLinearDimension('H_STEM_TUBE', (0.0, 0.0, 0.0), (0.0, 0.0, H_STEM_TUBE))
