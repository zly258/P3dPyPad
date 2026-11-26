# AutoCAD Plant 3D 连接端口拓扑与动态线性握点规范（`06_ports_and_interactive_grips.md`）

> **数据来源**：逆向提取自 `varmain/custom.pyc`、`variants.xml` 及官方技术白皮书 `PD4214-L` / `PD1746`。

---

## 二、 连接端口拓扑规范（Ports & `s.setPoint`）

在 Plant 3D 中，管件、阀门、支吊架和设备管嘴通过连接端口（Connection Ports）实现自动捕捕捉、同轴对齐与壁厚/等级匹配。

### 2.0 等级库里的端口行（不要和 `s.setPoint` 的序号搞混）

没有 `S0`。脚本第 1 个 `s.setPoint` 是几何端口 1，写进库时叫 `S1`，但 **S1 不占用 `PartPort` 行**。

对照 Plant 3D 2026 原厂库（`CPak ASME\ASME Pipes and Fittings Catalog.pcat`、`CPak ASME\CS150.pspc`、`CPak DIN\10HC01.pspc`）：`PartPort.Name` 从 `S2` 开始，`S1` 的计数是 0。管帽、盲板（`ConnectionPortCount=1`）的 `PartPort` 行数是 0。`SUPPORTS Catalog metric.acat` 与 `PipeSupportsSpec.pspc` 可以根本没有 `Port` / `PartPort` 表；支吊架零件行仍是 `PortName='S1'`、`EndType='Undefined_ET'`、`PartCategory='Default'`。

| 存在哪里 | 谁 | 写什么 |
| :--- | :--- | :--- |
| `EngineeringItems` | 每一个零件的主端口 S1 | `PortName='S1'`、`NominalDiameter`、`MatchingPipeOd`、`EndType`、`ConnectionPortCount` |
| `Port` + `PartPort` | 仅第 2 口及以后 | `PartPort.Name` 为 `S2`、`S3`…；`PartPort` 行数 = `ConnectionPortCount - 1` |
| 脚本 | 几何 | `s.setPoint` 次数 = `ConnectionPortCount`，与上面两行无关 |

`plant3d_occ/catalog/store.py` 必须保持：`ports <= 1` 不写 `PartPort`；多端口从 `index=2` 写起。把 S1 补进 `PartPort` 会让双口弯头被 Plant 当成 3 口。

配管等级（`.pspc`）本身仍要有 `Port` / `PartPort` **表**，否则规格编辑器的尺寸范围和下拉是空的。缺的是表，不是 S1 行。`.pspx` 的 `PlantSpecContent` 必须 `Target="<同名>.pspc"`，不能留着模板等级的文件名。

### 2.1 `s.setPoint` 精确语法
```python
# 形式 1：指定端口坐标点 p 与外法向向量 v
s.setPoint((x, y, z), (vx, vy, vz))

# 形式 2：额外指定端口绕轴旋转角 a（单位：度，常用于椭圆法兰 CPFWO 或方形风管对齐）
s.setPoint((x, y, z), (vx, vy, vz), a)
```

> **外法向向量 `(vx, vy, vz)` 铁律**：
> **方向向量 `(vx, vy, vz)` 必须指向“离开当前构件本体、朝向外部对接管道”的外法向方向（Outward Normal Vector）！**
> - 当两根管件对接时，Plant 3D 会强制令两个对接端口的方向向量满足 $\vec{v}_1 = -\vec{v}_2$（即面对面相向对齐）。
> - 如果方向向量写反（指向构件内部），连接上的管道会直接倒插穿入构件内部！

### 2.2 标准工程构件端口拓扑坐标与向量公式总表

| 端口拓扑类别 | 适用工程构件 | 端口编号 | 端口空间坐标 `(x, y, z)` | 外法向方向向量 `(vx, vy, vz)` | 原厂代表脚本与几何说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. 单端口：管托 / 管卡 / 滚轮架（水平管道支座）** | 滑动管托、鞍座、U型螺栓、滚轮支座 | Port 1 | `(0.0, 0.0, 0.0)`<br>*(位于被支撑管道中心线上)* | **`(-1.0, 0.0, 0.0)`**<br>*(沿管道轴线指向 `-X`)* | `CSGB001`, `CSGC000`, `CSGE002`, `CSGR005`（底座在 `-Z` 方向 `Z = -SH`） |
| **2. 单端口：吊架（悬吊于管道上方）** | 刚性吊杆、弹簧吊架 | Port 1 | `(0.0, 0.0, 0.0)`<br>*(位于被吊管道中心线上)* | **`(0.0, 0.0, 1.0)`** 或 **`(-1.0, 0.0, 0.0)`** | `CSGH001`, `CSGH002`（吊杆向上延伸至生根点，注意 `CSGH001` 旋转后 `setPoint((0,0,0), (0,0,1))`） |
| **3. 单端口：管帽 / 盲板法兰** | 管帽、盲板、人孔 | Port 1 | `(0.0, 0.0, 0.0)` | **`(-1.0, 0.0, 0.0)`** | `CPC`, `CPFBR`, `CMANHOLE`（本体沿 `+X` 延伸 `[0, L]`） |
| **4. 单端口：立式设备筒体 / 封头** | 容器筒体、封头、裙座 | Port 1 (底)<br>Port 2 (顶) | `(0.0, 0.0, 0.0)`<br>`(0.0, 0.0, H)` | **`(0.0, 0.0, -1.0)`**<br>**`(0.0, 0.0, 1.0)`** | `EQCYLINDER`, `EQELLIPSOIDHEAD`（沿 `+Z` 轴竖直生长） |
| **5. 双端口：同心直通件** | 直管、对焊法兰、同心大小头、闸阀/球阀/截止阀 | Port 1 (左)<br>Port 2 (右) | `(0.0, 0.0, 0.0)`<br>`(L, 0.0, 0.0)` | **`(-1.0, 0.0, 0.0)`**<br>**`(1.0, 0.0, 0.0)`** | `PIPE`, `CPFWR`, `CPJRC`, `VALVE`（或中心在原点时左端 `(-L1,0,0)`、右端 `(L2,0,0)`） |
| **6. 双端口：偏心大小头** | 底平/顶平偏心异径管 | Port 1 (大端)<br>Port 2 (小端) | `(0.0, 0.0, 0.0)`<br>`(L, 0.0, -E)` | **`(-1.0, 0.0, 0.0)`**<br>**`(1.0, 0.0, 0.0)`** | `CPJRE`, `CPJREL`（`CONE` 绕 Y 轴转 `90°` 后偏心量 `E` 落在 `-Z` 方向） |
| **7. 双端口：任意角度弯头 ($A^\circ$)** | 弯头、变径弯头、虾米腰弯头 | Port 1<br>Port 2 | 直接调用 `oArc.pointAt(0)`<br>直接调用 `oArc.pointAt(1)` | `oArc.directionAt(0)`<br>`oArc.directionAt(1)` | `ARC3D2_`, `CPB`, `CPBD`；若手工计算（切线长 $T = R \tan(A/2)$）：Port 1 为 `(T, 0, 0)` 向量 `(1, 0, 0)`，Port 2 随角度 `A` 在 XY 平面旋转 |
| **8. 双端口：角阀 (Angle Valve)** | 90° 角式截止阀、安全阀 | Port 1<br>Port 2 | `(L1, 0.0, 0.0)`<br>`(0.0, -L2, 0.0)` 或 `(0.0, L2, 0.0)` | **`(1.0, 0.0, 0.0)`**<br>**`(0.0, -1.0, 0.0)`** 或 `(0.0, 1.0, 0.0)` | `ANGLEVALVE`, `CPVA003000`, `CPVR001000` |
| **9. 三端口：正三通 / 斜三通 ($A^\circ$)** | 等径三通、异径三通、斜三通 | Port 1 (主管左)<br>Port 2 (主管右)<br>Port 3 (支管) | `(-L1, 0.0, 0.0)`<br>`(L2, 0.0, 0.0)`<br>`(L3*cos(A), L3*sin(A), 0.0)` | **`(-1.0, 0.0, 0.0)`**<br>**`(1.0, 0.0, 0.0)`**<br>**`(cos(A), sin(A), 0.0)`** | `CPTS`（当 `A=90°` 正三通时，Port 3 坐标为 `(0, L3, 0)`，外法向为 `(0, 1, 0)`） |
| **10. 三端口：Y型对称分叉三通 ($A^\circ$)** | Y型裤衩三通（两支管夹角 $A$） | Port 1 (主管)<br>Port 2 (右支)<br>Port 3 (左支) | `(-L1, 0.0, 0.0)`<br>`(L2*cos(A/2), -L2*sin(A/2), 0)`<br>`(L3*cos(A/2), +L3*sin(A/2), 0)` | **`(-1.0, 0.0, 0.0)`**<br>**`(cos(A/2), -sin(A/2), 0)`**<br>**`(cos(A/2), +sin(A/2), 0)`** | `CPTY`（利用 `mTransform().rotateZ(asRadiants(±A/2))` 计算） |
| **11. 四端口：正四通 / 斜四通** | 正四通、四通阀 | Port 1 (左)<br>Port 2 (右)<br>Port 3 (上支)<br>Port 4 (下支) | `(-L1, 0.0, 0.0)`<br>`(L2, 0.0, 0.0)`<br>`(0.0, L3, 0.0)`<br>`(0.0, -L4, 0.0)` | **`(-1.0, 0.0, 0.0)`**<br>**`(1.0, 0.0, 0.0)`**<br>**`(0.0, 1.0, 0.0)`**<br>**`(0.0, -1.0, 0.0)`** | `CPXT`, `CPXX`, `CPV4000000` |

> **90° 角式阀门 / 安全阀拓扑放置铁律**：
> 任何双端口夹角非 180° 的元件（如 90° 角式截止阀 `VALVE_ANGLE_GLOBE`、弹簧安全阀 `VALVE_SAFETY_PSV`、先导式安全阀 `VALVE_SAFETY_PILOT`），**不可**在 Plant 3D 中直接插入到连续直管中间（捕捉“最近点”），否则直管打断后两断口平行反向，无法同时对接 90° 端口，必然报错 **“无法连接不平行的端口”**。请在 `TooltipLong` 中明确提示用户：**需连接在管道开放端点（Endpoint）、设备管嘴（Nozzle）或移除弯头后的直角管端**。

---

## 三、 动态线性拉伸握点（Interactive Grips）与管道自动吸附联动

在工程设计中，支吊架（如管托高度 `SH`、生根立柱高 `L`、吊杆长度 `H`、横担跨距 `L`）需要根据现场土建钢梁或地面标高在 AutoCAD 模型空间中通过鼠标拖拽蓝色三角形动态握点（Linear Grip）实时拉伸。

### 3.1 `Ask4Dist=True` 与 `s.setLinearDimension` 双重绑定机制

要激活某个尺寸参数的动态拉伸握点，可以通过以下两种方式之一（在自定义脚本中推荐**同时使用**）：

1. **装饰器端声明 `Ask4Dist=True`**：
   ```python
   @param(SH=LENGTH, TooltipShort="Shoe Height", TooltipLong="Centerline to bottom of shoe", Ask4Dist=True)
   ```
   - 作用：编译为 `<Param Name="SH" ... Ask4Dist="true" />`，告诉 Plant 3D 在插入该支吊架时允许用户在命令行或视图中拾取两点距离，并在属性面板中启用动态尺寸输入。
2. **几何端注册 `s.setLinearDimension('ParamName', pt_start, pt_end)`**：
   ```python
   s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
   ```
   - **参数 1 (`'ParamName'`)**：字符串，**必须与函数签名中的参数名大小写完全一致**（如 `'SH'`, `'H'`, `'L'`, `'BH'`, `'H1'`）。
   - **参数 2 (`pt_start`)**：尺寸基准起点 `(x1, y1, z1)`（固定端，即握点拖拽时的锚定基点，通常为管道中心 `(0, 0, 0)` 或管底 `(0, 0, -D/2.0)`）。
   - **参数 3 (`pt_end`)**：尺寸拉伸终点 `(x2, y2, z2)`（移动端，即蓝色线性拉伸箭头所在的空间位置，通常为支架底板底面 `(0, 0, -SH)` 或吊杆顶部生根面）。
   - **向量长度一致性要求**：`pt_start` 与 `pt_end` 之间的欧氏距离 $\|\text{pt\_end} - \text{pt\_start}\|$ **必须正好等于当前参数 `'ParamName'` 的数值**！如果两点距离与参数值不符，拖拽握点时会出现跳变或比例失真！

### 3.2 原厂 49 个支吊架脚本中的 4 种标准 `setLinearDimension` 模式

通过对 `variants.zip` 中全部 49 处 `setLinearDimension` 调用进行反编译归纳，原厂共有以下 4 种标准坐标模式（取决于末尾旋转姿态）：

| 模式编号 | 适用支吊架类型 | 参数测量基准说明 | 末尾旋转指令 | 原厂 `setLinearDimension` 精确调用代码 | 原厂代表脚本 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **模式 A** | **中心高基准管托 / 滚轮架 / 假管支腿**<br>（高度从管道中心 `Z=0` 算至支座底面 `Z=-SH`） | `SH` 或 `H` 或 `L` = 管中心至支座底面总高 | `o1.rotateY(90)`<br>`s.setPoint((0,0,0), (-1,0,0))` | `s.setLinearDimension('SH', (0, 0, 0), (0, 0, -SH))` | `CSGB001`, `CSGB002`, `CSGB008`, `CSGC004`, `CSGF001`, `CSGR005` |
| **模式 B** | **管底高基准管托 / 管卡底座**<br>（高度从管道外壁底部 `Z=-D/2` 算至底面 `Z=-D/2-SH`） | `SH` 或 `BH` = 管外壁底至底座底面净高 | `o1.rotateY(90)`<br>`s.setPoint((0,0,0), (-1,0,0))` | `s.setLinearDimension('SH', (0, 0, -D / 2.0), (0, 0, -SH - (D / 2.0)))` | `CSGB000`, `CSGB004`, `CSGB005`, `CSGC000`, `CSGC001`, `CSGC003` |
| **模式 C** | **顶部悬吊架 / 型钢框架**<br>（局部坐标系未绕 Y 旋转或绕 Z 旋转后，高度沿 `-X` 方向映射为世界 Z 向） | `H` 或 `L` = 管中心至生根点距离 | `o4d.rotateZ(90.0)`<br>`s.setPoint((0,0,0), (0,0,1))` | `s.setLinearDimension('H', (0, 0, 0), (-H, 0, 0))` | `CSGH001`, `CSGH002`, `CSGE001`, `CSGE002`, `CSGB012` |
| **模式 D** | **双吊杆门式横担架 (Trapeze)**<br>（无管道外径 `D`，以横担顶面中心 `(0,0,0)` 为基准向上拉伸 `H1`） | `H1` = 横担至顶部生根梁高 | `o0.rotateZ(90.0).rotateY(90.0)` | `s.setLinearDimension('H1', (0, 0, 0), (0, 0, H1))` | `CSGT001`, `CSGT002` |

### 3.3 支吊架与 Plant 3D 管道自动吸附（Attach to Pipe）联动规则

当用户在 Plant 3D 中点击将该自定义支吊架放置在某根管道上时，Plant 3D 的 C++ 适配器会自动执行以下联动机制：
1. **自动管径传递（Parameter `D` Injection）**：
   - Plant 3D 会自动读取被点击母管的真实外径（Matching Pipe OD），并将其赋值给支吊架脚本中的参数 **`D`**！
   - **强制命名规范**：所有需要吸附在管道上并随管径自动缩放的支吊架脚本，**代表母管外径的第一个几何参数必须命名为 `D`**（如 `def MY_SUPPORT(s, D=114.3, ...)`）！如果命名为 `PIPE_OD` 或 `D_PIPE`，Plant 3D 将无法自动注入母管外径！
2. **原点与母管中心线重合**：
   - 插入时，支吊架的局部坐标系原点 `(0, 0, 0)`（即 `s.setPoint((0, 0, 0), (-1, 0, 0))` 所在点）会被严格锁定在母管的中心轴线上，且支吊架的 `X` 轴与母管轴线对齐，`-Z` 轴指向重力下方（地面方向）。
   - 因此，管托腹板与鞍座弧面应当从 `Z = -D / 2.0`（管底外壁）向下延伸至 `Z = -SH`（底板底面），或者先在 `+X` 方向从 `X = D / 2.0` 延伸至 `X = SH`，最后执行一次 `.rotateY(90)` 使其旋转到 `-Z` 轴下方！
