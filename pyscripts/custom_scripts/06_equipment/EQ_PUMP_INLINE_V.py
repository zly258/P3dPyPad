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
          TooltipShort=u"立式管道离心泵 (In-line)",
          TooltipLong=u"立式管道离心泵参数化模型，含水平同轴进出口双法兰、立式泵体与底脚、联轴支架及顶置立式电机",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"立式管道离心泵安装距、泵体与顶置电机主要尺寸参数")
@param(DN=LENGTH, TooltipShort=u"进出口公称通径", TooltipLong=u"水平同轴进出口法兰公称通径 DN (mm)")
@param(L_FF=LENGTH, TooltipShort=u"法兰面对面距", TooltipLong=u"进出口法兰面对面结构长度 L (mm)", Ask4Dist=True)
@param(H_CL=LENGTH, TooltipShort=u"流道中心高", TooltipLong=u"底板底面至水平管道中心线高度 H1 (mm)", Ask4Dist=True)
@param(D_BODY=LENGTH, TooltipShort=u"泵体蜗壳外径", TooltipLong=u"立式泵体蜗壳外径 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"底板底面至顶置电机顶部总高度 H (mm)", Ask4Dist=True)
@param(D_MOTOR=LENGTH, TooltipShort=u"电机外径", TooltipLong=u"顶置立式电机机身外径 (mm)")
def EQ_PUMP_INLINE_V(
    s,
    DN=80.0,
    L_FF=400.0,
    H_CL=160.0,
    D_BODY=260.0,
    H_TOTAL=820.0,
    D_MOTOR=230.0,
    ID=u"EQ_PUMP_INLINE_V",
    **kw
):
    u"""立式管道离心泵 In-line (底面 Z=0，进出口沿 X 轴同轴布置于 Z=H_CL，电机沿 +Z 向上)。"""
    DN = max(25.0, float(DN))
    L_FF = float(L_FF)
    if L_FF < 1.0:
        L_FF = 1.0
    D_BODY = max(140.0, float(D_BODY))
    R_BODY = D_BODY / 2.0
    D_MOTOR = max(130.0, float(D_MOTOR))
    R_MOT = D_MOTOR / 2.0

    r_p, r_f, t_f = _std_noz_dims(DN)
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    half_l = L_FF / 2.0

    # 1. 水平同轴管段 + 进出口双法兰
    o_main = CYLINDER(s, R=r_p, H=L_FF - 2.0 * t_f + 4.0, O=0.0).rotateY(90.0).translate((-half_l + t_f - 2.0, 0.0, H_CL))

    o_fl1 = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(90.0).translate((-half_l, 0.0, H_CL))
    o_fl2 = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(90.0).translate((half_l - t_f, 0.0, H_CL))
    o_main.uniteWith(o_fl1)
    o_fl1.erase()
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 底座安装底板 + 泵体下部支座
    base_l = max(D_BODY * 0.95, L_FF * 0.58)
    base_w = max(D_BODY * 0.95, r_f * 2.0)
    base_t = 22.0
    o_base = CORNERBOX(s, L=base_l, W=base_w, H=base_t).translate((-base_l / 2.0, -base_w / 2.0, 0.0))
    o_ped = CYLINDER(s, R=R_BODY * 0.65, H=H_CL - base_t + 10.0, O=0.0).translate((0.0, 0.0, base_t - 4.0))
    o_main.uniteWith(o_base)
    o_base.erase()
    o_main.uniteWith(o_ped)
    o_ped.erase()

    # 3. 立式蜗壳泵体 (垂直圆柱腔体)
    vol_h = max(110.0, r_p * 2.2)
    z_vol0 = H_CL - vol_h * 0.45
    o_vol = CYLINDER(s, R=R_BODY, H=vol_h, O=0.0).translate((0.0, 0.0, z_vol0))
    o_main.uniteWith(o_vol)
    o_vol.erase()

    # 4. 泵盖法兰 + 立式灯笼支架 + 电机安装法兰
    z_cap = z_vol0 + vol_h
    h_remain = H_TOTAL - z_cap
    h_stool = h_remain * 0.34
    h_mot = h_remain * 0.66

    o_cap = CYLINDER(s, R=R_BODY * 0.88, H=28.0, O=0.0).translate((0.0, 0.0, z_cap - 6.0))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    # 支架双立柱与中心轴
    z_st0 = z_cap + 18.0
    o_shaft = CYLINDER(s, R=max(20.0, R_MOT * 0.22), H=h_stool + 20.0, O=0.0).translate((0.0, 0.0, z_st0 - 10.0))
    o_main.uniteWith(o_shaft)
    o_shaft.erase()

    for sy in (-1.0, 1.0):
        o_arm = CORNERBOX(s, L=R_MOT * 0.55, W=R_MOT * 0.35, H=h_stool + 10.0).translate(
            (-R_MOT * 0.275, sy * R_MOT * 0.65 - R_MOT * 0.175, z_st0 - 5.0)
        )
        o_main.uniteWith(o_arm)
        o_arm.erase()

    z_mfl = z_st0 + h_stool - 24.0
    o_mfl = CYLINDER(s, R=R_MOT * 1.05, H=26.0, O=0.0).translate((0.0, 0.0, z_mfl))
    o_main.uniteWith(o_mfl)
    o_mfl.erase()

    # 5. 顶置立式电机 + 风罩 + 侧接线盒
    z_m0 = z_mfl + 22.0
    mot_body_h = max(120.0, H_TOTAL - z_m0)
    o_mot = CYLINDER(s, R=R_MOT, H=mot_body_h, O=0.0).translate((0.0, 0.0, z_m0 - 2.0))
    o_tbox = CORNERBOX(s, L=R_MOT * 0.55, W=R_MOT * 0.62, H=mot_body_h * 0.32).translate(
        (R_MOT * 0.78, -R_MOT * 0.31, z_m0 + mot_body_h * 0.28)
    )
    o_main.uniteWith(o_mot)
    o_mot.erase()
    o_main.uniteWith(o_tbox)
    o_tbox.erase()

    # 6. 注册 2 个端口 (水平同轴进出口)
    s.setPoint((-half_l, 0.0, H_CL), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, H_CL), (1.0, 0.0, 0.0))

    # 7. 注册线性标注
    s.setLinearDimension('L_FF', (-half_l, 0.0, H_CL), (half_l, 0.0, H_CL))
    s.setLinearDimension('H_CL', (-half_l, 0.0, 0.0), (-half_l, 0.0, H_CL))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
