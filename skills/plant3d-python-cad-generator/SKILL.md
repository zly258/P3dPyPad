---
name: plant3d-python-cad-generator
description: AutoCAD Plant 3D 参数化自定义构件（支吊架、管件、阀门、执行机构、非标设备组件）Python 脚本生成与逆向分析专家技能。当用户需要根据 DXF 图纸、尺寸表、工程草图或自然语言需求编写 AutoCAD Plant 3D 自定义脚本（基于 PnP3dACPAdapter.arx / varmain.primitiv / varmain.var_basic / aqa.math）、调试 PLANTREGISTERCUSTOMSCRIPTS 或 TESTACPSCRIPT 报错、或查询原厂 variants.zip 组件库时使用。
---

# AutoCAD Plant 3D 参数化 Python 脚本开发与架构师指南（`plant3d-python-cad-generator`）

本技能基于 **AutoCAD Plant 3D 官方技术白皮书（PD4214-L & PD1746）** 与 **原厂 `variants.zip` 全量 40,763 个反编译参数化脚本源码** 蒸馏构建，涵盖 `PnP3dACPAdapter.arx` C++ ACIS 几何内核绑定、原厂公共造型函数库、装饰器/端口/动态握点规范，以及按 6 大工程类别拆分的 20 个工业级典范源码母版。

---

## 一、 模块化知识库按需加载路由表（On-Demand Reference Routing）

为避免一次性加载大体积文档消耗上下文，本技能的所有 API 字典与源码母版均已拆分为高内聚的独立小文件（单文件 4~18 KB）。**请根据当前子任务需求，仅按需读取对应文件**：

### 1. 底层 API 与语法规范分册（`references/api/`）
| 分册文件路径 | 适用阶段与查询内容 |
| :--- | :--- |
| **`references/api/01_primitives_and_transforms.md`** | 查询全部 15 个 C++ 原生体素与扩展体素（`BOX`, `CYLINDER`, `CONE`, `ARC3D`, `ARC3D2`, `TORUS`, `HALFSPHERE`, `SPHERESEGMENT`, `ELLIPSOIDHEAD`, `ELLIPSOIDHEAD2`, `ELLIPSOIDSEGMENT`, `TORISPHERICHEAD`, `TORISPERICHEADH`, `PYRAMID`, `ROUNDRECT`, `EXTRUSION`, `ROTATIONBODY`）的函数签名、基准点与生长轴向 |
| **`references/api/02_csg_memory_and_introspection.md`** | 查询刚体空间变换（`.translate`, `.rotateX/Y/Z`, `.scale`, `.clone`）、CSG 布尔运算（`.uniteWith`, `.subtractFrom`, `.intersectWith`）、`.erase()` 内存释放铁律、种子体素（`oTMP`）模式及 `.parameters()` / `.pointAt()` / `.directionAt()` 实体内省接口 |
| **`references/api/03_var_basic_and_math_api.md`** | 查询 `varmain/var_basic.py` 全部 33 个公共造型与马鞍口迭代裁切函数、型钢与紧固件子函数（`CSTE_*`, `CNUT6_001`, `CBOLT_001`）、`aqa.math` 数学库与独立脚本 Inline 内联改写源码 |
| **`references/api/04_reusable_components_catalog.md`** | 查询 `variants.zip` 22 个子包 680+ 原厂可复用组件总表（支吊架 `CSG*`、弯头 `CPB*`、三通 `CPT*`、大小头 `CPJR*`、法兰 `CPF*`、阀门 `CPV*`、设备 `EQ*`）的功能说明、参数列表与物理含义 |
| **`references/api/05_decorators_and_metadata.md`** | 查询 `@activate`/`@group`/`@param`/`@enum` 装饰器语法、`varmain/custom.py` 逆序栈修饰机理、合法 `Group` 枚举值、参数类型映射与解析器死线规则 |
| **`references/api/06_ports_and_interactive_grips.md`** | 查询 `s.setPoint` 单/双/三端口坐标与外法向单位向量公式、`Ask4Dist=True` + `s.setLinearDimension` 交互式拉伸握点及管道外径 `D`/`PA` 自动吸附规范。**等级库端口行：没有 S0；S1 在 `EngineeringItems` 上，`PartPort` 从 S2 起，单口零件没有 `PartPort` 行，禁止补 S1** |
| **`references/api/07_occ_offline_verification.md`** | 查询离线核验链路：`plant3d_occ` 沙箱（`run_script_in_sandbox`）、发布校验（`validate.validate_script` 的 5 条判定与"悬空/焊合"区分）、预览与 HLR 标注渲染、CSV 尺寸表与 `.acat`/`.peqx` 打包元数据。**所有外形、数据、可发布性都以本分册的判定口径为准** |

### 2. 20 个原厂典范源码母版分册（`references/templates/`）
| 分册文件路径 | 对应构件类别与包含母版 |
| :--- | :--- |
| **`references/templates/00_templates_index.md`** | 20 个工业级典范母版的总目录与几何特征选型矩阵 |
| **`references/templates/01_structural_frames_and_guides.md`** | **类别一：型钢支吊架框架与多向导向架**（`CSGE001` L型角钢+T型钢悬臂架、`CSGE002` 带弧面鞍板框架、`CSGT001` 双吊杆门式横担架、`CSGB012` 位掩码四向导向托） |
| **`references/templates/02_shoes_clamps_and_rollers.md`** | **类别二：滑动管托、鞍座、管卡与滚轮架**（`CSGB001` 双箍管托、`CSGB004` 焊接鞍式管托、`CSGC000` U型螺栓总成、`CSGC004` 六角长螺母管卡、`CSGR005` 单/双滚轮架） |
| **`references/templates/03_spring_hangers_and_trunnions.md`** | **类别三：弹簧吊架与假管耳轴支座**（`CSGH001` 恒力/可变弹簧吊架、`CSGH002` 球面交集铰接弹簧吊架、`CSGF001` 调用 `CSGCutOut` 的假管耳轴支腿） |
| **`references/templates/04_fittings_elbows_tees_reducers_olets.md`** | **类别四：复杂管件**（`CPBD` 6种底座变径弯头、`CPTS` 任意倾角斜三通、`CPTY` 双分叉Y型三通、`CPJREL` 偏心大小头、`CPNO` 齐次变换弯头支管台） |
| **`references/templates/05_valves_and_actuators.md`** | **类别五：阀门与执行机构总成**（`CPVA003513` + `CPVX513` 角阀+椭球薄膜执行机构+侧手轮、`CPVI013000` 椭球鼓形阀体+双法兰） |
| **`references/templates/06_equipment_lugs_and_transitions.md`** | **类别六：非标设备组件与天圆地方**（`EQLUG` + `CSGP` + `BENDROUNDEDPLATE` 容器弧形垫板双筋支耳、`CADAPT_SQ2RO` + `CADAPT_SQ2SQ_Sub` 任意双轴偏心天圆地方过渡件） |

---

## 二、 标准主控工作流（Master Workflow）

当接收到用户的 **DXF 图纸、尺寸表、工程大样图截图或自然语言需求** 时，必须严格按以下四步执行，**严禁不经坐标系规划直接堆砌代码**：

### 步骤 1：参数提取与默认值防御规划
1. 识别构件类别（支吊架 `Support` / 弯头 `Elbow` / 三通 `Tee` / 变径 `Reducer` / 阀门 `Valve` / 法兰 `Flange` / 管台 `Olet` / 设备 `Equipment`），按需加载对应的模板分册。
2. 提取主控参数，遵循 Plant 3D 原厂命名惯例：
   - 管道外径统一用 `D`（支吊架/单径管件）或 `D1, D2, D3`（多端口管件）；
   - 生根总高/主体长度统一用 `L`、`H` 或 `SH`（并在 `@param` 中标记 `Ask4Dist=True`）；
   - 型钢尺寸用 `W`（翼缘宽）、`H`（截面高）、`T`（腹板/肢厚）、`TF`（翼缘厚）；
   - 底板尺寸用 `SL`（长）、`SW`（宽）、`ST`（厚）；壁厚参数用 `OF=-1.0`（或 `OF=0.0`）。
3. 为每个派生或可选尺寸编写防御性回退逻辑（如 `if SW <= 0.0: SW = SL`），确保任意可选参数传入 `0.0` 时不会产生零体积退化体素。

### 步骤 2：建立三维局部坐标系规划表（3D Local Coordinate Planning Table）
在编写任何 Python 代码前，必须先输出如下格式的 **三维局部坐标系与 CSG 规划表**：

| 序号 | 子件名称 | 选用体素 / 原厂子函数 | 原始基准点与生长轴向 | 刚体变换链（先旋转后平移） | 布尔关系与内存释放 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `o0` | 种子体 / 主体立板 | `BOX` / `CORNERBOX` / `CYLINDER` | 明确 `L, W, H` 轴向范围 | `.rotate*(...).translate((dx, dy, dz))` | 宿主主实体（保留） |
| `o1` | 底板 / 横梁 / 法兰 | `BOX` / `CSTE_U` / `CSTE_I` | 明确截面起点与拉伸方向 | `.rotate*(...).translate((dx, dy, dz))` | `o0.uniteWith(o1); o1.erase()` |
| `o2` | 管道鞍口 / 内流道 | `CYLINDER` / `ARC3D2` | 明确切割体贯穿裕量 | `.translate(...)` | `o0.subtractFrom(o2); o2.erase()` |

> **支吊架坐标系标准约定**：
> - 原点 `(0, 0, 0)` 必须位于**被支撑管道的中心轴线上**；
> - 管道轴线默认沿 **X 轴**（`s.setPoint((0, 0, 0), (-1, 0, 0))`）；
> - 支撑立柱沿 **`-Z` 轴**向下延伸至生根底面 `Z = -L`（或先在 `+X` / `+Y` 轴完成拼装，最后一步统一调用 `.rotateY(90)` 或 `.rotateZ(90)` 翻转到位）。

### 步骤 3：编写符合 AST 规范的 `.py` 源码
严格遵循下方 **十大防错铁律** 生成完整、可直接注册运行的 Python 脚本。

### 步骤 4：输出注册与测试命令说明
随代码附上将 `.py` 放入 `CPak Common\CustomScripts` 目录后的标准 AutoCAD Plant 3D 注册与测试指令：
1. 在 AutoCAD 命令行执行 `PLANTREGISTERCUSTOMSCRIPTS` 编译并更新注册表；
2. 执行 `(arxload "PnP3dACPAdapter.arx")`（若尚未加载）及 `TESTACPSCRIPT` 进行三维实体预览与握点检验。

---

## 三、 十大防错铁律（10 Hard Guardrails）

### 铁律 1：`BOX(s, L, W, H)` 轴向映射检查与 `CORNERBOX` 优先原则
- **原生 `BOX(s, L, W, H)` 的中心在 `(0, 0, 0)`**：
  - 在原厂 `varmain`（如 `CORNERBOX`, `EQBOX`, `CSGB001`, `CSTE_H`）底层实现中，原生 `BOX(s, L, W, H)` 未旋转时的 **`H` 沿 X 轴 `[-H/2, H/2]`，`L` 沿 Y 轴 `[-L/2, L/2]`，`W` 沿 Z 轴 `[-W/2, W/2]`**（平移 `(0, 0, W/2)` 后 `W` 沿 `+Z` 轴 `[0, W]`）。
  - 若需要严格满足 **`L -> X 轴`、`W -> Y 轴`、`H -> +Z 轴`** 的直观工程直觉：
    1. **方法 A（推荐）**：调用 `from varmain.var_basic import *` 中的 `CORNERBOX(s, L=dx, W=dy, H=dz)`（内部已自动执行 `BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate((L/2, W/2, H/2))`，角点在 `(0,0,0)`，`L->+X [0,L]`, `W->+Y [0,W]`, `H->+Z [0,H]`）；
    2. **方法 B**：对原生 `BOX(s, L=dx, W=dy, H=dz)` 显式调用 `.rotateX(-90).rotateY(-90)`，此时中心在 `(0,0,0)`，`L` 沿 X 轴 `[-L/2, L/2]`，`W` 沿 Y 轴 `[-W/2, W/2]`，`H` 沿 Z 轴 `[-H/2, H/2]`。

### 铁律 2：布尔运算后必须紧跟 `.erase()` 释放 ACIS 内存
- 每次调用 `main_body.uniteWith(sub)`、`main_body.subtractFrom(cutter)` 或 `main_body.intersectWith(bound)` 后，**下一行必须立即调用 `sub.erase()` / `cutter.erase()` / `bound.erase()`**。
- 漏写 `.erase()` 会导致被合并或作为切刀的体素残留在模型空间中，造成重影实体、挖孔失败（孔被残留切刀自己堵死）以及内存泄漏。

### 铁律 3：装饰器与 `def` 之间零空行、零注释，且 `@activate` 必须置顶
- `@activate(...)`、`@group(...)`、`@param(...)`、`@enum(...)` 与 `def FuncName(s, ..., **kw):` 之间**严禁出现任何空行或 `#` 注释**。
- `@activate` 必须是第一个（最顶层）装饰器——因为 Python 自下而上执行装饰器，最后执行的 `@activate` 内部调用了 `.reverse()` 将参数顺序翻正，并按位置索引将 `func.func_defaults` 绑定到参数列表。
- **所有业务参数必须提供默认值**，函数名必须与 `.py` 文件名（不含扩展名）大小写完全一致，且文件必须保存为 **UTF-8 无 BOM** 编码。

### 铁律 4：浮点数除法与几何退化防御边界保护
- 严禁依赖整数除法（脚本头部可加 `from __future__ import division` 或所有常数写为 `2.0`, `0.0`, `90.0`）。
- 凡涉及壁厚减法、立柱净高计算或圆锥/弯头半径，必须加下限保护，防止 `R <= 0` 或 `H <= 0` 触发 C++ ACIS 内核崩溃：
  ```python
  if R <= 0.0: R = 0.1
  if H <= 0.0: H = 0.1
  ```

### 铁律 5：空心圆管优先使用 `CYLINDER(s, R, H, O=r_inner)` 原生内孔参数
- 构造直管段、套筒、垫圈、法兰直颈时，**直接传入内半径 `O = r_inner`**（注意 `O` 是内半径而非壁厚，也不是内直径！），由 C++ 底层一步生成空心管，避免创建两个实心圆柱再做 `subtractFrom` 布尔差集。

### 铁律 6：`ARC3D` 与 `ARC3D2` 的参数 `D` 是管半径而非管外径
- `ARC3D(s, D=D/2.0, R=R, A=A)` 与 `ARC3D2(s, D=D1/2.0, D2=D2/2.0, R=R, A=A)` 中的 **`D` / `D2` 代表截面圆半径（`OD / 2.0`）**！若误传全直径 `D`，弯头会放大一倍并导致弯曲内侧自交崩溃。
- 弯曲半径 `R` 必须严格大于管半径 `D / 2.0`，调用前必须加原厂标准保护：
  ```python
  if R <= (D / 2.0):
      R = (D / 2.0) + 0.0001
  ```

### 铁律 7：多通管件/阀门采用“先并外壳、再并内芯、最后一次差集”法则
- 构造三通（`CPTS`/`CPTY`）、四通、带支座弯头（`CPBD`）或带接管容器时，严禁分别用空心管直接做布尔并集（主管壁会封闭支管孔口）。
- 正确顺序：
  1. 将所有外表面实心体合并为 `outer_body`；
  2. 将所有流道内芯实心体合并为 `inner_core`（内芯两端可适当外延 `0.1 mm` 避免共面奇异）；
  3. 最后执行一次 `outer_body.subtractFrom(inner_core); inner_core.erase()`。

### 铁律 8：子脚本装配时的“种子体素（Seed Body `oTMP`）”绑定法则
- 当主脚本的第一步几何操作是调用另一个封装子脚本（如 `CSGC000`, `CSTE_I`, `CPVA003000`）而非原生 C++ 体素时，为确保当前状态容器 `s` 正确绑定根实体句柄，应先创建一个极小的隐藏种子体素 `oTMP = CYLINDER(s, R=0.01, H=0.01, O=0.0)`（置于实体内部），再将各子脚本返回值依次 `oTMP.uniteWith(part); part.erase()`。

### 铁律 9：端口外法向向量必须指向构件外部，握点向量必须与生长方向一致
- `s.setPoint((px, py, pz), (vx, vy, vz))` 中的 `(vx, vy, vz)` 是**指向离开构件本体方向**的单位外法向向量（例如位于 `(-L1, 0, 0)` 的左端口向量必为 `(-1, 0, 0)`，位于 `(+L2, 0, 0)` 的右端口向量必为 `(1, 0, 0)`）。
- 凡调用 `s.setLinearDimension('ParamName', pt1, pt2)` 的参数，其 `@param` 声明必须包含 `Ask4Dist=True`，且 `|pt2 - pt1|` 的几何距离必须精确等于 `ParamName` 的当前值。

### 铁律 10：刚体变换一律遵循“先在原点自转定姿，再平移就位”
- `.rotateX()` / `.rotateY()` / `.rotateZ()` 始终绕**全局坐标系原点 `(0, 0, 0)`** 的坐标轴旋转，而非绕物体自身质心旋转！
- 若先 `.translate((x, y, z))` 再 `.rotate*(deg)`，体素会连同平移向量一起绕原点公转甩飞。因此单个零件定位必须严格遵守 **`Primitive(...) -> .rotate*(...) -> .translate((dx, dy, dz))`** 顺序（除非是在脚本最末尾对已围绕原点拼装完毕的总成执行整体翻转，如 `o0.rotateY(90)`）。

---

## 四、 双标准实战工程规范与三维核验扩展（Support Standards & Verification）

基于国家与行业标准《发电厂汽水管道支吊架设计手册》（CD-ZD2010 全 8 分册）与《管架标准图》（HG/T 21629-2021 全 23 大类）实战经验，补充以下架构级开发与核验铁律：

### 铁律 11：`CYLINDER` 的 `O` 在 Plant 3D 与离线 OCC 沙箱里语义一致（内孔半径）
- **两个内核都按 `O = 内孔半径` 解释**：Plant 3D 的 `PnP3dACPAdapter.arx` 与 `plant3d_occ` 的 `primitives/native.py` 实现一致——`CYLINDER(s, R, H, O=r_in)` 直接生成带通孔的圆管（`O=0` 或负数时为实心）。
- **判定边界（必须记住）**：仅当 `0 < O < R - 1e-4` 才真正挖孔；`O >= R` 被当作实心，`O <= 0` 也当实心。原厂脚本里常见的 `O=-1` 是"实心"写法，不是特殊魔法值。
- **不需要**为了兼容再补一次 `subtractFrom` 内圆柱：多一次布尔只会增加失败面。只有当脚本要同时喂给**别的**几何内核（非本仓库的解析器）时，才退回 `O=0.0` + 内圆柱差集。
- **壁厚不要反推**：`O` 不是壁厚。要留 `t` 壁厚就写 `O = R - t`，并保证 `t < R`。

### 铁律 12：支吊架同形构件科学去重与 CSV 预设驱动架构
- **同图号多代号去重合并**：标准图集中常存在外形几何完全一致、仅因材质、温度或微小安装附件差异而分配多个代号的情况（例如 CD-ZD2010 的 80000 系列悬臂梁、82340 系列简支梁，或 HG/T 21629 的多向管托、拉撑杆组）。
- **合并原则**：保持 1 个物理三维脚本（`.py`），将所有同形构件的规格数据全部合并汇编至该脚本同名的 `.csv` 中（首列 `预设名` 包含具体构件代号，如 `ZD_80030_10`），并附带 `DEDUP_INDEX.csv` 映射索引，大幅减小代码冗余度与后期维护成本。

### 铁律 13：图集原图（Atlas）与 B-Rep 实体 1:1 对照核验闭环
- 在开发支吊架脚本时，必须对照标准图集扫描页提取对应的图纸示意图（`<ID>_atlas.png`）。
- 提交前必须通过真实 OpenCASCADE/PyOCC 离线渲染管线输出三维实体图（`<ID>_render.png`），并拼装成左侧标准图集尺寸图、右侧 B-Rep 着色实体的 **1:1 同屏对比图（`<ID>_compare.png`）**，彻底杜绝悬空浮件、未擦除切刀、法向翻转和参数不联动等缺陷。
- **实体连通性判定口径**（与 `validate.validate_script` 一致）：
  - **允许**：多实体但两两包围盒间距 `≤ 2 mm`（螺母端面贴钢板、衬板与管壁相切这类**焊合件**）。OCC 在相切处融不成单实体，这是内核限制，不是建模错误——校验器只给 warning。
  - **不允许**：任一实体与其余全部实体间距 `> 2 mm`，即**悬空浮件**（漏位移、并集顺序错、切刀没擦）。这是 issue，必须修。
  - 判定依据是**实体间距**，不是"实体数必须等于 1"。

### 铁律 14：AutoCAD Plant 3D (Python 2.7) 中文 Unicode 与 UTF-8 声明铁律（消除 UnicodeDecodeError）
AutoCAD Plant 3D 宿主内部运行内嵌的 **Python 2.7** 解释器，其系统默认解码编码为 `ascii`。在 Python 2 中，普通 `"中文"` 是 `str`（未解码的 8-bit 字节串），当宿主 C++ 模块（`PnP3dACPAdapter.arx`）反射读取属性，或代码进行字符串格式化/拼接、或写入 XML 元数据时，会默认调用 `.decode('ascii')`，瞬间触发致命的 `UnicodeDecodeError: 'ascii' codec can't decode byte ...` 导致脚本注册失败或 AutoCAD 崩溃！
**必须严格遵循以下中文防错三要素**：

1. **所有包含中文字符的字符串字面量强制加 `u` 前缀（`u"..."` / `u'...'`）**：
   - `@activate`、`@group`、`@param`、`@enum` 装饰器中的中文文本（如 `TooltipShort=u"90度对焊弯头"`、`TooltipLong=u"长半径弯头描述"`）；
   - 函数签名中的默认值（如 `ID=u"E90-DN100"`，`ID=u"固定支架"`）；
   - 脚本内部的所有中文变量、提示信息与格式化字符串（如 `u"DN%g 规格" % D`）；
   - 英文结构标识符保持纯 ASCII（如 `Group="Elbow"`, `LengthUnit="mm"`, `Ports=2`, `D=LENGTH`）。
2. **文件第 1 行严格声明 UTF-8 编码**：
   - 必须写在第 1 行：`# -*- coding: utf-8 -*-`，文件保存为 UTF-8 无 BOM 格式。
3. **每个脚本最前部统一注入标准 Python 2 编码防御块**：
   ```python
   # -*- coding: utf-8 -*-
   import sys
   try:
       reload(sys)
       sys.setdefaultencoding('utf-8')
   except (NameError, AttributeError):
       pass
   ```
   - 在 Plant 3D (Python 2.7) 宿主下，`reload(sys); sys.setdefaultencoding('utf-8')` 将全局隐式转换编码提升为 UTF-8；
   - 外层包裹 `try...except`，在 Python 3（本地 PyOCC 离线仿真、单元测试、CI 环境）执行时静默跳过，确保双环境 100% 顺畅执行。

### 铁律 15：`s.setLinearDimension` 严格使用 3 个位置参数（禁止关键字参数）
- AutoCAD Plant 3D C++ 底层模块对 `s.setLinearDimension` 仅支持标准三参数 `METH_VARARGS` 签名：
  ```python
  s.setLinearDimension('ParamName', pt1, pt2)
  ```
- **严禁传入任何关键字参数**（如 `ext_dir=...`、`style=...`），否则在 AutoCAD Plant 3D 运行时会立即抛出 `TypeError: setLinearDimension() takes no keyword arguments`。
- `pt1` 与 `pt2` 为三维坐标元组 `(x, y, z)`，几何距离必须等于参数实际取值。

### 铁律 16：发布元数据必须"五件套完整"，否则 Plant 3D 里看不到或显示成脚本名
一个脚本要能发出去并被正确识别，下面五项缺一不可：

| 项 | 硬性要求 | 缺了会怎样 |
| :--- | :--- | :--- |
| `@activate` | 必须含 `Group`、`TooltipShort`、`TooltipLong`、`LengthUnit="mm"`、`Ports` | 没有 `Group` 的脚本会被 GUI 直接过滤掉，不进发布列表 |
| `@group` | **`@group("MainDimensions", TooltipLong="…")`**，`TooltipLong` 不能省 | 参数分组说明为空 |
| `@param` | 每个参数都要 `TooltipShort="短标签"` **且** `TooltipLong="长描述"` | 属性面板参数名旁空白；`.peqx` 描述退化成脚本名 |
| 同名 CSV | `<脚本名>.csv`（UTF-8 无 BOM），首列 `预设名`，其余列名与参数名逐一对应 | 发布校验直接拒绝：`不可发布：没有同名 CSV` |
| 端口 | 至少 1 个 `s.setPoint(...)` | 校验拒绝：`没有注册端口`，Plant 3D 里接不上管道 |

- `@activate` 的 `TooltipShort` / `TooltipLong` 里**允许出现括号**（`(GB/T 151 BEM)`、`(API 608)`）。解析器按**引号状态**扫描括号，不会在文本内的 `)` 处截断；不要为了"安全"把括号换成全角或删掉。
- 设备（`Group="Equipment"`）另有 `PartType` / `PartSubType` 要求，见 `references/api/07_occ_offline_verification.md` 的 peqx 小节。
- 参数默认值（`def` 签名里的默认值）应与 CSV 第一个规格一致；`STRING` 类型参数（位号、规格）在 `.peqx` 里没有对应类型，会被跳过，但脚本内仍然生效。

### 铁律 17：设备模板（.peqx）发布、中文化呈现与 `_PLANTEQUIPMENTMODIFY` 兼容性终极法则
设备发布走 `.peqx` 模板包（OPC/ZIP），不进管道 `.pcat` 元件库。在发布设备时必须严格遵循以下四大底层铁律，彻底杜绝 `_PLANTEQUIPMENTMODIFY` 报选择无效、创建设备抛 `NullReferenceException` 空引用崩溃、以及中文名称退化为英文等缺陷：

1. **`EquipmentType/@Name` 与 `<DisplayName>` 的职责划分与中文化支持**：
   - **`@Name` 属性必须保持纯 ASCII 脚本英文标识**（如 `EQUIPMENT_SHELL_TUBE_EXCHANGER`）。AutoCAD Plant 3D C++ 宿主在动态加载 Python 模块时调用 `varmain.dynloadVariant(name)`，内部执行了 `name = str(name)`，若 `@Name` 含有中文必在第 0 位抛出 `UnicodeEncodeError` 致命崩溃。
   - **`<DisplayName>` 与 `<Tooltip>` 全面支持 UTF-8 中文**！它们由 .NET 宿主程序集（`PnP3dEquipmentUI.dll`）读取并在 WinForm/WPF 对话框中呈现，原生采用 UTF-16/Unicode，完全支持中文。必须将脚本 `@activate(TooltipShort=u"...")` 提取的中文友好名称（如 `化工固定管板列管换热器 (GB/T 151 BEM)`）直接写入 `<DisplayName>`，严禁将其过度清洗为英文！
   - 提取 `@activate` 与 `@param` 元数据时，正则必须兼容 Python 2 常见的 `u"..."` 前缀（`[uU]?["\']`），确保带有 Unicode 标识的中文字符串不会丢失。

2. **根节点必须包含 `SubType="H"` 或 `SubType="V"`**：
   - 卧式设备（卧式换热器、卧式储罐、泵）：`SubType="H"`；
   - 立式设备（立式容器、反应釜、立式管道泵、加热炉）：`SubType="V"`；
   - **底层校验机理**：图纸中的设备实体为 `PnP3dEquipment`，执行 `_PLANTEQUIPMENTMODIFY` 时，`PnP3dEquipmentUI.dll` 会反查 `.peqx` 中的 `EquipmentType.xml` 并依据 `SubType` 进行模式初始化。若缺失 `SubType`，系统判定实体状态不合法，直接在命令行报错：`选择无效。只能选择一个设备项。`（`Invalid selection. Only one equipment item can be selected.`）。

3. **`<Nozzles>` 节点必须"非空且无 LOC"（同时消除 NullReferenceException 与"选择无效"）**：
   - `Type="C"`（自定义脚本设备）**严禁**使用 `Name="LOC"`（`Type="List"`）管嘴参数：LOC 是 `Type="F"` 基本体设备把管口吸附到第 N 个基本体的专用参数；脚本设备在宿主内部没有基本体列表（`m_primitiveList == null`），带 LOC 会让 `EquBaseDlg.RefreshNozzleProperties` 抛出 `System.NullReferenceException: 未将对象引用设置到对象的实例。`
   - `Type="C"` 的 `<Nozzles>` **同样不能是空容器**：官方全部 `Type="C"` 模板（SumpPump/CAPS1a/Strainer…）都至少含一个 `NozzleInfo`；空 `<Nozzles/>` 只出现在 `Type="F"` 的 `_TEMPLATE-H/V` 中。`Type="C"` + 空 Nozzles 会让 `_PLANTEQUIPMENTMODIFY` 选择校验失败，命令行报 `选择无效。只能选择一个设备项。`。
   - **正确结构**（照官方 SumpPump 风格）：每个端口一个 `<NozzleInfo Name="Nozzle N" PortName="SN" PortIndex="N">`，内含 `<NozzleType PartType="Nozzle" PartSubType="StraightNozzle" EndType="FL" />`、一个以 `.` 开头引用脚本真实直径参数的只读参数（如 `<ParameterInfo Name=".DN_SHELL" ... />`）、以及 `<PortProperties><PropertyInfo Name=".SizeRecordId" DefaultValue="{NOZZLE Catalog 真实法兰 GUID}" /></PortProperties>`。

4. **`PartType` 与 `PartSubType` 必须精准对齐官方原生标准枚举**：
   - 离心泵/管道泵：`PartType="Pump"`, `PartSubType="HorizontalCentrifugalPump"` 或 `"VerticalInlinePump"`；
   - 储罐：`PartType="Tank"`, `PartSubType="GeneralVessel"` 或 `"VerticalVessel"`；
   - 工艺容器/反应釜：`PartType="Vessel"`, `PartSubType="GeneralVessel"`；
   - 列管/板式换热器：`PartType="HeatExchanger"`, `PartSubType="ShellTubeHeatExchanger"`；
   - 严禁使用未注册的非法大类（如 `GlobalEquipment`），否则 Plant 3D 菜单树无法识别归类。

5. **`CustomScripts/variants.map` 映射格式铁律**：
   - 映射条目严格保持 `STEM = STEM`（如 `EQUIPMENT_CENTRIFUGAL_PUMP = EQUIPMENT_CENTRIFUGAL_PUMP`），**严禁带有 `\CustomScripts\` 路径或 `.py` 后缀**！原厂 `dynloadVariant` 内部会自动执行 `p + '.py'` 拼接，若带 `.py` 会解析成 `...py.py` 导致脚本加载失败。

### 铁律 18：等级库没有 S0；S1 不写进 `PartPort`（Plant 3D 2026 已核对，禁止“补端口”）
脚本里的 `s.setPoint` 第 1 个点叫端口 1，但元件库 / 等级库（`.pcat` / `.acat` / `.pspc`）**不是**从 `S0` 或 `PartPort.Name='S1'` 起算。2026 原厂 ASME 元件库（42785 行）、`CS150.pspc`、DIN `10HC01.pspc` 的 `PartPort` 里 **S1 行数都是 0**。

| 口数 | `EngineeringItems` | `PartPort` |
| :--- | :--- | :--- |
| 1（支吊架、管帽、盲板） | `PortName='S1'`，口径 / 端面 / 外径在零件行上 | **没有行**。原厂支吊架目录甚至没有 `Port` 表 |
| 2（弯头、管子、阀门） | 同上，这就是 S1 | 只有 `Name='S2'` |
| 3、4 | 零件行仍是 S1 | `S2`、`S3`、必要时 `S4` |

- **禁止**把 S1 再插进 `PartPort`。弯头会变成 3 个口，Plant 2026 里插不进去。`plant3d_occ/catalog/store.py` 的 `_write_one` 从 `range(2, ports+1)` 写附加端口，就是这个结构。
- 支吊架 `EndType='Undefined_ET'`、`PartCategory='Default'`、选项板上截断成 `Undefined_...`，与原厂 `CSGPRIM` 相同，不是符号丢失。
- 规格编辑器尺寸列表是空的，只在**整张 `Port`/`PartPort` 表都不存在**时发生（例如用没有端口表的 `PipeSupportsSpec` 当配管等级模板，或 `.pspx` 的 `PlantSpecContent` 仍指向别的 `.pspc`）。这和“没有 S1 行”不是一回事。
- 「使用给定的参数无法生成几何图元」是脚本没跑起来或跑崩了（旁边的资源串是「脚本 %s 未找到」）。「找不到表示指定的零件的符号」是几何失败后的块符号回退。都不是缺 S1。

细则与对照表见 `references/api/06_ports_and_interactive_grips.md`。

---

## 五、 调用 PyOCC / plant3d_occ 离线引擎做建模与外形核验

> **依赖声明**：本技能**依赖 `plant3d_occ` 离线引擎**做几何核验。两者分工是：
> - `skills/`（本目录）提供 **规范与判定口径**：原厂体素语义、装饰器/端口规范、防错铁律、验收标准；
> - `plant3d_occ/` 提供 **可执行的同一套语义**：`primitives/`（与 Plant 3D 对齐的 15 个体素与 `varmain.var_basic` 子函数）、`runner/sandbox.py`（脱离 AutoCAD 跑脚本）、`catalog/validate.py`（发布判定）、`catalog/preview.py`（外形/标注渲染）、`catalog/publish.py`（`.acat`/`.peqx` 打包）。
> - **判据一律以 `plant3d_occ` 的实现为准**：文档与代码冲突时信代码（例如 `CYLINDER` 的 `O`、`ARC3D` 的 `D`、`BOX` 的轴向映射都在 `primitives/native.py` 里有唯一权威定义）。详见 `references/api/07_occ_offline_verification.md`。

### 1. 三条标准命令行（外形 / 判定 / 出图）

```bash
# ① 渲染：轴测图（支吊架/设备带真实参数标注，其他构件仅着色；输出 JSON 报告到 stdout）
python plant3d_occ/main.py --render-preview pyscripts/custom_scripts/03_valves/VALVE_BALL.py --output-dir out/

# ② 发布判定：几何有效性 + 悬空/焊合 + 端口 + 包围盒 + 同名 CSV（退出码 0/1 可直接进 CI）
python -m plant3d_occ.catalog.validate pyscripts/custom_scripts/03_valves/VALVE_BALL.py
python -m plant3d_occ.catalog.validate <目录> --json

# ③ 全库外形体检：B-Rep 有效性与包围盒/体积/实体数
python tools/occ_verify/verify_shapes.py --root pyscripts/custom_scripts --json
```

- **`--render-preview` 产出**（只出 4 张，不再生成 `_shape.png`）：
  - `<stem>_640.png`（支吊架/设备为轴测参数标注图，其他构件为轴测着色图；标注只显示真实参数名，不含具体数值）；
  - `<stem>_200.png`（与 `<stem>_640.png` 对应的缩略图，Plant 3D 元件库缩略图就是它）；
  - `<stem>_64.png` / `<stem>_32.png`（着色带边小缩略图：灰面 + 黑面边界线，白底）。
- **更高分辨率消隐图**（1200×1200，`HLRBRep_Algo` 精确消隐，只在可见边正确时才有意义）用 Python API：`preview.render_exact_hlr_family_pngs(shapes, {1200: path}, session=session, params_meta=…, call_values=…)`。
- **核验指标**（顺序不要颠倒，前一条不过后面都没意义）：
  1. **能跑通**：沙箱不抛异常，且 `shapes` 非空；
  2. **几何非空**：包围盒非空且三个方向厚度均 > 0（退化成面/线的都是坏的）；
  3. **B-Rep 有效**：`BRepCheck_Analyzer(...).IsValid()` 为真；
  4. **无悬空**：实体两两间距 ≤ 2 mm（相切焊合件允许，见铁律 13）；
  5. **内孔贯通**：弯头/三通/法兰流道必须打通，壁厚不得为负；
  6. **消隐线干净**：外轮廓光滑无网格棱线，遮挡部分无杂乱虚线。

### 2. Python API：沙箱建模 + 多视角 HLR 合成图
```python
from plant3d_occ.runner.sandbox import run_script_in_sandbox
from plant3d_occ.renderer.offscreen import render_occt_viewer

# 1. 运行建模沙箱（不需要 AutoCAD；返回 (session, entry_name, shapes)）
session, entry_name, shapes = run_script_in_sandbox(
    "pyscripts/custom_scripts/01_pipe_fittings/ELBOW_90.py")

# 2. 生成正交多视角四视图合成大图（等轴测/正视/俯视/右视）
render_occt_viewer(shapes, output_png_path="cad_renders/ELBOW_90_views.png",
                   show_gui=False, render_mode="hlr")
```
- **多视角核验要点**：
  - **东南等轴测 (SE Iso)**：检验总成三维空间立体感与相对装配位置；
  - **正视图 (Front / XZ)**：检验生根立柱高度、法兰厚度及竖向对齐；
  - **俯视图 (Top / XY)**：检验横梁开孔、螺栓均布圆及管向投影；
  - **右视图 (Right / YZ)**：检验支撑间隙、加强筋板厚度及坡口倒角。

---

## 六、 无人值守 AutoCAD Plant 3D 自动化测试与模态阻塞防护 (Unattended Verification)

若当前运行宿主环境中已安装真实 AutoCAD Plant 3D（检测到 `acad.exe`），技能内建自包含脚本 `scripts/unattended_runner.py`（在项目内也可直接使用 `tools/autocad_runner/unattended_runner.py` 或快捷入口 `tools/unattended_plant3d_runner.py`）一键拉起无人值守真机验收流水线：

### 1. 命令行执行方式
```bash
# 优先使用 Skill 内置自包含脚本：
python <skill_dir>/scripts/unattended_runner.py --scripts-dir pyscripts/custom_scripts --output-dir pyscripts/cad_renders --close-after

# 或在项目根目录下直接调用：
python tools/autocad_runner/unattended_runner.py --scripts-dir pyscripts/custom_scripts --output-dir pyscripts/cad_renders --close-after
```

### 2. 自动化机制与核心保障
1. **自动配置注册表安全绕行 (SECURELOAD=0 & TRUSTEDPATHS)**：启动前自动扫描注册表全版本 AutoCAD 配置，将 `SECURELOAD` 设为 `0` 并将 `ApplicationPlugins` 及工程目录注入 `TRUSTEDPATHS`，**彻底杜绝启动时弹出「安全性 - 未签名的可执行文件 / 是否加载此插件」的模态阻塞对话框**；
2. **多层模态阻塞看门狗 (Modal Watchdog)**：基于 Win32 API 与 Windows TaskDialog / DirectUI 协议实时监控。针对安全弹窗自动触发 `Alt+A` / `CommandLink-1001` 始终加载；为“发生未处理异常”自动点击「继续」；为“图形修复管理器/代理信息/缺失字体”自动点击「关闭/确定/忽略」，确保 CAD 进程绝不因弹窗而挂起阻塞；
3. **自动下发批处理命令**：自动发送 `PYBATCH_RUN` 命令，在 CAD 内部逐个加载构件脚本、应用真实材质着色 (`ShadedWithEdges`)、全屏自适应，每个构件只生成一张轴测图或四视图拼图；
4. **精准捕获真实 Python 异常堆栈**：一旦脚本出错，通过 `dev_reload.log` 完整捕获出错文件、函数与具体报错代码行，输出至 `batch_report.json`，便于 AI 或开发者实施精准定向修复。


