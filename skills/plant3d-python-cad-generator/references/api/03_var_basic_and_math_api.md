# AutoCAD Plant 3D 原厂公共造型函数库与可复用组件参考手册 (`02_var_basic_and_math_library.md`)

> **数据源基准**：
> 反编译自 `variants.zip` 中的 `varmain/var_basic.pyc`、`varmain/var_util.pyc`、`varmain/divsub/*.pyc`、`varmain/eqfactory.pyc`、`aqa/math/__init__.pyc`、`aqa/math/olet.pyc`、`aqa/math/stubin.pyc` 以及全部 22 个原厂组件子目录。

---

## 一、 `varmain/var_basic.py` 原厂公共造型函数库完整解析

`varmain/var_basic.py` 是 Plant 3D 最核心的高频公共几何造型库，被超过 95% 的原厂脚本通过 `from varmain.var_basic import *` 导入。

### 1.1 `varmain/var_basic.py` 函数总览表

| 函数名称 | 完整参数签名 | 核心功能说明 | 内部实现原理摘要 |
| :--- | :--- | :--- | :--- |
| **`CORNERBOX`** | `CORNERBOX(s, L=300.0, W=200.0, H=100.0, ID='CORNERBOX', **kw)` | 角点位于 `(0,0,0)`、分别沿 `+X, +Y, +Z` 生长的规整长方体 | 调用 `BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate((L/2, W/2, H/2))` |
| **`SPHERE`** | `SPHERE(s, R=300.0, ID='SPHERE', **kw)` | 球心在 `(0,0,0)` 的完整实心球体 | 将两个 `HALFSPHERE(s, R=R)`（其中一个 `.rotateY(180)`）执行 `.uniteWith()` 合并 |
| **`CON_OF_MULT`** | `CON_OF_MULT(Val)` | 承插母端外径放大系数计算 | 返回 `Val * 1.1`（即标准外径的 1.1 倍） |
| **`CON_OF_DIV`** | `CON_OF_DIV(Val)` | 默认内径估算函数（当壁厚 `OF=-1` 时使用） | 返回 `(Val / CON_OF_MULT(100.0)) * 100.0`，即 `Val / 1.1`（约等于 `0.90909 * Val`） |
| **`CON_OM_MULT`** | `CON_OM_MULT(Val)` | 承插公端系数计算 | 内部直接调用 `CON_OF_DIV(Val)` |
| **`CON_OM_DIV`** | `CON_OM_DIV(Val)` | 承插公端逆向推导 | 返回 `(Val / CON_OM_MULT(100.0)) * 100.0`，即 `Val * 1.1` |
| **`getThickness`** | `getThickness(D, OF=0.0, Ever=None, mustCalc=False)` | 管件壁厚统一计算与规整函数 | 若全局忽略壁厚且 `not mustCalc` 则返回 `0.0`；若 `OF < 0`（如 `-1.0`）则自动按 `(D - D/1.1)/2` 推导壁厚 |
| **`getInsideDiameter`** | `getInsideDiameter(D, OF=0.0, Ever=None, mustCalc=False)` | 管件内径（流道直径）统一计算函数 | 调用 `getThickness` 计算壁厚后返回 `D - 2 * OF`；若内径 `<= 0` 则回退保护 |
| **`CON_OF`** | `CON_OF(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID='CON_OF', **kw)` | 承插母口（Socket Female）连接头构造 | 沿 `+X` 轴生成外径 `D2`、内孔半径 `R1=D1/2`、长 `L+expand` 的空心套筒 |
| **`CON_OM`** | `CON_OM(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID='CON_OM', **kw)` | 承插公口/插口（Spigot Male）连接头构造 | 用 `CONE` 构造外锥段并减去内圆柱通孔 `CYLINDER` |
| **`CON_MJ`** | `CON_MJ(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID='CON_MJ', **kw)` | 机械接口（Mechanical Joint）承口环构造 | 双层阶梯空心圆柱 `CYLINDER` 布尔并集 |
| **`CON_PL`** | `CON_PL(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID='CON_PL', **kw)` | 平端/光管端（Plain End）管段构造 | 外圆柱 `R1=D1/2` 减去内孔圆柱 `R2=D2/2` |
| **`ARC3D2_`** | `ARC3D2_(s, D=100.0, D2=0.0, R=300.0, A=90.0, ID='ARC3D2_', **kw)` | 带自动双端口绑定的变径弯头包装器 | 调用 `ARC3D2` 并利用 `pointAt(0/1)` 和 `directionAt(0/1)` 自动设置 `s.setPoint` |
| **`CON_Q__Calc`** | `CON_Q__Calc(CW=40.0, CH=0.0, CC=0.0, O=20.0)` | 羊角快速接头（Claw Coupling）34项几何尺寸链解算器 | 计算卡爪高度、斜角 `atan`、径向偏移等 34 个中间尺寸列表 `vC[0..33]` |
| **`CON_Q_`** / **`CON_Q__Sub`** | `CON_Q_(s, CW=40.0, CH=0.0, CC=0.0, O=20.0, ID='CON_Q_', **kw)` | 羊角快装接头（带对称双卡爪）三维实体构造 | 组合 `CYLINDER`、`CORNERBOX` 与 `CON_Q__Sub` 对称旋转 `180°` |
| **`CON_HM`** | `CON_HM(s, D=25.0, H=38.5, O2=0.0, OF=-1.0, ID='CON_HM', **kw)` | 宝塔软管接头（Hose Mender / Serrated Nipple） | 循环 `mCnt = round(H / (D * 0.3333) + 0.5)` 次，沿轴向叠加倒刺 `CONE` 并挖穿内孔 |
| **`CSGCutOut`** | `CSGCutOut(s, obj, D, kwdict)` | **耳轴/假管支座（Trunnion/Dummy Leg）与主管/弯头外表面马鞍口裁切算法** | 解析 `kwdict` 中的主管外径 `OD`、弯曲半径 `OR`、安装方位 `OO` (`'B'`, `'b'`, `'f1'`, `'f2'`, `'F'`, `'C'`)，生成 `ARC3D` 或 `CYLINDER` 刀具对支座 `obj` 执行 `.subtractFrom()` |
| **`ARC3DS2`** | `ARC3DS2(s, D=114.3, D2=88.9, R=175.0, A=90.0, S=4, ID='CPBS', **kw)` | **变径虾米腰分段弯头（Mitered Reducing Elbow）放样算法** | 当 `D == D2` 时直接调用 `ARC3DS`；当 `D != D2` 时，按节数 `S` 切分角度与递减半径，在空间布置 `ELLIPSE` 截面并逐段调用 `LOFT(s, e1, e2)` 放样拼接 |

### 1.2 `varmain/var_basic.py` 完整反编译源码（含逐段原理解析）

```python
from sys import PnP3dACPAdapterIgnoreWallThickness
from aqa.math import *
from varmain.primitiv import *

# 1. 规整角点长方体：消除原生 BOX 质心与轴向错位问题
def CORNERBOX(s, L=300.0, W=200.0, H=100.0, ID='CORNERBOX', **kw):
    # 旋转后 L 沿 +X [0, L]，W 沿 +Y [0, W]，H 沿 +Z [0, H]
    BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate(((L / 2.0), (W / 2.0), (H / 2.0)))
activate(CORNERBOX)

# 2. 完整球体：由上下两个半球拼合而成
def SPHERE(s, R=300.0, ID='SPHERE', **kw):
    o1 = HALFSPHERE(s, R=R)
    o2 = HALFSPHERE(s, R=R).rotateY(180)
    o1.uniteWith(o2)
    o2.erase()
activate(SPHERE)

# 3. 壁厚与内径标准推算函数族
def CON_OF_MULT(Val):
    return Val * 1.1

def CON_OF_DIV(Val):
    return (Val / CON_OF_MULT(100.0)) * 100.0  # 即 Val / 1.1

def CON_OM_MULT(Val):
    return CON_OF_DIV(Val)

def CON_OM_DIV(Val):
    return (Val / CON_OM_MULT(100.0)) * 100.0

def getThickness(D, OF=0.0, Ever=None, mustCalc=False):
    if PnP3dACPAdapterIgnoreWallThickness:
        if not mustCalc:
            Ever = None
            OF = 0.0
    if Ever:
        if OF != 0.0:
            if OF < 0.0:
                # 当 OF=-1（默认自动壁厚）时，壁厚 = (D - D/1.1) / 2 ≈ 0.04545 * D
                OF = (D - CON_OF_DIV(D)) / 2.0
    if OF > 0.0:
        retVal = OF
    else:
        retVal = 0.0
    return retVal

def getInsideDiameter(D, OF=0.0, Ever=None, mustCalc=False):
    OF = getThickness(D, OF, Ever, mustCalc)
    retVal = 0.0
    if OF > 0.0:
        retVal = D - (OF * 2.0)
        if retVal <= 0.0:
            OF = getThickness(D, -1.0, Ever, mustCalc)
            retVal = D - (OF * 2.0)
        else:
            retVal = 0.0
    return retVal

# 4. 四种标准管端接口造型（OF承口 / OM插口 / MJ机械接口 / PL平端）
def CON_OF(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID='CON_OF', **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if D2 <= 0.0 or D2 < D1:
        D2 = D1 + (sF * 2.0)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    expand = 0.0 if NOEXT else sF
    if OF <= 0.0:
        R1 = 0.0
    o0 = CYLINDER(s, R=R2, H=(L + expand), O=R1).rotateY(90).translate(((-expand), 0.0, 0.0))
    return o0
activate(CON_OF)

def CON_OM(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID='CON_OM', **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    if D2 <= 0.0 or D2 > D1:
        D2 = getInsideDiameter(D=D1, OF=OF, Ever=1, mustCalc=True)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    o0 = CONE(s, R1=R1, R2=R2, H=L, E=0.0).rotateY(90)
    if OF > 0.0:
        o1 = CYLINDER(s, R=R2, H=L, O=0.0).rotateY(90)
        o0.subtractFrom(o1)
        o1.erase()
    return o0
activate(CON_OM)

def CON_MJ(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID='CON_MJ', **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if D2 <= 0.0 or D2 < D1:
        D2 = D1 + (sF * 2.0)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    R3 = R2 + (R2 - R1)
    expand = 0.0 if NOEXT else sF
    if OF <= 0.0:
        R1 = 0.0
    o0 = CYLINDER(s, R=R2, H=(L + expand), O=R1).rotateY(90).translate(((-expand), 0.0, 0.0))
    o1 = CYLINDER(s, R=R3, H=sF, O=R2).rotateY(90).translate(((L - sF), 0.0, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    return o0
activate(CON_MJ)

def CON_PL(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID='CON_PL', **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    if D2 <= 0.0 or D2 > D1:
        D2 = getInsideDiameter(D=D1, OF=OF, Ever=1, mustCalc=True)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    o0 = CYLINDER(s, R=R1, H=L, O=0.0).rotateY(90)
    if OF > 0.0:
        o1 = CYLINDER(s, R=R2, H=L, O=0.0).rotateY(90)
        o0.subtractFrom(o1)
        o1.erase()
    return o0
activate(CON_PL)

# 5. 支管座/耳轴与母管（直管或弯头）正交及偏心马鞍口通用裁切函数
def CSGCutOut(s, obj, D, kwdict):
    OD = float(kwdict.get('OD', 0.0))
    if not OD:
        return None
    r = OD / 2.0
    OR = float(kwdict.get('OR', 0.0))
    OO = kwdict.get('OO', None)
    if OR > 0:
        # 母管为弯头（弯曲半径 OR > 0），根据安装方位 OO 构造 ARC3D 刀具
        if OO == 'B':
            offZ = OR
            offX = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((offX, 0, -offZ))
        elif OO == 'b':
            R = OR + r
            Q = (OR - r) + D
            offZ = OR - sqrt((R * R) - (Q * Q))
            offX = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((-offX, 0, -offZ))
        elif OO == 'f1':
            offZ = OR
            offY = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, offY, -offZ))
        elif OO == 'f2':
            offZ = OR
            offY = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, -offY, -offZ))
        elif OO == 'F':
            oh = BOX(s, L=OR, W=OD, H=OR)
        else:
            offZ = OR - sqrt(max((OR * (OD - D)) + (((OD * OD) - (D * D)) / 4.0), 0.0))
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, 0, -offZ))
    else:
        # 母管为直管（OR == 0），构造横向圆柱刀具裁切鞍座弧面
        oh = CYLINDER(s, R=r, H=(4.0 * D), O=0.0).rotateY(90.0).translate(((-2.0 * D), 0, 0))
        if OD > D:
            if OO == 'B':
                oh.translate((0, (-(OD - D)) / 2.0, 0))
            if OO == 'C':
                oh.translate((0, 0, sqrt((OD * OD) - (D * D)) / 2.0))
    obj.subtractFrom(oh)
    oh.erase()
```

---

## 二、 原厂标准型钢与紧固件造型库（`varmain/divsub/`）

在设计支吊架（`supportssub`）与设备支座时，原厂并非每次手写 `BOX` 拼凑型钢，而是直接调用 `varmain/divsub/` 下预置的 8 种标准型钢截面拉伸函数与 4 种紧固件函数：

### 2.1 标准型钢截面库（`cste_*.py`，默认沿 `+Z` 轴从 `0` 拉伸至 `L`）

| 函数名 | 所属模块 | 完整参数签名 | 截面类型与参数物理意义 |
| :--- | :--- | :--- | :--- |
| **`CSTE_H`** | `varmain.divsub.cste_h` | `CSTE_H(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_H', **kw)` | **H型钢 / 工字钢**：`W` 翼缘宽（沿 X），`H` 截面高（沿 Y，`[-H/2, H/2]`），`T` 翼缘与腹板厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_U`** | `varmain.divsub.cste_u` | `CSTE_U(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_U', **kw)` | **U型槽钢（Channel）**：`W` 槽高（沿 X，`[-W/2, W/2]`），`H` 腿宽（沿 Y，`[-H/2, H/2]`），`T` 壁厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_C`** | `varmain.divsub.cste_c` | `CSTE_C(s, W=70.0, H=50.0, B=20.0, T=8.0, L=-1.0, ID='CSTE_C', **kw)` | **C型卷边槽钢**：`W` 槽高，`H` 腿宽，`B` 卷边宽，`T` 壁厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_L`** | `varmain.divsub.cste_l` | `CSTE_L(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_L', **kw)` | **L型不等边/等边角钢**：`W` 肢1宽，`H` 肢2宽（`H<=0` 时等于 `W`），`T` 肢厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_T`** | `varmain.divsub.cste_t` | `CSTE_T(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_T', **kw)` | **T型钢**：`W` 翼缘宽，`H` 腹板高（`H<=0` 时取 `W/2`），`T` 板厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_O`** | `varmain.divsub.cste_o` | `CSTE_O(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_O', **kw)` | **方管 / 矩形空心钢（RHS/SHS）**：`W` 高，`H` 宽，`T` 壁厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_R`** | `varmain.divsub.cste_r` | `CSTE_R(s, D=114.3, L=100.0, OF=-1.0, ID='CSTE_R', **kw)` | **圆管型材（CHS）**：`D` 外径，`OF` 壁厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_F`** | `varmain.divsub.cste_f` | `CSTE_F(s, W=70.0, T=8.0, L=-1.0, ID='CSTE_F', **kw)` | **扁钢（Flat Bar）**：`W` 扁钢宽，`T` 扁钢厚，`L` 沿 `+Z` 拉伸长度 |
| **`CSTE_Z`** | `varmain.divsub.cste_z` | `CSTE_Z(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID='CSTE_Z', **kw)` | **Z型钢**：`W` 总宽，`H` 腹板高，`T` 壁厚，`L` 沿 `+Z` 拉伸长度 |

### 2.2 标准紧固件与法兰附件库（`varmain/divsub/`）

| 函数名 | 所属模块 | 完整参数签名 | 功能与内部构造原理 |
| :--- | :--- | :--- | :--- |
| **`NUT_BOLT_HEAD_6_001`** | `varmain.divsub.divutil` | `NUT_BOLT_HEAD_6_001(s, W=12.0, H=6.0, **kw)` | **带球面交集倒角的标准六角螺母/螺栓头毛坯**：用 3 个互成 `60°` 的 `BOX` 并集生成正六棱柱，再与外接 `SPHERE` 求交集（`.intersectWith()`）生成逼真的六角倒角！ |
| **`CNUT6_001`** | `varmain.divsub.cnut6_001` | `CNUT6_001(s, D=8.0, W=0.0, H=0.0, ID='NUT', **kw)` | **带内孔倒角的标准六角螺母**：默认 `H = 0.75 * D`、`W = 1.5 * D`（对边宽），沿 `+X` 轴 `[0, H]`，两端自带端口点 `pointAt(0)` `(0,0,0)` 与 `pointAt(1)` `(H,0,0)` |
| **`CBOLT6_001`** | `varmain.divsub.cbolt6_001` | `CBOLT6_001(s, D=8.0, L=30.0, W=0.0, H=0.0, P=0, **kw)` | **六角头螺栓**：由 `NUT_BOLT_HEAD_6_001` + 螺杆 `CYLINDER` + 末端倒角 `CONE` 组成，沿 `+X` 轴分布 |
| **`CBOLT_001`** | `varmain.divsub.cbolt_001` | `CBOLT_001(s, D=8.0, L=30.0, **kw)` | **双端倒角全螺纹螺柱/吊杆（Stud / Threaded Rod）**：沿 `+X` 轴 `[0, L]`，两端带 `0.1*R` 锥形倒角 |

---

## 三、 `aqa.math` 数学库完整解析

`aqa/math/__init__.py` 导入了底层 C++ 数学绑定 `pybasmath` 与 Python 标准库 `math`：

### 3.1 `aqa/math/__init__.py` 原厂反编译源码
```python
from pybasmath import *
from math import *

def asDegrees(rad):
    return (180.0 * rad) / mcPi

def asRadiants(deg):
    return (mcPi * deg) / 180.0

def areEqual(a, b, tol=1e-10):
    d = fabs(a - b)
    return (d == tol) or (d < tol)
```

### 3.2 `aqa.math` 导出符号全表

| 符号分类 | 函数 / 类 / 常量名 | 参数与返回值 | 关键说明与防错注意 |
| :--- | :--- | :--- | :--- |
| **圆周率常量** | `pi`, `mcPi` | `3.141592653589793` (`float`) | `pi` 来自标准库 `math`，`mcPi` 来自 C++ `pybasmath` |
| **角度转弧度** | **`asRadiants(deg)`** | 输入角度 `deg`，返回弧度 `rad` | **注意原厂拼写含字母 `t`（`asRadiants` 而非 `asRadians`）**！在自定义脚本中也可直接使用 `math.radians(deg)` |
| **弧度转角度** | **`asDegrees(rad)`** | 输入弧度 `rad`，返回角度 `deg` | 等价于 `math.degrees(rad)` |
| **浮点容差相等** | **`areEqual(a, b, tol=1e-10)`** | 返回 `bool` | 判断 `|a - b| <= tol`，用于判断弯头角度 `areEqual(A, 90.0)` 或管径相等 `areEqual(D, D2)` |
| **三角与反三角** | `sin(r)`, `cos(r)`, `tan(r)`, `asin(x)`, `acos(x)`, `atan(x)`, `atan2(y, x)` | 输入输出均为**弧度（Radians）** | 调用前必须将角度参数通过 `asRadiants(A)` 或 `radians(A)` 转为弧度 |
| **幂与根号** | `sqrt(x)`, `pow(x, y)`, `fabs(x)` | 返回 `float` | 在计算马鞍口弦高 $\sqrt{R^2 - r^2}$ 时，务必用 `max(..., 0.0)` 防止负数开方触发 `ValueError: math domain error` |
| **三维点类** | **`mPoint(x, y, z)`** | 方法：`.x()`, `.y()`, `.z()` | C++ `pybasmath` 导出的三维点对象，可直接传给 `.translate(pt)` 和 `s.setPoint(pt, vec)` |
| **三维向量类** | **`mVector(vx, vy, vz)`** | 方法：`.x()`, `.y()`, `.z()`, `.theta()` | C++ `pybasmath` 导出的三维向量对象，`.theta()` 返回向量在 XY 平面上的方位角（弧度） |
| **齐次变换矩阵** | **`mTransform()`** | 方法：`.translate((x,y,z))`, `.rotateX(rad)`, `.rotateY(rad)`, `.rotateZ(rad)` | 支持 `mTransform * mPoint` 和 `mTransform * mVector` 运算，以及 `obj.setTransformationMatrix(m)` |
| **支管台插入点偏移** | `aqa.math.olet.calcInsertionPoint`<br>`aqa.math.stubin.calcInsertionPoint` | `(elem, pick, ip, t, D, R, bpelem, bppick)` | Plant 3D 插入支管台（Olet）或直管接管嘴（Stub-in）时自动计算主管表面马鞍口交点偏移向量：$v_x = \sqrt{R(D-e) + \frac{D^2 - e^2}{4}} - R$ |

---

## 四、 直接复用 vs. 独立脚本内联（Inline）改写指南

### 4.1 方式一：直接导入复用原厂模块（最快、代码最精简）
由于 Plant 3D 运行时自动挂载了 `variants.zip`，任何自定义脚本都可以直接 `import` 原厂的公共函数和子组件（如型钢、管卡、螺母、手轮）：

```python
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *
from varmain.var_basic import *
from varmain.divsub.cste_h import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csgcsub.csgc002 import *

@activate(Group="Support", TooltipShort="H-Beam Cantilever Support", Ports="1", LengthUnit="mm")
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="Pipe OD")
@param(H=LENGTH, TooltipShort="Support Height", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="Beam Width")
def CUSTOM_HBEAM_SUPP(s, D=114.3, H=500.0, W=100.0, **kw):
    R1 = D / 2.0
    # 1. 直接复用原厂 CSGC002 生成管卡抱箍
    oClamp = CSGC002(s, D=D, L=40.0, W=6.0, K=D + 80.0).rotateY(-90)
    # 2. 直接复用原厂 CSTE_H 生成竖向 H 型钢立柱
    col_H = max(H - R1 - 6.0, 50.0)
    oCol = CSTE_H(s, W=W, H=W, T=8.0, L=col_H).rotateY(90).translate((R1 + 6.0, 0.0, 0.0))
    # 3. 种子体素合并
    o0 = CYLINDER(s, R=0.1, H=0.1, O=0.0)
    o0.uniteWith(oClamp)
    oClamp.erase()
    o0.uniteWith(oCol)
    oCol.erase()
    o0.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, -H))
```

### 4.2 方式二：自包含内联（Inline）改写（零外部子模块依赖）
在需要将单个 `.py` 脚本分发给不同版本 Plant 3D 或需要在纯原生体素下微调细节（如切角、开孔）时，可将原厂子函数内联为脚本内的辅助函数（**注意：辅助函数不要加 `@activate` 装饰器，且不要在内部调用 `s.setPoint`！**）：

```python
# 内联改写范例：将 CORNERBOX、H型钢与六角螺母内联为纯原生体素辅助函数
def _inline_cornerbox(s, L, W, H):
    return BOX(s, L=L, W=W, H=H).rotateX(-90.0).rotateY(-90.0).translate((L / 2.0, W / 2.0, H / 2.0))

def _inline_hbeam(s, W, H, T, L):
    # 沿 +Z 轴 [0, L] 拉伸的 H 型钢，截面中心在 (0, 0)
    o1 = BOX(s, L=T, W=L, H=W).translate((0.0, (T / 2.0) - (H / 2.0), L / 2.0))
    o2 = BOX(s, L=H, W=L, H=T).translate((0.0, 0.0, L / 2.0))
    o3 = BOX(s, L=T, W=L, H=W).translate((0.0, (H / 2.0) - (T / 2.0), L / 2.0))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    return o1

def _inline_hex_nut(s, D, W=0.0, H=0.0):
    if H <= 0.0:
        H = round(D * 750.0) / 1000.0
    if W <= 0.0:
        W = round(D * 1500.0) / 1000.0
    aWidth = (W * sqrt(3.0)) / 3.0
    o1 = BOX(s, L=W, W=H, H=aWidth)
    o2 = BOX(s, L=W, W=H, H=aWidth).rotateZ(60.0)
    o3 = BOX(s, L=W, W=H, H=aWidth).rotateZ(-60.0)
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o1.rotateY(90.0).translate((H / 2.0, 0.0, 0.0))
    hole = CYLINDER(s, R=D / 2.0, H=H, O=0.0).rotateY(90.0)
    o1.subtractFrom(hole)
    hole.erase()
    return o1
```

---
