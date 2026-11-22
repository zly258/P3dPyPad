# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"平卧式恒力弹簧支吊架",
    TooltipLong=u"化工高温蒸汽与临氢管线平卧式恒力弹簧支吊架 (符合 JB/T 8130.1 / HG/T 21629，含双耳管夹、松紧螺套吊杆、曲柄摇臂机构、卧式弹簧筒体与载荷位移刻度牌)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"吊点总高", TooltipLong=u"管道中心至顶部生根梁安装底面的总高度 (mm)")
@param(L_BOX=LENGTH, TooltipShort=u"恒力箱体长", TooltipLong=u"卧式恒力弹簧主筒体与框架总长度 (mm)")
@param(D_BOX=LENGTH, TooltipShort=u"弹簧筒外径", TooltipLong=u"恒力主弹簧圆筒外径 (mm)")
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"下部螺纹吊杆与花兰螺丝公称外径 (mm)")
@param(W_CLAMP=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"重型双螺栓管夹轴向宽度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支吊架编号", TooltipLong=u"恒力弹簧支吊架型号规格编码")
def SUPPORT_CONSTANT_SPRING(s, D=219.1, H=750.0, L_BOX=360.0, D_BOX=210.0, ROD_D=24.0, W_CLAMP=65.0, ID=u"PH1-DN200", **kw):
    D = max(32.0, float(D))
    H = max(D * 1.4 + 280.0, float(H))
    L_BOX = max(220.0, float(L_BOX))
    D_BOX = max(130.0, float(D_BOX))
    ROD_D = max(12.0, float(ROD_D))
    W_CLAMP = max(36.0, float(W_CLAMP))

    r_pipe = D / 2.0
    t_cl = max(10.0, D * 0.055)
    r_cl = r_pipe + t_cl
    r_rod = ROD_D / 2.0

    # 1. 下部重型双耳管夹 (包围管道外圆，X 向宽度 W_CLAMP)
    o_m = CYLINDER(s, R=r_cl, H=W_CLAMP, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.5, 0.0, 0.0))
    ear_w = r_cl * 2.45
    o_ear_low = BOX(s, L=ear_w, W=t_cl * 2.4, H=W_CLAMP).translate((0.0, 0.0, 0.0))
    o_m.uniteWith(o_ear_low); o_ear_low.erase()

    z_pin = r_cl + ROD_D * 1.6
    o_ear_top = BOX(s, L=ROD_D * 2.4, W=z_pin, H=W_CLAMP * 0.72).translate((0.0, 0.0, z_pin * 0.5))
    o_pin = CYLINDER(s, R=r_rod * 0.95, H=W_CLAMP * 1.05, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.525, 0.0, z_pin))
    o_m.uniteWith(o_ear_top); o_ear_top.erase()
    o_m.uniteWith(o_pin); o_pin.erase()

    # 2. 竖直吊杆 + 中部花兰松紧调节螺套 (Turnbuckle)
    z_frame_bot = H - D_BOX * 1.15
    h_rod = max(60.0, z_frame_bot - z_pin + 35.0)
    o_rod = CYLINDER(s, R=r_rod, H=h_rod, O=0.0).translate((0.0, 0.0, z_pin - 5.0))
    o_tb = CYLINDER(s, R=r_rod * 1.75, H=min(110.0, h_rod * 0.45), O=0.0).translate((0.0, 0.0, z_pin + h_rod * 0.28))
    o_m.uniteWith(o_rod); o_rod.erase()
    o_m.uniteWith(o_tb); o_tb.erase()

    # 3. 上部恒力弹簧主框架 + 枢轴摇臂箱 + 卧式弹簧筒体
    z_mid = H - D_BOX * 0.58
    w_frame = max(110.0, D_BOX * 0.65)
    h_frame = D_BOX * 1.05
    l_cam = L_BOX * 0.38
    # 摇臂箱覆盖 Y=0 吊杆轴线 (Y: [-l_cam*0.35, +l_cam*0.65], Z: [z_mid - h_frame*0.5, z_mid + h_frame*0.5])
    o_cam = BOX(s, L=l_cam, W=h_frame, H=w_frame).translate((0.0, l_cam * 0.15, z_mid))
    o_m.uniteWith(o_cam); o_cam.erase()

    # 枢轴横销与位移指示刻度牌凸台
    o_piv = CYLINDER(s, R=ROD_D * 0.85, H=w_frame + 24.0, O=0.0).rotateY(90.0).translate((-(w_frame * 0.5 + 12.0), 0.0, z_mid))
    o_scale = BOX(s, L=l_cam * 0.72, W=h_frame * 0.52, H=12.0).translate((w_frame * 0.52, l_cam * 0.15, z_mid))
    o_m.uniteWith(o_piv); o_piv.erase()
    o_m.uniteWith(o_scale); o_scale.erase()

    # 右侧平卧式主弹簧圆筒 (沿 +Y 延伸)
    l_cyl = L_BOX * 0.68
    y_cyl_start = l_cam * 0.35
    o_cyl = CYLINDER(s, R=D_BOX * 0.5, H=l_cyl, O=0.0).rotateX(-90.0).translate((0.0, y_cyl_start, z_mid))
    o_cap = CYLINDER(s, R=D_BOX * 0.54, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, y_cyl_start + l_cyl - 8.0, z_mid))
    o_adj = CYLINDER(s, R=ROD_D * 0.9, H=42.0, O=0.0).rotateX(-90.0).translate((0.0, y_cyl_start + l_cyl - 2.0, z_mid))
    for p in (o_cyl, o_cap, o_adj):
        o_m.uniteWith(p); p.erase()

    # 4. 顶部钢结构梁生根连接双吊耳与顶板 (Z = H)
    t_top = max(14.0, ROD_D * 0.65)
    h_lug = H - z_mid
    y_top_c = L_BOX * 0.32
    o_top_pl = BOX(s, L=L_BOX * 0.85, W=t_top, H=w_frame * 1.25).translate((0.0, y_top_c, H - t_top * 0.5))
    o_web_l = BOX(s, L=L_BOX * 0.75, W=h_lug, H=14.0).translate((-w_frame * 0.38, y_top_c, z_mid + h_lug * 0.5))
    o_web_r = BOX(s, L=L_BOX * 0.75, W=h_lug, H=14.0).translate((w_frame * 0.38, y_top_c, z_mid + h_lug * 0.5))
    for p in (o_top_pl, o_web_l, o_web_r):
        o_m.uniteWith(p); p.erase()

    # 切除管道通孔
    o_cut = CYLINDER(s, R=r_pipe, H=W_CLAMP + 20.0, O=0.0).rotateY(90.0).translate((-(W_CLAMP * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("L_BOX", (0.0, -l_cam * 0.35, H), (0.0, y_cyl_start + l_cyl, H))
