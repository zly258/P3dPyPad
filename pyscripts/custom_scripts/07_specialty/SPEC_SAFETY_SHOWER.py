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

@activate(Group="Instrument",
          TooltipShort=u"紧急冲淋洗眼器 (ANSI Z358.1)",
          TooltipLong=u"复合式紧急冲淋洗眼器，含圆形落地底板、主立管、顶部冲淋横臂与莲蓬头、拉杆开关、中部洗眼盆与手推阀板及侧向进水法兰口",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"紧急冲淋洗眼器总高、洗眼盆高度、冲淋臂长与进水口参数")
@param(D=LENGTH, TooltipShort=u"主立管外径", TooltipLong=u"立管及供水管外径 D (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"冲淋器总高", TooltipLong=u"底板面至顶部冲淋横管顶总高 H (mm)", Ask4Dist=True)
@param(H_BOWL=LENGTH, TooltipShort=u"洗眼盆高度", TooltipLong=u"底板面至洗眼盆上沿高度 (mm)")
@param(L_ARM=LENGTH, TooltipShort=u"冲淋臂伸长", TooltipLong=u"立管中心至冲淋莲蓬头中心水平距 (mm)", Ask4Dist=True)
@param(D_SHOWER=LENGTH, TooltipShort=u"莲蓬头直径", TooltipLong=u"顶部冲淋莲蓬头外径 (mm)")
@param(D_BOWL=LENGTH, TooltipShort=u"洗眼盆直径", TooltipLong=u"中部洗眼盆外径 (mm)")
@param(H_INLET=LENGTH, TooltipShort=u"进水口高度", TooltipLong=u"底板面至侧向进水法兰中心高度 (mm)")
def SPEC_SAFETY_SHOWER(
    s,
    D=42.4,
    H_TOTAL=2300.0,
    H_BOWL=1020.0,
    L_ARM=520.0,
    D_SHOWER=260.0,
    D_BOWL=280.0,
    H_INLET=1500.0,
    ID=u"SPEC_SAFETY_SHOWER",
    **kw
):
    u"""紧急冲淋洗眼器 (底板面在 Z=0, 冲淋/洗眼朝 +X, 进水法兰口朝 -X)。"""
    D = max(25.0, float(D))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    H_BOWL = max(750.0, min(H_TOTAL - 600.0, float(H_BOWL)))
    L_ARM = float(L_ARM)
    if L_ARM < 1.0:
        L_ARM = 1.0
    D_SHOWER = max(160.0, float(D_SHOWER))
    D_BOWL = max(200.0, float(D_BOWL))
    H_INLET = max(400.0, min(H_TOTAL - 300.0, float(H_INLET)))

    r_pipe = D / 2.0
    r_base = max(110.0, D * 2.8)

    # 1. 落地圆底板、底座套筒与主立管
    o_main = CYLINDER(s, R=r_base, H=16.0, O=0.0)
    o_collar = CONE(s, R1=r_pipe * 2.2, R2=r_pipe * 1.35, H=45.0, E=0.0).translate((0.0, 0.0, 14.0))
    o_main.uniteWith(o_collar)
    o_collar.erase()

    z_arm = H_TOTAL - r_pipe
    o_riser = CYLINDER(s, R=r_pipe, H=z_arm - 10.0, O=0.0).translate((0.0, 0.0, 10.0))
    o_main.uniteWith(o_riser)
    o_riser.erase()

    # 2. 侧向进水接管与进水法兰 (Port 1 在 -X)
    l_in = 140.0
    r_in_fl = max(55.0, r_pipe * 2.7)
    c_in_fl = 16.0
    o_in_pipe = CYLINDER(s, R=r_pipe * 0.95, H=l_in + 8.0, O=0.0).rotateY(90.0).translate((-l_in, 0.0, H_INLET))
    o_main.uniteWith(o_in_pipe)
    o_in_pipe.erase()

    o_in_fl = CYLINDER(s, R=r_in_fl, H=c_in_fl, O=0.0).rotateY(90.0).translate((-l_in, 0.0, H_INLET))
    o_main.uniteWith(o_in_fl)
    o_in_fl.erase()

    # 3. 顶部冲淋横臂、球阀块、拉杆把手与喇叭莲蓬头
    o_top_el = SPHERE(s, R=r_pipe * 1.25).translate((0.0, 0.0, z_arm))
    o_main.uniteWith(o_top_el)
    o_top_el.erase()

    o_arm = CYLINDER(s, R=r_pipe, H=L_ARM + 8.0, O=0.0).rotateY(90.0).translate((-4.0, 0.0, z_arm))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    # 冲淋阀门与下拉操作杆
    x_val = L_ARM * 0.42
    o_sval = CYLINDER(s, R=r_pipe * 1.45, H=75.0, O=0.0).rotateY(90.0).translate((x_val - 37.5, 0.0, z_arm))
    o_main.uniteWith(o_sval)
    o_sval.erase()

    o_lever = BOX(s, L=12.0, W=20.0, H=110.0).translate((x_val, r_pipe * 1.5, z_arm))
    o_main.uniteWith(o_lever)
    o_lever.erase()

    o_rod = CYLINDER(s, R=5.5, H=560.0, O=0.0).translate((x_val + 45.0, r_pipe * 1.5, z_arm - 560.0))
    o_main.uniteWith(o_rod)
    o_rod.erase()

    o_handle = BOX(s, L=14.0, W=16.0, H=140.0).translate((x_val + 45.0, r_pipe * 1.5, z_arm - 560.0))
    o_main.uniteWith(o_handle)
    o_handle.erase()

    # 顶部弯头与冲淋莲蓬头
    o_end_el = SPHERE(s, R=r_pipe * 1.22).translate((L_ARM, 0.0, z_arm))
    o_main.uniteWith(o_end_el)
    o_end_el.erase()

    o_drop = CYLINDER(s, R=r_pipe * 0.90, H=105.0, O=0.0).translate((L_ARM, 0.0, z_arm - 105.0))
    o_main.uniteWith(o_drop)
    o_drop.erase()

    o_head = CONE(s, R1=D_SHOWER / 2.0, R2=r_pipe * 1.15, H=110.0, E=0.0).translate((L_ARM, 0.0, z_arm - 210.0))
    o_main.uniteWith(o_head)
    o_head.erase()

    # 4. 中部洗眼支管、洗眼盆、双喷头与手推阀板
    x_bowl = L_ARM * 0.52
    h_bowl_body = 95.0
    z_bowl_bot = H_BOWL - h_bowl_body
    o_ebranch = CYLINDER(s, R=r_pipe * 0.85, H=x_bowl + 8.0, O=0.0).rotateY(90.0).translate((-4.0, 0.0, z_bowl_bot - 35.0))
    o_main.uniteWith(o_ebranch)
    o_ebranch.erase()

    o_epost = CYLINDER(s, R=r_pipe * 0.85, H=50.0, O=0.0).translate((x_bowl, 0.0, z_bowl_bot - 40.0))
    o_main.uniteWith(o_epost)
    o_epost.erase()

    o_bowl = CONE(s, R1=D_BOWL * 0.28, R2=D_BOWL / 2.0, H=h_bowl_body, E=0.0).translate((x_bowl, 0.0, z_bowl_bot))
    o_main.uniteWith(o_bowl)
    o_bowl.erase()

    o_brim = CYLINDER(s, R=D_BOWL / 2.0 + 6.0, H=14.0, O=0.0).translate((x_bowl, 0.0, H_BOWL - 10.0))
    o_main.uniteWith(o_brim)
    o_brim.erase()

    for sy in (-1.0, 1.0):
        o_noz = CYLINDER(s, R=10.0, H=55.0, O=0.0).translate((x_bowl, sy * D_BOWL * 0.22, H_BOWL - 15.0))
        o_main.uniteWith(o_noz)
        o_noz.erase()

    # 手推洗眼阀旗板
    o_flag_arm = CYLINDER(s, R=7.0, H=90.0, O=0.0).rotateX(90.0).translate((x_bowl - 45.0, 90.0, H_BOWL - 35.0))
    o_main.uniteWith(o_flag_arm)
    o_flag_arm.erase()

    o_flag = BOX(s, L=10.0, W=95.0, H=80.0).translate((x_bowl - 45.0, 88.0, H_BOWL + 15.0))
    o_main.uniteWith(o_flag)
    o_flag.erase()

    s.setPoint((-l_in, 0.0, H_INLET), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('L_ARM', (0.0, 0.0, z_arm), (L_ARM, 0.0, z_arm))
