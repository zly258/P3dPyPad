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

@activate(Group="Support", Ports=1, TooltipShort=u"化工立管焊接耳式支座 (HG/T 21629 F6)", TooltipLong=u"化工行业标准 HG/T 21629-2021 F6/F7 立管焊接耳式支座 (Vertical Pipe Welded Ear Support)，含立管抱瓦补强圈、对称双侧梯形立筋腹板、侧向加劲肋与带地脚孔承重底板", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"支吊架主要结构尺寸：管道口径、结构与型钢规格")
@param(D=LENGTH, TooltipShort=u"立管外径 OD", Ask4Dist=True, TooltipLong=u"立管外径 OD")
@param(L_SPAN=LENGTH, TooltipShort=u"两耳座地脚孔中心距", Ask4Dist=True, TooltipLong=u"两耳座地脚孔中心距")
@param(H_EAR=LENGTH, TooltipShort=u"耳座总高 H", Ask4Dist=True, TooltipLong=u"耳座总高 H")
@param(W_BASE=LENGTH, TooltipShort=u"耳座底板宽 B", TooltipLong=u"耳座底板宽 B")
@param(T_PLATE=LENGTH0, TooltipShort=u"板厚 T", TooltipLong=u"板厚 T")
@param(ID=STRING, TooltipShort=u"耳座代号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def SUPPORT_EAR_LUG(s, D=219.1, L_SPAN=420.0, H_EAR=260.0, W_BASE=140.0, T_PLATE=14.0, ID="F6-DN200", **kw):
    D = max(50.0, float(D))
    r_pipe = D / 2.0
    L_SPAN = max(D + 140.0, float(L_SPAN))
    H_EAR = max(140.0, float(H_EAR))
    W_BASE = max(90.0, float(W_BASE))
    t = max(8.0, float(T_PLATE))

    # 1. 立管外壁环形护板/补强圈 (围绕 Z 轴的立管外壁，高 H_EAR * 1.15)
    h_pad = H_EAR * 1.15
    r_pad = r_pipe + t * 0.75
    o_ear = CYLINDER(s, R=r_pad, H=h_pad, O=0.0).translate((0.0, 0.0, -t))

    # 2. 左右 (±Y) 对称焊接耳式支座 (含带孔底板、梯形主立板、正交加劲背板)
    y_hole = L_SPAN / 2.0
    l_ear_y = (y_hole + W_BASE * 0.45) - r_pipe
    for sy in (-1.0, 1.0):
        y_mid = sy * (r_pipe + l_ear_y * 0.5)
        # 水平承重底板 (z in [0, t])
        base = BOX(s, L=l_ear_y + 10.0, W=t, H=W_BASE).translate((0.0, y_mid - sy * 5.0, t * 0.5))
        hc = CYLINDER(s, R=11.0, H=t + 6.0, O=0.0).translate((0.0, sy * y_hole, -2.0))
        base.subtractFrom(hc); hc.erase()
        o_ear.uniteWith(base); base.erase()

        # 竖向梯形主腹板 (用下宽上窄两阶叠加 + 斜切角切除形成标准 JB/T 4712.3 / HG/T 21629 F6 耳式支座外形)
        web = BOX(s, L=l_ear_y, W=H_EAR - t, H=t).translate((0.0, y_mid, t + (H_EAR - t) * 0.5))
        # 切去外上角形成斜边
        cut_diag = BOX(s, L=l_ear_y * 1.2, W=H_EAR, H=t * 3.0).rotateX(sy * 28.0).translate((0.0, sy * (r_pipe + l_ear_y * 1.08), H_EAR * 0.78))
        web.subtractFrom(cut_diag); cut_diag.erase()
        o_ear.uniteWith(web); web.erase()

        # 贴管壁竖向背衬垫板
        back_rib = BOX(s, L=t, W=H_EAR * 0.92, H=W_BASE * 0.82).translate((0.0, sy * (r_pipe + t * 0.6), t + H_EAR * 0.46))
        o_ear.uniteWith(back_rib); back_rib.erase()

    # 3. 挖除立管中心外径 D (立管沿 Z 轴穿过中心)
    o_pipe_cut = CYLINDER(s, R=r_pipe, H=h_pad + 30.0, O=0.0).translate((0.0, 0.0, -15.0))
    o_ear.subtractFrom(o_pipe_cut); o_pipe_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))

    s.setLinearDimension("L_SPAN", (0.0, -y_hole, 0.0), (0.0, y_hole, 0.0))
    s.setLinearDimension("H_EAR", (-r_pad, -y_hole, 0.0), (-r_pad, -y_hole, H_EAR))
    s.setLinearDimension("D", (-r_pipe, 0.0, h_pad), (r_pipe, 0.0, h_pad))
