# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"三角斜撑悬臂托架",
    TooltipLong=u"化工框架柱或墙面生根三角斜撑重型悬臂管道托架 (D4 型，符合 HG/T 21629，含竖直立柱贴板、水平型钢挑梁、45° 斜撑杆与管道鞍式卡座)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承管道公称外径 (mm)")
@param(SPAN=LENGTH, TooltipShort=u"挑出跨距", TooltipLong=u"管道中心至墙面/钢柱生根安装面的水平距离 (mm)")
@param(H_DROP=LENGTH, TooltipShort=u"托架高度", TooltipLong=u"水平挑梁顶面至斜撑下端安装板底部的高度 (mm)")
@param(W_BEAM=LENGTH, TooltipShort=u"型钢宽度", TooltipLong=u"悬臂槽钢/H型钢截面宽度 (mm)")
@param(H_BEAM=LENGTH, TooltipShort=u"型钢高度", TooltipLong=u"悬臂槽钢/H型钢截面高度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"托架编号", TooltipLong=u"三角斜撑悬臂托架型号规格编码")
def SUPPORT_CANTILEVER_BRACKET(s, D=168.3, SPAN=350.0, H_DROP=420.0, W_BEAM=100.0, H_BEAM=100.0, ID=u"D4-DN150", **kw):
    D = max(25.0, float(D))
    r_pipe = D / 2.0
    SPAN = max(D * 0.8 + 120.0, float(SPAN))
    H_DROP = max(260.0, float(H_DROP))
    W_BEAM = max(65.0, float(W_BEAM))
    H_BEAM = max(65.0, float(H_BEAM))

    h_shoe = 55.0
    z_beam_top = -(r_pipe + h_shoe)
    l_arm = SPAN + r_pipe + 65.0
    y_wall = -SPAN

    # 1. 管道底部弧形鞍座与固定管卡垫块 (H=dx=W_BEAM, L=dy, W=dz)
    o_m = CYLINDER(s, R=r_pipe + 10.0, H=W_BEAM, O=0.0).rotateY(90.0).translate((-W_BEAM * 0.5, 0.0, 0.0))
    o_trim = BOX(s, L=(r_pipe + 15.0) * 2.2, W=r_pipe * 1.5, H=W_BEAM + 10.0).translate((0.0, 0.0, r_pipe * 0.45))
    o_m.subtractFrom(o_trim); o_trim.erase()

    h_sweb = h_shoe + r_pipe * 0.45
    o_shoe_web = BOX(s, L=14.0, W=h_sweb, H=W_BEAM * 0.9).translate((0.0, 0.0, z_beam_top + h_sweb * 0.5))
    o_shoe_base = BOX(s, L=D * 0.72, W=14.0, H=W_BEAM).translate((0.0, 0.0, z_beam_top + 5.0))
    o_m.uniteWith(o_shoe_web); o_shoe_web.erase()
    o_m.uniteWith(o_shoe_base); o_shoe_base.erase()

    # 2. 水平悬臂主挑梁 (H型钢上下翼缘 + 腹板，从 Y=-SPAN 延伸至 Y=+r_pipe+65)
    t_fl = max(10.0, H_BEAM * 0.14)
    y_arm_mid = y_wall + l_arm * 0.5
    o_fl_top = BOX(s, L=l_arm, W=t_fl, H=W_BEAM).translate((0.0, y_arm_mid, z_beam_top - t_fl * 0.5))
    o_fl_bot = BOX(s, L=l_arm, W=t_fl, H=W_BEAM).translate((0.0, y_arm_mid, z_beam_top - H_BEAM + t_fl * 0.5))
    o_arm_web = BOX(s, L=l_arm, W=H_BEAM, H=12.0).translate((0.0, y_arm_mid, z_beam_top - H_BEAM * 0.5))
    for p in (o_fl_top, o_fl_bot, o_arm_web):
        o_m.uniteWith(p); p.erase()

    # 3. 墙面/钢柱竖直生根背板 (位于 Y = -SPAN)
    t_wall = 16.0
    h_wall = H_DROP + 50.0
    o_wall = BOX(s, L=t_wall, W=h_wall, H=W_BEAM * 1.45).translate((0.0, y_wall + t_wall * 0.5, z_beam_top - H_DROP * 0.5 + 10.0))
    o_m.uniteWith(o_wall); o_wall.erase()

    # 4. 45° 斜撑杆 (连接墙面背板下部与水平挑梁前端底部)
    y_br0 = y_wall + t_wall * 0.5
    z_br0 = z_beam_top - H_DROP + 35.0
    y_br1 = r_pipe * 0.45
    z_br1 = z_beam_top - H_BEAM + t_fl * 0.5
    dy_br = y_br1 - y_br0
    dz_br = z_br1 - z_br0
    len_br = math.sqrt(dy_br * dy_br + dz_br * dz_br) + 30.0
    ang_deg = math.degrees(math.atan2(dy_br, dz_br))
    o_brace = BOX(s, L=H_BEAM * 0.65, W=len_br, H=W_BEAM * 0.68).rotateX(-ang_deg).translate((0.0, (y_br0 + y_br1) * 0.5, (z_br0 + z_br1) * 0.5))
    o_gusset = BOX(s, L=120.0, W=120.0, H=14.0).translate((0.0, y_wall + 60.0, z_beam_top - H_BEAM - 45.0))
    o_m.uniteWith(o_brace); o_brace.erase()
    o_m.uniteWith(o_gusset); o_gusset.erase()

    # 切除管道流道外圆
    o_cut = CYLINDER(s, R=r_pipe, H=W_BEAM + 30.0, O=0.0).rotateY(90.0).translate((-(W_BEAM * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("SPAN", (0.0, y_wall, 0.0), (0.0, 0.0, 0.0))
    s.setLinearDimension("H_DROP", (0.0, y_wall, z_beam_top - H_DROP), (0.0, y_wall, z_beam_top))
