# -*- coding: utf-8 -*-
# CD-ZD2010 415 滑动底板（钢质底板 + 顶面内嵌一层缩进的 PTFE 聚四氟乙烯滑片台阶）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="415滑动底板", TooltipLong="CD-ZD2010 415 滑动底板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="板长A1", TooltipLong="滑动底板长度 A1", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="板宽B1", TooltipLong="滑动底板宽度 B1")
@param(T=LENGTH, TooltipShort="总厚t", TooltipLong="滑动底板总厚度 t")
@param(PTFE_T=LENGTH, TooltipShort="四氟高", TooltipLong="顶面缩进PTFE复合层露出高度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_415(s, L=250.0, W=250.0, T=19.0, PTFE_T=5.0, ID=u"ZD_415", **kw):
    L = float(L); W = float(W); T = float(T); PTFE_T = float(PTFE_T)
    if L < 60.0 or L > 2000.0: L = 200.0
    if W < 60.0 or W > 2000.0: W = 200.0
    if T < 8.0: T = 14.0
    if PTFE_T < 3.0 or PTFE_T >= T * 0.7: PTFE_T = 5.0

    # 1. 下部碳钢基板 (A1 x B1 = L x W, 厚 steel_t)
    steel_t = T - PTFE_T
    o1 = BOX(s, L=W, W=steel_t, H=L).translate((0.0, 0.0, -(steel_t / 2.0)))

    # 2. 顶面内嵌缩进的 PTFE 聚四氟乙烯滑片台阶 (四周缩进 margin)
    margin = max(12.0, min(L, W) * 0.08)
    o_ptfe = BOX(s, L=W - 2.0 * margin, W=PTFE_T + 1.0, H=L - 2.0 * margin).translate((0.0, 0.0, (PTFE_T - 1.0) / 2.0))
    o1.uniteWith(o_ptfe); o_ptfe.erase()

    s.setPoint((0.0, 0.0, PTFE_T), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (-(L / 2.0), 0.0, 0.0), ((L / 2.0), 0.0, 0.0))
