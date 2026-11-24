# -*- coding: utf-8 -*-
# CD-ZD2010 117 导向支架套筒（外圆套筒 + 左右夹耳 + 内嵌6块径向纵向定位隔板包围内管）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="117导向支架套筒", TooltipLong="CD-ZD2010 117 导向支架套筒", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="内部管道外径 OD")
@param(L=LENGTH, TooltipShort="套筒长", TooltipLong="套筒沿管道轴向长度 B", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="壁厚", TooltipLong="套筒及径向隔板厚度")
@param(GAP=LENGTH, TooltipShort="径向高", TooltipLong="套筒径向隔板净高或间隙参数")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_117(s, D=159.0, L=200.0, T=8.0, GAP=5.0, ID=u"ZD_117", **kw):
    D = float(D); L = float(L); T = float(T); GAP = float(GAP)
    if D < 25.0: D = 25.0
    if L < 60.0: L = 60.0
    if T < 4.0: T = 4.0
    R_pipe = D / 2.0
    # 图集 117 中外筒直径 d 约为 2.2*D ~ 3.2*D (内嵌径向隔板)
    fin_h = max(D * 0.65, GAP * 12.0, 75.0)
    R_out = R_pipe + fin_h + T
    R_in_sleeve = R_out - T

    # 1. 外圆分瓣套筒圆环 (沿 X 轴长 L，在 Z=0 两侧带窄分型缝及夹耳)
    o1 = CYLINDER(s, R=R_out, H=L, O=0.0).rotateY(90.0).translate((-(L / 2.0), 0.0, 0.0))
    o_cav = CYLINDER(s, R=R_in_sleeve, H=L + 4.0, O=0.0).rotateY(90.0).translate((-(L / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_cav); o_cav.erase()

    # 2. 内嵌管夹环 + 6 块放射状径向纵向定位隔板 (30°, 90°, 150°, 210°, 270°, 330°)
    o_hub = CYLINDER(s, R=R_pipe + T, H=L * 0.92, O=0.0).rotateY(90.0).translate((-(L * 0.46), 0.0, 0.0))
    o1.uniteWith(o_hub); o_hub.erase()
    for deg in (0.0, 60.0, 120.0):
        o_fin = BOX(s, L=T, W=R_in_sleeve * 2.0, H=L * 0.92).rotateX(deg)
        o1.uniteWith(o_fin); o_fin.erase()

    # 3. 左右两侧 (±Y) 分型缝与外部水平夹紧螺栓耳
    seam_gap = max(6.0, T * 0.8)
    ear_ext = T * 3.5
    for sy in (-1.0, 1.0):
        yc = sy * (R_out + ear_ext / 2.0 - T * 0.5)
        for sz in (-1.0, 1.0):
            o_ear = BOX(s, L=ear_ext, W=T, H=L).translate((0.0, yc, sz * (seam_gap / 2.0 + T / 2.0)))
            o1.uniteWith(o_ear); o_ear.erase()
        for sx in (-1.0, 1.0):
            o_b = CYLINDER(s, R=T * 0.55, H=seam_gap + T * 4.0, O=0.0).translate((sx * (L * 0.3), sy * (R_out + ear_ext * 0.45), -(seam_gap / 2.0 + T * 2.0)))
            o1.uniteWith(o_b); o_b.erase()

    # 4. 切除中心内管通孔 (R = R_pipe)
    o_pipe = CYLINDER(s, R=R_pipe, H=L + 20.0, O=0.0).rotateY(90.0).translate((-(L / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (-(L / 2.0), 0.0, 0.0), ((L / 2.0), 0.0, 0.0))
