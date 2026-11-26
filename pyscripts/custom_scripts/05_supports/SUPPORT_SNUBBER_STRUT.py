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
          TooltipShort=u"刚性拉撑杆/液压阻尼器 (SNUBBER)",
          TooltipLong=u"刚性拉撑杆/液压阻尼器，含重型管夹、两端球铰耳环与销轴、加粗液压阻尼缸筒、储油筒凸台与结构锚固座",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"液压阻尼器/拉撑杆主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被限位管道外径 D (mm)")
@param(L_PIN=LENGTH, TooltipShort=u"销距长度", TooltipLong=u"管道中心至结构锚固板背面的水平总距 L_PIN (mm)", Ask4Dist=True)
@param(D_BODY=LENGTH, TooltipShort=u"阻尼筒外径", TooltipLong=u"中间加粗液压阻尼缸筒外径 (mm)")
@param(D_ROD=LENGTH, TooltipShort=u"活塞杆径", TooltipLong=u"伸出活塞杆与调节杆外径 (mm)")
@param(CLAMP_W=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"管道侧重型抱箍宽度 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"锚固板厚", TooltipLong=u"结构端锚固底板厚度 (mm)")
def SUPPORT_SNUBBER_STRUT(
    s,
    D=168.3,
    L_PIN=480.0,
    D_BODY=86.0,
    D_ROD=36.0,
    CLAMP_W=50.0,
    T_PLT=14.0,
    ID=u"SUPPORT_SNUBBER_STRUT",
    **kw
):
    u"""刚性拉撑杆/液压阻尼器 (原点在管道中心线, 管道沿 X 轴, 阻尼杆沿 -Y 水平拉撑)。"""
    D = max(50.0, float(D))
    r_p = D / 2.0
    D_BODY = float(D_BODY)
    if D_BODY < 1.0:
        D_BODY = 1.0
    D_ROD = max(20.0, min(D_BODY * 0.55, float(D_ROD)))
    CLAMP_W = max(35.0, float(CLAMP_W))
    T_PLT = max(10.0, float(T_PLT))
    L_PIN = float(L_PIN)
    if L_PIN < 1.0:
        L_PIN = 1.0

    clamp_t = max(10.0, CLAMP_W * 0.22)
    r_out = r_p + clamp_t
    ear_gap = max(10.0, clamp_t * 1.1)

    # 1. 管道侧重型双耳管夹（沿 Y 方向分瓣，-Y 侧延伸为重型连接耳）
    o_main = CYLINDER(s, R=r_out, H=CLAMP_W, O=r_p).rotateY(90.0).translate((-CLAMP_W / 2.0, 0.0, 0.0))
    o_slot = CORNERBOX(s, L=CLAMP_W + 8.0, W=r_out * 2.6, H=ear_gap).translate(
        (-(CLAMP_W / 2.0 + 4.0), -r_out * 1.3, -ear_gap / 2.0))
    o_main.subtractFrom(o_slot)
    o_slot.erase()

    ear_pos_l = max(32.0, clamp_t * 3.0)
    ear_neg_l = max(62.0, D_ROD * 1.7)
    for sz in (-1.0, 1.0):
        ez = (ear_gap / 2.0) if sz > 0 else -(ear_gap / 2.0 + clamp_t)
        o_ep = CORNERBOX(s, L=CLAMP_W, W=ear_pos_l, H=clamp_t).translate((-CLAMP_W / 2.0, r_p, ez))
        o_main.uniteWith(o_ep)
        o_ep.erase()
        o_en = CORNERBOX(s, L=CLAMP_W, W=ear_neg_l, H=clamp_t).translate((-CLAMP_W / 2.0, -(r_p + ear_neg_l), ez))
        o_main.uniteWith(o_en)
        o_en.erase()

    # 管夹紧固螺栓 + 管端球铰销轴
    pin_r = max(10.0, D_ROD * 0.34)
    bh = ear_gap + clamp_t * 2.0 + pin_r * 2.2
    y_pin1 = -(r_out + ear_neg_l * 0.68)
    for by in (r_out + ear_pos_l * 0.45, -(r_out + ear_neg_l * 0.25), y_pin1):
        o_b = CYLINDER(s, R=pin_r, H=bh, O=0.0).translate((0.0, by, -bh / 2.0))
        o_main.uniteWith(o_b)
        o_b.erase()

    # 2. 两端球铰耳环（管端 y_pin1 与 结构端 y_pin2）+ 中间活塞杆
    y_wall = -L_PIN
    y_pin2 = y_wall + T_PLT + max(42.0, D_ROD * 1.2)
    eye_r = max(24.0, D_ROD * 0.78)
    eye_h = max(ear_gap + 2.0, D_ROD * 0.72)

    for yp in (y_pin1, y_pin2):
        # 球铰外圈圆柱 + 内嵌球体特征
        o_eye = CYLINDER(s, R=eye_r, H=eye_h, O=0.0).translate((0.0, yp, -eye_h / 2.0))
        o_main.uniteWith(o_eye)
        o_eye.erase()
        o_ball = SPHERE(s, R=eye_r * 0.78).translate((0.0, yp, 0.0))
        o_main.uniteWith(o_ball)
        o_ball.erase()

    # 贯通活塞杆（连接两端球铰耳环）
    rod_span = y_pin1 - y_pin2
    o_rod = CYLINDER(s, R=D_ROD * 0.5, H=rod_span, O=0.0).rotateX(-90.0).translate((0.0, y_pin2, 0.0))
    o_main.uniteWith(o_rod)
    o_rod.erase()

    # 3. 中间加粗液压阻尼缸筒（含两端压盖法兰与顶部小型储油筒）
    y_body_mid = (y_pin1 + y_pin2) * 0.50
    body_l = max(120.0, rod_span * 0.52)
    r_body = D_BODY / 2.0
    o_body = CYLINDER(s, R=r_body, H=body_l, O=0.0).rotateX(-90.0).translate((0.0, y_body_mid - body_l / 2.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    # 缸筒两端压盖台阶环
    gland_l = max(14.0, body_l * 0.11)
    for sy in (-1.0, 1.0):
        gy = (y_body_mid + body_l / 2.0 - gland_l) if sy > 0 else (y_body_mid - body_l / 2.0)
        o_gl = CYLINDER(s, R=r_body + 6.0, H=gland_l, O=0.0).rotateX(-90.0).translate((0.0, gy, 0.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    # 液压阻尼器外置小储油筒（偏置于上方，强化阻尼器工业辨识度）
    acc_r = r_body * 0.36
    acc_l = body_l * 0.52
    o_acc = CYLINDER(s, R=acc_r, H=acc_l, O=0.0).rotateX(-90.0).translate(
        (0.0, y_body_mid - acc_l / 2.0, r_body + acc_r * 0.55))
    o_main.uniteWith(o_acc)
    o_acc.erase()
    o_neck = CORNERBOX(s, L=acc_r * 1.2, W=acc_l * 0.6, H=acc_r * 1.2).translate(
        (-acc_r * 0.6, y_body_mid - acc_l * 0.3, r_body * 0.7))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    # 4. 结构端双耳锚固座 + 干净矩形底板
    plt_w = max(140.0, D_BODY * 1.7)
    o_plt = CORNERBOX(s, L=plt_w, W=T_PLT, H=plt_w).translate((-plt_w / 2.0, y_wall, -plt_w / 2.0))
    o_main.uniteWith(o_plt)
    o_plt.erase()

    clev_len = (y_pin2 - (y_wall + T_PLT)) + eye_r * 0.85
    clev_x = max(56.0, eye_r * 2.1)
    for sz in (-1.0, 1.0):
        cz = (eye_h / 2.0) if sz > 0 else -(eye_h / 2.0 + clamp_t)
        o_cl = CORNERBOX(s, L=clev_x, W=clev_len + 2.0, H=clamp_t).translate(
            (-clev_x / 2.0, y_wall + T_PLT - 2.0, cz))
        o_main.uniteWith(o_cl)
        o_cl.erase()

    o_pin2 = CYLINDER(s, R=pin_r, H=eye_h + clamp_t * 2.0 + 18.0, O=0.0).translate(
        (0.0, y_pin2, -(eye_h + clamp_t * 2.0 + 18.0) / 2.0))
    o_main.uniteWith(o_pin2)
    o_pin2.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_PIN', (0.0, 0.0, 0.0), (0.0, y_wall, 0.0))
    s.setLinearDimension('D_BODY', (0.0, y_body_mid, -r_body), (0.0, y_body_mid, r_body))
