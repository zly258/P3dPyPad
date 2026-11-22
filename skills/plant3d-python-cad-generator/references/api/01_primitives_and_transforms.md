# AutoCAD Plant 3D 底层体素与空间变换权威字典 (`01_native_primitives_and_csg.md`)

> **数据源基准**：
> 1. 官方技术白皮书：`Annex B: Creating Custom Component Scripts in Plant 3D` (PD4214-L, 47页) 与 `Scripting Components for AutoCAD Plant 3D` (PD1746, 14页)
> 2. 原厂反编译字节码库：`variants.zip` -> `varmain/primitiv.pyc`（底层 `from pyvariant import *` C++/Python ACIS 几何内核绑定）、`varmain/var_basic.pyc`、`varmain/eqfactory.pyc` 及 40,763 个内置参数化组件脚本统计分析。

---

## 一、 架构总览与全局常量

在 AutoCAD Plant 3D 中，参数化脚本由内嵌的 Python 2.7/3.x 解释器通过 `PnP3dACPAdapter.arx` 执行。所有底层三维几何体素均由 C++ 扩展模块 `pyvariant` 导出，并在 `varmain/primitiv.py` 中通过 `from pyvariant import *` 暴露给上层脚本。

### 1.1 `varmain/primitiv.py` 原厂反编译源码
```python
from pyvariant import *

def PIPE(s, D=114.3, L=100.0, ID='PIPE', **kw):
    CYLINDER(s, R=(D / 2.0), H=L).rotateY(90.0)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))

activate(PIPE)

def linkFuncToDbman(func):
    pass

defaultPipeLength = 100.0
defaultNozzleLength = 100.0
defaultTolerance = 0.001
```

### 1.2 全局内置常量与系统标志
| 常量 / 变量名 | 所属模块 | 默认值 / 类型 | 物理含义与工程用途 |
| :--- | :--- | :--- | :--- |
| `defaultPipeLength` | `varmain.primitiv` | `100.0` (`float`) | 默认管段/型钢拉伸长度（当 `L <= 0` 时回退使用，见 `CSTE_*` 型钢库） |
| `defaultNozzleLength` | `varmain.primitiv` | `100.0` (`float`) | 默认设备管嘴长度 |
| `defaultTolerance` | `varmain.primitiv` | `0.001` (`float`) | 几何建模容差与种子体素（Seed Body）最小尺寸基准 |
| `PnP3dACPAdapterIgnoreWallThickness` | `sys` / `varmain.var_basic` | `bool` | Plant 3D 内核壁厚忽略标志；为 `True` 时不执行内部流道挖孔布尔差集以提升大模型渲染性能 |

---

## 二、 全部 C++ 原生几何体素与扩展体素权威字典

在 `variants.zip` 全部 5,698 个核心脚本（不含阀门端口组合派生文件）中，各体素的调用频次统计如下：
`CYLINDER` (3,354次)、`CONE` (336次)、`ARC3D2` (221次)、`BOX` (168次)、`SPHERE` (104次)、`PYRAMID` (28次)、`TORUS` (19次)、`ARC3D` (16次)、`ELLIPSOIDHEAD` (5次)、`CORNERBOX` (5次)、`HALFSPHERE` (4次)、`TORISPHERICHEAD` (3次)、`ROUNDRECT` (3次)、`SPHERESEGMENT` (3次)、`ELLIPSOIDHEAD2` (1次)、`TORISPHERICHEAD2` (1次)、`TORISPHERICHEADH` (1次)、`ELLIPSOIDSEGMENT` (1次)、`ARC3DS` (1次)、`ELLIPSE` + `LOFT` (1次)。

> **核心警示（Coordinate & Parameter Traps）**：
> 1. **所有原生体素的第一个位置参数必须是主对象句柄 `s`**（即 `def FUNC(s, ...)` 传入的 `s`）。
> 2. **绝大多数回转体素（`CYLINDER`, `CONE`, `HALFSPHERE`, `ELLIPSOIDHEAD`, `TORISPHERICHEAD`, `PYRAMID`, `ROUNDRECT`）默认沿 `+Z` 轴向上生长**，底面圆心位于原点 `(0, 0, 0)`。而 Plant 3D 管道主轴线默认沿 **`+X` 轴**，因此直管、法兰、大小头创建后通常紧跟 `.rotateY(90)` 将 `+Z` 轴旋转至 `+X` 轴！
> 3. **`BOX(s, L, W, H)` 的轴向映射极其特殊**（非直觉的 X-Y-Z 对应），必须严格核对下表！
> 4. **`ARC3D` / `ARC3D2` / `ARC3DS` 中的参数 `D` 和 `D2` 是半径（1/2 管径）而非全直径**！

### 2.1 全部体素精确签名与坐标系速查总表

| 序号 | 体素名称 | 精确函数签名（含重载与关键字参数） | 局部坐标系基准点 (Base Point) | 初始生长方向与各轴向区间范围 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **`BOX`** | `BOX(s, L, W, H)` | **几何质心 (Center of Gravity)** `(0, 0, 0)` | 质心在原点；**注意轴向错位映射**（详见 2.2 节深度剖析） |
| 2 | **`CYLINDER`** | 重载1（正圆柱/空心管）：`CYLINDER(s, R, H, O=0.0)`<br>重载2（椭圆圆柱）：`CYLINDER(s, R1, R2, H, O=0.0)` | **底面圆心 (Center of Bottom)** `(0, 0, 0)` | 高度 `H` 沿 **`+Z` 轴** `[0, H]`；径向在 XY 平面 `[-R, R]`（椭圆时 `R1` 沿 X，`R2` 沿 Y） |
| 3 | **`CONE`** | `CONE(s, R1, R2, H, E=0.0)` | **底面圆心 (Center of Bottom)** `(0, 0, 0)` | 高度 `H` 沿 **`+Z` 轴** `[0, H]`；底半径 `R1` 在 `Z=0`，顶半径 `R2` 在 `Z=H`；偏心距 `E` 沿 **`+X` 轴**偏移顶面圆心至 `(E, 0, H)` |
| 4 | **`ARC3D`** | `ARC3D(s, D, R, A)` | **两端中心线切线交点 (Centerline Intersection)** `(0, 0, 0)` | 在 **XY 平面**内弯曲；**`D` 为管半径（即外径的 1/2）**，`R` 为弯曲半径，`A` 为弯曲角度（度） |
| 5 | **`ARC3D2`** | `ARC3D2(s, D, D2, R, A)` | **两端中心线切线交点** `(0, 0, 0)` | 在 **XY 平面**内弯曲的变径弯头；`D` 为端1半径，`D2` 为端2半径（若 `D2=0` 则同 `D`） |
| 6 | **`ARC3DS`** | `ARC3DS(s, D, R, A, S)` 或 `ARC3DS(s, D, D2, R, A, S)` | **两端中心线切线交点** `(0, 0, 0)` | 虾米腰分段弯头；`D` 为管半径，`R` 为弯曲半径，`A` 为角度，`S` 为节数（Segments） |
| 7 | **`TORUS`** | `TORUS(s, R1, R2)` | **圆环中心点** `(0, 0, 0)` | 环中心线位于 **XY 平面**（绕 Z 轴回转）；`R1` 为大圆环半径（中心到管心），`R2` 为截面圆管半径 |
| 8 | **`HALFSPHERE`** | `HALFSPHERE(s, R)` | **底面圆心 (Center of Bottom)** `(0, 0, 0)` | 极点朝向 **`+Z` 轴** `[0, R]`，赤道大圆在 `Z=0` 的 XY 平面上 |
| 9 | **`SPHERESEGMENT`** | `SPHERESEGMENT(s, R, P, Q)` | **球台下底面圆心** `(0, 0, 0)` | 沿 **`+Z` 轴** `[0, P]`；`R` 为球半径，`P` 为球冠/球台高度，`Q` 为下底面距球心的 Z 向距离 |
| 10 | **`ELLIPSOIDHEAD`** | `ELLIPSOIDHEAD(s, R)` | **底面圆心 (Center of Bottom)** `(0, 0, 0)` | 标准椭球封头，沿 **`+Z` 轴** `[0, H]`；可通过 `obj.parameters()['H']` 读取真实总高 |
| 11 | **`ELLIPSOIDHEAD2`** | `ELLIPSOIDHEAD2(s, R, SF=...)` | **底面圆心** `(0, 0, 0)` | 2:1 比例椭球封头（短半轴 `b = 0.5 * R`），含直边段 `SF`（可选），沿 **`+Z` 轴**生长 |
| 12 | **`ELLIPSOIDSEGMENT`** | `ELLIPSOIDSEGMENT(s, RX, RY, A1, A2, A3, A4)` | **几何质心 (Center of Gravity)** `(0, 0, 0)` | 橄榄球形旋转椭球片段；长半轴 `RX` 沿 **X 轴**，短半轴 `RY` 沿 **Y/Z 轴** |
| 13 | **`TORISPHERICHEAD`** | `TORISPHERICHEAD(s, R)`（兼容拼写 `TORISPERICHEAD`） | **底面圆心** `(0, 0, 0)` | 标准碟形封头（DIN 28011 / 归一化碟形），沿 **`+Z` 轴**生长，高度通过 `.parameters()['H']` 查询 |
| 14 | **`TORISPHERICHEAD2`** | `TORISPHERICHEAD2(s, R, SF=25.4)` | **底面圆心** `(0, 0, 0)` | 固定过渡小圆弧半径（默认 `r=25.0` 或带直边 `SF`）的碟形封头，沿 **`+Z` 轴**生长 |
| 15 | **`TORISPHERICHEADH`** | `TORISPHERICHEADH(s, R, H)`（兼容拼写 `TORISPERICHEADH`） | **底面圆心** `(0, 0, 0)` | 指定总高度 `H` 的自定义碟形封头（当直管段不足标准封头高时使用，见 `CPC` 管帽源码），沿 **`+Z` 轴** `[0, H]` |
| 16 | **`PYRAMID`** | `PYRAMID(s, L, W, H, HT=0.0)` | **底面矩形中心 (Center of Bottom Rectangle)** `(0, 0, 0)` | 高度 `H` 沿 **`+Z` 轴** `[0, H]`；若省略 `HT` 或 `HT=0` 则为尖顶四棱锥，若 `HT > H` 则为平顶四棱台（截头锥） |
| 17 | **`ROUNDRECT`** | `ROUNDRECT(s, L, W, H, R2, E=0.0)` | **底面矩形中心 (Center of Rectangle)** `(0, 0, 0)` | 天圆地方过渡件，沿 **`+Z` 轴** `[0, H]`；底面为 `L × W` 矩形 (`Z=0`)，顶面为半径 `R2` 的圆 (`Z=H`)，圆心沿 `+X` 偏心 `E` |
| 18 | **`ELLIPSE` + `LOFT`** | `e = ELLIPSE(s, R1, R2, A1=0, A2=2*pi)`<br>`o = LOFT(s, e1, e2)` | `ELLIPSE` 圆心在 `(0, 0, 0)`，位于 XY 平面 | 空间双截面放样（见 `var_basic.ARC3DS2` 变径虾米腰弯头）；放样后必须调用 `e1.erase()` 和 `e2.erase()` |
| 19 | **`EXTRUSION` / `ROTATIONBODY`** | 扩展层造型：在 Plant 3D 原厂库中通过组合 `BOX`/`CYLINDER`/`CONE`/`TORUS` 或 `CSTE_*` 型钢拉伸函数实现 | 依具体构造函数而定 | 在自定义脚本中，型钢拉伸优先复用 `CSTE_H`/`CSTE_U`/`CSTE_L`/`CSTE_T` 或 `BOX`，回转体优先组合 `CYLINDER`+`CONE`+`TORUS` |

---

### 2.2 重点体素深度剖析与轴向防坑指南

#### （1）`BOX(s, L, W, H)`：最易出错的轴向映射与两种工程模式
官方手册 `PD4214-L` 第 7 页仅说明 `BOX(s, L, W, H)` 的基准点为质心（Center of Gravity），但未明确标注 `L, W, H` 与局部坐标系 `X, Y, Z` 的对应关系。通过对原厂 `varmain/var_basic.py` (`CORNERBOX`)、`varmain/eqfactory.py` (`EQBOX`)、`varmain/dummy_var.py` (`CDBOX`) 及 `varmain/divsub/cste_h.py` (`CSTE_H`) 的字节码反编译验证：

1. **原厂 C++ `BOX(s, L, W, H)` 底层轴向**：
   - 在未旋转的原始状态下，`BOX(s, L, W, H)` 的质心位于 `(0, 0, 0)`：
     - **`H` 参数沿 X 轴分布**：区间 `[-H/2, +H/2]`（验证：`CDBOX` 中 `BOX(s, W=D, H=L, L=D).translate((L/2, 0, 0))` 刚好占据 `X ∈ [0, L]`；`CSGB001` 中腹板 `BOX(s, L=ST, W=SL, H=HS).translate((HS/2 + R1, 0, 0))` 沿 X 轴生长 `HS`）。
     - **`L` 参数沿 Y 轴分布**：区间 `[-L/2, +L/2]`（验证：`CSTE_H` 中翼缘 `BOX(s, L=T, W=L, H=W).translate((0, T/2, L/2))` 沿 Y 轴偏移 `T/2`）。
     - **`W` 参数沿 Z 轴分布**：区间 `[-W/2, +W/2]`（验证：`EQBOX` 中 `BOX(s, L=W, W=H, H=D).translate((0, 0, H/2))` 使底面落在 `Z=0`，顶面落在 `Z=H`，即沿 `+Z` 轴 `[0, W]`）。
2. **绕 Y 轴旋转 90° 后的常用工程姿态（`BOX(...).rotateY(90)`）**：
   - 当执行 `.rotateY(90)`（或支吊架末尾统一执行 `o1.rotateY(90)`）时，原来的 X 轴（`H`）旋转至 `-Z` 轴，原来的 Z 轴（`W`）旋转至 `+X` 轴，原来的 Y 轴（`L`）保持不变。
   - 而在部分自定义脚本约定或经过先期旋转的局部坐标系中，常将 `BOX(s, L, W, H)` 结合 `.translate((0, 0, W/2))` 视为 `W` 沿 `+Z` 轴 `[0, W]` 生长。
3. **原厂推荐的角点基准封装：`CORNERBOX(s, L, W, H)`**：
   - 原厂工程师为了消除 `BOX` 质心与轴向交换带来的心智负担，在 `varmain/var_basic.py` 中专门封装了 `CORNERBOX`：
   ```python
   def CORNERBOX(s, L=300.0, W=200.0, H=100.0, ID='CORNERBOX', **kw):
       BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate(((L / 2.0), (W / 2.0), (H / 2.0)))
   ```
   - 调用 `CORNERBOX(s, L=dx, W=dy, H=dz)` 后，角点位于 `(0, 0, 0)`，**`L` 严格沿 `+X` 轴 `[0, L]`，`W` 严格沿 `+Y` 轴 `[0, W]`，`H` 严格沿 `+Z` 轴 `[0, H]`**！

#### （2）`CYLINDER(s, R, H, O)` 与椭圆圆柱重载 `CYLINDER(s, R1, R2, H, O)`
- **标准正圆柱 / 空心圆管**：
  ```python
  o1 = CYLINDER(s, R=D/2.0, H=L, O=r_inner)
  ```
  - `R`：外半径（必须 `> 0`）。
  - `H`：沿 `+Z` 轴的拉伸高度（必须 `> 0`）。
  - `O`：同心内孔半径（Hole Radius）。当 `O=0.0`（或省略）时为实心圆柱；当 `0 < O < R` 时，底层 ACIS 内核直接生成带通孔的空心圆管，**无需再创建内圆柱做 `.subtractFrom()`**！
- **椭圆截面圆柱（Elliptical Cylinder）**：
  ```python
  o2 = CYLINDER(s, R1=a, R2=b, H=L, O=0.0)
  ```
  - 当传入 `R1` 和 `R2` 时，生成底面在 `Z=0`、半轴分别为 `R1`（X向）和 `R2`（Y向）、高为 `H`（+Z向）的椭圆柱（在 `varmain/weldentsub/cpnssub/cpns.py` 马鞍口过渡段与 `varmain/eqfactory.py` 中广泛使用）。

#### （3）`CONE(s, R1, R2, H, E)`：同心圆锥/圆台与偏心大小头
- **函数签名**：`CONE(s, R1=r_bottom, R2=r_top, H=height, E=eccentricity)`
- **参数详解**：
  - `R1`：`Z = 0` 处的下底面半径（圆心固定在 `(0, 0, 0)`）。
  - `R2`：`Z = H` 处的上顶面半径。当 `R2 = 0.0` 时生成尖顶圆锥（如阀门锥体表示 `VALVE`）；当 `R2 > 0.0` 时生成圆台（Frustum）。**注意**：若在设备脚本中 `R1 == R2`，部分 ACIS 版本会报退化错误，原厂 `EQCONE_` 中专门做了防御保护：`if D1 == D2: D2 = 0.99 * D1`。
  - `H`：沿 `+Z` 轴的垂直高度。
  - `E`：上顶面圆心相对于下底面圆心的偏心距（Eccentricity），默认沿局部 **`+X` 轴**偏移，即上顶面圆心坐标为 `(E, 0, H)`。
- **偏心大小头（`CPJRE`）旋转后的偏移方向**：
  - 当执行 `CONE(s, R1=D1/2.0, R2=D2/2.0, H=L, E=E).rotateY(90)` 时：
  - 原 `+Z` 轴（高度 `H=L`）旋转到 **`+X` 轴**；
  - 原 `+X` 轴（偏心距 `E`）绕 Y 轴顺时针旋转 90° 后指向 **`-Z` 轴**！
  - 因此小端端口（Port 2）的坐标为 `(L, 0, -E)`，底平（Bottom Flat）安装时 `E = (D1 - D2) / 2.0`。

#### （4）`ARC3D(s, D, R, A)`、`ARC3D2(s, D, D2, R, A)` 与 `ARC3DS(s, D, R, A, S)`
- **核心防坑死线**：
  1. **参数 `D` 和 `D2` 是截面圆的半径（`Radius = OD / 2.0`），绝不是外径 `OD`！** 原厂所有弯头脚本（如 `CPB`, `CPBD`）均写作 `ARC3D2(s, D=D/2.0, D2=D2/2.0, R=R, A=A)`。
  2. **弯曲半径防退化保护**：弯曲半径 `R` 必须严格大于截面半径 `D/2.0`，否则 ACIS 扫掠自交崩溃！原厂标准防御写法：
     ```python
     if R <= (D / 2.0):
         R = (D / 2.0) + 0.0001
     ```
  3. **局部坐标系与基准点**：
     - 原点 `(0, 0, 0)` 位于弯头两端接口中心延长线的交点（Tangent Intersection Point，当 `A=180°` 时特殊处理）。
     - 弯头自带两个隐藏特征点，可直接通过 `o0.pointAt(0)` / `o0.directionAt(0)` 和 `o0.pointAt(1)` / `o0.directionAt(1)` 获取两端端口的精确坐标与外法向向量（详见第四节内省接口）！

#### （5）容器封头家族（`ELLIPSOIDHEAD`, `TORISPHERICHEAD`, `HALFSPHERE`, `SPHERESEGMENT`, `ELLIPSOIDSEGMENT`）
1. **`ELLIPSOIDHEAD(s, R)` 与 `ELLIPSOIDHEAD2(s, R, SF=...)`**：
   - `R` 为封头外半径（`D / 2.0`），底面圆心在 `(0, 0, 0)`，封头极点朝向 `+Z` 轴。
   - **高度自省**：创建后无需手动估算封头总高，直接调用：
     ```python
     oHead = ELLIPSOIDHEAD(s, R=D/2.0)
     vT = oHead.parameters()
     head_H = float(vT['H'])
     ```
2. **`TORISPHERICHEAD(s, R)`、`TORISPHERICHEAD2(s, R, SF=25.4)` 与 `TORISPHERICHEADH(s, R, H)`**：
   - 碟形封头（由球面冠部 + 过渡环壳折边 + 可选直边组成）。
   - 注意原厂 C++ 导出表中同时支持 `TORISPHERICHEAD` 与 `TORISPERICHEAD`（少一个 `H`）两种拼写，推荐使用标准拼写 `TORISPHERICHEAD` 和 `TORISPHERICHEADH`。
   - 当管帽总长 `L` 小于标准碟形封头高度 `vTH` 时，必须擦除原封头并改用定高碟形封头 `TORISPHERICHEADH(s, R=D/2.0, H=L)`（见原厂 `varmain/capsub/cpc.py`）。
3. **`SPHERESEGMENT(s, R, P, Q)`**：
   - 球带/球冠体素：`R` 为球半径，`Q` 为截切下底面距球心的距离，`P` 为球带厚度（高度），下底面中心在 `(0, 0, 0)`。
4. **`ELLIPSOIDSEGMENT(s, RX, RY, A1, A2, A3, A4)`**：
   - 旋转椭球片段（见原厂隔膜阀体 `CPVI013000`）：
     ```python
     oC1 = ELLIPSOIDSEGMENT(s, RX=(vC[42] / 2.0), RY=vC[41], A1=360.0, A2=0.0, A3=0.0, A4=180.0)
     ```
   - `RX` 为沿 X 轴的半轴，`RY` 为径向半轴，`A1=360.0, A2=0.0` 表示绕 X 轴旋转整周 `360°`，`A3=0.0, A4=180.0` 表示从椭球一端极点扫掠到另一端极点，质心在 `(0, 0, 0)`。

#### （6）截面过渡体素：`PYRAMID(s, L, W, H, HT)` 与 `ROUNDRECT(s, L, W, H, R2, E)`
1. **`PYRAMID(s, L, W, H, HT)`**：
   - 底面矩形中心在 `(0, 0, 0)`（位于 `Z=0` 平面），高度 `H` 沿 `+Z` 轴。
   - **关键几何公式**：若要创建一个下底为 `D1 × W1`、上顶为 `D2 × W2`（按比例缩放 `D1 > D2 > 0`）、高为 `H` 的四棱台（截头金字塔），必须传入虚拟尖顶总高 `HT`：
     $$\text{HT} = \frac{H \cdot D_1}{D_1 - D_2}$$
     （见原厂 `varmain/eqfactory.py` 中 `EQPYRAMID_` 与 `varmain/dummy_var.py` 中 `CDBTEE` 的标准实现）。
2. **`ROUNDRECT(s, L, W, H, R2, E)`**：
   - 矩形变圆（天圆地方）过渡件：下底面 (`Z=0`) 为 `L × W` 矩形，中心在 `(0, 0, 0)`；上顶面 (`Z=H`) 为半径 `R2` 的圆，圆心在 `(E, 0, H)`。

---
