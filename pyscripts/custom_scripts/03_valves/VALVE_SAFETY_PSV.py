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
          TooltipShort=u"弹簧全启式安全阀 (API 526)",
          TooltipLong=u"API 526 弹簧全启式安全阀 (PSV)，含90度水平面异径角式突面法兰、铸钢阀体、细高锥形弹簧罩与顶部封闭顶帽；两口成90度，请连接在管端(端点)或设备管嘴，不可直接插入连续直管中间",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"弹簧全启式安全阀外形尺寸")
@param(D_IN=LENGTH, TooltipShort=u"入口管径外径", TooltipLong=u"底部入口连接管外径 (mm)")
@param(D_OUT=LENGTH, TooltipShort=u"出口管径外径", TooltipLong=u"侧面出口连接管外径 (mm)")
@param(H_IN=LENGTH, TooltipShort=u"中心至底口距", TooltipLong=u"出口中心线至底部入口法兰面距离 (mm)", Ask4Dist=True)
@param(L_OUT=LENGTH, TooltipShort=u"中心至侧口距", TooltipLong=u"入口中心线至右侧出口法兰面距离 (mm)", Ask4Dist=True)
@param(D_FL_IN=LENGTH, TooltipShort=u"入口法兰外径", TooltipLong=u"底部入口法兰外径 (mm)")
@param(D_FL_OUT=LENGTH, TooltipShort=u"出口法兰外径", TooltipLong=u"侧面出口法兰外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"中心至顶帽高", TooltipLong=u"出口中心线至安全阀顶帽顶面高度 (mm)", Ask4Dist=True)
def VALVE_SAFETY_PSV(
    s,
    D_IN=88.9,
    D_OUT=114.3,
    H_IN=156.0,
    L_OUT=165.0,
    D_FL_IN=200.0,
    D_FL_OUT=220.0,
    H_TOP=460.0,
    ID=u"VALVE_SAFETY_PSV",
    **kw
):
    D_IN = max(25.0, float(D_IN))
    D_OUT = max(D_IN, float(D_OUT))
    H_IN = float(H_IN)
    if H_IN < 1.0:
        H_IN = 1.0
    L_OUT = float(L_OUT)
    if L_OUT < 1.0:
        L_OUT = 1.0
    D_FL_IN = max(D_IN + 40.0, float(D_FL_IN))
    D_FL_OUT = max(D_OUT + 40.0, float(D_FL_OUT))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    r_in = D_IN / 2.0
    r_out = D_OUT / 2.0
    r_fl_in = D_FL_IN / 2.0
    r_fl_out = D_FL_OUT / 2.0
    c_in = max(18.0, r_fl_in * 0.22)
    c_out = max(18.0, r_fl_out * 0.2)
    rf_t = 2.5

    # 1. 水平入口，沿 -Y，和 +X 出口成 90 度。入口朝下时 Plant 会报「无法连接不平行的端口」。
    o_main = CYLINDER(s, R=r_fl_in * 0.72, H=rf_t + 2.0, O=0.0).rotateX(-90.0).translate((0.0, -H_IN, 0.0))
    o_fl1 = CYLINDER(s, R=r_fl_in, H=c_in - rf_t, O=0.0).rotateX(-90.0).translate((0.0, -H_IN + rf_t, 0.0))
    o_main.uniteWith(o_fl1)
    o_fl1.erase()
    o_in_neck = CYLINDER(s, R=r_in * 1.18, H=H_IN - c_in + 10.0, O=0.0).rotateX(-90.0).translate((0.0, -H_IN + c_in - 2.0, 0.0))
    o_main.uniteWith(o_in_neck)
    o_in_neck.erase()

    # 2. 右侧出口异径突面法兰 (Port 2: L_OUT, 0, 0)
    o_rf2 = CYLINDER(s, R=r_fl_out * 0.72, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((L_OUT - rf_t - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_rf2)
    o_rf2.erase()
    o_fl2 = CYLINDER(s, R=r_fl_out, H=c_out - rf_t, O=0.0).rotateY(90.0).translate((L_OUT - c_out, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_out_neck = CYLINDER(s, R=r_out * 1.15, H=L_OUT - c_out + 10.0, O=0.0).rotateY(90.0).translate((-6.0, 0.0, 0.0))
    o_main.uniteWith(o_out_neck)
    o_out_neck.erase()

    # 3. 90度转角主阀腔 + 圆形中法兰
    r_body = max(r_out * 1.24, r_in * 1.38)
    o_body = CYLINDER(s, R=r_body, H=r_out * 2.15, O=0.0).translate((0.0, 0.0, -r_out * 1.05))
    o_main.uniteWith(o_body)
    o_body.erase()

    z_mf = r_out * 1.05
    mf_t = max(24.0, c_out * 1.25)
    r_mf = r_body * 1.28
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    # 4. 标志性细高锥形弹簧罩 (Spring Bonnet)
    z_bon_bot = z_mf + mf_t - 4.0
    cap_h = max(65.0, (H_TOP - z_bon_bot) * 0.24)
    z_cap_bot = H_TOP - cap_h
    bon_h = max(110.0, z_cap_bot - z_bon_bot + 6.0)
    r_bon_bot = r_mf * 0.68
    r_bon_top = max(26.0, r_bon_bot * 0.56)
    o_bon = CONE(s, R1=r_bon_bot, R2=r_bon_top, H=bon_h, E=0.0).translate((0.0, 0.0, z_bon_bot))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    # 弹簧罩上下加强筋环
    o_collar = CYLINDER(s, R=r_bon_top * 1.32, H=16.0, O=0.0).translate((0.0, 0.0, z_cap_bot - 12.0))
    o_main.uniteWith(o_collar)
    o_collar.erase()

    # 5. 顶部封闭顶帽 (Top Cap) + 侧向微启扳手耳
    o_cap = CYLINDER(s, R=r_bon_top * 1.08, H=cap_h - 10.0, O=0.0).translate((0.0, 0.0, z_cap_bot))
    o_main.uniteWith(o_cap)
    o_cap.erase()
    o_cap_top = CONE(s, R1=r_bon_top * 1.08, R2=r_bon_top * 0.65, H=14.0, E=0.0).translate((0.0, 0.0, H_TOP - 14.0))
    o_main.uniteWith(o_cap_top)
    o_cap_top.erase()

    s.setPoint((L_OUT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, -H_IN, 0.0), (0.0, -1.0, 0.0))
    s.setLinearDimension('L_OUT', (0.0, 0.0, 0.0), (L_OUT, 0.0, 0.0))
    s.setLinearDimension('H_IN', (0.0, 0.0, 0.0), (0.0, -H_IN, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
