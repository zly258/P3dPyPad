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
          TooltipShort=u"高密度绝热保冷管托 (HG/T 21629 C1)",
          TooltipLong=u"低温保冷管托，含高密度聚氨酯绝热瓦块、下半圆U形钢护壳、双道紧固抱箍、双立板与滑动底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"保冷管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑低温管道外径 D (mm)")
@param(T_INS=LENGTH, TooltipShort=u"保冷层厚", TooltipLong=u"高密度绝热保冷瓦块厚度 (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至滑动底板下表面总高度 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"保冷管托沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"滑动底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"U形护壳、立板与底板厚度 (mm)")
def SHOE_CRYOGENIC_INSUL(
    s,
    D=168.3,
    T_INS=80.0,
    H1=150.0,
    L1=350.0,
    B1=220.0,
    T_PLT=10.0,
    ID=u"SHOE_CRYOGENIC_INSUL",
    **kw
):
    u"""保冷管托 (原点在管道中心线, 管道沿 X 轴, 支座向 -Z 延伸)。"""
    D = max(32.0, float(D))
    r_p = D / 2.0
    T_INS = max(40.0, float(T_INS))
    H1 = float(H1)
    if H1 < 1.0:
        H1 = 1.0
    L1 = float(L1)
    if L1 < 1.0:
        L1 = 1.0
    B1 = float(B1)
    if B1 < 1.0:
        B1 = 1.0
    T_PLT = max(6.0, float(T_PLT))

    r_ins = r_p + T_INS
    t_shell = max(5.0, T_PLT * 0.7)
    r_shell = r_ins + t_shell
    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT

    # 1. 高密度绝热保冷瓦块（略长于U形钢护壳，体现保冷块台阶轮廓）
    ins_l = L1 * 0.92
    o_main = CYLINDER(s, R=r_ins, H=ins_l, O=r_p).rotateY(90.0).translate((-ins_l / 2.0, 0.0, 0.0))

    # 2. 下半圆 U 形钢护壳（含左右水平翻边，紧密包裹下半保冷瓦块）
    shell_l = L1 * 0.80
    o_shell = CYLINDER(s, R=r_shell, H=shell_l, O=r_ins - 1.5).rotateY(90.0).translate((-shell_l / 2.0, 0.0, 0.0))
    o_cut_top = CORNERBOX(s, L=shell_l + 20.0, W=r_shell * 2.6, H=r_shell * 1.5).translate(
        (-(shell_l / 2.0 + 10.0), -r_shell * 1.3, 0.0))
    o_shell.subtractFrom(o_cut_top)
    o_cut_top.erase()
    o_main.uniteWith(o_shell)
    o_shell.erase()

    # U形钢护壳两侧水平翻边耳条
    flange_w = max(20.0, T_PLT * 2.4)
    for sy in (-1.0, 1.0):
        fy = (r_ins - 2.0) if sy > 0 else -(r_ins - 2.0 + flange_w)
        o_fl = CORNERBOX(s, L=shell_l, W=flange_w, H=t_shell).translate((-shell_l / 2.0, fy, -t_shell))
        o_main.uniteWith(o_fl)
        o_fl.erase()

    # 3. 两道外部紧固钢带抱箍（绕过上半保冷瓦块并压紧于翻边）
    band_w = max(24.0, L1 * 0.08)
    band_t = max(4.0, t_shell * 0.7)
    band_sp = shell_l * 0.58
    for sx in (-1.0, 1.0):
        bx = sx * (band_sp / 2.0) - band_w / 2.0
        o_band = CYLINDER(s, R=r_ins + band_t, H=band_w, O=r_ins - 1.0).rotateY(90.0).translate((bx, 0.0, 0.0))
        o_main.uniteWith(o_band)
        o_band.erase()

    # 4. 滑动底板 + 双纵向支腿立板（承托 U 形护壳底部）
    o_base = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))
    o_main.uniteWith(o_base)
    o_base.erase()

    web_sp = max(T_PLT * 3.0, min(B1 * 0.56, r_shell * 0.90))
    web_top_z = -math.sqrt(max(1.0, r_shell * r_shell - (web_sp / 2.0) ** 2)) + 10.0
    web_h = max(20.0, web_top_z - (z_base_top - 1.0))
    for sy in (-1.0, 1.0):
        wy = sy * (web_sp / 2.0) - T_PLT / 2.0
        o_web = CORNERBOX(s, L=L1, W=T_PLT, H=web_h).translate((-L1 / 2.0, wy, z_base_top - 1.0))
        o_wcut = CYLINDER(s, R=r_ins, H=L1 + 30.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 15.0), 0.0, 0.0))
        o_web.subtractFrom(o_wcut)
        o_wcut.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    # 两端横向连接肋
    rib_w = max(16.0, web_sp - T_PLT + 2.0)
    rib_h = max(20.0, (-r_shell + 12.0) - (z_base_top - 1.0))
    for sx in (-1.0, 1.0):
        rx = sx * (shell_l * 0.36) - T_PLT / 2.0
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx, -rib_w / 2.0, z_base_top - 1.0))
        o_rcut = CYLINDER(s, R=r_ins, H=L1 + 30.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 15.0), 0.0, 0.0))
        o_rib.subtractFrom(o_rcut)
        o_rcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
