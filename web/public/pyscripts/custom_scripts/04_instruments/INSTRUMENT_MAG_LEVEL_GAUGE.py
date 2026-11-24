# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Instrument", Ports=2, TooltipShort=u"侧装磁翻板液位计 (UHZ / HG/T 21584)", TooltipLong=u"化工行业标准 HG/T 21584 侧装式磁性浮子（磁翻板）液位计 (Side-Mounted Magnetic Level Gauge)，含立式不锈钢浮子室主导管、顶底排污排气法兰、侧向双过程连接法兰与前侧红白翻柱指示标尺槽", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"磁翻板液位计主要结构尺寸：上下测量中心距、主导管径与侧伸距")
@param(D_CHAMBER=LENGTH, TooltipShort=u"主导管外径", Ask4Dist=True, TooltipLong=u"立式浮子室不锈钢主导管外径 (如 57, 60.3 mm)")
@param(L_CC=LENGTH, TooltipShort=u"测量中心距 L", Ask4Dist=True, TooltipLong=u"上下两过程连接法兰中心距 L")
@param(L_SIDE=LENGTH, TooltipShort=u"侧接管中心距", Ask4Dist=True, TooltipLong=u"主导管中心至侧向过程法兰面距离")
@param(DN_NOZ=LENGTH, TooltipShort=u"侧接管外径", TooltipLong=u"过程连接横管外径 (如 DN25 为 33.7mm)")
@param(FL_OD=LENGTH, TooltipShort=u"过程法兰径", TooltipLong=u"过程连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"过程法兰厚", TooltipLong=u"过程连接法兰厚度")
@param(W_SCALE=LENGTH, TooltipShort=u"翻板标尺宽", TooltipLong=u"前侧磁翻柱显示面板宽度")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 LG/LT-101")
def INSTRUMENT_MAG_LEVEL_GAUGE(s, D_CHAMBER=60.3, L_CC=1000.0, L_SIDE=150.0, DN_NOZ=33.7, FL_OD=115.0, FL_T=16.0, W_SCALE=68.0, ID=u"LG-101-L1000", **kw):
    D_CHAMBER = max(45.0, float(D_CHAMBER))
    L_CC = max(400.0, float(L_CC))
    L_SIDE = max(100.0, float(L_SIDE))
    DN_NOZ = max(21.3, float(DN_NOZ))
    FL_OD = max(DN_NOZ + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    W_SCALE = max(48.0, float(W_SCALE))

    r_ch = D_CHAMBER / 2.0
    r_noz = DN_NOZ / 2.0
    r_fl = FL_OD / 2.0
    ext_end = 135.0

    # 1. 立式浮子室主导管 (z in [-ext_end, L_CC + ext_end]) + 顶部端盖与底部排污盲板法兰
    z_bot = -ext_end
    z_top = L_CC + ext_end
    o_m = CYLINDER(s, R=r_ch, H=z_top - z_bot, O=0.0).translate((0.0, 0.0, z_bot))
    fl_b = CYLINDER(s, R=r_fl * 0.95, H=FL_T * 1.6, O=0.0).translate((0.0, 0.0, z_bot))
    cap_t = CYLINDER(s, R=r_ch * 1.35, H=28.0, O=0.0).translate((0.0, 0.0, z_top - 28.0))
    o_m.uniteWith(fl_b); fl_b.erase()
    o_m.uniteWith(cap_t); cap_t.erase()

    # 2. 左侧 (-X) 上下两根过程连接横管 (位于 z=0 与 z=L_CC) 与连接法兰
    for zp in (0.0, L_CC):
        nz = CYLINDER(s, R=r_noz, H=L_SIDE, O=0.0).rotateY(90.0).translate((-L_SIDE, 0.0, zp))
        fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L_SIDE, 0.0, zp))
        o_m.uniteWith(nz); nz.erase()
        o_m.uniteWith(fl); fl.erase()

    # 3. 前侧 (-Y) 红白磁翻柱指示面板盒 + 捆绑抱箍与液位远传干簧管变送盒
    o_scale = BOX(s, L=28.0, W=L_CC + 40.0, H=W_SCALE).translate((0.0, -(r_ch + 16.0), L_CC * 0.5))
    o_m.uniteWith(o_scale); o_scale.erase()
    for zc in (L_CC * 0.15, L_CC * 0.5, L_CC * 0.85):
        cl = BOX(s, L=r_ch * 2.0 + 24.0, W=16.0, H=W_SCALE * 0.85).translate((0.0, -8.0, zc))
        o_m.uniteWith(cl); cl.erase()

    # 右侧远传变送器小表头
    o_xmtr = CYLINDER(s, R=48.0, H=95.0, O=0.0).rotateX(90.0).translate((r_ch + 55.0, 47.5, L_CC * 0.78))
    o_xarm = BOX(s, L=24.0, W=24.0, H=65.0).translate((r_ch + 28.0, 0.0, L_CC * 0.78))
    o_m.uniteWith(o_xmtr); o_xmtr.erase()
    o_m.uniteWith(o_xarm); o_xarm.erase()

    s.setPoint((-L_SIDE, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((-L_SIDE, 0.0, L_CC), (-1.0, 0.0, 0.0))
    s.setLinearDimension("L_CC", (-L_SIDE, 0.0, 0.0), (-L_SIDE, 0.0, L_CC))
    s.setLinearDimension("L_SIDE", (-L_SIDE, 0.0, 0.0), (0.0, 0.0, 0.0))
