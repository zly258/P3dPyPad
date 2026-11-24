# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="4",
    TooltipShort=u"可拆式板式换热器",
    TooltipLong=u"化工紧凑型可拆式板式换热器 (PHE，符合 NB/T 47004 / ISO 15547，含前固定压紧板与四法兰接管口、人字波纹换热板片束、后活动压紧板、上下导杆横梁、后支柱与两侧夹紧长螺柱)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_FRAME=LENGTH, TooltipShort=u"框架总长", TooltipLong=u"前固定压紧板至后立柱的框架总长 (mm)")
@param(W_PLATE=LENGTH, TooltipShort=u"压紧板宽", TooltipLong=u"固定与活动压紧板的横向宽度 (mm)")
@param(H_FRAME=LENGTH, TooltipShort=u"设备总高", TooltipLong=u"地脚底板至上导梁顶面的总高度 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"接管外径", TooltipLong=u"冷热侧四接管公称外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"接管法兰径", TooltipLong=u"四接管法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"可拆式板式换热器位号与换热面积编码")
def EQUIPMENT_PLATE_HEAT_EXCHANGER(s, L_FRAME=1450.0, W_PLATE=620.0, H_FRAME=1550.0, D_NOZ=114.3, FL_OD=220.0, ID=u"E-103-PHE-80m2", **kw):
    L_FRAME = max(750.0, float(L_FRAME))
    W_PLATE = max(360.0, float(W_PLATE))
    H_FRAME = max(850.0, float(H_FRAME))
    D_NOZ = max(48.0, float(D_NOZ))
    FL_OD = max(D_NOZ + 65.0, float(FL_OD))

    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_fl = 22.0
    t_pl = 58.0
    h_foot = 90.0
    h_pl = H_FRAME - h_foot - 50.0

    x_front = -L_FRAME * 0.5
    x_pack_end = x_front + L_FRAME * 0.58
    x_rear = L_FRAME * 0.5 - 65.0

    # 1. 前固定压紧板 (Fixed Frame Plate) + 前地脚支座 (BOX: H=dx, L=dy, W=dz)
    z_pl_c = h_foot + h_pl * 0.5
    o_m = BOX(s, L=W_PLATE, W=h_pl, H=t_pl).translate((x_front + t_pl * 0.5, 0.0, z_pl_c))
    o_foot_f = BOX(s, L=W_PLATE * 1.18, W=h_foot, H=160.0).translate((x_front + t_pl * 0.5, 0.0, h_foot * 0.5))
    o_m.uniteWith(o_foot_f); o_foot_f.erase()

    # 2. 中部波纹板片束 (Corrugated Plate Pack) + 后活动压紧板 (Follower Plate)
    l_pack = x_pack_end - (x_front + t_pl)
    o_pack = BOX(s, L=W_PLATE * 0.88, W=h_pl * 0.86, H=l_pack).translate((x_front + t_pl + l_pack * 0.5, 0.0, z_pl_c))
    o_move = BOX(s, L=W_PLATE, W=h_pl * 0.94, H=t_pl * 0.9).translate((x_pack_end + t_pl * 0.45, 0.0, z_pl_c))
    o_m.uniteWith(o_pack); o_pack.erase()
    o_m.uniteWith(o_move); o_move.erase()

    # 3. 顶部承载工字横梁 + 下部导向横杆 + 后端支承立柱与后地脚
    o_top_bar = BOX(s, L=110.0, W=95.0, H=L_FRAME - 20.0).translate((0.0, 0.0, H_FRAME - 47.5))
    o_bot_bar = CYLINDER(s, R=26.0, H=L_FRAME - 20.0, O=0.0).rotateY(90.0).translate((-(L_FRAME * 0.5 - 10.0), 0.0, h_foot + 45.0))
    o_rear_col = BOX(s, L=160.0, W=H_FRAME - h_foot, H=110.0).translate((x_rear, 0.0, h_foot + (H_FRAME - h_foot) * 0.5))
    o_foot_r = BOX(s, L=W_PLATE * 0.92, W=h_foot, H=180.0).translate((x_rear, 0.0, h_foot * 0.5))
    for p in (o_top_bar, o_bot_bar, o_rear_col, o_foot_r):
        o_m.uniteWith(p); p.erase()

    # 两侧 6 根夹紧长螺柱 (Tie Rods)
    l_tie = (x_pack_end + t_pl + 90.0) - (x_front - 30.0)
    for sy in (-1.0, 1.0):
        for zf in (0.24, 0.52, 0.80):
            zt = h_foot + h_pl * zf
            tr = CYLINDER(s, R=15.0, H=l_tie, O=0.0).rotateY(90.0).translate((x_front - 30.0, sy * (W_PLATE * 0.5 + 18.0), zt))
            o_m.uniteWith(tr); tr.erase()

    # 4. 前固定压紧板四角工艺法兰接管 (全部朝向 -X, X = x_noz_end)
    x_noz_end = x_front - 150.0
    dy_noz = W_PLATE * 0.28
    z_upper = h_foot + h_pl * 0.78
    z_lower = h_foot + h_pl * 0.22
    pts = [
        (-dy_noz, z_upper),
        (-dy_noz, z_lower),
        (dy_noz, z_upper),
        (dy_noz, z_lower),
    ]
    for yn, zn in pts:
        nz = CYLINDER(s, R=r_noz, H=160.0, O=0.0).rotateY(-90.0).translate((x_front + 10.0, yn, zn))
        fl = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((x_noz_end + t_fl, yn, zn))
        o_m.uniteWith(nz); nz.erase()
        o_m.uniteWith(fl); fl.erase()
        s.setPoint((x_noz_end, yn, zn), (-1.0, 0.0, 0.0))

    s.setLinearDimension("L_FRAME", (-L_FRAME / 2.0, 0.0, 0.0), (L_FRAME / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_PLATE", (x_front, -W_PLATE / 2.0, 0.0), (x_front, W_PLATE / 2.0, 0.0))
    s.setLinearDimension("H_FRAME", (x_front, 0.0, 0.0), (x_front, 0.0, H_FRAME))
