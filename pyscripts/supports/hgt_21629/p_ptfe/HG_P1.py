# -*- coding: utf-8 -*-
# HG/T 21629-2021 P1 尺寸固定的PTFE滑板（图 C.14-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="尺寸固定的PTFE滑板", TooltipLong="HG/T 21629-2021 P1 尺寸固定的PTFE滑板 图C.14-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="所支承管道外径")
@param(L=LENGTH, TooltipShort="滑板长", TooltipLong="PTFE滑板组件顺管向长度", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="滑板宽", TooltipLong="PTFE滑板组件横向宽度")
@param(T=LENGTH, TooltipShort="总厚度", TooltipLong="PTFE滑板与钢基板总厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_P1(s, D=114.3, L=150.0, W=80.0, T=10.0, ID=u"P1", **kw):
    D = float(D); L = float(L); W = float(W); T = float(T)
    if D < 15.0: D = 15.0
    if L < 30.0: L = 120.0
    if W < 30.0: W = 80.0
    if T < 4.0: T = 10.0
    R1 = D / 2.0
    t_steel = T * 0.6
    t_ptfe = T * 0.4
    z0 = -(R1 + T / 2.0)
    o1 = BOX(s, L=W, W=t_steel, H=L).translate((0.0, 0.0, z0 - t_ptfe / 2.0))
    o_lug = BOX(s, L=W + 28.0, W=t_steel, H=max(20.0, L * 0.25)).translate((0.0, 0.0, z0 - t_ptfe / 2.0))
    o_ptfe = BOX(s, L=W * 0.86, W=t_ptfe, H=L * 0.88).translate((0.0, 0.0, z0 + t_steel / 2.0))
    o1.uniteWith(o_lug); o_lug.erase()
    o1.uniteWith(o_ptfe); o_ptfe.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
