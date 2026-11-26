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
          TooltipShort=u"防爆可燃/有毒气体探测器 (GB/T 50493)",
          TooltipLong=u"化工防爆固定式可燃/有毒气体探测器，含背部安装板、防爆圆形显示表壳、底部防雨传感器探头罩及顶部声光报警灯",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"气体探测器表壳直径、总高、安装板及探头尺寸")
@param(D_CASE=LENGTH, TooltipShort=u"防爆壳直径", TooltipLong=u"防爆圆形主表壳外径 (mm)")
@param(T_CASE=LENGTH, TooltipShort=u"防爆壳厚度", TooltipLong=u"防爆主表壳前后厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"底部探头罩底面至顶部声光灯顶面总高 (mm)", Ask4Dist=True)
@param(W_PLATE=LENGTH, TooltipShort=u"安装板宽", TooltipLong=u"背部固定安装板宽度 (mm)")
@param(H_PLATE=LENGTH, TooltipShort=u"安装板高", TooltipLong=u"背部固定安装板高度 (mm)")
def INST_GAS_DETECTOR(
    s,
    D_CASE=146.0,
    T_CASE=98.0,
    H_TOTAL=340.0,
    W_PLATE=168.0,
    H_PLATE=210.0,
    ID=u"INST_GAS_DETECTOR",
    **kw
):
    u"""防爆可燃/有毒气体探测器 (Port 1 在背部安装板中心 (0, T_CASE/2 + 18, 0)，表盘朝 -Y)。"""
    D_CASE = max(110.0, float(D_CASE))
    T_CASE = max(72.0, float(T_CASE))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    W_PLATE = float(W_PLATE)
    if W_PLATE < 1.0:
        W_PLATE = 1.0
    H_PLATE = max(D_CASE + 30.0, float(H_PLATE))

    r_case = D_CASE / 2.0
    y_back = T_CASE / 2.0 + 18.0

    # 1. 防爆圆形主表壳 (居中于 Z=0，液晶窗口朝 -Y) + 前表盖环
    o_main = CYLINDER(s, R=r_case, H=T_CASE, O=0.0).rotateX(-90.0).translate((0.0, -T_CASE / 2.0, 0.0))
    o_bezel = CYLINDER(s, R=r_case + 7.0, H=20.0, O=0.0).rotateX(-90.0).translate((0.0, -T_CASE / 2.0 - 12.0, 0.0))
    o_main.uniteWith(o_bezel)
    o_bezel.erase()

    # 2. 背部重型安装底板 (+Y 侧，Port 1 落在底板背面中心)
    o_pad = CORNERBOX(s, L=D_CASE * 0.72, W=24.0, H=D_CASE * 0.72).translate((-D_CASE * 0.36, T_CASE / 2.0 - 10.0, -D_CASE * 0.36))
    o_main.uniteWith(o_pad)
    o_pad.erase()
    o_plate = CORNERBOX(s, L=W_PLATE, W=12.0, H=H_PLATE).translate((-W_PLATE / 2.0, y_back - 12.0, -H_PLATE / 2.0))
    o_main.uniteWith(o_plate)
    o_plate.erase()

    # 3. 底部防爆气体传感器探头与防雨罩 (-Z)
    h_bot = (H_TOTAL - D_CASE) * 0.52
    o_sneck = CYLINDER(s, R=28.0, H=h_bot * 0.52 + 14.0, O=0.0).translate((0.0, 0.0, -r_case - h_bot * 0.52))
    o_main.uniteWith(o_sneck)
    o_sneck.erase()
    o_hood = CONE(s, R1=34.0, R2=46.0, H=h_bot * 0.56).rotateX(180.0).translate((0.0, 0.0, -r_case - h_bot * 0.44))
    o_main.uniteWith(o_hood)
    o_hood.erase()

    # 4. 顶部防爆声光报警闪光灯 (+Z) + 左右电缆穿线格兰
    h_top = H_TOTAL - D_CASE - h_bot
    o_bneck = CYLINDER(s, R=24.0, H=34.0, O=0.0).translate((0.0, 0.0, r_case - 8.0))
    o_main.uniteWith(o_bneck)
    o_bneck.erase()
    o_bbase = CYLINDER(s, R=38.0, H=22.0, O=0.0).translate((0.0, 0.0, r_case + 20.0))
    o_main.uniteWith(o_bbase)
    o_bbase.erase()
    h_dome = max(36.0, h_top - 42.0)
    o_lens = CYLINDER(s, R=32.0, H=h_dome * 0.68, O=0.0).translate((0.0, 0.0, r_case + 38.0))
    o_main.uniteWith(o_lens)
    o_lens.erase()
    o_dome = HALFSPHERE(s, R=32.0).translate((0.0, 0.0, r_case + 38.0 + h_dome * 0.65))
    o_main.uniteWith(o_dome)
    o_dome.erase()
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=15.0, H=34.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_case - 6.0), 8.0, 0.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((0.0, y_back, 0.0), (0.0, 1.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, -r_case - h_bot), (0.0, 0.0, r_case + h_top))
    s.setLinearDimension('W_PLATE', (-W_PLATE / 2.0, y_back, 0.0), (W_PLATE / 2.0, y_back, 0.0))
