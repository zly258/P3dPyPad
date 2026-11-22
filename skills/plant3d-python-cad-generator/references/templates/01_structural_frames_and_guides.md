# AutoCAD Plant 3D 原厂典范源码母版 —— 类别一：型钢支吊架框架与多向导向架类（`CSGE001`, `CSGE002`, `CSGT001`, `CSGB012`）

> **所属分册**：`references/templates/01_structural_frames_and_guides.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别一：型钢支吊架框架与多向导向架类（`varmain/supportssub/`）

### 典范 01：`CSGE001` —— L型角钢横梁 + T型钢立柱 + U型螺栓管卡组合悬臂架
- **原厂路径**：`varmain/supportssub/csgesub/csge001.pyc`
- **工程用途**：管道下方立柱支撑总成，顶部采用 `CSGC000`（U型螺栓+弧形垫块）抱紧管道，中部横向设置 `CSTE_L` 角钢托梁，下部采用 `CSTE_T` T型钢立柱直达底板 `o4`。

#### 参数字典表
| 参数名 | 类型 | 默认值 | 物理含义与缺省推导规则 |
| :--- | :--- | :--- | :--- |
| `D` | `LENGTH` | `116.0` | 被支撑管道外径（Pipe OD） |
| `L` | `LENGTH` | `400.0` | 管中心至底板底面的总生根高度（绑定 `setLinearDimension('L', ...)`） |
| `LS`, `WS` | `LENGTH` | `30.0`, `0.0` | U型螺栓伸出长度 `LS` 与螺杆直径 `WS` |
| `BL`, `BW`, `BH` | `LENGTH` | `80.0`, `60.0`, `10.0` | 管卡下方鞍座垫块长、宽、高（管底至垫块底面距离为 `BH`） |
| `MW`, `MH` | `LENGTH` | `0.0`, `0.0` | U型螺栓六角螺母对边宽与厚度 |
| `WT`, `HT`, `TT` | `LENGTH` | `100.0`, `0.0`, `8.0` | T型钢立柱翼缘宽 `WT`、截面高 `HT`（缺省 `WT/2`）、板厚 `TT` |
| `WL`, `HL`, `TL`, `LL` | `LENGTH` | `0.0`, `0.0`, `0.0`, `200.0` | L型角钢宽 `WL`（缺省 `HT+TL`）、高 `HL`、厚 `TL`（缺省 `TT`）、长 `LL` |
| `SL`, `SW`, `ST` | `LENGTH` | `250.0`, `150.0`, `0.0` | 底部生根底板长 `SL`、宽 `SW`、厚 `ST`（缺省 `TT`） |

#### 局部坐标系推导
- **原点 `(0, 0, 0)`**：位于被支撑管道中心轴线上。
- **管道走向**：沿 X 轴（`s.setPoint((0, 0, 0), (-1, 0, 0))`）。
- **立柱生长方向**：沿 `-Z` 轴向下延伸至 `Z = -L`。
- **关键距离**：`R = D/2.0 + BH` 为管中心至鞍座垫块底面的距离；T型钢立柱净长 `LT = L - R`。

#### 原厂反编译源码与逐行几何注释
```python
from aqa.math import *
from varmain.divsub.cste_l import *
from varmain.divsub.cste_t import *
from varmain.primitiv import *
from varmain.supportssub.csgcsub.csgc000 import *
from varmain.var_basic import *

def CSGE001(s, D=116.0, L=400.0, LS=30.0, WS=0.0, BL=80.0, BW=60.0, BH=10.0,
            MW=0.0, MH=0.0, WT=100.0, HT=0.0, TT=8.0, WL=0.0, HL=0.0, TL=0.0,
            LL=200.0, SL=250.0, SW=150.0, ST=0.0, ID='CSGE001', **kw):
    # 1. 缺省参数自洽推导（防止 0 值传入导致建模退化）
    if (TL <= 0.0):
        TL = TT
    MD = TL  # 螺母安装偏移量等于角钢肢厚 TL
    if (SW <= 0.0):
        SW = SL
    if (ST <= 0.0):
        ST = TT
    if (HT <= 0.0):
        HT = (WT / 2.0)
    if (WL <= 0.0):
        WL = (HT + TL)
    if (HL <= 0.0):
        HL = WL

    # 2. 核心标高计算：R 为管中心到垫块底面距离，LT 为立柱高度
    R = ((D / 2.0) + BH)
    LT = (L - R)

    # 3. 实例化子部件：
    # o1: 顶部 U 型螺栓与垫块组件 CSGC000（自身已完成旋转，中心在原点）
    o1 = CSGC000(s, D=D, L=LS, W=WS, BL=BL, BW=BW, BH=BH, MW=MW, MH=MH, MD=MD)
    # o2: L型角钢横梁，初始沿 +Z 拉伸，绕 X 转 -90° 使其沿 Y 轴展布，再平移到 Z = -(R + HL/2)
    o2 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(-90.0).rotateZ(180).translate(((TL / 2.0), (LL / 2.0), (-(R + (HL / 2.0)))))
    # o3: T型钢立柱，绕 Y 轴翻转 180° 使其向 -Z 方向延伸，顶部位于 Z = -R
    o3 = CSTE_T(s, W=WT, H=HT, T=TT, L=LT).rotateY(180.0).rotateZ(90.0).translate((0.0, 0.0, (-R)))
    # o4: 底部生根钢板，注意原生 BOX(L=SL, H=SW, W=ST) 中 W 沿 Z 轴、H 沿 X 轴、L 沿 Y 轴！
    o4 = None
    if (SL > 0.0) and (SW > 0.0):
        o4 = BOX(s, L=SL, H=SW, W=ST).translate((0.0, 0.0, (-(L - (ST / 2.0)))))

    # 4. 种子体素（Seed Body Pattern）：因 o1/o2/o3 均为子脚本返回值，用极小 BOX o0 作为主实体锚点
    o0 = BOX(s, L=(TL * 0.01), H=(TL * 0.01), W=(TL * 0.01)).translate((0.0, 0.0, (-(R + (TL / 2.0)))))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    if o4:
        o0.uniteWith(o4)
        o4.erase()

    # 5. 端口与线性拉伸握点定义（沿 -Z 方向控制高度 L）
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, (-L)))
```

---

### 典范 02：`CSGE002` —— 带鞍座弧面裁切腹板的T型钢立柱角钢支架
- **原厂路径**：`varmain/supportssub/csgesub/csge002.pyc`
- **工程亮点**：在 `CSGE001` 基础上增加了直接托住管底的加强筋板 `o4`，并使用 `r4 = CYLINDER(s, R=D/2.0, ...)` 与 `o4.subtractFrom(r4)` 裁切出贴合管道外壁的马鞍弧面；同时展示**先在建模坐标系完成装配，最后统一调用 `o0.rotateY(90)` 旋转至目标方向**的经典技巧。

#### 新增参数说明
| 参数名 | 类型 | 默认值 | 物理含义 |
| :--- | :--- | :--- | :--- |
| `NO` | `LENGTH` | `10.0` | 鞍座筋板距角钢内壁的偏置距离 |
| `NL`, `NW`, `NT` | `LENGTH` | `50.0`, `30.0`, `0.0` | 鞍座弧形托板的长度 `NL`、超出管底宽度 `NW`、板厚 `NT`（缺省 `TT`） |

#### 原厂反编译源码与逐行几何注释
```python
def CSGE002(s, D=116.0, L=400.0, LS=30.0, WS=0.0, BL=80.0, BW=60.0, BH=10.0,
            MW=0.0, MH=0.0, WT=100.0, HT=0.0, TT=8.0, WL=0.0, HL=0.0, TL=0.0,
            LL=200.0, NO=10.0, NL=50.0, NW=30.0, NT=0.0, SL=250.0, SW=150.0,
            ST=0.0, ID='CSGE002', **kw):
    if (TL <= 0.0): TL = TT
    MD = TL
    if (SW <= 0.0): SW = SL
    if (ST <= 0.0): ST = TT
    if (NT <= 0.0): NT = TT
    if (NO < 0.0):  NO = 0.0
    if (HT <= 0.0): HT = (WT / 2.0)
    if (WL <= 0.0): WL = (HT + TL)
    if (HL <= 0.0): HL = WL

    R = ((D / 2.0) + BH)
    LT = ((L - (TL / 2.0)) - (HL / 2.0))
    TMP1 = (-((R + HL) - (HT / 2.0)))

    # 建模阶段：管道临时沿 Z 轴放置，待所有布尔运算完成后再统一 .rotateY(90)
    o1 = CSGC000(s, D=D, L=LS, W=WS, BL=BL, BW=BW, BH=BH, MW=MW, MH=MH, MD=MD).rotateY(-90).rotateZ(180.0)
    o2 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(90.0).rotateZ(180).translate(((-(R + (HL / 2.0))), (-(LL / 2.0)), (-(TL / 2.0))))
    o3 = CSTE_T(s, W=WT, H=HT, T=TT, L=LT).rotateY(180.0).rotateZ(90.0).translate((TMP1, 0.0, (LT - L)))

    # 构造贴合管外壁的弧形鞍座板 o4：用管道外径圆柱 r4 执行 subtractFrom
    o4 = None
    if (NL > 0.0) and (NW > 0.0):
        NW = (NW + (D / 2.0))
        o4 = BOX(s, L=NT, H=NW, W=NL).translate(((-(NW / 2.0)), 0.0, (((NL / 2.0) + NO) + ((WL - TL) / 2.0))))
        r4 = CYLINDER(s, R=(D / 2.0), H=((HL + NO) + NL), O=0.0)

    o5 = None
    if (SL > 0.0) and (SW > 0.0):
        o5 = BOX(s, L=SL, H=SW, W=ST).translate((TMP1, 0.0, (-(L - (ST / 2.0)))))

    o0 = BOX(s, L=(TL * 0.01), H=(TL * 0.01), W=(TL * 0.01)).translate(((-(R + (TL / 2.0))), 0.0, 0.0))
    o0.uniteWith(o1); o1.erase()
    o0.uniteWith(o2); o2.erase()
    o0.uniteWith(o3); o3.erase()
    if o4:
        o4.subtractFrom(r4)
        r4.erase()
        o0.uniteWith(o4)
        o4.erase()
    if o5:
        o0.uniteWith(o5)
        o5.erase()

    # 终局旋转：将整体绕 Y 轴旋转 90°，此时原 -Z 方向变为 -X 方向
    o0.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), ((-L), 0, 0))
```

---

### 典范 03：`CSGT001` —— 双吊杆门式横担梁框架（Trapeze Hanger）
- **原厂路径**：`varmain/supportssub/csgtsub/csgt001.pyc`
- **工程亮点**：
  1. **运行时几何内省**：调用 `CNUT6_001` 生成六角螺母后，通过 `MH = abs(o1.pointAt(1).y() - o1.pointAt(0).y())` 动态查询螺母实际高度，无需硬编码公式。
  2. **双螺母防松微旋**：下层锁紧螺母 `o6` 在 `o5` 基础上多执行一次 `.rotateY(15.0)`，真实还原工程中双螺母错位 15° 锁紧的视觉细节。
  3. **对称循环复用**：用 `for cnt in [1, 2]:` 循环生成左右两套吊杆、U型吊耳与螺母组件，分别平移 `xM = -L/2.0` 与 `+L/2.0` 后并入横担梁 `o0`。

#### 参数字典表
| 参数名 | 类型 | 默认值 | 物理含义 |
| :--- | :--- | :--- | :--- |
| `L` | `LENGTH` | `300.0` | 两根吊杆中心间距 |
| `W`, `K`, `O` | `LENGTH` | `50.0`, `25.0`, `0.0` | 横担梁宽度 `W`、高度 `K`、两端悬挑外伸长度 `O`（横梁总长 `L + 2*O`） |
| `H1`, `H2` | `LENGTH` | `200.0`, `0.0` | 左吊杆高度 `H1`（带拉伸握点）、右吊杆高度 `H2`（缺省等于 `H1`） |
| `HD3` | `LENGTH` | `0.0` | 吊杆螺杆直径（缺省 `W / 25.0`） |
| `HT4`, `HL4`, `HW4`, `HH4` | `LENGTH` | `0.0` | 顶部 U 型生根吊耳板厚 `HT4`、跨度 `HL4`、宽度 `HW4`、耳高 `HH4` |

#### 原厂反编译源码与逐行几何注释
```python
def CSGT001(s, L=300.0, W=50.0, K=25.0, O=0.0, H1=200.0, H2=0.0, HD3=0.0,
            HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGT001', **kw):
    if (K <= 0.0):   K = W
    if (O <= 0.0):   O = (W / 2.0)
    if (H2 <= 0.0):  H2 = H1
    if (HD3 <= 0.0): HD3 = (W / 25.0)
    if (HT4 <= 0.0): HT4 = (HD3 * 0.25)
    if (HL4 <= 0.0): HL4 = (HD3 + (HT4 * 3.0))
    if (HW4 <= 0.0): HW4 = HD3
    if (HH4 <= 0.0): HH4 = HD3

    # 横担主梁 o0：H=(L + 2*O) 沿 X 轴，L=K 沿 Y 轴，W=W 沿 Z 轴
    o0 = BOX(s, L=K, W=W, H=(L + (O * 2.0))).translate((0.0, (-(K / 2.0)), 0.0))

    # 左右双侧吊杆总成循环构造
    for cnt in [1, 2]:
        H = H1 if (cnt == 1) else H2
        # o1: 横梁上表面螺母；利用 pointAt(1) 与 pointAt(0) 动态测出螺母厚度 MH
        o1 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(90.0).rotateX(90.0).translate((0.0, 0.0, 0.0))
        MH = abs((o1.pointAt(1).y() - o1.pointAt(0).y()))
        # o2: 顶部吊耳下方调节螺母
        o2 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, ((H - HD3) - HH4), 0.0))
        # o5, o6: 横梁下表面双锁紧螺母（o6 额外旋转 15° 体现错牙效果）
        o5 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, (-K), 0.0))
        o6 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).rotateY(15.0).translate((0.0, (-(K + MH)), 0.0))

        # o3: 全螺纹吊杆本体
        hExt = ((MH * 2.5) + K)
        cL3 = H
        o3 = CBOLT_001(s, D=HD3, L=(cL3 + hExt)).rotateZ(90.0).translate((0.0, (-hExt), 0.0))

        # o4a, o4b, o4c, o4d: 顶部 U 型生根夹耳与销轴
        xL1 = (HL4 + (HT4 * 2.0))
        xH1 = ((H - ((HH4 - HT4) / 2.0)) - HT4)
        o4a = BOX(s, L=HH4, W=HW4, H=HT4).translate((((HL4 / 2.0) - (HT4 / 2.0)), (H - (HH4 / 2.0)), 0.0))
        o4b = BOX(s, L=HH4, W=HW4, H=HT4).translate(((-((HL4 / 2.0) - (HT4 / 2.0))), (H - (HH4 / 2.0)), 0.0))
        o4c = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, (H - (HT4 / 2.0)), 0.0))
        o4d = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate(((xL1 / 2.0), xH1, 0.0))

        # 将单侧所有零件合并到 o4d
        for part in (o4c, o4b, o4a, o3, o2, o1, o5, o6):
            o4d.uniteWith(part)
            part.erase()

        # 左右平移 ±L/2.0 并入横担梁 o0
        xM = (-(L / 2.0)) if (cnt == 1) else (+(L / 2.0))
        o4d.translate((xM, 0.0, 0.0))
        o0.uniteWith(o4d)
        o4d.erase()

    o0.rotateZ(90.0).rotateY(90.0)
    s.setLinearDimension('H1', (0, 0, 0), (0, 0, H1))
```

---

### 典范 04：`CSGB012` —— 四向位掩码控制十字翼缘抗剪导向滑托
- **原厂路径**：`varmain/supportssub/csgbsub/csgb012.pyc`
- **工程亮点**：使用整数参数 `TI` 的二进制位掩码（`TI & 1`, `TI & 2`, `TI & 4`, `TI & 8`）控制管道四周 `-X / +X / +Y / -Y` 四个方向T型滑托翼板的独立显隐（用于立管四向导向架或保温管多肋滑托）。

#### 原厂反编译源码与逐行几何注释
```python
def CSGB012(s, D=116.0, L=30.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0,
            SH=150.0, TI=0, CS=0, ID='CSGB012', **kw):
    if (K <= 0.0):  K = (D + (L * 2.0))
    if (SW <= 0.0): SW = D
    R1 = (D / 2.0)
    R2 = (R1 + W)
    R3 = (R1 + (W / 2.0))
    LS = (SL - L)
    HS = (SH - R3)
    if (ST <= 0.0): ST = W

    # 1. 前后两道抱箍 CSGC002（绕 Z 轴旋转 -45° 避开正交十字腹板！）
    o9 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).rotateZ(-45.0)
    o0 = None
    if not (CS > 0):
        if (CS == -2):
            o0 = None
        else:
            o9.translate((0.0, 0.0, (-(LS / 2.0))))
            o0 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).rotateZ(-45.0).translate((0.0, 0.0, (LS / 2.0)))

    # 2. 位掩码 TI 控制四个正交方向的 T 型翼板（每个方向由腹板 + 翼缘板组成）
    o1 = o2 = o3 = o4 = o5 = o6 = o7 = o8 = None
    if (TI > 0):
        if not (TI & 1):  # 方向 1 (180°)
            o1 = BOX(s, L=ST, W=SL, H=HS).translate((((HS / 2.0) + R3), 0, 0)).rotateZ(90.0).rotateZ(90.0)
            o2 = BOX(s, L=SW, W=SL, H=ST).translate(((SH - (ST / 2.0)), 0, 0)).rotateZ(90.0).rotateZ(90.0)
        if not (TI & 2):  # 方向 2 (0°)
            o3 = BOX(s, L=ST, W=SL, H=HS).translate((((HS / 2.0) + R3), 0, 0)).rotateZ(90.0).rotateZ(-90.0)
            o4 = BOX(s, L=SW, W=SL, H=ST).translate(((SH - (ST / 2.0)), 0, 0)).rotateZ(90.0).rotateZ(-90.0)
        if not (TI & 4):  # 方向 3 (+90°)
            o5 = BOX(s, L=ST, W=SL, H=HS).translate((((HS / 2.0) + R3), 0, 0)).rotateZ(90.0)
            o6 = BOX(s, L=SW, W=SL, H=ST).translate(((SH - (ST / 2.0)), 0, 0)).rotateZ(90.0)
        if not (TI & 8):  # 方向 4 (-90°)
            o7 = BOX(s, L=ST, W=SL, H=HS).translate((((HS / 2.0) + R3), 0, 0)).rotateZ(90.0).rotateZ(180.0)
            o8 = BOX(s, L=SW, W=SL, H=ST).translate(((SH - (ST / 2.0)), 0, 0)).rotateZ(90.0).rotateZ(180.0)

    # 3. 若 o1 被禁用（None），则创建一个微小的隐藏圆柱作为布尔并集的宿主实体
    if o1:
        o1.uniteWith(o2); o2.erase()
    else:
        o1 = CYLINDER(s, R=(W * 0.1), H=(W * 0.1), O=0.0).rotateX(90.0).translate((((K - L) / 2.0), (-(W / 2.0)), (-(LS / 2.0)))).rotateZ(45.0)

    for pair in ((o3, o4), (o5, o6), (o7, o8)):
        if pair[0]:
            o1.uniteWith(pair[0]); pair[0].erase()
            o1.uniteWith(pair[1]); pair[1].erase()
    o1.uniteWith(o9); o9.erase()
    if o0:
        o1.uniteWith(o0); o0.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('SH', (0, 0, 0), ((-SH), 0, 0))
```

---
