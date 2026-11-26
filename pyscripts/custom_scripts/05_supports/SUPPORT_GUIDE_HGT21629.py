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
          TooltipShort=u"导向管托 (HG/T 21629 B1)",
          TooltipLong=u"HG/T 21629-2021 B1 导向管托，含双立板滑动管托、公用底座垫板与两侧L型限位导向挡块",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"导向管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至管托底板底面净高 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"管托底宽", TooltipLong=u"内部滑动管托底板宽度 B1 (mm)")
@param(STOP_H=LENGTH, TooltipShort=u"挡块高度", TooltipLong=u"两侧导向限位挡块高度 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"立板、底板与挡块厚度 (mm)")
def SUPPORT_GUIDE_HGT21629(
    s,
    D=168.3,
    H1=100.0,
    L1=300.0,
    B1=140.0,
    STOP_H=45.0,
    T_PLT=10.0,
    ID=u"SUPPORT_GUIDE_HGT21629",
    **kw
):
    u"""导向管托 (原点在管道中心线, 管道沿 X 轴, 限制 Y 向位移)。"""
    D = max(32.0, float(D))
    r_p = D / 2.0
    H1 = float(H1)
    if H1 < 1.0:
        H1 = 1.0
    L1 = float(L1)
    if L1 < 1.0:
        L1 = 1.0
    B1 = float(B1)
    if B1 < 1.0:
        B1 = 1.0
    STOP_H = max(25.0, float(STOP_H))
    T_PLT = max(6.0, float(T_PLT))

    z_shoe_bot = -(r_p + H1)
    z_sub_bot = z_shoe_bot - T_PLT
    z_shoe_top = z_shoe_bot + T_PLT
    sub_b = B1 + T_PLT * 2.0 + 90.0
    sub_l = L1 * 0.75

    # 1. 下部公用结构垫板（与两侧限位挡块及管托底面紧密贴合）
    o_main = CORNERBOX(s, L=sub_l, W=sub_b, H=T_PLT).translate((-sub_l / 2.0, -sub_b / 2.0, z_sub_bot))

    # 2. 滑动管托底板（坐落于结构垫板上，沿 X 方向突出，体现可轴向滑动特征）
    o_sbase = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_shoe_bot - 0.5))
    o_main.uniteWith(o_sbase)
    o_sbase.erase()

    # 3. 双纵向立板 + 两端横肋（带管弧口）
    web_sp = max(T_PLT * 2.8, min(B1 * 0.56, D * 0.55))
    web_top_z = -math.sqrt(max(1.0, r_p * r_p - (web_sp / 2.0) ** 2)) + 14.0
    web_h = max(25.0, web_top_z - (z_shoe_top - 1.0))
    for sy in (-1.0, 1.0):
        wy = sy * (web_sp / 2.0) - T_PLT / 2.0
        o_web = CORNERBOX(s, L=L1, W=T_PLT, H=web_h).translate((-L1 / 2.0, wy, z_shoe_top - 1.0))
        o_pcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_web.subtractFrom(o_pcut)
        o_pcut.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    rib_w = max(14.0, web_sp - T_PLT + 2.0)
    rib_h = max(20.0, (-r_p + 12.0) - (z_shoe_top - 1.0))
    for sx in (-1.0, 1.0):
        rx = sx * (L1 * 0.36) - T_PLT / 2.0
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx, -rib_w / 2.0, z_shoe_top - 1.0))
        o_rcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_rib.subtractFrom(o_rcut)
        o_rcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 4. 两侧限位导向挡块（带压板防抬升凸缘 + 外侧加强肋）
    gap_y = 3.0
    stop_l = min(sub_l * 0.78, L1 * 0.52)
    lip_w = max(18.0, T_PLT * 2.0)
    for sy in (-1.0, 1.0):
        # 竖向限位立板
        y_inner = sy * (B1 / 2.0 + gap_y)
        y_wall = y_inner if sy > 0 else (y_inner - T_PLT)
        o_stop = CORNERBOX(s, L=stop_l, W=T_PLT, H=STOP_H).translate((-stop_l / 2.0, y_wall, z_shoe_bot - 1.0))
        o_main.uniteWith(o_stop)
        o_stop.erase()

        # 顶部防跳动压耳（盖在管托底板边缘上方，留 3mm 间隙）
        y_lip = (y_inner - lip_w + T_PLT) if sy > 0 else (y_inner - T_PLT)
        o_lip = CORNERBOX(s, L=stop_l, W=lip_w, H=T_PLT).translate(
            (-stop_l / 2.0, y_lip, z_shoe_bot + STOP_H - T_PLT))
        o_main.uniteWith(o_lip)
        o_lip.erase()

        # 外侧双加强肋
        gus_w = (sub_b / 2.0) - (B1 / 2.0 + gap_y + T_PLT)
        for sx in (-1.0, 1.0):
            gx = sx * (stop_l * 0.35) - T_PLT / 2.0
            gy = (y_inner + T_PLT - 1.0) if sy > 0 else (y_inner - T_PLT - gus_w + 1.0)
            o_gus = CORNERBOX(s, L=T_PLT, W=gus_w, H=STOP_H * 0.85).translate((gx, gy, z_shoe_bot - 1.0))
            o_main.uniteWith(o_gus)
            o_gus.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_shoe_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_shoe_bot), (L1 / 2.0, 0.0, z_shoe_bot))
    s.setLinearDimension('B1', (0.0, -sub_b / 2.0, z_sub_bot), (0.0, sub_b / 2.0, z_sub_bot))
