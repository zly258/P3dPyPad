# AutoCAD Plant 3D 原厂典范源码母版 —— 类别二：滑动管托、焊接鞍座、管卡与滚轮支座类（`CSGB001`, `CSGB004`, `CSGC000`, `CSGC004`, `CSGR005`）

> **所属分册**：`references/templates/02_shoes_clamps_and_rollers.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别二：滑动管托、焊接鞍座、管卡与滚轮支座类（`varmain/supportssub/`）

### 典范 05：`CSGB001` —— 带双抱箍与底部耐磨滑板的T型滑动管托
- **原厂路径**：`varmain/supportssub/csgbsub/csgb001.pyc`
- **工程用途**：最常用的标准管夹滑动管托（Clamped Pipe Shoe），由立板 `o1`、底板 `o2`、可选底部聚四氟乙烯/不锈钢耐磨滑板 `o3` 以及前后两付 `CSGC002` 管卡组成。

#### 原厂反编译源码与逐行几何注释
```python
def CSGB001(s, D=116.0, L=30.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0,
            SH=150.0, E=0.0, HL=0.0, HW=0.0, HH=0.0, ID='CSGB001', **kw):
    R1 = (D / 2.0)
    HS = (SH - R1)  # 立板净高 = 管中心至底面高度 SH - 管外半径 R1

    # 1. T型管托主体：立板 o1 + 底板 o2（此时沿 +X 轴方向代表向下高度）
    o1 = BOX(s, L=ST, W=SL, H=HS).translate((((HS / 2.0) + R1), 0, 0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate(((SH - (ST / 2.0)), 0, 0))
    o1.uniteWith(o2)
    o2.erase()

    # 2. 可选底部耐磨滑板/垫板 o3（当 HL > 0 且 HW > 0 时生成）
    if (HL > 0.0) and (HW > 0.0):
        if (HH <= 0.0):
            HH = (ST * 2.0)
        o3 = BOX(s, L=HW, W=HL, H=HH).translate(((SH - (HH / 2.0)), 0, 0))
        o1.uniteWith(o3)
        o3.erase()

    # 3. 前后双管夹 CSGC002，间距 LS = SL - L - 2*E
    if (L > 0.0) and (W > 0.0):
        LS = ((SL - L) - (E * 2.0))
        o4 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0, 0, (0 - (LS / 2.0))))
        o1.uniteWith(o4); o4.erase()
        o5 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0, 0, (LS / 2.0)))
        o1.uniteWith(o5); o5.erase()

    # 4. 整体绕 Y 轴旋转 90°，将原 +X 方向翻转为 -Z 方向（管托位于管下方）
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, 0), (0, 0, (-SH)))
```

---

### 典范 06：`CSGB004` —— 带端板、八角切角减重孔与弧面布尔差集的焊接鞍式管托
- **原厂路径**：`varmain/supportssub/csgbsub/csgb004.pyc`
- **工程亮点**：
  1. **贯穿管道差集**：立板与两端肋板延伸入管内（`HS = SH + R1`），随后用 `o6 = CYLINDER(s, R=R1, H=SL)` 一次性布尔差集（`o1.subtractFrom(o6)`），自动在立板与两侧端板上同时切出精确贴合管道外壁的圆弧鞍口！
  2. **45° 旋转方块拼合八角切角减重槽**：当 `SC > 0` 时，用 `o7`（主体长方体）+ `o8`/`o9`（两个绕 Y 轴旋转 45° 的方块 `CC = sqrt(2)*SC`）+ `o0` 合并成一个带 45° 倒角的切刀体，从腹板 `o1` 中减去（`o1.subtractFrom(o7)`），形成带折角过渡的腹板减重/排液缺口。

#### 原厂反编译源码与逐行几何注释
```python
def CSGB004(s, D=116.0, SL=180.0, SW=100.0, ST=8.0, SH=75.0, SE=25.0, SC=30.0,
            HL=50.0, HW=160.0, HH=20.0, P=1, ID='CSGB004', **kw):
    R1 = (D / 2.0)
    HS = (SH + R1)  # 주의：此处 SH 是管底至管托底面的净高，故总高 HS = SH + R1

    # 1. 纵向腹板 o1、底板 o2、可选耐磨板 o3、前后横向封头端板 o4/o5
    o1 = BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0), 0.0, 0.0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate(((HS - (ST / 2.0)), 0.0, 0.0))
    o3 = None
    if (HL > 0.0) and (HW > 0.0):
        if (HH <= 0.0): HH = (ST * 2.0)
        o3 = BOX(s, L=HW, W=HL, H=HH).translate(((HS - (HH / 2.0)), 0.0, 0.0))
    if (P > 0):
        o4 = BOX(s, L=SW, W=ST, H=HS).translate(((HS / 2.0), 0.0, ((-(SL / 2.0)) + (ST / 2.0))))
        o5 = BOX(s, L=SW, W=ST, H=HS).translate(((HS / 2.0), 0.0, ((SL / 2.0) - (ST / 2.0))))
    else:
        o4 = o5 = None

    for part in (o2, o3, o4, o5):
        if part:
            o1.uniteWith(part); part.erase()

    # 2. 用管道外径圆柱 o6 一次性切除腹板与前后封头端板上的圆弧马鞍面
    o6 = CYLINDER(s, R=R1, H=SL, O=0.0).translate((0.0, 0.0, (-(SL / 2.0))))
    o1.subtractFrom(o6)
    o6.erase()

    # 3. 构造带 45° 斜切角的腹板中部减重槽切刀 o7
    if (SC > 0.0):
        CT = (ST * 2.0)
        if (P > 0.0) and (SE <= 0.0):
            SE = ST
        CW = (SL - (SE * 2.0))
        o7 = BOX(s, L=CT, W=CW, H=R1).translate(((R1 / 2.0), 0.0, 0.0))
        CL = (CW - (SC * 2.0))
        CC = sqrt((pow(SC, 2.0) * 2.0))
        o8 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((R1, 0.0, (CL / 2.0)))
        o7.uniteWith(o8); o8.erase()
        o9 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((R1, 0.0, (-(CL / 2.0))))
        o7.uniteWith(o9); o9.erase()
        o0 = BOX(s, L=CT, W=CL, H=SC).translate(((R1 + (SC / 2.0)), 0.0, 0.0))
        o7.uniteWith(o0); o0.erase()
        o1.subtractFrom(o7)
        o7.erase()

    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    # 注意握点起点在管底 (0, 0, -D/2)，终点在 (0, 0, -SH - D/2)
    s.setLinearDimension('SH', (0, 0, ((-D) / 2.0)), (0, 0, ((-SH) - (D / 2.0))))
```

---

### 典范 07：`CSGC000` —— `TORUS` 半环裁切 + 双腿圆柱 + 鞍座垫块 U 型螺栓组件
- **原厂路径**：`varmain/supportssub/csgcsub/csgc000.pyc`
- **工程亮点**：展示了标准 U 型螺栓的标准构造范式——先创建完整圆环 `TORUS(s, R1=R1+R2, R2=R2)`，再用下半空间包围盒 `o4` 执行 `o1.subtractFrom(o4)` 留下上半 180° 圆弧，最后并入两侧直螺杆圆柱 `o2, o3`、弧形鞍座垫块 `o5`（减去管道圆柱 `o6`）和两侧六角螺母 `o7, o8`。

#### 原厂反编译源码与逐行几何注释
```python
def CSGC000(s, D=116.0, L=30.0, W=0.0, BL=80.0, BW=60.0, BH=10.0,
            MW=0.0, MH=0.0, MD=0.0, ID='CSGC000', **kw):
    if (W <= 0.0):
        W = (2.0 * getThickness(D=D, OF=0.0, Ever=1, mustCalc=True))
    R1 = (D / 2.0)       # 管道外半径
    R2 = (W / 2.0)       # U型螺栓圆钢半径
    R3 = (R1 + R2)       # U型螺栓中心弯曲半径
    sL = ((R1 + BH) + L) # 直腿总长
    sS = (sL + W)
    if (MW == 0.0): MW = (2.0 * W)
    if (MH == 0.0): MH = W
    if (MD == 0.0): MD = (L / 3.0)

    # 1. 完整圆环 o1 + 两侧直腿圆柱 o2/o3 + 半空间裁切盒 o4
    o1 = TORUS(s, R1=R3, R2=R2).translate((0.0, 0.0, 0.0))
    o2 = CYLINDER(s, R=R2, H=sL, O=0.0).rotateY(90.0).translate((0.0, (R1 + R2), 0.0))
    o3 = CYLINDER(s, R=R2, H=sL, O=0.0).rotateY(90.0).translate((0.0, (-(R1 + R2)), 0.0))
    o4 = BOX(s, L=((R1 + W) * 2.0), W=L, H=(sS + W)).translate((((sS + W) / 2.0), 0.0, 0.0))

    # 2. 管底鞍座垫块 o5（用管道圆柱 o6 挖出半圆凹槽）
    o5 = None
    if (BL > 0.0):
        if (BW <= 0.0): BW = L
        o5 = BOX(s, L=BL, W=BW, H=sL).translate((((sL / 2.0) - L), 0.0, 0.0))
        o6 = CYLINDER(s, R=R1, H=BW, O=0.0).translate((0.0, 0.0, (-(BW / 2.0))))

    # 3. 两侧六角螺母 o7, o8
    o7 = o8 = None
    if (MW > 0.0) and (MH > 0.0) and (L > 0.0):
        o7 = CNUT6_001(s, D=W, W=MW, H=MH).translate((((MD + R1) + BH), (R1 + R2), 0.0))
        o8 = CNUT6_001(s, D=W, W=MW, H=MH).translate((((MD + R1) + BH), (-(R1 + R2)), 0.0))

    # 4. 布尔序列：先将 TORUS 裁成半环，再并入双腿、垫块和螺母
    o1.subtractFrom(o4); o4.erase()
    o1.uniteWith(o2); o2.erase()
    o1.uniteWith(o3); o3.erase()
    if o5:
        o5.subtractFrom(o6); o6.erase()
        o1.uniteWith(o5); o5.erase()
    if o7:
        o1.uniteWith(o7); o7.erase()
    if o8:
        o1.uniteWith(o8); o8.erase()

    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('BH', (0, 0, ((-D) / 2.0)), (0, 0, ((-BH) - (D / 2.0))))
```

---

### 典范 08：`CSGC004` —— 三块 60° 旋转 BOX 合成正六角柱的轻量化造型法
- **原厂路径**：`varmain/supportssub/csgcsub/csgc004.pyc`
- **工程亮点**：展示了不调用 `EXTRUSION` 而仅用 3 个相同尺寸的 `BOX`（分别旋转 `0°`, `+60°`, `-60°`）快速布尔合并生成**正六棱柱连接螺母**的经典几何算法（对边宽 `M1`，单边宽 `KWdt = M1 * tan(30°)`）。

#### 原厂反编译源码与逐行几何注释
```python
import math
import aqa.math
from varmain.primitiv import *
from varmain.supportssub.csgcsub.csgc003 import *
from varmain.var_basic import *

def CSGC004(s, D=116.0, L=30.0, W=4.0, K=0.0, H=95.0, M1=10.0, M2=0.0, ID='CSGC004', **kw):
    R1 = (D / 2.0)
    R2 = (R1 + W)
    H1 = (H - M2)
    if not (H1 < (R2 + W)) and (M2 == 0.0):
        H1 = (R2 + W)

    # 正六边形几何公式：对边距离为 M1 时，每个矩形面的边宽 KWdt = M1 * tan(30°)
    KWdt = (M1 * math.tan(aqa.math.asRadiants(30.0)))
    H2 = (H - H1)

    # 用三个绕 X 轴相差 60° 的 BOX 并集构造正六棱柱螺母套筒
    o1a = BOX(s, L=M1, W=KWdt, H=H2).translate((((0.0 - (H2 / 2.0)) - H1), 0.0, 0.0))
    o1b = BOX(s, L=M1, W=KWdt, H=H2).translate((((0.0 - (H2 / 2.0)) - H1), 0.0, 0.0)).rotateX(60.0)
    o1c = BOX(s, L=M1, W=KWdt, H=H2).translate((((0.0 - (H2 / 2.0)) - H1), 0.0, 0.0)).rotateX(-60.0)
    o2 = CSGC003(s, D=D, L=L, W=W, K=K, H=(H1 - R1)).rotateY(-90)

    o1a.uniteWith(o1b); o1b.erase()
    o1a.uniteWith(o1c); o1c.erase()
    o1a.rotateZ(180.0)
    o1a.uniteWith(o2); o2.erase()
    o1a.rotateY(90)

    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, (-H)))
```

---

### 典范 09：`CSGR005` —— 单/双滚轮可调双螺杆悬挂/支撑滚轮架
- **原厂路径**：`varmain/supportssub/csgrsub/csgr005.pyc`
- **工程亮点**：通过 `bPY = [-HB/2.0, HB/2.0]`（左右双螺杆）与 `bPZ = [0.0]` 或 `[0.0, 2*RC]`（`DOUBROLL=1` 双排滚轮）构建二维网格循环，自动装配弧形凹面滚轮 `CSGR000`、横向轮轴销 `o4`、轴承座套筒 `o2/o3`、全螺纹吊杆 `CBOLT_001` 与上下调节螺母 `CNUT6_001`。

#### 原厂反编译源码与逐行几何注释
```python
def CSGR005(s, D=116.0, BW=220.0, BH=0.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0,
            RTYPE=0, H=230.0, HD3=0.0, HS=10.0, HO=0.0, HB=0.0, DOUBROLL=0,
            test=False, doAllNuts=True, ID='CSGR005', **kw):
    # 调用滚轮几何计算辅助函数，获取滚轮凹弧半径与中心高 RC
    R1, R2, R3, RC, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if (BH <= 0.0): BH = R2
    if (HB <= 0.0): HB = (((BW - RL) / 2.0) + RL)
    rD = (RDI * 0.5) if (HD3 <= 0.0) else HD3
    nH = (round((rD * 750)) / 1000)   # 螺母厚度 ~ 0.75 * d
    rW = (round((rD * 1500)) / 1000)  # 螺母对边宽 ~ 1.50 * d
    tP = ((-RC) - nH)
    bL = ((H - RC) - BH)
    tP1 = (tP - ((H - RC) - nH))
    tP2 = (tP1 - HS)
    if (HO <= 0.0): HO = (nH * 1.5)
    rP = ((-RC) - BH)

    # 定义 Y 向（左右螺杆）与 Z 向（单/双滚轮轴向位置）坐标数组
    bPY = [(-(HB / 2.0)), (HB / 2.0)]
    bPZ = [0.0]
    if DOUBROLL:
        bPZ.append((RC * 2.0))
    bL += (HO + HS)
    bD = ((BW - HB) / 2.0)
    rE = ((BH + R3) + (nH * 1.5))
    extRod = False

    # 种子实体 o0
    o0 = CYLINDER(s, R=(rD * 0.01), H=(rD * 0.01), O=0.0).rotateX(180.0).translate((0.0, bPY[0], tP))
    for pY in bPY:
        for pZ in bPZ:
            if (pZ != bPZ[0]) and (not extRod):
                rE += pZ
                extRod = True
            o1 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(-90.0).translate((0.0, pY, (((-RC) + R3) + pZ)))
            o2 = CYLINDER(s, R=bD, H=(BH * 0.2), O=0.0).translate((0.0, pY, (((-RC) - BH) + pZ)))
            o3 = CYLINDER(s, R=(bD * 0.75), H=(BH + R3), O=0.0).translate((0.0, pY, (((-RC) - BH) + pZ)))
            rotAng = 90.0 if (pY != bPY[0]) else -90.0
            o4 = CYLINDER(s, R=(bD * 0.75), H=((HB - RL) / 2.0), O=0.0).rotateX(rotAng).translate((0.0, pY, ((-RC) + pZ)))
            for part in (o1, o2, o3, o4):
                o0.uniteWith(part); part.erase()
        o5 = CBOLT_001(s, D=rD, L=(bL + rE), W=rW, H=nH).rotateY(90.0).translate((0.0, pY, (rP + rE)))
        if doAllNuts:
            o6 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(-90.0).translate((0.0, pY, tP1))
            o0.uniteWith(o6); o6.erase()
        if not ((nH * 1.5) > HO):
            o7 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(90.0).translate((0.0, pY, tP2))
            o0.uniteWith(o7); o7.erase()
        o0.uniteWith(o5); o5.erase()

    # 并入单/双滚轮本体 CSGR000
    for pZ in bPZ:
        xtest = test if (pZ == bPZ[0]) else False
        o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=1, RTYPE=RTYPE, W=0.0, WD=0.0, test=xtest).translate((0.0, 0.0, pZ))
        o0.uniteWith(o1); o1.erase()

    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, (-H)))
```

---
