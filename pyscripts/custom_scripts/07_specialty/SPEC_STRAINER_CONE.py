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
          TooltipShort=u"锥形临时过滤器 (HG/T 21637)",
          TooltipLong=u"HG/T 21637 法兰夹持式锥形临时过滤器，含夹持环、加长锥形滤网壳体、加强环与侧向标识提柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"锥形临时过滤器夹持环、锥体长度与提柄尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"安装管道外径 D (mm)")
@param(L_RING=LENGTH, TooltipShort=u"夹持环厚度", TooltipLong=u"法兰间夹持厚度 L (mm)", Ask4Dist=True)
@param(D_RING=LENGTH, TooltipShort=u"夹持环外径", TooltipLong=u"对夹外定位环外径 (mm)")
@param(L_CONE=LENGTH, TooltipShort=u"锥体长度", TooltipLong=u"锥形滤网壳体伸出长度 (mm)", Ask4Dist=True)
@param(H_TAB=LENGTH, TooltipShort=u"提柄高度", TooltipLong=u"夹持环外缘至侧提柄顶端高度 (mm)")
@param(W_TAB=LENGTH, TooltipShort=u"提柄宽度", TooltipLong=u"侧向标识提柄宽度 (mm)")
def SPEC_STRAINER_CONE(
    s,
    D=114.3,
    L_RING=12.0,
    D_RING=162.0,
    L_CONE=220.0,
    H_TAB=85.0,
    W_TAB=32.0,
    ID=u"SPEC_STRAINER_CONE",
    **kw
):
    u"""锥形临时过滤器 (夹持环中心在原点, 锥体沿 +X 伸出, 标识提柄朝 +Z)。"""
    D = max(25.0, float(D))
    L_RING = float(L_RING)
    if L_RING < 1.0:
        L_RING = 1.0
    D_RING = max(D + 20.0, float(D_RING))
    L_CONE = float(L_CONE)
    if L_CONE < 1.0:
        L_CONE = 1.0
    H_TAB = max(35.0, float(H_TAB))
    W_TAB = max(18.0, float(W_TAB))

    half_r = L_RING / 2.0
    r_ring = D_RING / 2.0
    r_cone1 = D / 2.0 * 0.90
    r_cone2 = max(8.0, D / 2.0 * 0.18)

    # 1. 法兰对夹定位环
    o_main = CYLINDER(s, R=r_ring, H=L_RING, O=0.0).rotateY(90.0).translate((-half_r, 0.0, 0.0))

    # 2. 长锥形滤网壳体 (沿 +X 方向)
    o_cone = CONE(s, R1=r_cone1, R2=r_cone2, H=L_CONE, E=0.0).rotateY(90.0).translate((half_r - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 锥体中部加强箍环与前端封头
    r_mid = r_cone1 * 0.55 + r_cone2 * 0.45
    o_rib = CYLINDER(s, R=r_mid + 3.5, H=max(8.0, L_CONE * 0.05), O=0.0).rotateY(90.0).translate((half_r + L_CONE * 0.45, 0.0, 0.0))
    o_main.uniteWith(o_rib)
    o_rib.erase()

    o_tip = SPHERE(s, R=r_cone2 * 1.05).translate((half_r + L_CONE - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    # 4. 侧向标识提柄与顶部加厚拉手头 (沿 +Z)
    t_tab = max(5.0, L_RING * 0.70)
    o_tab = BOX(s, L=W_TAB, W=H_TAB + 12.0, H=t_tab).translate((0.0, 0.0, r_ring + H_TAB / 2.0 - 6.0))
    o_main.uniteWith(o_tab)
    o_tab.erase()

    o_head = BOX(s, L=W_TAB * 1.45, W=max(16.0, H_TAB * 0.22), H=t_tab * 1.35).translate((0.0, 0.0, r_ring + H_TAB))
    o_main.uniteWith(o_head)
    o_head.erase()

    s.setPoint((-half_r, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_r, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_RING', (-half_r, 0.0, 0.0), (half_r, 0.0, 0.0))
    s.setLinearDimension('L_CONE', (half_r, 0.0, 0.0), (half_r + L_CONE, 0.0, 0.0))
