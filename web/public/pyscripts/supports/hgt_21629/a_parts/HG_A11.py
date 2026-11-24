# -*- coding: utf-8 -*-
# HG/T 21629-2021 A11 单孔吊板（图 C.1-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="单孔吊板", TooltipLong="HG/T 21629-2021 A11 单孔吊板 图C.1-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A11(s, D=100.0, H=333.5, B=290.0, T=90.0, d=117.0, ID=u"A11", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if T < 6.0: T = 8.0
    if B < 30.0: B = 50.0
    if d < 10.0: d = 16.0
    if d > B * 0.62: d = B * 0.52
    R_bot = B / 2.0
    if H < R_bot * 0.8: H = R_bot * 1.1
    # 1. 上部矩形立板（从 Z = 0 向上至顶部焊接面 Z = H）
    o1 = BOX(s, L=B, W=H, H=T).translate((0.0, 0.0, H / 2.0))
    # 2. 下部半圆弧底（圆心在 Z = 0）
    o_bot = CYLINDER(s, R=R_bot, H=T, O=0.0).rotateY(90.0).translate((-(T / 2.0), 0.0, 0.0))
    o1.uniteWith(o_bot); o_bot.erase()
    # 3. 顶部焊缝过渡台与中心横向圆吊孔（在 Z = 0 处沿 X 轴打孔）
    o_weld = BOX(s, L=B, W=max(5.0, T * 0.45), H=T * 1.5).translate((0.0, 0.0, H - max(2.5, T * 0.22)))
    o1.uniteWith(o_weld); o_weld.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, 0.0))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
