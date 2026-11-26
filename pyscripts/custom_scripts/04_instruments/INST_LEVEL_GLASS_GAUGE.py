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
          TooltipShort=u"玻璃板液位计 (HG/T 21592)",
          TooltipLong=u"化工重型铠装反射/透射式玻璃板液位计，含矩形重型视窗表体、上下角型针形根部截止阀与侧向双法兰",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"玻璃板液位计中心距、表体截面及法兰尺寸")
@param(L_C2C=LENGTH, TooltipShort=u"法兰中心距", TooltipLong=u"上下侧向过程法兰中心距 C-C (mm)", Ask4Dist=True)
@param(W_BODY=LENGTH, TooltipShort=u"表体宽度", TooltipLong=u"矩形重型玻璃板表体宽度 (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"表体厚度", TooltipLong=u"矩形重型玻璃板表体前后厚度 (mm)")
@param(L_NOZ=LENGTH, TooltipShort=u"接管伸出距", TooltipLong=u"表体中心至侧向法兰密封面距离 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"侧向过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
def INST_LEVEL_GLASS_GAUGE(
    s,
    L_C2C=600.0,
    W_BODY=82.0,
    D_BODY=76.0,
    L_NOZ=165.0,
    D_FL=105.0,
    C_FL=18.0,
    ID=u"INST_LEVEL_GLASS_GAUGE",
    **kw
):
    u"""玻璃板液位计 (Port 1 在 (-L_NOZ, 0, -L_C2C/2), Port 2 在 (-L_NOZ, 0, +L_C2C/2))。"""
    L_C2C = float(L_C2C)
    if L_C2C < 1.0:
        L_C2C = 1.0
    W_BODY = max(62.0, float(W_BODY))
    D_BODY = max(58.0, float(D_BODY))
    L_NOZ = float(L_NOZ)
    if L_NOZ < 1.0:
        L_NOZ = 1.0
    D_FL = max(90.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))

    half_c = L_C2C / 2.0
    r_fl = D_FL / 2.0
    h_glass = L_C2C - 108.0

    # 1. 中央矩形重型铠装玻璃板表体 + 前侧视窗压板框 (-Y)
    o_main = CORNERBOX(s, L=W_BODY, W=D_BODY, H=h_glass).translate((-W_BODY / 2.0, -D_BODY / 2.0, -h_glass / 2.0))
    # 前后压板凸缘与U型夹紧肋块
    o_front = CORNERBOX(s, L=W_BODY + 12.0, W=14.0, H=h_glass - 16.0).translate((-(W_BODY + 12.0) / 2.0, -D_BODY / 2.0 - 10.0, -(h_glass - 16.0) / 2.0))
    o_main.uniteWith(o_front)
    o_front.erase()
    # 沿高度方向分布4道重型压紧螺栓筋块 (LOD 300 简化表达)
    for i in range(4):
        zr = -h_glass * 0.36 + i * (h_glass * 0.24)
        o_rib = CORNERBOX(s, L=W_BODY + 24.0, W=D_BODY + 10.0, H=20.0).translate((-(W_BODY + 24.0) / 2.0, -(D_BODY + 10.0) / 2.0, zr - 10.0))
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 2. 上下过渡连接颈 + 角型根部截止阀块 + 手轮 (+X) + 侧向法兰 (-X)
    for sz in (-1.0, 1.0):
        zz = sz * half_c
        # 竖向连接短管
        z_conn_bot = (h_glass / 2.0 - 8.0) if sz > 0 else (zz - 10.0)
        h_conn = abs(zz - sz * (h_glass / 2.0)) + 20.0
        o_cn = CYLINDER(s, R=20.0, H=h_conn, O=0.0).translate((0.0, 0.0, z_conn_bot))
        o_main.uniteWith(o_cn)
        o_cn.erase()
        # 角阀方体
        o_vb = CORNERBOX(s, L=64.0, W=58.0, H=62.0).translate((-32.0, -29.0, zz - 31.0))
        o_main.uniteWith(o_vb)
        o_vb.erase()
        # 阀杆与小手轮 (+X)
        o_st = CYLINDER(s, R=12.0, H=48.0, O=0.0).rotateY(90.0).translate((26.0, 0.0, zz))
        o_main.uniteWith(o_st)
        o_st.erase()
        o_wh = CYLINDER(s, R=38.0, H=14.0, O=0.0).rotateY(90.0).translate((68.0, 0.0, zz))
        o_main.uniteWith(o_wh)
        o_wh.erase()
        # 侧向连接短管与过程法兰 (-X)
        o_noz = CYLINDER(s, R=20.0, H=L_NOZ - 16.0, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_noz)
        o_noz.erase()
        o_fl = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_fl)
        o_fl.erase()

    # 3. 顶部放空丝堵与底部排污阀嘴
    o_vent = CYLINDER(s, R=14.0, H=34.0, O=0.0).translate((0.0, 0.0, half_c + 26.0))
    o_main.uniteWith(o_vent)
    o_vent.erase()
    o_drain = CYLINDER(s, R=15.0, H=46.0, O=0.0).translate((0.0, 0.0, -half_c - 72.0))
    o_main.uniteWith(o_drain)
    o_drain.erase()

    s.setPoint((-L_NOZ, 0.0, -half_c), (-1.0, 0.0, 0.0))
    s.setPoint((-L_NOZ, 0.0, half_c), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_C2C', (-L_NOZ, 0.0, -half_c), (-L_NOZ, 0.0, half_c))
    s.setLinearDimension('L_NOZ', (-L_NOZ, 0.0, 0.0), (0.0, 0.0, 0.0))
