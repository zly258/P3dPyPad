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
          TooltipShort=u"公用工程软管站 (HG/T 20570)",
          TooltipLong=u"落地立柱式公用工程四路软管站，含底座立柱支架、软管挂架、水/汽/氮/风 4 路分配管汇、球阀与快装接头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"公用工程软管站总管外径、立柱高度及管汇宽度")
@param(D=LENGTH, TooltipShort=u"分配总管外径", TooltipLong=u"水平分配管汇外径 D (mm)")
@param(H_POST=LENGTH, TooltipShort=u"立柱总高", TooltipLong=u"底座至支架立柱顶总高 H (mm)", Ask4Dist=True)
@param(W_MANIFOLD=LENGTH, TooltipShort=u"管汇总宽", TooltipLong=u"4 路分配总管法兰面至盲端总宽 W (mm)", Ask4Dist=True)
@param(H_MANIFOLD=LENGTH, TooltipShort=u"管汇中心高", TooltipLong=u"地面至分配总管中心线高度 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"进气/水法兰外径", TooltipLong=u"总管入口法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"总管入口法兰厚度 (mm)")
def SPEC_UTILITY_STATION(
    s,
    D=60.3,
    H_POST=1450.0,
    W_MANIFOLD=680.0,
    H_MANIFOLD=1100.0,
    D_FL=165.0,
    C_FL=18.0,
    ID=u"SPEC_UTILITY_STATION",
    **kw
):
    u"""公用工程软管站 (底板面在 Z=0, 总管沿 X, 入口法兰在 -W_MANIFOLD/2 朝 -X)。"""
    D = max(32.0, float(D))
    D_FL = max(D + 45.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    W_MANIFOLD = float(W_MANIFOLD)
    if W_MANIFOLD < 1.0:
        W_MANIFOLD = 1.0
    H_MANIFOLD = max(750.0, float(H_MANIFOLD))
    H_POST = float(H_POST)
    if H_POST < 1.0:
        H_POST = 1.0

    r_hdr = D / 2.0
    r_fl = D_FL / 2.0
    half_w = W_MANIFOLD / 2.0
    y_post = -(r_hdr + 85.0)

    # 1. 落地底板、方管立柱支架与顶部铭牌背板
    o_main = BOX(s, L=240.0, W=16.0, H=240.0).translate((0.0, y_post, 8.0))
    o_post = BOX(s, L=80.0, W=H_POST - 12.0, H=80.0).translate((0.0, y_post, (H_POST + 12.0) / 2.0))
    o_main.uniteWith(o_post)
    o_post.erase()

    # 上部横梁背板 (支撑 4 路管汇)
    o_beam = BOX(s, L=18.0, W=110.0, H=W_MANIFOLD * 0.82).translate((0.0, y_post + 45.0, H_MANIFOLD))
    o_main.uniteWith(o_beam)
    o_beam.erase()

    # 软管挂架托鞍 (立柱前侧)
    o_rack_arm = BOX(s, L=120.0, W=24.0, H=180.0).translate((0.0, y_post + 95.0, H_MANIFOLD - 360.0))
    o_main.uniteWith(o_rack_arm)
    o_rack_arm.erase()
    o_rack_lip = BOX(s, L=18.0, W=90.0, H=180.0).translate((0.0, y_post + 150.0, H_MANIFOLD - 330.0))
    o_main.uniteWith(o_rack_lip)
    o_rack_lip.erase()

    # 2. 主分配总管 + 左端入口法兰 (Port 1) + 右端盲帽 + 双管卡支座
    o_fl = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_w, 0.0, H_MANIFOLD))
    o_main.uniteWith(o_fl)
    o_fl.erase()

    o_hdr = CYLINDER(s, R=r_hdr, H=W_MANIFOLD - C_FL + 4.0, O=0.0).rotateY(90.0).translate((-half_w + C_FL - 4.0, 0.0, H_MANIFOLD))
    o_main.uniteWith(o_hdr)
    o_hdr.erase()

    o_cap = CYLINDER(s, R=r_hdr * 1.15, H=18.0, O=0.0).rotateY(90.0).translate((half_w - 18.0, 0.0, H_MANIFOLD))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    for sx in (-1.0, 1.0):
        xc = sx * (W_MANIFOLD * 0.34)
        o_clp = BOX(s, L=abs(y_post + 45.0) + r_hdr * 0.5, W=36.0, H=30.0).translate((xc, (y_post + 45.0) / 2.0, H_MANIFOLD))
        o_main.uniteWith(o_clp)
        o_clp.erase()

    # 3. 水 / 汽 / 氮 / 风 4 路下伸支管 + 切断球阀 + 快装接头
    r_br = max(13.0, r_hdr * 0.48)
    span_x = W_MANIFOLD * 0.64
    for i in range(4):
        xb = -span_x / 2.0 + span_x * float(i) / 3.0
        # 支管
        o_br = CYLINDER(s, R=r_br, H=195.0, O=0.0).translate((xb, 0.0, H_MANIFOLD - 195.0))
        o_main.uniteWith(o_br)
        o_br.erase()
        # 球阀阀体与手柄
        z_v = H_MANIFOLD - 105.0
        o_vb = CYLINDER(s, R=r_br * 1.55, H=46.0, O=0.0).translate((xb, 0.0, z_v - 23.0))
        o_main.uniteWith(o_vb)
        o_vb.erase()
        o_vh = BOX(s, L=68.0, W=12.0, H=14.0).translate((xb, r_br * 1.6 + 22.0, z_v))
        o_main.uniteWith(o_vh)
        o_vh.erase()
        # 快装接头外圈与接头嘴
        o_qc = CYLINDER(s, R=r_br * 1.45, H=34.0, O=0.0).translate((xb, 0.0, H_MANIFOLD - 215.0))
        o_main.uniteWith(o_qc)
        o_qc.erase()
        o_qn = CONE(s, R1=r_br * 0.72, R2=r_br * 1.10, H=28.0, E=0.0).translate((xb, 0.0, H_MANIFOLD - 240.0))
        o_main.uniteWith(o_qn)
        o_qn.erase()

    s.setPoint((-half_w, 0.0, H_MANIFOLD), (-1.0, 0.0, 0.0))
    s.setLinearDimension('W_MANIFOLD', (-half_w, 0.0, H_MANIFOLD), (half_w, 0.0, H_MANIFOLD))
    s.setLinearDimension('H_POST', (0.0, y_post, 0.0), (0.0, y_post, H_POST))
