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
          TooltipShort=u"储罐阻火呼吸阀 (SY/T 0511)",
          TooltipLong=u"SY/T 0511 储罐顶用阻火呼吸阀，含底部单法兰、阻火盘与双侧正负压呼吸阀罩壳",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"阻火呼吸阀总高、总宽与法兰尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"储罐接管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"底部安装法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"底部安装法兰厚度 (mm)")
@param(H_VALVE=LENGTH, TooltipShort=u"阀门总高", TooltipLong=u"底部法兰面至呼吸阀罩顶总高 H (mm)", Ask4Dist=True)
@param(W_TOTAL=LENGTH, TooltipShort=u"双罩总宽", TooltipLong=u"双侧正负压呼吸阀罩壳外缘总宽 W (mm)", Ask4Dist=True)
@param(D_HOUSING=LENGTH, TooltipShort=u"阀罩外径", TooltipLong=u"单侧正/负压呼吸阀罩壳外径 (mm)")
def SPEC_BREATHER_VALVE(
    s,
    D=114.3,
    D_FL=220.0,
    C_FL=20.0,
    H_VALVE=480.0,
    W_TOTAL=460.0,
    D_HOUSING=180.0,
    ID=u"SPEC_BREATHER_VALVE",
    **kw
):
    u"""储罐阻火呼吸阀 (底法兰面在 Z=0, Port 1 在原点朝向 -Z, 双侧呼吸阀罩沿 +/-X)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    H_VALVE = float(H_VALVE)
    if H_VALVE < 1.0:
        H_VALVE = 1.0
    D_HOUSING = max(D * 1.15, float(D_HOUSING))
    W_TOTAL = float(W_TOTAL)
    if W_TOTAL < 1.0:
        W_TOTAL = 1.0

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_arr = r_fl * 1.22
    r_house = D_HOUSING / 2.0
    x_off = (W_TOTAL - D_HOUSING) / 2.0

    # 1. 底部单法兰与进气短管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    z_arr_bot = C_FL + max(35.0, H_VALVE * 0.14)
    o_neck = CYLINDER(s, R=r_pipe * 1.08, H=z_arr_bot - C_FL + 8.0, O=0.0).translate((0.0, 0.0, C_FL - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    # 2. 阻火盘（下法兰 + 阻火芯壳 + 上法兰）
    h_arr = max(45.0, H_VALVE * 0.15)
    c_arr = max(14.0, C_FL * 0.85)
    o_af1 = CYLINDER(s, R=r_arr, H=c_arr, O=0.0).translate((0.0, 0.0, z_arr_bot))
    o_main.uniteWith(o_af1)
    o_af1.erase()

    o_acore = CYLINDER(s, R=r_arr * 0.84, H=h_arr, O=0.0).translate((0.0, 0.0, z_arr_bot))
    o_main.uniteWith(o_acore)
    o_acore.erase()

    o_af2 = CYLINDER(s, R=r_arr, H=c_arr, O=0.0).translate((0.0, 0.0, z_arr_bot + h_arr - c_arr))
    o_main.uniteWith(o_af2)
    o_af2.erase()

    # 3. 中央三通腔体与双侧水平支管
    z_tee = z_arr_bot + h_arr + max(30.0, r_pipe * 0.9)
    o_stem = CYLINDER(s, R=r_pipe * 1.15, H=z_tee - (z_arr_bot + h_arr) + r_pipe + 8.0, O=0.0).translate((0.0, 0.0, z_arr_bot + h_arr - 4.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    o_arm = CYLINDER(s, R=r_pipe * 0.92, H=2.0 * x_off, O=0.0).rotateY(90.0).translate((-x_off, 0.0, z_tee))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    # 4. 双侧正负压呼吸阀罩壳（立式阀腔 + 顶部防雨帽盖）
    z_house_bot = z_tee - r_pipe * 0.6
    z_cap_bot = H_VALVE - max(28.0, r_house * 0.42)
    h_house = max(60.0, z_cap_bot - z_house_bot)
    cap_h = H_VALVE - z_cap_bot
    for sx in (-1.0, 1.0):
        cx = sx * x_off
        o_body = CYLINDER(s, R=r_house * 0.90, H=h_house + 4.0, O=0.0).translate((cx, 0.0, z_house_bot))
        o_main.uniteWith(o_body)
        o_body.erase()

        o_rim = CYLINDER(s, R=r_house, H=max(14.0, h_house * 0.14), O=0.0).translate((cx, 0.0, z_cap_bot - 10.0))
        o_main.uniteWith(o_rim)
        o_rim.erase()

        o_cap = CONE(s, R1=r_house * 1.05, R2=r_house * 0.25, H=cap_h, E=0.0).translate((cx, 0.0, z_cap_bot))
        o_main.uniteWith(o_cap)
        o_cap.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_VALVE', (0.0, 0.0, 0.0), (0.0, 0.0, H_VALVE))
    s.setLinearDimension('W_TOTAL', (-W_TOTAL / 2.0, 0.0, z_tee), (W_TOTAL / 2.0, 0.0, z_tee))
