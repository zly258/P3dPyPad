# AutoCAD Plant 3D 刚体变换、CSG 布尔运算、ACIS 内存管理与实体内省字典（`02_csg_memory_and_introspection.md`）

> **数据来源**：逆向提取自 `PnP3dACPAdapter.arx`、`varmain/primitiv.pyc` 及官方技术白皮书 `PD4214-L` / `PD1746`。

---

## 三、 刚体空间变换与矩阵 API（Modifier Functions）

### 3.1 基础空间变换方法与链式调用规则

所有由体素构造函数返回的对象（如 `o1 = BOX(...)` 或 `o1 = CYLINDER(...)`）均支持原位修改（In-place Modification）并返回自身引用 `self`，因此支持流畅的链式调用（Method Chaining）：

| 方法签名 | 参数类型与单位 | 旋转正方向 / 几何规则 | 原厂链式调用示例 |
| :--- | :--- | :--- | :--- |
| **`.translate((dx, dy, dz))`**<br>或 `.translate(mPoint / mVector)` | 3元组 `(float, float, float)` 或 `mPoint` / `mVector` | 沿当前世界/组件坐标系 `(X, Y, Z)` 平移 `(dx, dy, dz)` | `CYLINDER(s, R=10, H=50).translate((0, 0, -25))` |
| **`.rotateX(angle_deg)`** | `float`（**角度制 Degrees**，非弧度！） | 绕 **X 轴**按**右手定则**旋转（拇指指向 `+X`，四指从 `+Y` 转向 `+Z` 为正角度） | `CONE(s, R1=20, R2=10, H=50).rotateX(-90)`（将 `+Z` 转至 `+Y`） |
| **`.rotateY(angle_deg)`** | `float`（**角度制 Degrees**） | 绕 **Y 轴**按**右手定则**旋转（拇指指向 `+Y`，四指从 `+Z` 转向 `+X` 为正角度：`+90°` 将 `+Z` 转至 `+X`，将 `+X` 转至 `-Z`） | `CYLINDER(s, R=50, H=100).rotateY(90)`（将 `+Z` 圆柱转至 `+X` 管道轴向） |
| **`.rotateZ(angle_deg)`** | `float`（**角度制 Degrees**） | 绕 **Z 轴**按**右手定则**旋转（拇指指向 `+Z`，四指从 `+X` 转向 `+Y` 为正角度） | `BOX(s, L=10, W=20, H=30).rotateZ(45)` |
| **`.scale((sx, sy, sz))`** | 3元组 `(float, float, float)` | 沿 X, Y, Z 轴缩放（工程中极少使用，优先通过参数化尺寸建模） | `obj.scale((1.0, 1.0, 1.0))` |
| **`.clone()`** | 无参数 | 深拷贝当前 ACIS 实体并返回新句柄（拷贝出的临时刀具体在布尔运算后同样必须 `.erase()`） | `o2 = o1.clone().rotateZ(180)` |

> **旋转与平移顺序铁律**：
> 链式调用 `.rotateY(90).translate((B, 0, 0))` 是**按从左到右的顺序依次围绕全局原点 `(0, 0, 0)` 执行**！
> - **永远先在原点 `(0, 0, 0)` 完成姿态旋转（`.rotateX/Y/Z`），最后再执行空间平移（`.translate`）**；
> - 若先执行 `.translate((x, y, z))` 再执行 `.rotateZ(angle)`，则实体不仅自身自转，还会围绕全局原点 `(0, 0, 0)` 发生公转（原厂常利用这一特性做圆周阵列，如 `CPVX006` 执行机构中的四根立柱：`.translate((R3, 0, 0)).rotateZ(45)`、`135`、`225`、`315`）。

### 3.2 高阶变换矩阵类 `mTransform` 与 `.setTransformationMatrix(t)`

当需要同时变换实体以及计算其端口坐标 `mPoint` / 方向向量 `mVector` 时（如斜三通 `CPTS`、Y型三通 `CPTY`、弯头支管台 `CPNO`、偏心锥体 `EQCONE`），使用 `aqa.math`（底层 `pybasmath`）提供的 `mPoint`、`mVector`、`mTransform`：

1. **构造点与向量**：
   - `p = mPoint(x, y, z)`：支持 `p.x()`, `p.y()`, `p.z()` 读取各分量，支持 `p[0], p[1], p[2]` 索引。
   - `v = mVector(vx, vy, vz)`：支持 `v.x()`, `v.y()`, `v.z()`, `v.theta()`（获取 XY 平面方位角弧度）。
2. **构造变换矩阵 `mTransform()`**：
   - **重要区别**：实体方法 `obj.rotateZ(deg)` 接收的是**角度（Degrees）**，而矩阵方法 `mTransform().rotateZ(rad)` 在 `EQCONE` / `CPTS` 中接收的是**弧度（Radians，需用 `asRadiants(deg)` 转换）**！
   - 平移矩阵：`t1 = mTransform().translate((xMove, yMove, zMove))`
   - 矩阵作用于点/向量：`p_new = t1 * p_old`，`v_new = t1 * v_old`
   - 矩阵直接赋予实体：`obj.setTransformationMatrix(t1)`
3. **原厂实战范例（摘自 `varmain/teesub/cptssub/cpts.py` 与 `varmain/weldentsub/cpnosub/cpno.py`）**：
   ```python
   # 范例 1：CPTS 斜三通利用 mTransform 计算旋转后的第 3 端口坐标与法向量
   pP3 = mTransform().rotateZ(asRadiants(A)) * mPoint(0, (L3 + I3), 0)
   pD3 = mTransform().rotateZ(asRadiants(A)) * mVector(0, 1, 0)
   s.setPoint(pP3, pD3)

   # 范例 2：CPNO 弯头支管台利用 setTransformationMatrix 对齐弯头末端
   o1 = ARC3D(s, D=R1, R=vC[6], A=vC[2])
   p2 = o1.pointAt(1)
   xMove = 0.0 - p2.x()
   yMove = vC[7] - p2.y()
   t1 = mTransform().translate((xMove, yMove, 0.0))
   o1.setTransformationMatrix(t1)
   pA2o = t1 * o1.pointAt(1)
   ```

---

## 四、 CSG 布尔运算与 ACIS 内存回收铁律

### 4.1 三大布尔运算 API

| 方法签名 | 布尔逻辑 | 数学表达 | 关键行为说明 |
| :--- | :--- | :--- | :--- |
| **`main_obj.uniteWith(sub_obj)`** | **并集（Union）** | $A \leftarrow A \cup B$ | 将 `sub_obj` 合并到 `main_obj` 中，结果保存在 `main_obj`；`sub_obj` 仍驻留内存，必须销毁 |
| **`main_obj.subtractFrom(cutter_obj)`** | **差集（Subtraction）** | $A \leftarrow A \setminus B$ | **从调用者 `main_obj` 中减去参数 `cutter_obj`**（注意方法名虽叫 `subtractFrom`，但被减体是 `main_obj`，刀具是 `cutter_obj`！） |
| **`main_obj.intersectWith(bound_obj)`** | **交集（Intersection）** | $A \leftarrow A \cap B$ | 保留 `main_obj` 与 `bound_obj` 的公共重叠体积，结果保存在 `main_obj` |
| **`temp_obj.erase()`** | **释放内存** | `delete BODY*` | 从 C++ ACIS 内核与 AutoCAD 块表记录中销毁 `temp_obj`，防止幽灵重叠实体与内存泄漏 |

### 4.2 内存管理铁律与三大工程范式

1. **铁律：每次布尔运算后必须紧跟 `.erase()`**
   - 在 Plant 3D 中，只要调用了 `BOX(s, ...)` 或 `CYLINDER(s, ...)`，C++ 适配器就会立即在当前块表记录（`AcDbBlockTableRecord`）中创建一个 ACIS 实体。
   - 当执行 `o1.uniteWith(o2)` 或 `o1.subtractFrom(o2)` 后，`o2` 的几何体已被复制并合并/裁切进 `o1`，但 **`o2` 原本的独立实体依然存在于块定义中**！
   - 如果忘记调用 `o2.erase()`：
     - 在**并集**时会导致两个完全重叠的实体残留在模型中，引发消隐线错误与文件体积暴增；
     - 在**差集**（挖孔）时，刀具体 `o2` 会把刚刚挖出的孔洞再次堵死，导致视觉上“布尔差集完全失效”！
2. **范式一：多步布尔差集先并后减（加速 ACIS 布尔求交）**
   - 当需要从主件 `o1` 上挖去多个孔洞或切口（如内腔流道 `o3` + 支管流道 `o4`）时，原厂标准写法是先将所有刀具 `uniteWith` 合并为一个整体刀具，最后只对主件执行一次 `subtractFrom`：
   ```python
   o3.uniteWith(o4)
   o4.erase()
   o1.subtractFrom(o3)
   o3.erase()
   ```
3. **范式二：调用子组件函数时的种子体素（Seed Body `oTMP`）模式**
   - 当主脚本首步不是直接调用原生体素（如 `CYLINDER`），而是先调用另一个子脚本函数（如 `o1 = CSGC000(s, ...)` 或 `oV = CPVA003000(s, ...)`）时，为了确保 `s` 的根实体句柄正确绑定且不污染端口表，原厂标准模式是创建一个微小种子体素 `oTMP` 并将其与子组件合并：
   ```python
   oTMP = CYLINDER(s, R=0.01, H=0.01, O=0.0)
   oTMP.uniteWith(oV)
   oV.erase()
   ```

---

## 五、 实体内省与查询接口（Request Functions）

Plant 3D 提供了 5 个核心内省查询方法，允许脚本在运行时动态读取已创建体素或子组件的几何参数、变换矩阵与连接端口信息：

| 方法签名 | 返回值类型 | 功能详解与典型应用场景 |
| :--- | :--- | :--- |
| **`obj.parameters()`** | `dict` 或带属性的参数对象 | 返回体素的构造参数字典。最常用于查询标准封头（`ELLIPSOIDHEAD`, `TORISPHERICHEAD`）由内核自动计算出的真实高度 `H`：<br>`vT = o2.parameters(); vTH = float(vT["H"])` |
| **`obj.transformationMatrix()`** | `mTransform` | 返回实体当前的累积空间变换矩阵 |
| **`obj.numberOfPoints()`** | `int` | 返回实体或子组件上已注册的连接端口（Connection Points）数量 |
| **`obj.pointAt(n, inECS=0)`** | `mPoint` | 返回第 `n` 个连接端口（0-indexed：`0`, `1`, `2`...）的三维坐标点 `mPoint`（支持 `.x()`, `.y()`, `.z()`）。`inECS=0`（默认）返回 WCS 坐标，`inECS=1` 返回未变换的局部 ECS 坐标 |
| **`obj.directionAt(n, inECS=0)`** | `mVector` | 返回第 `n` 个连接端口的外法向单位方向向量 `mVector`。`inECS=0`（默认）返回 WCS 方向向量 |

### 5.1 内省接口组合装配实战示例

#### 示例 A：动态读取六角螺母厚度（摘自原厂 `CSGT001` 龙门吊架源码）
```python
o1 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(90.0).rotateX(90.0)
# 利用 CNUT6_001 内部预设的两个端口点 pointAt(0) 与 pointAt(1) 动态测量螺母实际厚度 MH
MH = abs(o1.pointAt(1).y() - o1.pointAt(0).y())
```

#### 示例 B：继承子组件的端口坐标与方向向量（摘自原厂 `ARC3D2_` 与 `CDCTEE` 源码）
```python
def ARC3D2_(s, D=100.0, D2=0.0, R=300.0, A=90.0, ID='ARC3D2_', **kw):
    sT = ARC3D2(s, D=D, D2=D2, R=R, A=A)
    # 直接提取 ARC3D2 内置的两个端点坐标与切向向量，注册为当前构件的连接端口
    s.setPoint(sT.pointAt(0), sT.directionAt(0))
    s.setPoint(sT.pointAt(1), sT.directionAt(1))
```
