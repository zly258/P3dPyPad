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
          TooltipShort=u"法兰式热电偶/温度计含锥形套管 (ASME PTC 19.3)",
          TooltipLong=u"化工法兰式双金属/热电偶温度计总成，含比例饱满的锥形重型保护套管、过程法兰、加长散热颈及防爆圆盒接线表头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"温度计法兰、插入深度、颈高及表头尺寸")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
@param(L_IMM=LENGTH, TooltipShort=u"套管插入深", TooltipLong=u"法兰密封面至保护套管端头插入深度 (mm)", Ask4Dist=True)
@param(D_ROOT=LENGTH, TooltipShort=u"套管根径", TooltipLong=u"锥形保护套管根部外径 (mm)")
@param(D_TIP=LENGTH, TooltipShort=u"套管端径", TooltipLong=u"锥形保护套管端部外径 (mm)")
@param(H_EXT=LENGTH, TooltipShort=u"法兰上总高", TooltipLong=u"法兰密封面至防爆接线盒顶面总高 (mm)", Ask4Dist=True)
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"防爆接线表头外径 (mm)")
def INST_TEMP_THERMOWELL(
    s,
    D_FL=115.0,
    C_FL=18.0,
    L_IMM=220.0,
    D_ROOT=38.0,
    D_TIP=24.0,
    H_EXT=235.0,
    D_HEAD=104.0,
    ID=u"INST_TEMP_THERMOWELL",
    **kw
):
    u"""法兰式温度计/热电偶含锥形保护套管 (Port 1 在 Z=0 法兰密封面，套管向 -Z 伸出)。"""
    D_FL = max(85.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    L_IMM = float(L_IMM)
    if L_IMM < 1.0:
        L_IMM = 1.0
    D_ROOT = max(28.0, float(D_ROOT))
    D_TIP = max(18.0, min(D_ROOT - 4.0, float(D_TIP)))
    H_EXT = float(H_EXT)
    if H_EXT < 1.0:
        H_EXT = 1.0
    D_HEAD = max(80.0, float(D_HEAD))

    r_fl = D_FL / 2.0
    r_root = D_ROOT / 2.0
    r_tip = D_TIP / 2.0
    r_head = D_HEAD / 2.0

    # 1. 过程连接法兰 (Z=[0, C_FL])
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)

    # 2. 比例饱满的锥形重型保护套管 (-Z) + 圆头端帽
    h_cone = max(40.0, L_IMM - r_tip)
    o_well = CONE(s, R1=r_root, R2=r_tip, H=h_cone).rotateX(180.0).translate((0.0, 0.0, 2.0))
    o_main.uniteWith(o_well)
    o_well.erase()
    o_tip = SPHERE(s, R=r_tip).translate((0.0, 0.0, -h_cone + 2.0))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    # 3. 法兰上加粗延长颈 + 六角锁母
    h_head = 88.0
    z_head_bot = H_EXT - h_head
    o_hub = CYLINDER(s, R=max(r_root * 1.15, 22.0), H=28.0, O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    o_neck = CYLINDER(s, R=18.0, H=max(40.0, z_head_bot - C_FL + 14.0), O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_hex = CORNERBOX(s, L=44.0, W=44.0, H=24.0).translate((-22.0, -22.0, z_head_bot - 22.0))
    o_main.uniteWith(o_hex)
    o_hex.erase()

    # 4. 防爆圆盒接线表头 + 螺纹表盖 + 侧向穿线管嘴
    o_head = CYLINDER(s, R=r_head, H=h_head - 16.0, O=0.0).translate((0.0, 0.0, z_head_bot))
    o_main.uniteWith(o_head)
    o_head.erase()
    o_lid = CYLINDER(s, R=r_head + 6.0, H=20.0, O=0.0).translate((0.0, 0.0, H_EXT - 20.0))
    o_main.uniteWith(o_lid)
    o_lid.erase()
    # 侧向防爆电缆引入口 (+X)
    o_gl = CYLINDER(s, R=16.0, H=38.0, O=0.0).rotateY(90.0).translate((r_head - 8.0, 0.0, z_head_bot + (h_head - 16.0) * 0.45))
    o_main.uniteWith(o_gl)
    o_gl.erase()
    # 铭牌/表头锁耳 (-X)
    o_lug = CORNERBOX(s, L=20.0, W=26.0, H=34.0).translate((-r_head - 12.0, -13.0, z_head_bot + 16.0))
    o_main.uniteWith(o_lug)
    o_lug.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_IMM', (0.0, 0.0, 0.0), (0.0, 0.0, -L_IMM))
    s.setLinearDimension('H_EXT', (0.0, 0.0, 0.0), (0.0, 0.0, H_EXT))
