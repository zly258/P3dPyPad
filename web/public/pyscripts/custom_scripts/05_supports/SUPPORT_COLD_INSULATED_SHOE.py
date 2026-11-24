# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"深冷PIR高密度保冷管托",
    TooltipLong=u"化工液化烃/乙烯/LNG低温管线高密度聚异氰脲酸酯(PIR/HDPU)隔冷管托 (符合 HG/T 21629，含全圆保冷瓦块、防潮密封止水环、上下对夹外护钢箍、螺栓耳座与底座滑板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"低温管道公称外径 (mm)")
@param(T_INS=LENGTH, TooltipShort=u"保冷层厚度", TooltipLong=u"高密度PIR/HDPU保冷瓦块径向厚度 (mm)")
@param(H=LENGTH, TooltipShort=u"管托中心高", TooltipLong=u"管道中心至管托底板底面的安装高度 (mm)")
@param(L=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"保冷管托轴向总长度 (mm)")
@param(W=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"下部滑动钢底板宽度 (mm)")
@param(T_SHOE=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"外护箍板与底座钢板壁厚 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管托编号", TooltipLong=u"深冷保冷管托型号规格编码")
def SUPPORT_COLD_INSULATED_SHOE(s, D=168.3, T_INS=80.0, H=230.0, L=320.0, W=220.0, T_SHOE=12.0, ID=u"L1-DN150-80", **kw):
    D = max(25.0, float(D))
    T_INS = max(40.0, float(T_INS))
    r_pipe = D / 2.0
    r_ins = r_pipe + T_INS
    T_SHOE = max(8.0, float(T_SHOE))
    r_clamp = r_ins + T_SHOE * 0.75
    H = max(r_clamp + 45.0, float(H))
    L = max(200.0, float(L))
    W = max(D + T_INS * 1.2, float(W))

    z_bot = -H

    # 1. 高密度 PIR 保冷瓦块主体 + 两端防潮密封止水凸环
    o_m = CYLINDER(s, R=r_ins, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    for sx in (-1.0, 1.0):
        vb = CYLINDER(s, R=r_ins + 4.0, H=16.0, O=0.0).rotateY(90.0).translate((sx * (L * 0.5 - 12.0) - 8.0, 0.0, 0.0))
        o_m.uniteWith(vb); vb.erase()

    # 2. 外层上下对夹护壳钢箍 + 两侧水平紧固螺栓耳板 (BOX: H=dx=l_shell, L=dy, W=dz)
    l_shell = L * 0.78
    o_shell = CYLINDER(s, R=r_clamp, H=l_shell, O=0.0).rotateY(90.0).translate((-l_shell * 0.5, 0.0, 0.0))
    o_ears = BOX(s, L=r_clamp * 2.38, W=T_SHOE * 3.0, H=l_shell).translate((0.0, 0.0, 0.0))
    o_m.uniteWith(o_shell); o_shell.erase()
    o_m.uniteWith(o_ears); o_ears.erase()

    # 耳板紧固螺柱
    for sx in (-0.32, 0.0, 0.32):
        for sy in (-1.0, 1.0):
            bt = CYLINDER(s, R=7.0, H=T_SHOE * 4.8, O=0.0).translate((sx * l_shell, sy * r_clamp * 1.08, -T_SHOE * 2.4))
            o_m.uniteWith(bt); bt.erase()

    # 3. 下部断冷桥 T 型钢底座与防滑腹板
    h_web = H - r_ins * 0.78
    z_web_c = z_bot + T_SHOE + h_web * 0.5
    o_web = BOX(s, L=T_SHOE, W=h_web, H=l_shell).translate((0.0, 0.0, z_web_c))
    o_base = BOX(s, L=W, W=T_SHOE, H=l_shell).translate((0.0, 0.0, z_bot + T_SHOE * 0.5))
    o_m.uniteWith(o_web); o_web.erase()
    o_m.uniteWith(o_base); o_base.erase()

    for sx in (-0.34, 0.34):
        rib = BOX(s, L=W * 0.86, W=h_web * 0.9, H=T_SHOE).translate((sx * l_shell, 0.0, z_bot + T_SHOE + h_web * 0.45))
        o_m.uniteWith(rib); rib.erase()

    # 4. 切除中心低温管道通孔
    o_cut = CYLINDER(s, R=r_pipe, H=L + 30.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, z_bot), (L / 2.0, 0.0, z_bot))
    s.setLinearDimension("W", (0.0, -W / 2.0, z_bot), (0.0, W / 2.0, z_bot))
