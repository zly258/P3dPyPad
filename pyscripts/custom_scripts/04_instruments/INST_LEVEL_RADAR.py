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
          TooltipShort=u"顶装法兰雷达液位计 (GB/T 20729)",
          TooltipLong=u"化工顶装法兰式高频脉冲/调频连续波雷达液位计，含过程法兰、饱满喇叭口天线、加粗散热连接颈及防爆双腔表头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"雷达液位计法兰、喇叭天线及顶表头尺寸")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"过程安装法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程安装法兰厚度 (mm)")
@param(L_HORN=LENGTH, TooltipShort=u"天线总长", TooltipLong=u"法兰密封面至喇叭口端面伸入深度 (mm)", Ask4Dist=True)
@param(D_HORN=LENGTH, TooltipShort=u"喇叭口径", TooltipLong=u"雷达喇叭天线开口外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"上部总高", TooltipLong=u"法兰密封面至表头顶面高度 (mm)", Ask4Dist=True)
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"防爆双腔雷达表头外径 (mm)")
def INST_LEVEL_RADAR(
    s,
    D_FL=200.0,
    C_FL=20.0,
    L_HORN=245.0,
    D_HORN=122.0,
    H_TOP=275.0,
    D_HEAD=124.0,
    ID=u"INST_LEVEL_RADAR",
    **kw
):
    u"""顶装法兰雷达液位计 (Port 1 在 Z=0 法兰底面，喇叭天线向 -Z 伸入罐内)。"""
    D_FL = max(140.0, float(D_FL))
    C_FL = max(16.0, float(C_FL))
    L_HORN = float(L_HORN)
    if L_HORN < 1.0:
        L_HORN = 1.0
    D_HORN = max(75.0, min(D_FL - 40.0, float(D_HORN)))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0
    D_HEAD = max(96.0, float(D_HEAD))

    r_fl = D_FL / 2.0
    r_horn = D_HORN / 2.0
    r_head = D_HEAD / 2.0

    # 1. 过程连接法兰 (Z=[0, C_FL])
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)

    # 2. 饱满喇叭口雷达天线 (-Z): 波导直管段 + 扩张喇叭锥 + 喇叭口加固环
    h_wg = L_HORN * 0.34
    h_bell = L_HORN - h_wg
    o_wg = CYLINDER(s, R=max(22.0, r_horn * 0.42), H=h_wg + 4.0, O=0.0).translate((0.0, 0.0, -h_wg))
    o_main.uniteWith(o_wg)
    o_wg.erase()
    o_bell = CONE(s, R1=max(22.0, r_horn * 0.42), R2=r_horn, H=h_bell + 2.0).rotateX(180.0).translate((0.0, 0.0, -h_wg + 2.0))
    o_main.uniteWith(o_bell)
    o_bell.erase()
    o_lip = CYLINDER(s, R=r_horn + 4.0, H=12.0, O=0.0).translate((0.0, 0.0, -L_HORN))
    o_main.uniteWith(o_lip)
    o_lip.erase()

    # 3. 法兰上加粗隔离颈 + 防爆双腔圆筒表头 (+Z)
    z_head_c = H_TOP - r_head
    o_hub = CYLINDER(s, R=38.0, H=34.0, O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    o_neck = CYLINDER(s, R=26.0, H=max(50.0, z_head_c - C_FL), O=0.0).translate((0.0, 0.0, C_FL + 10.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    l_head = D_HEAD * 1.38
    o_head = CYLINDER(s, R=r_head, H=l_head, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0, z_head_c))
    o_main.uniteWith(o_head)
    o_head.erase()
    o_fcap = CYLINDER(s, R=r_head + 6.0, H=18.0, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_fcap)
    o_fcap.erase()
    o_rcap = CYLINDER(s, R=r_head + 4.0, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, l_head / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_rcap)
    o_rcap.erase()
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=14.0, H=30.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_head - 6.0), 20.0, z_head_c - 6.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_HORN', (0.0, 0.0, 0.0), (0.0, 0.0, -L_HORN))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
