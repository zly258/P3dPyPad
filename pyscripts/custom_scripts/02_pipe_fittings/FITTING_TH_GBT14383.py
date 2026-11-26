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

@activate(Group="Coupling",
          TooltipShort=u"锻钢内螺纹管箍 Coupling (GB/T 14383)",
          TooltipLong=u"GB/T 14383-2021 锻钢全管箍内螺纹接头 (Class 3000)，含加厚锻钢筒体、两端倒角与阶梯内孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="THD")
@group("MainDimensions", TooltipLong=u"锻钢内螺纹管箍主要几何参数")
@param(D_OUT=LENGTH, TooltipShort=u"管箍外径", TooltipLong=u"管箍锻钢主体外径 D_OUT (mm)")
@param(D_TH=LENGTH, TooltipShort=u"螺纹孔径", TooltipLong=u"内螺纹公称孔径 D_TH (mm)")
@param(D_IN=LENGTH, TooltipShort=u"通流内径", TooltipLong=u"中心通流内径 D_IN (mm)")
@param(L_LEN=LENGTH, TooltipShort=u"管箍总长", TooltipLong=u"管箍端面至端面总长度 L (mm)", Ask4Dist=True)
@param(J_TH=LENGTH, TooltipShort=u"螺纹深度", TooltipLong=u"单端内螺纹旋合深度 J_TH (mm)")
def FITTING_TH_GBT14383(
    s,
    D_OUT=44.5,
    D_TH=33.4,
    D_IN=26.6,
    L_LEN=51.0,
    J_TH=17.5,
    ID=u"FITTING_TH_GBT14383",
    **kw
):
    u"""锻钢内螺纹全管箍 (沿 X 轴 [-L/2, +L/2])。"""
    D_OUT = max(20.0, float(D_OUT))
    D_TH = max(12.0, min(D_OUT - 4.0, float(D_TH)))
    D_IN = max(8.0, min(D_TH - 1.5, float(D_IN)))
    L_LEN = float(L_LEN)
    if L_LEN < 1.0:
        L_LEN = 1.0
    J_TH = max(6.0, min(L_LEN * 0.45, float(J_TH)))

    r_out = D_OUT / 2.0
    r_ch = max(D_TH / 2.0 + 1.5, r_out - 2.0)
    r_th = D_TH / 2.0
    r_in = D_IN / 2.0
    ch = min(2.5, L_LEN * 0.06)
    half_l = L_LEN / 2.0

    # 主体圆柱 + 两端倒角过渡
    o_body = CYLINDER(s, R=r_out, H=L_LEN - 2.0 * ch, O=0.0).rotateY(90.0).translate((-(half_l - ch), 0.0, 0.0))
    o_c1 = CONE(s, R1=r_ch, R2=r_out, H=ch, E=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_c2 = CONE(s, R1=r_out, R2=r_ch, H=ch, E=0.0).rotateY(90.0).translate((half_l - ch, 0.0, 0.0))
    o_body.uniteWith(o_c1)
    o_c1.erase()
    o_body.uniteWith(o_c2)
    o_c2.erase()

    # 内部通流孔 + 两端螺纹台阶孔（不画细微螺纹牙型）
    o_cut = CYLINDER(s, R=r_in, H=L_LEN + 4.0, O=0.0).rotateY(90.0).translate((-half_l - 2.0, 0.0, 0.0))
    o_th1 = CYLINDER(s, R=r_th, H=J_TH + 2.0, O=0.0).rotateY(90.0).translate((-half_l - 2.0, 0.0, 0.0))
    o_th2 = CYLINDER(s, R=r_th, H=J_TH + 2.0, O=0.0).rotateY(90.0).translate((half_l - J_TH, 0.0, 0.0))
    o_cut.uniteWith(o_th1)
    o_th1.erase()
    o_cut.uniteWith(o_th2)
    o_th2.erase()

    o_body.subtractFrom(o_cut)
    o_cut.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_LEN', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
