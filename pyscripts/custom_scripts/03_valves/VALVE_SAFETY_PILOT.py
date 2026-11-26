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
          TooltipShort=u"先导式安全阀 (API 526)",
          TooltipLong=u"先导式安全阀，含90度异径底进侧出突面法兰主阀体、低矮厚重主阀穹顶盖、侧挂先导阀体组件及外部导压取压管；两口成90度，请连接在立管管端(端点)或设备管嘴，不可直接插入连续直管中间",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"先导式安全阀外形尺寸")
@param(D_IN=LENGTH, TooltipShort=u"入口管径外径", TooltipLong=u"底部入口连接管外径 (mm)")
@param(D_OUT=LENGTH, TooltipShort=u"出口管径外径", TooltipLong=u"侧面出口连接管外径 (mm)")
@param(H_IN=LENGTH, TooltipShort=u"中心至底口距", TooltipLong=u"出口中心线至底部入口法兰面距离 (mm)", Ask4Dist=True)
@param(L_OUT=LENGTH, TooltipShort=u"中心至侧口距", TooltipLong=u"入口中心线至右侧出口法兰面距离 (mm)", Ask4Dist=True)
@param(D_FL_IN=LENGTH, TooltipShort=u"入口法兰外径", TooltipLong=u"底部入口法兰外径 (mm)")
@param(D_FL_OUT=LENGTH, TooltipShort=u"出口法兰外径", TooltipLong=u"侧面出口法兰外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"中心至先导顶高", TooltipLong=u"出口中心线至先导阀顶面高度 (mm)", Ask4Dist=True)
def VALVE_SAFETY_PILOT(
    s,
    D_IN=114.3,
    D_OUT=168.3,
    H_IN=179.0,
    L_OUT=181.0,
    D_FL_IN=220.0,
    D_FL_OUT=285.0,
    H_TOP=390.0,
    ID=u"VALVE_SAFETY_PILOT",
    **kw
):
    D_IN = max(40.0, float(D_IN))
    D_OUT = max(D_IN, float(D_OUT))
    H_IN = float(H_IN)
    if H_IN < 1.0:
        H_IN = 1.0
    L_OUT = float(L_OUT)
    if L_OUT < 1.0:
        L_OUT = 1.0
    D_FL_IN = max(D_IN + 45.0, float(D_FL_IN))
    D_FL_OUT = max(D_OUT + 45.0, float(D_FL_OUT))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    r_in = D_IN / 2.0
    r_out = D_OUT / 2.0
    r_fl_in = D_FL_IN / 2.0
    r_fl_out = D_FL_OUT / 2.0
    c_in = max(20.0, r_fl_in * 0.2)
    c_out = max(20.0, r_fl_out * 0.18)
    rf_t = 2.5

    # 1. 主阀 90度异径底进侧出突面法兰
    o_main = CYLINDER(s, R=r_fl_in * 0.72, H=rf_t + 2.0, O=0.0).translate((0.0, 0.0, -H_IN))
    o_fl1 = CYLINDER(s, R=r_fl_in, H=c_in - rf_t, O=0.0).translate((0.0, 0.0, -H_IN + rf_t))
    o_main.uniteWith(o_fl1)
    o_fl1.erase()
    o_in_neck = CYLINDER(s, R=r_in * 1.18, H=H_IN - c_in + 10.0, O=0.0).translate((0.0, 0.0, -H_IN + c_in - 2.0))
    o_main.uniteWith(o_in_neck)
    o_in_neck.erase()

    o_rf2 = CYLINDER(s, R=r_fl_out * 0.72, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((L_OUT - rf_t - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_rf2)
    o_rf2.erase()
    o_fl2 = CYLINDER(s, R=r_fl_out, H=c_out - rf_t, O=0.0).rotateY(90.0).translate((L_OUT - c_out, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_out_neck = CYLINDER(s, R=r_out * 1.15, H=L_OUT - c_out + 10.0, O=0.0).rotateY(90.0).translate((-6.0, 0.0, 0.0))
    o_main.uniteWith(o_out_neck)
    o_out_neck.erase()

    # 2. 主阀活塞室与紧凑平顶螺栓穹顶盖 (区别于弹簧安全阀的高弹簧罩)
    r_body = max(r_out * 1.2, r_in * 1.45)
    z_dome_fl = r_out * 1.08
    o_body = CYLINDER(s, R=r_body, H=z_dome_fl + r_out * 1.05, O=0.0).translate((0.0, 0.0, -r_out * 1.05))
    o_main.uniteWith(o_body)
    o_body.erase()

    dome_fl_t = max(28.0, c_out * 1.35)
    r_dome_fl = r_body * 1.24
    o_dfl = CYLINDER(s, R=r_dome_fl, H=dome_fl_t, O=0.0).translate((0.0, 0.0, z_dome_fl))
    o_main.uniteWith(o_dfl)
    o_dfl.erase()

    z_dome_top = z_dome_fl + dome_fl_t + max(42.0, r_body * 0.45)
    o_dome = CYLINDER(s, R=r_body * 0.92, H=z_dome_top - (z_dome_fl + dome_fl_t) + 6.0, O=0.0).translate((0.0, 0.0, z_dome_fl + dome_fl_t - 4.0))
    o_main.uniteWith(o_dome)
    o_dome.erase()

    # 穹顶顶盖导压接头座
    o_top_boss = CYLINDER(s, R=18.0, H=24.0, O=0.0).translate((0.0, 0.0, z_dome_top - 4.0))
    o_main.uniteWith(o_top_boss)
    o_top_boss.erase()

    # 3. 侧挂先导阀体与安装托架 (位于 -X 侧)
    px = -(r_dome_fl + 56.0)
    pz_bot = z_dome_fl - 30.0
    o_brk = CORNERBOX(s, L=abs(px) - r_body * 0.7 + 20.0, W=52.0, H=16.0).translate((px - 10.0, -26.0, pz_bot))
    o_main.uniteWith(o_brk)
    o_brk.erase()

    # 先导阀方体阀块 + 上部调压弹簧帽
    p_blk_h = max(72.0, r_body * 0.7)
    o_pblk = CORNERBOX(s, L=68.0, W=68.0, H=p_blk_h).translate((px - 34.0, -34.0, pz_bot + 12.0))
    o_main.uniteWith(o_pblk)
    o_pblk.erase()

    z_p_bon = pz_bot + 12.0 + p_blk_h - 4.0
    p_bon_h = max(85.0, H_TOP - z_p_bon)
    o_pbon = CYLINDER(s, R=26.0, H=p_bon_h, O=0.0).translate((px, 0.0, z_p_bon))
    o_main.uniteWith(o_pbon)
    o_pbon.erase()
    o_pcap = CYLINDER(s, R=20.0, H=24.0, O=0.0).translate((px, 0.0, z_p_bon + p_bon_h - 14.0))
    o_main.uniteWith(o_pcap)
    o_pcap.erase()

    # 4. 外部导压管 (入口取压管 -> 先导阀底; 先导阀侧 -> 主阀穹顶顶盖)
    r_tube = 8.0
    z_tap = -(H_IN - c_in) * 0.58
    # 入口取压水平管
    o_t1 = CYLINDER(s, R=r_tube, H=abs(px) + 10.0, O=0.0).rotateY(90.0).translate((px, 0.0, z_tap))
    o_main.uniteWith(o_t1)
    o_t1.erase()
    # 入口取压竖直管 (接先导阀底部)
    o_t2 = CYLINDER(s, R=r_tube, H=(pz_bot + 18.0) - z_tap, O=0.0).translate((px, 0.0, z_tap))
    o_main.uniteWith(o_t2)
    o_t2.erase()
    o_elb1 = SPHERE(s, R=r_tube * 1.25).translate((px, 0.0, z_tap))
    o_main.uniteWith(o_elb1)
    o_elb1.erase()

    # 穹顶导压竖直段 + 水平段
    z_dome_pipe = z_dome_top + 14.0
    o_t3 = CYLINDER(s, R=r_tube, H=abs(px) + 12.0, O=0.0).rotateY(90.0).translate((px, 0.0, z_dome_pipe))
    o_main.uniteWith(o_t3)
    o_t3.erase()
    o_t4 = CYLINDER(s, R=r_tube, H=abs(z_dome_pipe - (pz_bot + 12.0 + p_blk_h * 0.5)) + 16.0, O=0.0).translate((px, 0.0, min(z_dome_pipe, pz_bot + 12.0 + p_blk_h * 0.5)))
    o_main.uniteWith(o_t4)
    o_t4.erase()
    o_elb2 = SPHERE(s, R=r_tube * 1.25).translate((px, 0.0, z_dome_pipe))
    o_main.uniteWith(o_elb2)
    o_elb2.erase()

    s.setPoint((0.0, 0.0, -H_IN), (0.0, 0.0, -1.0))
    s.setPoint((L_OUT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_IN', (0.0, 0.0, -H_IN), (0.0, 0.0, 0.0))
    s.setLinearDimension('L_OUT', (0.0, 0.0, 0.0), (L_OUT, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
