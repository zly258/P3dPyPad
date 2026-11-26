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

_HGT20592_PN16_A = {
    10: (17.2, 90.0, 16.0),
    15: (21.3, 95.0, 16.0),
    20: (26.9, 105.0, 18.0),
    25: (33.7, 115.0, 18.0),
    32: (42.4, 140.0, 18.0),
    40: (48.3, 150.0, 18.0),
    50: (60.3, 165.0, 18.0),
    65: (76.1, 185.0, 18.0),
    80: (88.9, 200.0, 20.0),
    100: (114.3, 220.0, 20.0),
    125: (139.7, 250.0, 22.0),
    150: (168.3, 285.0, 22.0),
    200: (219.1, 340.0, 24.0),
    250: (273.0, 405.0, 26.0),
    300: (323.9, 460.0, 28.0),
    350: (355.6, 520.0, 30.0),
    400: (406.4, 580.0, 32.0),
    450: (457.0, 640.0, 40.0),
    500: (508.0, 715.0, 44.0),
    600: (610.0, 840.0, 54.0),
    700: (711.0, 910.0, 36.0),
    800: (813.0, 1025.0, 38.0),
    900: (914.0, 1125.0, 40.0),
}

def _std_noz_dims(dn_val):
    dn_i = int(round(float(dn_val)))
    if dn_i in _HGT20592_PN16_A:
        od, d_fl, t_fl = _HGT20592_PN16_A[dn_i]
        return od / 2.0, d_fl / 2.0, t_fl
    keys = sorted(_HGT20592_PN16_A.keys())
    if dn_i < keys[0]:
        od, d_fl, t_fl = _HGT20592_PN16_A[keys[0]]
        return od / 2.0, d_fl / 2.0, t_fl
    if dn_i > keys[-1]:
        od = float(dn_val) * 1.016
        return od / 2.0, (od + 210.0) / 2.0, 42.0
    for k0, k1 in zip(keys, keys[1:]):
        if k0 <= dn_i <= k1:
            t = (dn_i - k0) / float(k1 - k0)
            v0, v1 = _HGT20592_PN16_A[k0], _HGT20592_PN16_A[k1]
            od = v0[0] + t * (v1[0] - v0[0])
            d_fl = v0[1] + t * (v1[1] - v0[1])
            t_fl = v0[2] + t * (v1[2] - v0[2])
            return od / 2.0, d_fl / 2.0, t_fl
    return float(dn_val) * 0.54, float(dn_val) * 0.54 + 55.0, 22.0

@activate(Group="Equipment",
          TooltipShort=u"离心压缩机/鼓风机撬块 (API 617)",
          TooltipLong=u"API 617 离心压缩机/鼓风机撬块参数化模型，含重型公共钢结构撬座、主驱动电机与散热轮廓、增速齿轮箱、联轴器护罩、离心压缩机蜗壳及轴向进口/顶部出口法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"离心压缩机撬块主要尺寸参数")
@param(DN_SUC=LENGTH, TooltipShort=u"吸气口通径", TooltipLong=u"压缩机轴向吸气口公称通径 DN (mm)")
@param(DN_DIS=LENGTH, TooltipShort=u"排气口通径", TooltipLong=u"压缩机切向排气口公称通径 DN (mm)")
@param(L_SKID=LENGTH, TooltipShort=u"撬座总长", TooltipLong=u"公共钢结构底座总长 L (mm)", Ask4Dist=True)
@param(W_SKID=LENGTH, TooltipShort=u"撬座总宽", TooltipLong=u"公共钢结构底座总宽 W (mm)", Ask4Dist=True)
@param(H_SKID=LENGTH, TooltipShort=u"撬座高度", TooltipLong=u"公共底座型钢框架高度 (mm)")
@param(H_CL=LENGTH, TooltipShort=u"轴系中心高", TooltipLong=u"撬座底面至压缩机主轴中心线高度 (mm)", Ask4Dist=True)
@param(D_VOLUTE=LENGTH, TooltipShort=u"蜗壳外径", TooltipLong=u"离心压缩机蜗壳外轮廓直径 (mm)")
@param(D_MOTOR=LENGTH, TooltipShort=u"主电机机座径", TooltipLong=u"主驱动电机外轮廓直径 (mm)")
@param(L_MOTOR=LENGTH, TooltipShort=u"主电机长度", TooltipLong=u"主驱动电机机身长度 (mm)")
def EQ_COMPRESSOR_SKID(
    s,
    DN_SUC=300.0,
    DN_DIS=200.0,
    L_SKID=3600.0,
    W_SKID=1600.0,
    H_SKID=280.0,
    H_CL=1050.0,
    D_VOLUTE=1050.0,
    D_MOTOR=720.0,
    L_MOTOR=1150.0,
    ID=u"EQ_COMPRESSOR_SKID",
    **kw
):
    u"""API 617 离心压缩机撬块 (沿 X 轴布置：-X 主电机 -> 中部增速齿轮箱 -> +X 蜗壳压缩机，底座底面 Z=0)。"""
    DN_SUC = max(100.0, float(DN_SUC))
    DN_DIS = max(80.0, float(DN_DIS))
    L_SKID = float(L_SKID)
    if L_SKID < 1.0:
        L_SKID = 1.0
    W_SKID = float(W_SKID)
    if W_SKID < 1.0:
        W_SKID = 1.0
    H_SKID = max(180.0, float(H_SKID))
    D_VOLUTE = max(650.0, float(D_VOLUTE))
    D_MOTOR = max(450.0, float(D_MOTOR))
    L_MOTOR = max(700.0, float(L_MOTOR))
    R_VOL = D_VOLUTE * 0.5
    R_MOT = D_MOTOR * 0.5
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0

    half_l = L_SKID * 0.5
    half_w = W_SKID * 0.5

    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    # 1. 公共钢结构撬座 (底板 + 主框架 + 顶台面)
    o_main = CORNERBOX(s, L=L_SKID, W=W_SKID, H=H_SKID * 0.85).translate((-half_l, -half_w, 0.0))
    # 撬座四周底缘法兰唇边
    o_lip = CORNERBOX(s, L=L_SKID + 80.0, W=W_SKID + 80.0, H=28.0).translate((-half_l - 40.0, -half_w - 40.0, 0.0))
    o_main.uniteWith(o_lip)
    o_lip.erase()
    # 撬座顶面板
    o_deck = CORNERBOX(s, L=L_SKID + 40.0, W=W_SKID + 40.0, H=H_SKID * 0.22).translate(
        (-half_l - 20.0, -half_w - 20.0, H_SKID * 0.78)
    )
    o_main.uniteWith(o_deck)
    o_deck.erase()

    # 2. 主驱动电机 (-X 端，带散热肋轮廓、风扇罩、接线盒与安装底脚)
    x_mot_start = -half_l + 200.0
    x_mot_end = x_mot_start + L_MOTOR
    o_mot = CYLINDER(s, R=R_MOT, H=L_MOTOR, O=0.0).rotateY(90.0).translate((x_mot_start, 0.0, H_CL))
    o_main.uniteWith(o_mot)
    o_mot.erase()
    # 电机后端冷却风罩
    o_mcowl = CYLINDER(s, R=R_MOT * 0.92, H=L_MOTOR * 0.16, O=0.0).rotateY(90.0).translate(
        (x_mot_start - L_MOTOR * 0.14, 0.0, H_CL)
    )
    o_main.uniteWith(o_mcowl)
    o_mcowl.erase()
    # 电机外周 6 条散热肋块 (LOD 300 辨识特征)
    for k in range(6):
        ang = k * 60.0 + 30.0
        o_fin = CORNERBOX(s, L=L_MOTOR * 0.72, W=36.0, H=44.0).translate(
            (x_mot_start + L_MOTOR * 0.14, -18.0, R_MOT - 10.0)
        ).rotateX(ang).translate((0.0, 0.0, H_CL))
        o_main.uniteWith(o_fin)
        o_fin.erase()
    # 电机顶部大接线盒 + 底座支墩
    o_tbox = CORNERBOX(s, L=L_MOTOR * 0.34, W=R_MOT * 0.75, H=R_MOT * 0.55).translate(
        (x_mot_start + L_MOTOR * 0.33, -R_MOT * 0.375, H_CL + R_MOT * 0.85)
    )
    o_mped = CORNERBOX(s, L=L_MOTOR * 0.82, W=D_MOTOR * 0.92, H=H_CL - H_SKID - R_MOT * 0.55).translate(
        (x_mot_start + L_MOTOR * 0.09, -D_MOTOR * 0.46, H_SKID - 4.0)
    )
    o_main.uniteWith(o_tbox)
    o_tbox.erase()
    o_main.uniteWith(o_mped)
    o_mped.erase()

    # 3. 低速联轴器护罩 + 增速齿轮箱 (中部)
    l_cpl1 = max(240.0, L_SKID * 0.08)
    x_gb_start = x_mot_end + l_cpl1
    l_gb = max(620.0, L_SKID * 0.21)
    w_gb = max(720.0, W_SKID * 0.52)
    h_gb_top = H_CL + R_MOT * 0.88
    o_cpl1 = CYLINDER(s, R=R_MOT * 0.36, H=l_cpl1 + 40.0, O=0.0).rotateY(90.0).translate((x_mot_end - 20.0, 0.0, H_CL))
    o_gb = CORNERBOX(s, L=l_gb, W=w_gb, H=h_gb_top - H_SKID + 6.0).translate((x_gb_start, -w_gb * 0.5, H_SKID - 6.0))
    # 增速箱中分法兰边
    o_gb_fl = CORNERBOX(s, L=l_gb + 70.0, W=w_gb + 70.0, H=48.0).translate(
        (x_gb_start - 35.0, -(w_gb + 70.0) * 0.5, H_CL - 24.0)
    )
    # 润滑油冷却器辅助筒 (挂于齿轮箱 -Y 侧)
    o_oil = CYLINDER(s, R=115.0, H=l_gb * 0.88, O=0.0).rotateY(90.0).translate(
        (x_gb_start + l_gb * 0.06, -w_gb * 0.5 - 120.0, H_SKID + 200.0)
    )
    o_oil_br = CORNERBOX(s, L=l_gb * 0.6, W=140.0, H=110.0).translate(
        (x_gb_start + l_gb * 0.2, -w_gb * 0.5 - 120.0, H_SKID + 145.0)
    )
    for ob in (o_cpl1, o_gb, o_gb_fl, o_oil, o_oil_br):
        o_main.uniteWith(ob)
        ob.erase()

    # 4. 高速联轴器护罩 + 离心压缩机蜗壳 (+X 端)
    l_cpl2 = max(240.0, L_SKID * 0.08)
    w_vol = max(380.0, D_VOLUTE * 0.42)
    x_vol_start = min(half_l - w_vol - 220.0, x_gb_start + l_gb + l_cpl2)
    x_vol_mid = x_vol_start + w_vol * 0.5
    o_cpl2 = CYLINDER(s, R=R_MOT * 0.30, H=(x_vol_start - (x_gb_start + l_gb)) + 60.0, O=0.0).rotateY(90.0).translate(
        (x_gb_start + l_gb - 30.0, 0.0, H_CL)
    )
    o_main.uniteWith(o_cpl2)
    o_cpl2.erase()

    # 压缩机蜗壳主圆盘体 + 蜗壳中分外法兰环 + 压缩机支座
    o_vol = CYLINDER(s, R=R_VOL, H=w_vol, O=0.0).rotateY(90.0).translate((x_vol_start, 0.0, H_CL))
    o_vfl = CYLINDER(s, R=R_VOL + 65.0, H=46.0, O=0.0).rotateY(90.0).translate((x_vol_mid - 23.0, 0.0, H_CL))
    o_vped = CORNERBOX(s, L=w_vol * 1.15, W=D_VOLUTE * 0.88, H=H_CL - H_SKID - R_VOL * 0.4).translate(
        (x_vol_mid - w_vol * 0.575, -D_VOLUTE * 0.44, H_SKID - 4.0)
    )
    for ob in (o_vol, o_vfl, o_vped):
        o_main.uniteWith(ob)
        ob.erase()

    # 5. 2 个工艺法兰口
    # Port 1: 压缩机轴向吸气进口 (+X)
    r_ps, r_fs, t_fs = _fl_dims(DN_SUC)
    x_suc_face = half_l + 180.0
    o_sp = CYLINDER(s, R=r_ps, H=x_suc_face - t_fs - (x_vol_start + w_vol - 40.0) + 2.0, O=0.0).rotateY(90.0).translate(
        (x_vol_start + w_vol - 40.0, 0.0, H_CL)
    )
    o_sf = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).rotateY(90.0).translate((x_suc_face - t_fs, 0.0, H_CL))
    o_main.uniteWith(o_sp)
    o_sp.erase()
    o_main.uniteWith(o_sf)
    o_sf.erase()
    p_suc = (x_suc_face, 0.0, H_CL)

    # Port 2: 压缩机切向排气出口 (+Z, 偏向 +Y 蜗壳切向)
    r_pd, r_fd, t_fd = _fl_dims(DN_DIS)
    y_dis = R_VOL * 0.52
    z_dis_face = H_CL + R_VOL + 260.0
    o_dp = CYLINDER(s, R=r_pd, H=z_dis_face - t_fd - (H_CL + R_VOL * 0.35) + 2.0, O=0.0).translate(
        (x_vol_mid, y_dis, H_CL + R_VOL * 0.35)
    )
    o_df = CYLINDER(s, R=r_fd, H=t_fd, O=0.0).translate((x_vol_mid, y_dis, z_dis_face - t_fd))
    o_main.uniteWith(o_dp)
    o_dp.erase()
    o_main.uniteWith(o_df)
    o_df.erase()
    p_dis = (x_vol_mid, y_dis, z_dis_face)

    # 6. 注册 2 个工艺端口
    s.setPoint(p_suc, (1.0, 0.0, 0.0))
    s.setPoint(p_dis, (0.0, 0.0, 1.0))

    # 7. 注册线性标注
    s.setLinearDimension('L_SKID', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('W_SKID', (0.0, -half_w, 0.0), (0.0, half_w, 0.0))
    s.setLinearDimension('H_CL', (x_vol_mid, 0.0, 0.0), (x_vol_mid, 0.0, H_CL))
