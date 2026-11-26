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

@activate(Group="Equipment",
          TooltipShort=u"储罐/塔器盘梯及顶部平台 (HG/T 21541)",
          TooltipLong=u"立式储罐与塔器配套螺旋盘梯及顶部检修平台模块，含落地起步底板、内外双螺旋钢梯梁、防滑踏步、连续外侧双道安全护栏及无缝衔接顶部扇形平台",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"储罐/塔器盘梯及顶部平台主要几何尺寸参数")
@param(D_TANK=LENGTH, TooltipShort=u"配套罐体直径", TooltipLong=u"配套立式储罐或塔器公称直径 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"盘梯总高", TooltipLong=u"地面至顶部检修平台高度 (mm)", Ask4Dist=True)
@param(W_STAIR=LENGTH, TooltipShort=u"梯段净宽", TooltipLong=u"盘梯踏步宽度 (mm)")
@param(SPAN_DEG=ANGLE, TooltipShort=u"盘旋包角", TooltipLong=u"盘梯沿罐壁圆周展开角度 (deg)")
def EQ_TANK_STAIR_PLATFORM(
    s,
    D_TANK=3000.0,
    H_TOTAL=4200.0,
    W_STAIR=750.0,
    SPAN_DEG=120.0,
    ID=u"EQ_TANK_STAIR_PLATFORM",
    **kw
):
    u"""立式储罐/塔器盘梯及顶部检修平台 (中心轴 Z 轴, 地面 Z=0, Port 1 为罐壁贴合定位基准点)。"""
    D_TANK = float(D_TANK)
    if D_TANK < 1.0:
        D_TANK = 1.0
    R_T = D_TANK / 2.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    W_STAIR = max(600.0, float(W_STAIR))
    SPAN_DEG = max(60.0, min(240.0, float(SPAN_DEG)))

    r_inner = R_T + 30.0
    r_outer = r_inner + W_STAIR
    r_mid = (r_inner + r_outer) * 0.5
    h_rail = 1050.0

    n_steps = max(12, min(24, int(round(H_TOTAL / 210.0))))
    step_h = H_TOTAL / float(n_steps)
    d_ang = SPAN_DEG / float(n_steps)

    # 1. 底部钢制起步底板与双斜梁落地支座 (替代原厚重实心块)
    o_main = CORNERBOX(s, L=W_STAIR + 80.0, W=220.0, H=28.0).translate((r_inner - 40.0, -110.0, 0.0))

    # 2. 盘旋梯段：踏步 + 连续内外钢梯梁 + 径向托架 + 外侧连续护栏
    prev_out = (r_outer, 0.0)
    for idx in range(n_steps):
        ang_deg = idx * d_ang
        rad = math.radians(ang_deg)
        z_s = (idx + 1) * step_h - 35.0
        step_len = max(250.0, r_mid * math.radians(d_ang) * 1.18)

        # 防滑踏步板
        o_step = CORNERBOX(s, L=W_STAIR, W=step_len, H=35.0).translate((r_inner, -step_len * 0.5, z_s)).rotateZ(ang_deg)
        o_main.uniteWith(o_step); o_step.erase()

        # 每 3 级一道径向角钢支撑托架（贴罐壁）
        if idx % 3 == 0:
            o_brk = CORNERBOX(s, L=W_STAIR + 20.0, W=60.0, H=160.0).translate((r_inner - 20.0, -30.0, max(0.0, z_s - 155.0))).rotateZ(ang_deg)
            o_main.uniteWith(o_brk); o_brk.erase()

        # 外侧护栏立柱
        px, py = r_outer * math.cos(rad), r_outer * math.sin(rad)
        if idx % 2 == 0 or idx == n_steps - 1:
            o_post = CYLINDER(s, R=20.0, H=h_rail + 40.0, O=0.0).translate((px, py, max(0.0, z_s - 20.0)))
            o_main.uniteWith(o_post); o_post.erase()

        # 连续梯梁与双道扶手（从 idx=0 连到顶部平台入口 SPAN_DEG）
        next_ang = (idx + 1) * d_ang
        next_rad = math.radians(next_ang)
        z0 = idx * step_h
        z1 = (idx + 1) * step_h

        # 内外双螺旋梯梁
        for r_str in (r_inner + 25.0, r_outer - 25.0):
            sx0, sy0 = r_str * math.cos(rad), r_str * math.sin(rad)
            sx1, sy1 = r_str * math.cos(next_rad), r_str * math.sin(next_rad)
            sxy = math.hypot(sx1 - sx0, sy1 - sy0)
            s3d = math.hypot(sxy, step_h)
            syaw = math.degrees(math.atan2(sy1 - sy0, sx1 - sx0))
            spitch = math.degrees(math.atan2(step_h, sxy))
            o_str = CYLINDER(s, R=30.0, H=s3d + 35.0, O=0.0).rotateY(90.0 - spitch).rotateZ(syaw).translate((sx0, sy0, max(14.0, z0)))
            o_main.uniteWith(o_str); o_str.erase()

        # 外侧双道斜扶手 + 踢脚板连接
        nx, ny = r_outer * math.cos(next_rad), r_outer * math.sin(next_rad)
        dxy = math.hypot(nx - px, ny - py)
        d3d = math.hypot(dxy, step_h)
        yaw = math.degrees(math.atan2(ny - py, nx - px))
        pitch = math.degrees(math.atan2(step_h, dxy))
        for hr in (h_rail * 0.52, h_rail):
            o_hr = CYLINDER(s, R=18.0, H=d3d + 25.0, O=0.0).rotateY(90.0 - pitch).rotateZ(yaw).translate((px, py, z0 + hr))
            o_main.uniteWith(o_hr); o_hr.erase()
        prev_out = (nx, ny)

    # 3. 顶部检修平台（沿 SPAN_DEG 无缝衔接，与最顶踏步平齐，展开 50 deg）
    plat_deg = 50.0
    n_plat = 5
    w_plat = W_STAIR + 200.0
    r_p_out = r_inner + w_plat

    # 入口过渡立柱 + 扶手过渡段（消除阶梯护栏与平台护栏的断口）
    rad_j = math.radians(SPAN_DEG)
    jx0, jy0 = r_outer * math.cos(rad_j), r_outer * math.sin(rad_j)
    jx1, jy1 = r_p_out * math.cos(rad_j), r_p_out * math.sin(rad_j)
    o_jp = CYLINDER(s, R=20.0, H=h_rail + 40.0, O=0.0).translate((jx0, jy0, H_TOTAL - 40.0))
    o_main.uniteWith(o_jp); o_jp.erase()
    jseg = math.hypot(jx1 - jx0, jy1 - jy0)
    jyaw = math.degrees(math.atan2(jy1 - jy0, jx1 - jx0))
    for hr in (h_rail * 0.52, h_rail):
        o_jr = CYLINDER(s, R=18.0, H=jseg + 25.0, O=0.0).rotateY(90.0).rotateZ(jyaw).translate((jx0, jy0, H_TOTAL + hr))
        o_main.uniteWith(o_jr); o_jr.erase()

    # 扇形平台板与底部径向托架
    for k in range(n_plat):
        a_deg = SPAN_DEG + (k + 0.5) * (plat_deg / float(n_plat))
        seg_w = r_p_out * math.radians(plat_deg / float(n_plat)) * 1.18
        o_pl = CORNERBOX(s, L=w_plat, W=seg_w, H=50.0).translate((r_inner, -seg_w * 0.5, H_TOTAL - 50.0)).rotateZ(a_deg)
        o_main.uniteWith(o_pl); o_pl.erase()
        if k in (0, n_plat // 2, n_plat - 1):
            o_pbrk = CORNERBOX(s, L=w_plat, W=75.0, H=240.0).translate((r_inner - 20.0, -37.5, H_TOTAL - 280.0)).rotateZ(a_deg)
            o_main.uniteWith(o_pbrk); o_pbrk.erase()

    # 平台外圈及末端封闭护栏
    for k in range(n_plat + 1):
        a_deg = SPAN_DEG + k * (plat_deg / float(n_plat))
        rad = math.radians(a_deg)
        px, py = r_p_out * math.cos(rad), r_p_out * math.sin(rad)
        o_pp = CYLINDER(s, R=20.0, H=h_rail + 40.0, O=0.0).translate((px, py, H_TOTAL - 40.0))
        o_main.uniteWith(o_pp); o_pp.erase()
        if k > 0:
            rad0 = math.radians(SPAN_DEG + (k - 1) * (plat_deg / float(n_plat)))
            x0, y0 = r_p_out * math.cos(rad0), r_p_out * math.sin(rad0)
            seg = math.hypot(px - x0, py - y0)
            yaw = math.degrees(math.atan2(py - y0, px - x0))
            for hr in (120.0, h_rail * 0.52, h_rail):
                o_pr = CYLINDER(s, R=18.0, H=seg + 25.0, O=0.0).rotateY(90.0).rotateZ(yaw).translate((x0, y0, H_TOTAL + hr))
                o_main.uniteWith(o_pr); o_pr.erase()

    # 平台远端封口护栏（从 r_inner 到 r_p_out）
    rad_end = math.radians(SPAN_DEG + plat_deg)
    ex0, ey0 = r_inner * math.cos(rad_end), r_inner * math.sin(rad_end)
    ex1, ey1 = r_p_out * math.cos(rad_end), r_p_out * math.sin(rad_end)
    o_ep = CYLINDER(s, R=20.0, H=h_rail + 40.0, O=0.0).translate((ex0, ey0, H_TOTAL - 40.0))
    o_main.uniteWith(o_ep); o_ep.erase()
    eseg = math.hypot(ex1 - ex0, ey1 - ey0)
    eyaw = math.degrees(math.atan2(ey1 - ey0, ex1 - ex0))
    for hr in (120.0, h_rail * 0.52, h_rail):
        o_er = CYLINDER(s, R=18.0, H=eseg + 25.0, O=0.0).rotateY(90.0).rotateZ(eyaw).translate((ex0, ey0, H_TOTAL + hr))
        o_main.uniteWith(o_er); o_er.erase()

    # 4. 罐体贴合定位端口与线性标注
    s.setPoint((r_inner, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (r_outer + 150.0, 0.0, 0.0), (r_outer + 150.0, 0.0, H_TOTAL))
    s.setLinearDimension('D_TANK', (0.0, 0.0, 0.0), (R_T, 0.0, 0.0))
