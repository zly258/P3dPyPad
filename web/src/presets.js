// -*- coding: utf-8 -*-
/**
 * AutoCAD Plant 3D 经典工程构件预设脚本库
 */

export const PRESET_SCRIPTS = [
  {
    id: 'ELBOW_90',
    name: '90度长半径对焊弯头 (ELBOW_90)',
    category: '管件类',
    description: 'ASME B16.9 / GB/T 12459 90度长半径无缝对焊弯头，带空间圆环流道、两端坡口与切线直段',
    code: `# -*- coding: utf-8 -*-
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *

@activate(Group="Elbow", TooltipShort=u"90度对焊弯头", TooltipLong=u"90度长半径无缝对焊弯头（带标准对焊坡口与全贯通内流道）", LengthUnit="mm", Ports=2)
@group("MainDimensions", TooltipLong=u"弯头主要几何尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", TooltipLong=u"弯头公称管道外径 OD")
@param(R=LENGTH, TooltipShort=u"弯曲半径 R", TooltipLong=u"中心线弯曲半径 (长半径 1.5D)")
@param(THK=LENGTH0, TooltipShort=u"管道壁厚 T", TooltipLong=u"公称壁厚，大于0时贯通内流道")
@param(TL=LENGTH0, TooltipShort=u"切线直段 TL", TooltipLong=u"端口对焊切线直段延伸长度")
@param(BW=LENGTH0, TooltipShort=u"坡口长度 BW", TooltipLong=u"端口 37.5° 对焊坡口倒角轴向长度")
@param(ID=STRING, TooltipShort=u"构件位号", TooltipLong=u"弯头规格标识，如 E90-DN100")
def ELBOW_90(s, D=114.3, R=152.4, THK=6.0, TL=25.0, BW=3.0, ID=u"ELBOW_90-DN100", **kw):
    D = float(D)
    R = float(R)
    THK = float(THK)
    TL = float(TL)
    BW = float(BW)

    r_outer = D / 2.0
    if R <= r_outer + 5.0:
        R = r_outer * 1.5
    if TL < 0.0:
        TL = 0.0
    if BW < 0.0:
        BW = 0.0
    if THK <= 0.0 or THK >= r_outer * 0.8:
        THK = max(3.0, r_outer * 0.11)

    r_inner = r_outer - THK
    bevel_len = min(max(0.0, BW), TL * 0.45) if TL > 2.0 else 0.0
    r_bevel_tip = r_inner + min(1.6, THK * 0.25)

    # 1. 主弯曲段：ARC3D 在 XY 平面内，两端中心线切线交点在 (0, 0, 0)
    o_main = ARC3D(s, D=r_outer, R=R, A=90.0)

    # 2. 两端切线直段 + 标准 37.5° 对焊坡口锥台
    if TL > 0.0:
        cyl_len = max(1.0, TL - bevel_len)
        # 端口 1 (沿 +Y 延伸)
        o_ext1 = CYLINDER(s, R=r_outer, H=cyl_len, O=0.0).rotateX(-90.0).translate((0.0, R, 0.0))
        o_main.uniteWith(o_ext1); o_ext1.erase()
        if bevel_len > 0.5:
            o_bev1 = CONE(s, R1=r_outer, R2=r_bevel_tip, H=bevel_len).rotateX(-90.0).translate((0.0, R + cyl_len, 0.0))
            o_main.uniteWith(o_bev1); o_bev1.erase()

        # 端口 2 (沿 +X 延伸)
        o_ext2 = CYLINDER(s, R=r_outer, H=cyl_len, O=0.0).rotateY(90.0).translate((R, 0.0, 0.0))
        o_main.uniteWith(o_ext2); o_ext2.erase()
        if bevel_len > 0.5:
            o_bev2 = CONE(s, R1=r_outer, R2=r_bevel_tip, H=bevel_len).rotateY(90.0).translate((R + cyl_len, 0.0, 0.0))
            o_main.uniteWith(o_bev2); o_bev2.erase()

    # 3. 贯通内流道
    o_core = ARC3D(s, D=r_inner, R=R, A=90.0)
    core_ext = TL + 5.0
    o_c1 = CYLINDER(s, R=r_inner, H=core_ext, O=0.0).rotateX(-90.0).translate((0.0, R, 0.0))
    o_core.uniteWith(o_c1); o_c1.erase()
    o_c2 = CYLINDER(s, R=r_inner, H=core_ext, O=0.0).rotateY(90.0).translate((R, 0.0, 0.0))
    o_core.uniteWith(o_c2); o_c2.erase()

    o_main.subtractFrom(o_core)
    o_core.erase()

    # 4. 端口设置与工程标注
    p1_y = R + TL
    p2_x = R + TL
    s.setPoint((0.0, p1_y, 0.0), (0.0, 1.0, 0.0))
    s.setPoint((p2_x, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("R", (0.0, 0.0, -r_outer), (R, 0.0, -r_outer))
    s.setLinearDimension("D", (p2_x, 0.0, -r_outer), (p2_x, 0.0, r_outer))
    if TL > 0.0:
        s.setLinearDimension("TL", (R, 0.0, r_outer), (R + TL, 0.0, r_outer))
`
  },
  {
    id: 'TEE_EQUAL',
    name: '等径/异径对焊三通 (TEE_EQUAL)',
    category: '管件类',
    description: 'GB/T 12459 锻制对焊三通，带三端坡口、拔制过渡肩圈与T形贯通内腔',
    code: `# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *

@activate(Group="Tee", Ports=3, TooltipShort=u"对焊等径/异径三通 (GB/T 12459)", TooltipLong=u"化工标准 GB/T 12459 锻制对焊三通，带三端坡口、拔制过渡圆领与T形贯通内腔", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"管件主要结构尺寸：口径、中心距与壁厚")
@param(D=LENGTH, TooltipShort=u"主管外径 OD", TooltipLong=u"主管外径 OD")
@param(D_B=LENGTH, TooltipShort=u"支管外径 OD_B", TooltipLong=u"支管外径 OD_B")
@param(C=LENGTH, TooltipShort=u"主管中心距 C", TooltipLong=u"主管中心至端面距 C")
@param(M=LENGTH, TooltipShort=u"支管中心距 M", TooltipLong=u"主管中心至支管端面距 M")
@param(THK=LENGTH0, TooltipShort=u"壁厚 T", TooltipLong=u"公称壁厚 T")
@param(ID=STRING, TooltipShort=u"件号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def TEE_EQUAL(s, D=114.3, D_B=114.3, C=105.0, M=105.0, THK=6.0, ID="TEE-DN100", **kw):
    D = max(20.0, float(D))
    D_B = max(15.0, min(D, float(D_B) if float(D_B) > 0 else D))
    C = max(D * 0.65, float(C))
    M = max(D * 0.65, float(M))
    THK = max(2.5, min(D * 0.25, float(THK)))

    r_main = D / 2.0
    r_br = D_B / 2.0
    r_in_main = max(4.0, r_main - THK)
    r_in_br = max(3.0, r_br - THK * 0.9)
    bev = min(3.0, THK * 0.45)

    # 1. 主管筒体 (沿 X 轴 [-C, +C])
    L_main = 2.0 * (C - bev)
    o_body = CYLINDER(s, R=r_main, H=L_main, O=0.0).rotateY(90.0).translate((-L_main / 2.0, 0.0, 0.0))
    b_l = CONE(s, R1=r_main, R2=r_main - bev * 0.6, H=bev, E=0.0).rotateY(-90.0).translate((-(C - bev), 0.0, 0.0))
    o_body.uniteWith(b_l); b_l.erase()
    b_r = CONE(s, R1=r_main, R2=r_main - bev * 0.6, H=bev, E=0.0).rotateY(90.0).translate((C - bev, 0.0, 0.0))
    o_body.uniteWith(b_r); b_r.erase()

    # 2. 中部锻造三通拔制过渡肩圈 + 支管筒体 (沿 +Z 轴 [0, M])
    o_collar = CONE(s, R1=r_br + THK * 1.3, R2=r_br, H=r_main * 0.45, E=0.0).translate((0.0, 0.0, r_main * 0.65))
    o_body.uniteWith(o_collar); o_collar.erase()

    o_br = CYLINDER(s, R=r_br, H=M - bev, O=0.0).translate((0.0, 0.0, 0.0))
    o_body.uniteWith(o_br); o_br.erase()
    b_t = CONE(s, R1=r_br, R2=r_br - bev * 0.6, H=bev, E=0.0).translate((0.0, 0.0, M - bev))
    o_body.uniteWith(b_t); b_t.erase()

    # 3. T 形贯通内流道
    o_bore = CYLINDER(s, R=r_in_main, H=2.0 * C + 10.0, O=0.0).rotateY(90.0).translate((-(C + 5.0), 0.0, 0.0))
    o_bore_br = CYLINDER(s, R=r_in_br, H=M + 6.0, O=0.0).translate((0.0, 0.0, 0.0))
    o_bore.uniteWith(o_bore_br); o_bore_br.erase()
    o_body.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-C, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, M), (0.0, 0.0, 1.0))

    s.setLinearDimension("C", (-C, 0.0, -r_main), (0.0, 0.0, -r_main))
`
  },
  {
    id: 'REDUCER_CONCENTRIC',
    name: '同心对焊异径管/大小头 (REDUCER_CONCENTRIC)',
    category: '管件类',
    description: 'GB/T 12459 同心对焊大小头，带两端直管延伸段、圆台过渡段与贯通内孔',
    code: `# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *

@activate(Group="Reducer", Ports=2, TooltipShort=u"同心对焊大小头 (GB/T 12459)", TooltipLong=u"化工标准 GB/T 12459 同心对焊异径管，带两端直管段、锥形过渡段与中空内腔", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"管件主要结构尺寸：口径、中心距与壁厚")
@param(D1=LENGTH, TooltipShort=u"大端外径 OD1", TooltipLong=u"大端外径 OD1")
@param(D2=LENGTH, TooltipShort=u"小端外径 OD2", TooltipLong=u"小端外径 OD2")
@param(H=LENGTH, TooltipShort=u"异径管总长 H", TooltipLong=u"异径管总长 H")
@param(THK=LENGTH0, TooltipShort=u"壁厚 T", TooltipLong=u"壁厚 T")
@param(ID=STRING, TooltipShort=u"件号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def REDUCER_CONCENTRIC(s, D1=168.3, D2=114.3, H=140.0, THK=7.1, ID="RED-150x100", **kw):
    D1 = max(25.0, float(D1))
    D2 = max(15.0, min(D1 * 0.92, float(D2)))
    H = max(40.0, float(H))
    THK = max(2.5, min(D2 * 0.25, float(THK)))

    r1 = D1 / 2.0
    r2 = D2 / 2.0
    tl1 = H * 0.18
    tl2 = H * 0.16
    h_cone = H - tl1 - tl2

    # 沿 +X 轴从 x=0 (大端 D1) 到 x=H (小端 D2)
    o_body = CYLINDER(s, R=r1, H=tl1, O=0.0).rotateY(90.0)
    o_cone = CONE(s, R1=r1, R2=r2, H=h_cone, E=0.0).rotateY(90.0).translate((tl1, 0.0, 0.0))
    o_body.uniteWith(o_cone); o_cone.erase()
    o_s = CYLINDER(s, R=r2, H=tl2, O=0.0).rotateY(90.0).translate((tl1 + h_cone, 0.0, 0.0))
    o_body.uniteWith(o_s); o_s.erase()

    # 贯通内流道
    ri1 = max(4.0, r1 - THK)
    ri2 = max(3.0, r2 - THK * 0.85)
    o_bore = CYLINDER(s, R=ri1, H=tl1 + 4.0, O=0.0).rotateY(90.0).translate((-3.0, 0.0, 0.0))
    o_bcone = CONE(s, R1=ri1, R2=ri2, H=h_cone, E=0.0).rotateY(90.0).translate((tl1, 0.0, 0.0))
    o_bore.uniteWith(o_bcone); o_bcone.erase()
    o_bs = CYLINDER(s, R=ri2, H=tl2 + 4.0, O=0.0).rotateY(90.0).translate((tl1 + h_cone - 1.0, 0.0, 0.0))
    o_bore.uniteWith(o_bs); o_bs.erase()

    o_body.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("H", (0.0, 0.0, -r1), (H, 0.0, -r1))
    s.setLinearDimension("D1", (0.0, -r1, 0.0), (0.0, r1, 0.0))
    s.setLinearDimension("D2", (H, -r2, 0.0), (H, r2, 0.0))
`
  },
  {
    id: 'FLANGE_WN',
    name: '带颈对焊法兰 WN/RF (FLANGE_WN)',
    category: '法兰类',
    description: 'ASME B16.5 / GB/T 9115 带颈对焊钢制管法兰，带突面密封台与圆锥高颈过渡',
    code: `# -*- coding: utf-8 -*-
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *

@activate(Group="Flange", TooltipShort=u"带颈对焊法兰 WN", TooltipLong=u"带颈对焊法兰（WN/RF，突面密封，锥形高颈过渡，全贯通内孔）", LengthUnit="mm", Ports=2)
@group("MainDimensions", TooltipLong=u"法兰主要几何尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", TooltipLong=u"与法兰对焊的管道外径 OD")
@param(L=LENGTH, TooltipShort=u"法兰总长 L", TooltipLong=u"密封面到对焊端的轴向总长度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(THK=LENGTH0, TooltipShort=u"管道壁厚", TooltipLong=u"对焊端管道壁厚")
@param(ID=STRING, TooltipShort=u"构件位号", TooltipLong=u"法兰规格标识，如 WN-DN100")
def FLANGE_WN(s, D=114.3, L=100.0, FL_OD=220.0, FL_T=20.0, THK=6.0, ID=u"FLANGE-WN-DN100", **kw):
    D = float(D)
    L = float(L)
    FL_OD = float(FL_OD)
    FL_T = float(FL_T)
    THK = float(THK)

    r_pipe = D / 2.0
    if FL_OD <= D * 1.25:
        FL_OD = D * 1.9
    if FL_T <= 4.0:
        FL_T = max(12.0, D * 0.18)
    if THK <= 0.0 or THK >= r_pipe * 0.7:
        THK = max(3.0, r_pipe * 0.11)
    if L <= FL_T + 10.0:
        L = FL_T + max(25.0, D * 0.5)

    r_flange = FL_OD / 2.0
    r_bore = max(2.0, r_pipe - THK)
    rf_t = max(2.0, FL_T * 0.12)
    rf_r = min(r_flange * 0.82, r_flange - max(6.0, FL_T * 0.45))
    hub_r = max(r_pipe + THK, r_flange * 0.46)
    hub_len = max(10.0, L - FL_T)

    # 1. 法兰盘（密封面位于 X=0，向 +X 延伸 FL_T）
    o_disc = CYLINDER(s, R=r_flange, H=FL_T, O=0.0).rotateY(90.0)

    # 2. 突面密封台（向 -X 突出 rf_t）
    o_rf = CYLINDER(s, R=rf_r, H=rf_t, O=0.0).rotateY(90.0).translate((-rf_t, 0.0, 0.0))
    o_disc.uniteWith(o_rf)
    o_rf.erase()

    # 3. 锥形高颈：根部 hub_r 过渡到对焊端管道外径 r_pipe
    o_hub = CONE(s, R1=hub_r, R2=r_pipe, H=hub_len, E=0.0).rotateY(90.0).translate((FL_T, 0.0, 0.0))
    o_disc.uniteWith(o_hub)
    o_hub.erase()

    # 4. 全贯通内孔
    o_bore = CYLINDER(s, R=r_bore, H=L + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(rf_t + 3.0), 0.0, 0.0))
    o_disc.subtractFrom(o_bore)
    o_bore.erase()

    # 5. 端口：密封面中心 + 对焊端中心
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
`
  },
  {
    id: 'VALVE_BALL',
    name: '两片式法兰球阀 (VALVE_BALL)',
    category: '阀门类',
    description: 'API 608 / GB/T 12237 两片式分体铸钢法兰球阀，带阀杆平台、手柄与连接螺柱',
    code: `# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *

@activate(Group="Valve", Ports=2, TooltipShort=u"两片式法兰球阀", TooltipLong=u"两片式分体连接法兰球阀，带球形阀腔、中体连接法兰与手柄", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阀门主要结构尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", TooltipLong=u"管道外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", TooltipLong=u"结构长度 L")
@param(H=LENGTH, TooltipShort=u"中心至手柄高 H", TooltipLong=u"中心至手柄高 H")
@param(LEVER_L=LENGTH, TooltipShort=u"手柄总长", TooltipLong=u"手柄总长")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰密封面外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def VALVE_BALL(s, D=114.3, L=230.0, H=195.0, LEVER_L=280.0, FL_OD=220.0, FL_T=22.0, ID="Q41F-16C", **kw):
    D = max(20.0, float(D))
    L = max(120.0, float(L))
    H = max(95.0, float(H))
    LEVER_L = max(120.0, float(LEVER_L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.88
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 左右两片式流道筒节 + 两端 RF 法兰
    o_valve = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_valve.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_valve.uniteWith(c_fl); c_fl.erase()

    # 2. 中部球体包容腔 + 两片式中体连接法兰盘
    r_chamber = r_pipe * 1.48
    w_chamber = L * 0.46
    o_cham = CYLINDER(s, R=r_chamber, H=w_chamber, O=0.0).rotateY(90.0).translate((-w_chamber * 0.5, 0.0, 0.0))
    o_valve.uniteWith(o_cham); o_cham.erase()

    r_split_fl = min(r_fl * 0.94, r_chamber * 1.24)
    t_split = FL_T * 1.4
    o_split = CYLINDER(s, R=r_split_fl, H=t_split, O=0.0).rotateY(90.0).translate((-t_split * 0.35, 0.0, 0.0))
    o_valve.uniteWith(o_split); o_split.erase()

    # 3. 顶部防吹出阀杆脖颈 + 方形安装平台
    z_pad = r_chamber + (H - r_chamber) * 0.45
    r_stem_boss = r_pipe * 0.38
    o_boss = CYLINDER(s, R=r_stem_boss, H=z_pad, O=0.0)
    o_valve.uniteWith(o_boss); o_boss.erase()

    pad_w = r_stem_boss * 2.35
    o_pad = BOX(s, L=pad_w, W=12.0, H=pad_w).translate((0.0, 0.0, z_pad - 6.0))
    o_valve.uniteWith(o_pad); o_pad.erase()

    r_stem = max(8.0, r_pipe * 0.18)
    o_stem = CYLINDER(s, R=r_stem, H=H - z_pad + 14.0, O=0.0).translate((0.0, 0.0, z_pad - 2.0))
    o_valve.uniteWith(o_stem); o_stem.erase()

    # 4. 手柄杠杆
    h_bar_t = 9.0
    h_bar_w = max(22.0, r_stem * 2.4)
    l_grip = LEVER_L * 0.75
    o_grip = BOX(s, L=h_bar_w, W=h_bar_t, H=l_grip).translate((l_grip * 0.5, 0.0, H))
    o_valve.uniteWith(o_grip); o_grip.erase()

    # 5. 贯通内腔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_valve.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
`
  }
];
