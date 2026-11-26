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

@activate(Group="Valve",
          TooltipShort=u"对夹双瓣止回阀 (API 594)",
          TooltipLong=u"对夹式双瓣蝶形止回阀，含紧凑厚圆环阀体、双侧突面密封台阶、双销轴定位螺塞与顶部吊耳",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="WAF")
@group("MainDimensions", TooltipLong=u"对夹双瓣止回阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"对夹阀体端面至端面厚度 L (mm)", Ask4Dist=True)
@param(D_BODY=LENGTH, TooltipShort=u"阀体外径", TooltipLong=u"对夹圆环阀体外径 (mm)")
def VALVE_CHECK_WAFER(
    s,
    D=168.3,
    L_FACE=76.0,
    D_BODY=218.0,
    ID=u"VALVE_CHECK_WAFER",
    **kw
):
    D = max(40.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_BODY = float(D_BODY)
    if D_BODY < 1.0:
        D_BODY = 1.0

    half_l = L_FACE / 2.0
    r_body = D_BODY / 2.0
    rf_t = 3.0

    # 1. 紧凑厚圆环阀体 + 两侧突面密封台阶 + 中心加强筋环
    o_main = CYLINDER(s, R=r_body, H=L_FACE - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(half_l - rf_t), 0.0, 0.0))
    o_rf = CYLINDER(s, R=r_body * 0.88, H=L_FACE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_main.uniteWith(o_rf)
    o_rf.erase()

    o_rib = CYLINDER(s, R=r_body * 1.03, H=max(12.0, L_FACE * 0.22), O=0.0).rotateY(90.0).translate((-max(6.0, L_FACE * 0.11), 0.0, 0.0))
    o_main.uniteWith(o_rib)
    o_rib.erase()

    # 2. 上下双销轴止动螺塞凸台 (双瓣止回阀标志性外观)
    pin_r = max(10.0, r_body * 0.11)
    for sx in (-1.0, 1.0):
        o_pin = CYLINDER(s, R=pin_r, H=r_body * 2.12, O=0.0).translate((sx * L_FACE * 0.18, 0.0, -r_body * 1.06))
        o_main.uniteWith(o_pin)
        o_pin.erase()

    # 3. 顶部起吊吊耳 (带加强座)
    lug_h = max(32.0, r_body * 0.34)
    lug_w = max(24.0, r_body * 0.24)
    o_lug = CORNERBOX(s, L=max(14.0, L_FACE * 0.24), W=lug_w, H=lug_h).translate((-max(7.0, L_FACE * 0.12), -lug_w / 2.0, r_body - 4.0))
    o_main.uniteWith(o_lug)
    o_lug.erase()
    o_eye = CYLINDER(s, R=lug_w * 0.52, H=max(14.0, L_FACE * 0.24), O=0.0).rotateY(90.0).translate((-max(7.0, L_FACE * 0.12), 0.0, r_body + lug_h - 4.0))
    o_main.uniteWith(o_eye)
    o_eye.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('D_BODY', (0.0, -r_body, 0.0), (0.0, r_body, 0.0))
