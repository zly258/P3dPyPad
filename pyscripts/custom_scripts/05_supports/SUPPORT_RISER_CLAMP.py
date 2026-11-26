# -*- coding: utf-8 -*-
import math
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

@activate(Group="Support",
          TooltipShort=u"立管承重双耳抱箍支架 (HG/T 21629 G1)",
          TooltipLong=u"立管承重双耳抱箍支架，管道沿Z轴竖直穿过，含双半圆重型抱箍、双侧长承重耳板、紧固螺栓与端部承压垫板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"立管承重双耳抱箍支架主要几何参数")
@param(D=LENGTH, TooltipShort=u"立管外径", TooltipLong=u"被支撑竖直立管外径 D (mm)")
@param(L_SPAN=LENGTH, TooltipShort=u"总跨度", TooltipLong=u"双侧承重长耳板总跨度 L_SPAN (mm)", Ask4Dist=True)
@param(CLAMP_H=LENGTH, TooltipShort=u"抱箍高度", TooltipLong=u"抱箍与耳板竖向高度 (mm)", Ask4Dist=True)
@param(CLAMP_T=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"抱箍与承重耳板厚度 (mm)")
@param(BOLT_D=LENGTH, TooltipShort=u"螺栓直径", TooltipLong=u"抱箍紧固螺栓直径 (mm)")
def SUPPORT_RISER_CLAMP(
    s,
    D=168.3,
    L_SPAN=460.0,
    CLAMP_H=60.0,
    CLAMP_T=12.0,
    BOLT_D=16.0,
    ID=u"SUPPORT_RISER_CLAMP",
    **kw
):
    u"""立管承重双耳抱箍支架 (原点在立管中心线, 管道沿 Z 轴, 端口法向 (0,0,-1))。"""
    D = max(32.0, float(D))
    r_p = D / 2.0
    CLAMP_H = float(CLAMP_H)
    if CLAMP_H < 1.0:
        CLAMP_H = 1.0
    CLAMP_T = max(8.0, float(CLAMP_T))
    BOLT_D = max(10.0, float(BOLT_D))
    L_SPAN = float(L_SPAN)
    if L_SPAN < 1.0:
        L_SPAN = 1.0

    r_out = r_p + CLAMP_T
    ear_gap = max(8.0, CLAMP_T * 0.9)
    ear_len = L_SPAN / 2.0 - r_p

    # 1. 双半圆重型抱箍（沿 Z 轴包覆立管，沿 X 平面剖分留紧固间隙）
    o_main = CYLINDER(s, R=r_out, H=CLAMP_H, O=r_p).translate((0.0, 0.0, -CLAMP_H / 2.0))
    o_slot = CORNERBOX(s, L=r_out * 2.6, W=ear_gap, H=CLAMP_H + 10.0).translate(
        (-r_out * 1.3, -ear_gap / 2.0, -(CLAMP_H / 2.0 + 5.0)))
    o_main.subtractFrom(o_slot)
    o_slot.erase()

    # 2. 双侧承重长耳板（沿 ±X 延伸，对称双板夹持）
    for sx in (-1.0, 1.0):
        ex = (r_p + CLAMP_T * 0.25) if sx > 0 else -(L_SPAN / 2.0)
        el = L_SPAN / 2.0 - (r_p + CLAMP_T * 0.25)
        for sy in (-1.0, 1.0):
            ey = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + CLAMP_T)
            o_ear = CORNERBOX(s, L=el, W=CLAMP_T, H=CLAMP_H).translate((ex, ey, -CLAMP_H / 2.0))
            o_main.uniteWith(o_ear)
            o_ear.erase()

        # 端部底部承压垫块（将双耳端连接为整块搁置面，落于楼板梁上）
        pad_l = max(55.0, el * 0.36)
        pad_w = ear_gap + CLAMP_T * 2.0 + 16.0
        px = (L_SPAN / 2.0 - pad_l) if sx > 0 else -(L_SPAN / 2.0)
        o_pad = CORNERBOX(s, L=pad_l, W=pad_w, H=CLAMP_T).translate(
            (px, -pad_w / 2.0, -CLAMP_H / 2.0 - CLAMP_T + 1.0))
        o_main.uniteWith(o_pad)
        o_pad.erase()

        # 双紧固螺栓（靠近管壁1组 + 外侧1组，穿透双耳板并带螺母）
        bx_list = (sx * (r_out + BOLT_D * 1.6), sx * (r_out + el * 0.52))
        bw = ear_gap + CLAMP_T * 2.0 + BOLT_D * 1.8
        for bx in bx_list:
            o_bolt = CYLINDER(s, R=BOLT_D * 0.5, H=bw, O=0.0).rotateX(-90.0).translate((bx, -bw / 2.0, 0.0))
            o_main.uniteWith(o_bolt)
            o_bolt.erase()
            for sy in (-1.0, 1.0):
                ny = (ear_gap / 2.0 + CLAMP_T - 0.5) if sy > 0 else -(ear_gap / 2.0 + CLAMP_T + BOLT_D * 0.75 - 0.5)
                o_nut = CYLINDER(s, R=BOLT_D * 0.88, H=BOLT_D * 0.75, O=0.0).rotateX(-90.0).translate((bx, ny, 0.0))
                o_main.uniteWith(o_nut)
                o_nut.erase()

    # 3. 抱箍上沿 4 块防滑承重挡块（剪切耳，贴合立管外壁）
    lug_h = max(20.0, CLAMP_H * 0.42)
    lug_w = max(18.0, CLAMP_T * 1.6)
    for ang_deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(ang_deg)
        lx = (r_p + CLAMP_T * 0.5) * math.cos(rad)
        ly = (r_p + CLAMP_T * 0.5) * math.sin(rad)
        o_lug = CORNERBOX(s, L=CLAMP_T, W=lug_w, H=lug_h).translate(
            (-CLAMP_T / 2.0, -lug_w / 2.0, CLAMP_H / 2.0 - 2.0)).rotateZ(ang_deg).translate((lx, ly, 0.0))
        o_main.uniteWith(o_lug)
        o_lug.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_SPAN', (-L_SPAN / 2.0, 0.0, 0.0), (L_SPAN / 2.0, 0.0, 0.0))
    s.setLinearDimension('CLAMP_H', (0.0, r_out, -CLAMP_H / 2.0), (0.0, r_out, CLAMP_H / 2.0))
