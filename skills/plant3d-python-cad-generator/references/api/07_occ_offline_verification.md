# 07 · `plant3d_occ` 离线核验链路（沙箱 / 判定 / 出图 / 打包）

本分册是**判定口径的唯一权威**。`skills/` 里的规范、模板、铁律都按这里的实现口径写；
文档与代码冲突时，以 `plant3d_occ/` 的源码为准。

适用范围：**不需要 AutoCAD**。装了 `pythonocc-core` + `numpy` + `Pillow` 就能跑几何与校验；
装了 `PySide6` 才能跑 GUI（`main.py` 的界面）。

```
plant3d_occ/
├── primitives/      原生体素 + var_basic 子函数（与 Plant 3D 对齐的语义层）
├── core/            OccBody（链式 API）、OccSession（端口/握点/尺寸）、布尔与有效性判定
├── runner/sandbox.py 脱离 AutoCAD 执行脚本（py2.7 兼容垫片）
├── catalog/model.py  脚本元数据解析（@activate/@group/@param、CSV、域分类）
├── catalog/validate.py 发布判定
├── catalog/preview.py  外形图 / 轴测标注图渲染
├── catalog/publish.py  .acat / .peqx 打包
└── renderer/        离屏查看器、HLR、多视图合成
```

---

## 一、沙箱执行

```python
from plant3d_occ.runner.sandbox import run_script_in_sandbox

session, entry_name, shapes = run_script_in_sandbox(path, kwargs=None)
#   kwargs：覆盖脚本默认值的参数字典，如 {"D": 168.3, "H": 1200.0}
```

- 返回的 `shapes` 是 `OccBody` 列表（不是裸 `TopoDS_Shape`）。取裸形状：`body.shape` 或 `session.get_final_shapes()`。
- 沙箱会做三件兼容处理，所以**同一份脚本能同时跑在 Plant 3D（Python 2.7）和这里的 Python 3**：
  1. `reload(sys)` / `sys.setdefaultencoding('utf-8')` 被安全改写为 no-op；
  2. `varmain.primitiv` / `varmain.custom` / `varmain.var_basic` / `varmain.divsub.*` / `aqa.math` / `pyvariant` 提供同名模块；
  3. `@activate` / `@group` / `@param` / `@enum` 的逆序栈语义被复刻，所以装饰器顺序与空行规则照旧生效。
- 脚本里出现未实现的系统模块时会抛 `ImportError`——这是**脚本依赖了本机没有的原厂子模块**的信号，不是几何错误。

`OccSession` 上可直接读的核验数据：

| 属性 | 内容 |
| :--- | :--- |
| `session.ports` | `[{"point": (x,y,z), "dir": (x,y,z)}, ...]`，来自 `s.setPoint` |
| `session.grips` | `[{"name", "pt1", "pt2", "ext_dir"?, "style"?}, ...]`，来自 `s.setLinearDimension` |
| `session.get_final_shapes()` | 合并共面后的最终实体（已做 `ShapeUpgrade_UnifySameDomain`，且**只在结果有效时**才采用） |

---

## 二、发布判定 `catalog/validate.py`

```bash
python -m plant3d_occ.catalog.validate <脚本或目录> [--params D=168.3 H=1200] [--json]
```

```python
from plant3d_occ.catalog import validate
result = validate.validate_script(path)      # dict
result["ok"]        # bool：issues 为空才为 True
result["issues"]    # 致命问题（必须修）
result["warnings"]  # 提示（允许通过）
result["solids"]    # 实体个数
result["ports"]     # 端口个数
result["bbox"]      # [xmin, ymin, zmin, xmax, ymax, zmax]
result["entry"]     # 入口函数名
```

判定顺序（任一条不过即 `ok=False`，后面的检查不再有意义）：

| # | 判定 | 口径 | 不合格文案 |
| :--- | :--- | :--- | :--- |
| 1 | 可发布 | `model.inspect_script` 不报错、没有 `skip_reason`（最常见原因：**缺同名 CSV**、缺 `@activate`、缺 `Group`） | `不可发布：没有同名 CSV` |
| 2 | 能跑 | 沙箱不抛异常 | `运行失败：…` |
| 3 | 有实体 | `shapes` 非空、实体里至少 1 个 `TopoDS_SOLID` | `没有产出任何实体` / `实体里没有有效的 SOLID` |
| 4 | **无悬空** | 多实体时按包围盒间距判定：任一实体与其余**全部**实体间距 `> FLOATING_GAP(2.0 mm)` → 悬空（issue）；全部 `≤ 2 mm` → 相切焊合（warning） | `有 N 个实体悬空（与其余实体间距 > 2.0 mm…）` |
| 5 | 有端口 | `s.setPoint` 至少 1 个。这是几何端口，**不是** `PartPort` 行数；S1 不进 `PartPort`，见 `06_ports_and_interactive_grips.md` §2.0 | `没有注册端口（s.setPoint），Plant 3D 里接不上管道` |
| 6 | 包围盒可用 | 非空、有限、三个方向厚度 `> 0` | `包围盒为空` / `包围盒…退化（厚度为 0）` |
| 7 | 端口位置 | 管件/阀门/仪表：端口点必须在包围盒内（容差 `PORT_TOLERANCE = 1.0 mm`）；支吊架：只校验"别超过包围盒对角线" | `端口 N 在 (…) 落在包围盒…之外` |

> **不要用"实体数 = 1"当判据**。OCC 在内核层面无法把相切面融成单实体（螺母端面贴钢板、
> 衬板与管壁相切都属此类），这类焊合件外形正确，只出 warning。真正的缺陷是**间距 > 2 mm 的悬空**。

---

## 三、外形与标注出图 `catalog/preview.py`

```bash
# 命令行
python plant3d_occ/main.py --render-preview <脚本> --output-dir out/
# stdout 输出 JSON：{"ok": true, "paths": {"640": "...", "200": "...", ...}}
```

```python
from plant3d_occ.catalog import preview
from plant3d_occ.catalog.model import inspect_script, needs_dimension_annotation

display = preview.open_offscreen_display()                  # 离屏 OpenGl 上下文
job = inspect_script(script_path)
paths = preview.render_custom_script_previews(               # 支吊架/设备带参数标注，其他仅着色
    display, shapes, out_dir, stem,
    session=session, params_meta=params_meta, call_values=call_values,
    annotate=needs_dimension_annotation(job))
preview.render_exact_hlr_family_pngs(                        # 精确消隐线（HLRBRep_Algo）
    shapes, {1200: os.path.join(out_dir, stem + "_dim.png")},
    session=session, params_meta=params_meta, call_values=call_values)
preview.close_display(display)
```

| 输出 | 内容 | 用途 |
| :--- | :--- | :--- |
| `<stem>_640.png` | 1200×1200 精确消隐线 + 轴测尺寸标注（发布主图） | 尺寸核对 |
| `<stem>_200.png` | 标注图缩略，Plant 3D 元件库缩略图 | 发布 |
| `<stem>_64/32.png` | 着色带边小缩略图（灰面 + 黑边界线，白底） | 发布 |
| `<stem>_dim.png`（自定名） | 1200×1200 精确消隐线 + 标注 | 交付图纸 |

**标注来源**（决定"标注完不完整"）：

1. 脚本自己注册的 `s.setLinearDimension(name, pt1, pt2)` —— 优先级最高，标签就是参数名；
2. 若没有注册 `D`/`D_VESSEL`/`D_CASE`，自动在 0 号端口处补一个管径尺寸；
3. 不再按包围盒合成 `总长`/`总宽`/`总高` 等概括尺寸；没有真实参数注册时不补标注。

`params_meta` / `call_values` 传 `model.inspect_script(path)` 的 `params_meta` 与 `sizes[0]["call"]`；
标注标签只显示真实参数名，不显示具体数值。**文字字体中文优先**（微软雅黑/黑体/宋体），
Arial 没有中文字形会把中文标签渲染成方框。

---

## 四、CSV 尺寸表与元数据解析 `catalog/model.py`

```python
from plant3d_occ.catalog.model import inspect_script
job = inspect_script(path)
```

关键字段：

| 字段 | 说明 |
| :--- | :--- |
| `stem` / `group` / `domain` | 脚本名、`@activate(Group=)`、域（`piping` / `support` / `instrumentation` / `equipment`） |
| `tooltip_short` / `tooltip_long` | `@activate` 里的短名与长描述（**peqx 的 DisplayName 取这里**） |
| `ports` / `length_unit` / `first_port_endtypes` | 端口数、单位、首端口端部类型 |
| `params` / `params_meta` | 参数表与带 `tooltip`/`tooltip_long`/`ask4dist`/`group` 的元数据，供属性面板与 `s.setLinearDimension` 对齐 |
| `sizes` | CSV 规格行：`[{"name": "DN100_…", "call": {...}}, ...]` |
| `csv_path` / `skip_reason` | 同名 CSV 路径；缺 CSV 时 `skip_reason` 为 `没有同名 CSV` |

**同名 CSV 规范**：`<脚本名>.csv`，UTF-8（无 BOM），首行表头，**首列固定 `预设名`**，
其余列名与脚本参数名逐一对应；额外列（如 `DN`）会被当作透传参数，脚本用 `**kw` 吞掉即可。

---

## 五、打包：`.acat`（构件）与 `.peqx`（设备）

```python
from plant3d_occ.catalog.publish import publish_scripts
publish_scripts(paths, content_dir=…, validate=True, auto_generate_sizes=True,
                equipment_type=("Pump", "HorizontalCentrifugalPump"))   # 仅对设备生效
```

### 构件（`Group` 非 `Equipment`）→ `CustomScripts/`
| 产物 | 作用 |
| :--- | :--- |
| `<stem>.py`（+ `.pyc`） | 脚本本体，Plant 3D 编译后加载 |
| `<stem>.xml` | `ArrayOfScript` 参数声明（`LDesId`/`SDesId` 是**本地化键**，取值范围就是脚本名，显示文本来自脚本 `@activate`） |
| `<stem>_200/640.png` 等 | 缩略图与标注示意图 |
| `variants.map` | 脚本名 → `\CustomScripts\<stem>.py` 的注册表 |
| `ScriptGroup.xml` | 分组菜单归属 |

### 设备 `Group="Equipment"` → `CPak Common\equipment\<stem>.peqx`
`.peqx` 是 zip，内部固定结构：

```
[Content_Types].xml
_rels/.rels                          EquipmentType 关系 + 预览图关系
content/EquipmentType.xml            Name / Type=C / PartType / PartSubType / GUID
preview/<name>.png                   200×200 参数示意图（可缺）
```

硬约束（漏了 Plant 3D 设备菜单里就看不到）：

- `EquipmentType/@Name` **必须等于脚本名**（不含 `.py`）；
- `@Type="C"`（完全脚本定义）；
- `@GUID` 按脚本名做 `uuid5`，同脚本可重复生成且不变；
- `@PartType` / `@PartSubType` 必须取自自带模板出现过的组合。

`PartType / PartSubType` 合法组合（`catalog/equipment.py` 的 `EQUIPMENT_TYPES` / `EQUIPMENT_TYPE_CHOICES`）：

| 设备 | PartType | PartSubType |
| :--- | :--- | :--- |
| 通用设备 | `GlobalEquipment` | `GeneralVessel` |
| 容器 | `Vessel` | `GeneralVessel` |
| 储罐（立式/卧式） | `Tank` | `VerticalVessel` / `GeneralVessel` |
| 离心泵 | `Pump` | `HorizontalCentrifugalPump` |
| 立式管道泵 | `Pump` | `VerticalInlinePump` |
| 潜污泵 | `Pump` | `CentrifugalSumpPump` |
| 管壳式换热器 | `HeatExchanger` | `ShellTubeHeatExchanger` |
| 板式换热器 | `HeatExchanger` | `PlateAndFrameExchanger` |
| 加热炉 | `Heater` | `FiredHeater` |
| 过滤器 | `StrainerEquipment` | `General` |

参数类型映射：`LENGTH→d`、`LENGTH0→d0`、`ANGLE→a`、`INT→r`、`BOOL→b`、`STRING→跳过`（脚本内仍生效）。

### 元数据解析与设备包发布的四个防错坑（已修，勿回退）

1. **`@activate` 括号**：`TooltipShort="… (GB/T 151 BEM)"` 里的 `)` 曾让 `[^)]*` 正则提前截断，
   导致脚本发布名退化成脚本名。现行实现 `model.activate_body()` 按**引号状态**扫描括号，
   文本里带括号是合法的，不要删。
2. **`TooltipShort` / `TooltipLong` 缺一**：属性面板参数名旁会空白，`.peqx` 描述会退化成脚本名。
   两者都要写。
3. **Unicode `u"..."` 前缀解析**：Python 2.7 脚本中中文字符串通常带有 `u` 前缀（`TooltipShort=u"..."`）。
   元数据解析正则必须显式包含 `[uU]?["\']`，严禁只写 `["\']`，否则会导致整段中文短描述提取失败。
4. **设备包 `.peqx` 的 SubType 与 Nozzles 约束**：
   - 根节点必须包含 `SubType="H"` 或 `SubType="V"`，否则 `_PLANTEQUIPMENTMODIFY` 报“选择无效”；
   - `Type="C"` 的 `<Nozzles>` 必须**非空且无 LOC**：带 `Name="LOC"`（Type="List"）会因脚本设备没有基本体列表而抛 `NullReferenceException`；完全空的 `<Nozzles/>`（仅 Type=F 模板合法）会让 MODIFY 选择校验失败报“选择无效”。正确做法是按脚本 `Ports` 数量生成官方 SumpPump 风格的 `NozzleInfo`（`PortName="SN"` + `PortIndex="N"` + 引用脚本直径参数的 `.` 前缀只读参数 + `.SizeRecordId`），严禁 LOC；
   - `EquipmentType/@Name` 保持纯 ASCII，而 `<DisplayName>` 与 `<Tooltip>` 全面支持 UTF-8 中文显示。

---

## 六、核验工具（仓库内，可直接对任意脚本库跑）

```bash
python tools/occ_verify/verify_primitives.py     # 19 条原语契约自检（BOX 轴向、O、D 半径…）
python tools/occ_verify/verify_shapes.py --root <脚本目录> --json   # 全库外形体检
```

`verify_primitives.py` 覆盖的契约（全部应 PASS，任何一条 FAIL 说明语义层被改坏）：
`BOX` 轴向映射（H→X, L→Y, W→Z）、`CYLINDER` 的 `O` 内孔、椭圆重载、`CONE` 偏心 `E`、
`TORUS`、`HALFSPHERE`、`ELLIPSOIDHEAD/SEGMENT`、`PYRAMID/ROUNDRECT/SPHERESEGMENT` 生长方向、
`ARC3D` 的 `D` 是**半径**、`translate/rotateX/rotateY` 顺序、`subtractFrom/uniteWith` 结果有效性。

---

## 七、已知内核限制（不是脚本 bug，不要"修"）

| 现象 | 原因 | 处理 |
| :--- | :--- | :--- |
| 相切面并集后仍是 2 个 SOLID | OCC 无法在相切（零厚度接触）处融成单实体 | 允许；`validate` 只给 warning |
| 某些装配体布尔返回空几何 | OCCT 在退化拓扑上返回"有效但为空"的复合体 | 引擎已加包围盒非空判定并保留上一步结果；不要去改脚本凑几何 |
| `SetFuzzyValue(1e-4)` 反而产出无效壳 | 容差把相邻面糊在一起 | 引擎按"精确→校验→fuzzy 重试→取最后有效"三态处理 |
| `ShapeUpgrade_UnifySameDomain` 把输入改坏 | 该 API **原地改写**拓扑 | 引擎在副本上合并，且只在结果有效时采用 |
