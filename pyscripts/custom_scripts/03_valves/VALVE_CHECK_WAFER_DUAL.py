# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Valve", Ports=2, TooltipShort=u"对夹双瓣蝶式止回阀 (H76H / API 594)", TooltipLong=u"化工标准 GB/T 12236 / API 594 对夹式双瓣旋启蝶形止回阀 (Wafer Dual-Plate Check Valve)，含紧凑圆筒对夹阀体、中心定位销轴与止回限位轴、内部双半圆阀瓣及顶部吊环耳", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"对夹止回阀主要结构尺寸：口径、对夹厚度与外圆直径")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"对夹结构厚 L", Ask4Dist=True, TooltipLong=u"对夹安装面间距 L (API 594)")
@param(OD_BODY=LENGTH, TooltipShort=u"阀体外径 OD", Ask4Dist=True, TooltipLong=u"对夹圆筒阀体外径（嵌于法兰螺栓圈内）")
@param(PIN_D=LENGTH, TooltipShort=u"中轴销径", TooltipLong=u"中心弹簧铰链销轴直径")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，如 CV-103")
def VALVE_CHECK_WAFER_DUAL(s, D=219.1, L=95.0, OD_BODY=284.0, PIN_D=22.0, ID=u"H76H-16C-DN200", **kw):
    D = max(50.0, float(D))
    L = max(48.0, float(L))
    OD_BODY = max(D + 36.0, float(OD_BODY))
    PIN_D = max(12.0, float(PIN_D))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.90
    r_body = OD_BODY / 2.0

    # 1. 对夹圆筒主阀体 + 外部环向加强凸筋
    o_v = CYLINDER(s, R=r_body, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_rib = CYLINDER(s, R=r_body * 1.03, H=L * 0.42, O=0.0).rotateY(90.0).translate((-L * 0.21, 0.0, 0.0))
    o_v.uniteWith(o_rib); o_rib.erase()

    # 2. 上下两端固定铰链轴与止推销轴封头凸台 + 顶部起吊耳板
    boss_h = r_body + 22.0
    for dx in (-L * 0.16, L * 0.16):
        o_pb = CYLINDER(s, R=PIN_D * 0.95, H=2.0 * boss_h, O=0.0).translate((dx, 0.0, -boss_h))
        o_v.uniteWith(o_pb); o_pb.erase()

    lug_h = 46.0
    o_lug = BOX(s, L=16.0, W=lug_h, H=54.0).translate((0.0, 0.0, r_body + lug_h * 0.45))
    o_lhole = CYLINDER(s, R=11.0, H=28.0, O=0.0).rotateX(90.0).translate((0.0, 14.0, r_body + lug_h * 0.55))
    o_lug.subtractFrom(o_lhole); o_lhole.erase()
    o_v.uniteWith(o_lug); o_lug.erase()

    # 3. 切除内流道，再并入中心立柱隔梁、双转轴与微开双瓣蝶板
    o_bore = CYLINDER(s, R=r_bore, H=L + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 3.0), 0.0, 0.0))
    o_v.subtractFrom(o_bore); o_bore.erase()

    o_web = BOX(s, L=PIN_D * 1.35, W=2.0 * r_bore + 12.0, H=L * 0.72).translate((0.0, 0.0, 0.0))
    o_v.uniteWith(o_web); o_web.erase()

    for sy in (-1.0, 1.0):
        flap = CYLINDER(s, R=r_bore * 0.92, H=10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
        cut_half = BOX(s, L=r_bore * 2.2, W=r_bore * 2.4, H=30.0).translate((0.0, -sy * r_bore * 1.1, 0.0))
        flap.subtractFrom(cut_half); cut_half.erase()
        flap.rotateZ(sy * 18.0).translate((L * 0.08, 0.0, 0.0))
        o_v.uniteWith(flap); flap.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_body), (L / 2.0, 0.0, -r_body))
    s.setLinearDimension("OD_BODY", (0.0, -r_body, r_body), (0.0, r_body, r_body))
