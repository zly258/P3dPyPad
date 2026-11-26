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
          TooltipShort=u"压力表总成含根部阀 (GB/T 1226)",
          TooltipLong=u"化工管线法兰式压力表总成，含连接法兰、重型根部针形截止阀、加粗散热连接颈及大表盘圆筒表壳",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"压力表总成法兰、表盘直径及总高尺寸")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"根部连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"根部连接法兰厚度 (mm)")
@param(D_DIAL=LENGTH, TooltipShort=u"表盘外径", TooltipLong=u"压力表表盘外径 (mm)", Ask4Dist=True)
@param(T_DIAL=LENGTH, TooltipShort=u"表壳厚度", TooltipLong=u"压力表表壳厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"法兰底面至表盘顶部总高度 (mm)", Ask4Dist=True)
@param(W_VALVE=LENGTH, TooltipShort=u"根部阀宽", TooltipLong=u"根部截止阀阀体宽度 (mm)")
def INST_PRESSURE_GAUGE(
    s,
    D_FL=95.0,
    C_FL=16.0,
    D_DIAL=150.0,
    T_DIAL=52.0,
    H_TOTAL=340.0,
    W_VALVE=48.0,
    ID=u"INST_PRESSURE_GAUGE",
    **kw
):
    u"""法兰式压力表总成含根部阀 (Port 1 在 Z=0 法兰底面，表盘朝 -Y)。"""
    D_FL = max(65.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_DIAL = float(D_DIAL)
    if D_DIAL < 1.0:
        D_DIAL = 1.0
    T_DIAL = max(36.0, float(T_DIAL))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    W_VALVE = max(36.0, float(W_VALVE))

    r_fl = D_FL / 2.0
    r_dial = D_DIAL / 2.0
    z_dial_c = H_TOTAL - r_dial

    # 1. 底部连接法兰与凸面台阶
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    o_hub = CYLINDER(s, R=max(22.0, r_fl * 0.48), H=26.0, O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    # 2. 根部针形截止阀体 + 侧向阀盖与T型手柄
    z_v_bot = C_FL + 20.0
    h_v = max(54.0, W_VALVE * 1.25)
    o_vbody = CORNERBOX(s, L=W_VALVE, W=W_VALVE, H=h_v).translate((-W_VALVE / 2.0, -W_VALVE / 2.0, z_v_bot))
    o_main.uniteWith(o_vbody)
    o_vbody.erase()

    z_v_mid = z_v_bot + h_v * 0.5
    o_bonnet = CYLINDER(s, R=16.0, H=42.0, O=0.0).rotateY(90.0).translate((W_VALVE * 0.4, 0.0, z_v_mid))
    o_main.uniteWith(o_bonnet)
    o_bonnet.erase()
    o_stem = CYLINDER(s, R=8.0, H=30.0, O=0.0).rotateY(90.0).translate((W_VALVE * 0.4 + 38.0, 0.0, z_v_mid))
    o_main.uniteWith(o_stem)
    o_stem.erase()
    o_thandle = CYLINDER(s, R=9.0, H=76.0, O=0.0).rotateX(-90.0).translate((W_VALVE * 0.4 + 62.0, -38.0, z_v_mid))
    o_main.uniteWith(o_thandle)
    o_thandle.erase()

    # 3. 散热/缓冲连接颈 + 六角接头
    z_neck_bot = z_v_bot + h_v - 4.0
    h_neck = max(36.0, z_dial_c - r_dial * 0.85 - z_neck_bot)
    o_neck = CYLINDER(s, R=15.0, H=h_neck + 16.0, O=0.0).translate((0.0, 0.0, z_neck_bot))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_hex = CORNERBOX(s, L=38.0, W=38.0, H=22.0).translate((-19.0, -19.0, z_dial_c - r_dial - 14.0))
    o_main.uniteWith(o_hex)
    o_hex.erase()

    # 4. 大表盘圆筒表壳 + 前表圈 + 后泄压盖 (朝 -Y)
    o_case = CYLINDER(s, R=r_dial, H=T_DIAL, O=0.0).rotateX(-90.0).translate((0.0, -T_DIAL / 2.0, z_dial_c))
    o_main.uniteWith(o_case)
    o_case.erase()
    o_bezel = CYLINDER(s, R=r_dial + 6.0, H=14.0, O=0.0).rotateX(-90.0).translate((0.0, -T_DIAL / 2.0 - 8.0, z_dial_c))
    o_main.uniteWith(o_bezel)
    o_bezel.erase()
    o_back = CYLINDER(s, R=r_dial * 0.55, H=12.0, O=0.0).rotateX(-90.0).translate((0.0, T_DIAL / 2.0 - 2.0, z_dial_c))
    o_main.uniteWith(o_back)
    o_back.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('D_DIAL', (-r_dial, -T_DIAL / 2.0, z_dial_c), (r_dial, -T_DIAL / 2.0, z_dial_c))
