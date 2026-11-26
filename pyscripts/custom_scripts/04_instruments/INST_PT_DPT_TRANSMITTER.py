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
          TooltipShort=u"压力/差压变送器含三阀组 (IEC 61518)",
          TooltipLong=u"化工智能压力/差压变送器总成，含底部连接法兰、三阀组阀块及手轮、双法兰膜盒传感器与防爆双腔液晶表头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"变送器法兰、三阀组及双腔表头总体尺寸")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"底部过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(W_MANIFOLD=LENGTH, TooltipShort=u"三阀组宽", TooltipLong=u"三阀组阀块横向宽度 (mm)")
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"双腔防爆表头圆筒外径 (mm)")
@param(L_HEAD=LENGTH, TooltipShort=u"表头长度", TooltipLong=u"双腔防爆表头轴向长度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"法兰底面至变送器顶面总高 (mm)", Ask4Dist=True)
def INST_PT_DPT_TRANSMITTER(
    s,
    D_FL=105.0,
    C_FL=18.0,
    W_MANIFOLD=136.0,
    D_HEAD=112.0,
    L_HEAD=156.0,
    H_TOTAL=390.0,
    ID=u"INST_PT_DPT_TRANSMITTER",
    **kw
):
    u"""压力/差压变送器含三阀组 (Port 1 在 Z=0 法兰底面，液晶表盘朝 -Y)。"""
    D_FL = max(75.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    W_MANIFOLD = float(W_MANIFOLD)
    if W_MANIFOLD < 1.0:
        W_MANIFOLD = 1.0
    D_HEAD = max(86.0, float(D_HEAD))
    L_HEAD = max(120.0, float(L_HEAD))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    r_fl = D_FL / 2.0
    r_head = D_HEAD / 2.0
    z_head_c = H_TOTAL - r_head

    # 1. 底部连接法兰与引压短管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    o_stem0 = CYLINDER(s, R=24.0, H=42.0, O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_stem0)
    o_stem0.erase()

    # 2. 三阀组阀块 + 左右及前侧三只针阀T型手柄
    z_mf = C_FL + 36.0
    h_mf = 54.0
    d_mf = 64.0
    o_mf = CORNERBOX(s, L=W_MANIFOLD, W=d_mf, H=h_mf).translate((-W_MANIFOLD / 2.0, -d_mf / 2.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    z_mf_mid = z_mf + h_mf * 0.5
    for sx in (-1.0, 1.0):
        o_vb = CYLINDER(s, R=13.0, H=34.0, O=0.0).rotateY(sx * 90.0).translate((sx * (W_MANIFOLD / 2.0 - 4.0), 0.0, z_mf_mid))
        o_main.uniteWith(o_vb)
        o_vb.erase()
        o_vh = CYLINDER(s, R=8.0, H=58.0, O=0.0).rotateX(-90.0).translate((sx * (W_MANIFOLD / 2.0 + 26.0), -29.0, z_mf_mid))
        o_main.uniteWith(o_vh)
        o_vh.erase()
    # 中间平衡阀 (-Y)
    o_vb_mid = CYLINDER(s, R=13.0, H=32.0, O=0.0).rotateX(90.0).translate((0.0, -d_mf / 2.0 + 4.0, z_mf_mid))
    o_main.uniteWith(o_vb_mid)
    o_vb_mid.erase()
    o_vh_mid = CYLINDER(s, R=8.0, H=54.0, O=0.0).rotateY(90.0).translate((-27.0, -d_mf / 2.0 - 24.0, z_mf_mid))
    o_main.uniteWith(o_vh_mid)
    o_vh_mid.erase()

    # 3. 共面/H型差压膜盒传感器模块
    z_cell = z_mf + h_mf - 2.0
    h_cell = 92.0
    w_cell = W_MANIFOLD * 0.78
    o_cell_c = CYLINDER(s, R=44.0, H=w_cell * 0.72, O=0.0).rotateY(90.0).translate((-w_cell * 0.36, 0.0, z_cell + h_cell * 0.5))
    o_main.uniteWith(o_cell_c)
    o_cell_c.erase()
    for sx in (-1.0, 1.0):
        o_flp = CORNERBOX(s, L=24.0, W=78.0, H=h_cell).translate((sx * (w_cell * 0.36) - 12.0, -39.0, z_cell))
        o_main.uniteWith(o_flp)
        o_flp.erase()

    # 4. 传感器过渡颈与双腔防爆圆筒表头
    z_neck_bot = z_cell + h_cell - 8.0
    h_neck = max(36.0, z_head_c - z_neck_bot)
    o_neck = CYLINDER(s, R=24.0, H=h_neck, O=0.0).translate((0.0, 0.0, z_neck_bot))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    o_head = CYLINDER(s, R=r_head, H=L_HEAD, O=0.0).rotateX(-90.0).translate((0.0, -L_HEAD / 2.0, z_head_c))
    o_main.uniteWith(o_head)
    o_head.erase()
    # 前液晶表盖环 + 后接线盖环
    o_fcap = CYLINDER(s, R=r_head + 6.0, H=18.0, O=0.0).rotateX(-90.0).translate((0.0, -L_HEAD / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_fcap)
    o_fcap.erase()
    o_rcap = CYLINDER(s, R=r_head + 4.0, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, L_HEAD / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_rcap)
    o_rcap.erase()
    # 左右防爆电缆格兰接口
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=14.0, H=30.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_head - 8.0), 16.0, z_head_c - 6.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('W_MANIFOLD', (-W_MANIFOLD / 2.0, 0.0, z_mf_mid), (W_MANIFOLD / 2.0, 0.0, z_mf_mid))
