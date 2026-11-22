# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"管道法兰式静态混合器",
    TooltipLong=u"化工酸碱中和/药剂在线混合用 SK/Kenics 型法兰式静态混合器 (符合 HG/T 20570，含加厚混合管体、两端高颈对焊法兰、外部强化箍环、药剂加注副法兰口与内部正反交替螺旋混合叶片)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"混合管外径", TooltipLong=u"静态混合器主管公称外径 (mm)")
@param(L=LENGTH, TooltipShort=u"混合器总长", TooltipLong=u"两端连接法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"主法兰外径", TooltipLong=u"主管两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"主管连接法兰厚度 (mm)")
@param(D_INJ=LENGTH, TooltipShort=u"加药口管径", TooltipLong=u"侧向药剂注入接管外径 (mm)")
@param(H_INJ=LENGTH, TooltipShort=u"加药口高度", TooltipLong=u"药剂注入法兰面至主管中心的距离 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"管道静态混合器位号与型号编码")
def EQUIPMENT_STATIC_MIXER(s, D=168.3, L=900.0, FL_OD=285.0, FL_T=26.0, D_INJ=60.3, H_INJ=210.0, ID=u"MX-101-DN150", **kw):
    D = max(48.0, float(D))
    L = max(350.0, float(L))
    FL_OD = max(D + 75.0, float(FL_OD))
    FL_T = max(16.0, float(FL_T))
    D_INJ = max(25.0, float(D_INJ))
    r_pipe = D / 2.0
    r_fl = FL_OD / 2.0
    H_INJ = max(r_fl + 45.0, float(H_INJ))

    r_bore = r_pipe * 0.86
    r_inj = D_INJ / 2.0
    r_fl_inj = r_inj + 42.0

    # 1. 静态混合器主筒体 + 两端高颈法兰 + 3 道外部混合单元分节标识抱箍环
    o_m = CYLINDER(s, R=r_pipe * 1.05, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    for sx in (-0.28, 0.0, 0.28):
        rg = CYLINDER(s, R=r_pipe * 1.18, H=24.0, O=0.0).rotateY(90.0).translate((sx * L - 12.0, 0.0, 0.0))
        o_m.uniteWith(rg); rg.erase()

    # 顶部铭牌支架与吊耳
    o_lug = BOX(s, L=16.0, W=65.0, H=85.0).translate((0.0, 0.0, r_pipe * 1.15 + 25.0))
    o_m.uniteWith(o_lug); o_lug.erase()

    # 2. 上游药剂加注副法兰接管 (Port 3 at X = -L*0.32, Z = +H_INJ)
    x_inj = -L * 0.32
    n_inj = CYLINDER(s, R=r_inj, H=H_INJ, O=0.0).translate((x_inj, 0.0, 0.0))
    f_inj = CYLINDER(s, R=r_fl_inj, H=18.0, O=0.0).translate((x_inj, 0.0, H_INJ - 18.0))
    o_m.uniteWith(n_inj); n_inj.erase()
    o_m.uniteWith(f_inj); f_inj.erase()

    # 3. 切除主管流道并置入 4 组正交交错螺旋导流混合叶片
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    l_elem = (L - 2.0 * FL_T) * 0.18
    for idx, sx in enumerate((-0.34, -0.11, 0.11, 0.34)):
        ang_x = 45.0 + 90.0 * (idx % 2)
        el = BOX(s, L=r_bore * 1.92, W=8.0, H=l_elem).rotateX(ang_x).translate((sx * L, 0.0, 0.0))
        o_m.uniteWith(el); el.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((x_inj, 0.0, H_INJ), (0.0, 0.0, 1.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("FL_OD", (-L / 2.0, -r_fl, 0.0), (-L / 2.0, r_fl, 0.0))
    s.setLinearDimension("H_INJ", (x_inj, 0.0, 0.0), (x_inj, 0.0, H_INJ))
