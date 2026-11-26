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
          TooltipShort=u"计量泵/隔膜泵总成",
          TooltipLong=u"机械/液压隔膜计量泵总成参数化模型，含底板、蜗轮蜗杆传动箱、冲程调节手轮、立式驱动电机、竖直隔膜泵头及上下进出口法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"计量泵/隔膜泵底板、传动箱、泵头与进出口主要尺寸参数")
@param(DN=LENGTH, TooltipShort=u"进出口通径", TooltipLong=u"上下进出口法兰公称通径 DN (mm)")
@param(L_BASE=LENGTH, TooltipShort=u"底板长度", TooltipLong=u"安装底板长度 L (mm)", Ask4Dist=True)
@param(W_BASE=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"安装底板宽度 W (mm)")
@param(H_HEAD_CL=LENGTH, TooltipShort=u"泵头中心高", TooltipLong=u"底板底面至隔膜泵头中心高度 (mm)")
@param(H_PORT_SPAN=LENGTH, TooltipShort=u"进出口法兰距", TooltipLong=u"上下进出口法兰面对面垂直间距 (mm)", Ask4Dist=True)
@param(H_MOTOR_TOP=LENGTH, TooltipShort=u"电机顶标高", TooltipLong=u"底板底面至立式电机顶部总高 (mm)", Ask4Dist=True)
def EQ_PUMP_METERING(
    s,
    DN=25.0,
    L_BASE=420.0,
    W_BASE=260.0,
    H_HEAD_CL=210.0,
    H_PORT_SPAN=320.0,
    H_MOTOR_TOP=540.0,
    ID=u"EQ_PUMP_METERING",
    **kw
):
    u"""计量泵/隔膜泵总成 (底板底面 Z=0，传动箱居中，隔膜泵头位于 +X 前端，上下进出口法兰垂直同轴)。"""
    DN = max(10.0, float(DN))
    L_BASE = float(L_BASE)
    if L_BASE < 1.0:
        L_BASE = 1.0
    W_BASE = max(180.0, float(W_BASE))
    H_HEAD_CL = max(150.0, float(H_HEAD_CL))
    H_PORT_SPAN = max(200.0, min(H_HEAD_CL * 1.85, float(H_PORT_SPAN)))
    H_MOTOR_TOP = float(H_MOTOR_TOP)
    if H_MOTOR_TOP < 1.0:
        H_MOTOR_TOP = 1.0

    r_p, r_f, t_f = _std_noz_dims(DN)

    base_t = 18.0
    # 1. 安装底板 (Z: 0 -> base_t)
    o_main = CORNERBOX(s, L=L_BASE, W=W_BASE, H=base_t).translate((-L_BASE * 0.5, -W_BASE * 0.5, 0.0))

    # 2. 传动箱体 (居中偏后)
    gb_l = L_BASE * 0.56
    gb_w = W_BASE * 0.68
    gb_h = H_HEAD_CL * 1.25 - base_t
    x_gb0 = -gb_l * 0.55
    o_gb = CORNERBOX(s, L=gb_l, W=gb_w, H=gb_h + 6.0).translate((x_gb0, -gb_w / 2.0, base_t - 4.0))
    o_main.uniteWith(o_gb)
    o_gb.erase()

    # 3. 后端冲程调节手轮 (-X 端)
    r_knob = max(32.0, gb_w * 0.24)
    o_kstem = CYLINDER(s, R=r_knob * 0.45, H=48.0, O=0.0).rotateY(-90.0).translate((x_gb0 + 8.0, 0.0, H_HEAD_CL))
    o_knob = CYLINDER(s, R=r_knob, H=28.0, O=0.0).rotateY(-90.0).translate((x_gb0 - 34.0, 0.0, H_HEAD_CL))
    o_main.uniteWith(o_kstem)
    o_kstem.erase()
    o_main.uniteWith(o_knob)
    o_knob.erase()

    # 4. 顶部立式驱动电机 (安装于传动箱上方)
    z_m0 = base_t + gb_h - 4.0
    r_mot = max(62.0, gb_w * 0.42)
    h_mot = max(140.0, H_MOTOR_TOP - z_m0)
    x_mot = x_gb0 + gb_l * 0.42
    o_mfl = CYLINDER(s, R=r_mot * 1.08, H=20.0, O=0.0).translate((x_mot, 0.0, z_m0))
    o_mot = CYLINDER(s, R=r_mot, H=h_mot, O=0.0).translate((x_mot, 0.0, z_m0 + 14.0))
    o_tbox = CORNERBOX(s, L=r_mot * 0.55, W=r_mot * 0.58, H=h_mot * 0.34).translate(
        (x_mot - r_mot * 0.275, r_mot * 0.78, z_m0 + h_mot * 0.30)
    )
    o_main.uniteWith(o_mfl)
    o_mfl.erase()
    o_main.uniteWith(o_mot)
    o_mot.erase()
    o_main.uniteWith(o_tbox)
    o_tbox.erase()

    # 5. 前端连接颈 + 竖直隔膜泵头 (+X 侧)
    x_gb1 = x_gb0 + gb_l
    neck_l = max(55.0, L_BASE * 0.16)
    r_neck = max(35.0, gb_w * 0.24)
    o_neck = CYLINDER(s, R=r_neck, H=neck_l + 15.0, O=0.0).rotateY(90.0).translate((x_gb1 - 10.0, 0.0, H_HEAD_CL))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    x_head = x_gb1 + neck_l + 28.0
    r_head = max(65.0, gb_w * 0.46)
    head_t = max(56.0, DN * 1.6 + 24.0)
    o_head = CYLINDER(s, R=r_head, H=head_t, O=0.0).rotateY(90.0).translate((x_head - head_t / 2.0, 0.0, H_HEAD_CL))
    o_main.uniteWith(o_head)
    o_head.erase()

    # 6. 上下单向阀体及上下进出口法兰 (沿 Z 轴，中心在 x_head, y=0)
    z_bot_face = max(base_t + 12.0, H_HEAD_CL - H_PORT_SPAN / 2.0)
    z_top_face = z_bot_face + H_PORT_SPAN

    o_vcol = CYLINDER(s, R=r_p * 1.25, H=H_PORT_SPAN - 2.0 * t_f + 4.0, O=0.0).translate((x_head, 0.0, z_bot_face + t_f - 2.0))
    o_f_bot = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((x_head, 0.0, z_bot_face))
    o_f_top = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((x_head, 0.0, z_top_face - t_f))
    o_main.uniteWith(o_vcol)
    o_vcol.erase()
    o_main.uniteWith(o_f_bot)
    o_f_bot.erase()
    o_main.uniteWith(o_f_top)
    o_f_top.erase()

    # 7. 注册 2 个端口 (下吸入口 -Z, 上排出口 +Z)
    s.setPoint((x_head, 0.0, z_bot_face), (0.0, 0.0, -1.0))
    s.setPoint((x_head, 0.0, z_top_face), (0.0, 0.0, 1.0))

    # 8. 注册线性标注
    s.setLinearDimension('L_BASE', (-L_BASE * 0.5, -W_BASE * 0.5, 0.0), (L_BASE * 0.5, -W_BASE * 0.5, 0.0))
    s.setLinearDimension('H_PORT_SPAN', (x_head, 0.0, z_bot_face), (x_head, 0.0, z_top_face))
    s.setLinearDimension('H_MOTOR_TOP', (x_mot, 0.0, 0.0), (x_mot, 0.0, H_MOTOR_TOP))
