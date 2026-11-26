[English](#english) | [简体中文](#简体中文)

## English

### Chemical Industry AutoCAD Plant 3D Parametric Component Library (170 Scripts)

This directory contains **170** parametric Python component scripts and **170** co-located CSV specification tables (`1,876` total spec rows, including `1,431` rows verified against published standards) for AutoCAD Plant 3D 2019–2026.

- **Full Component Index**: [CATALOG_INDEX.csv](./CATALOG_INDEX.csv)
- **AutoCAD Plant 3D 2026 Ready-to-Use Bundle Guide**: [Plant 3D 2026 Installation & Usage Guide](../../docs/%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E(AutoCAD%20Plant%203D%202026).md)
- **Release Downloads (`v1.1.0`)**: [GitHub Releases (`ChemicalPlant170-Plant3D2026-v1.1.0.zip`)](https://github.com/zly258/P3dPyPad/releases/tag/v1.1.0)
- **Online 3D Workbench & Report**: [https://zly258.github.io/P3dPyPad/](https://zly258.github.io/P3dPyPad/)

#### Category Breakdown

| Category | Directory | Scripts | Coverage |
|---|---|---:|---|
| Flanges, Blinds & Gaskets | `01_flanges/` | 22 | `HG/T 20592`, `ASME B16.5` / `B16.47` / `B16.48` / `B16.20`, `NB/T 47023`, `ISO 2852` (367 spec rows) |
| Pipe Fittings & Olets | `02_pipe_fittings/` | 28 | `GB/T 12459`, `GB/T 14383`, `GB/T 19326`, `SH/T 3408` elbows, tees, crosses, reducers, caps (872 spec rows) |
| Industrial Valves | `03_valves/` | 27 | Gate, globe, ball, butterfly, check, knife gate, diaphragm, plug, safety PSV/pilot, steam trap (336 spec rows) |
| Process Instruments | `04_instruments/` | 22 | Control valves, flowmeters, level gauges/transmitters, pressure/temperature instruments |
| Pipe Supports & Hangers | `05_supports/` | 19 | Pipe shoes, clamps, U-bolts, spring hangers, rigid rod hangers, trunnions, guides |
| Process Equipment | `06_equipment/` | 29 | Towers, reactors, heat exchangers (`AES`/`BEM`/`BKU`), storage tanks, pumps, compressors, vessels |
| Specialty Piping Items | `07_specialty/` | 23 | Strainers, sight glasses, expansion joints, flame arresters, flexible hoses, breather valves, sample coolers |
| **Total** | **`pyscripts/custom_scripts/`** | **170** | **170 CSV tables / 1,876 spec rows (1,431 standard-verified)** |

#### CSV & Placement Notes

- All non-equipment CSVs follow the native Plant 3D / P3dPyPad schema (`PartNumber`, `DN`, `DN2`, `DN3`, `EndType`, `EndType2`, `PressureClass`, `Facing`, `Schedule`, `Standard`, `SKEY`, `ShortDesc`, `LongDesc`, plus `@param` columns) with no embedded commas inside cells.
- **90-degree valves** (`VALVE_ANGLE_GLOBE`, `VALVE_SAFETY_PSV`, `VALVE_SAFETY_PILOT`) have perpendicular ports and must be connected to pipe endpoints or equipment nozzles, not inserted into the middle of a continuous straight pipe.

---

## 简体中文

### 化工行业 AutoCAD Plant 3D 参数化元件库（170 套原生规范版）

本目录收录 **170** 套面向 AutoCAD Plant 3D 2019–2026 的化工行业参数化 Python 构件脚本及 **170** 份同目录 CSV 规格表（合计 **1,876 档**规格，其中 **1,431 档**逐行核实自标准原表）。

- **全量构件索引表**：[CATALOG_INDEX.csv](./CATALOG_INDEX.csv)
- **AutoCAD Plant 3D 2026 成品库安装使用说明**：[使用说明(AutoCAD Plant 3D 2026).md](../../docs/%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E(AutoCAD%20Plant%203D%202026).md)
- **成品压缩包下载（`v1.1.0`）**：[GitHub Releases (`ChemicalPlant170-Plant3D2026-v1.1.0.zip`)](https://github.com/zly258/P3dPyPad/releases/tag/v1.1.0)
- **在线三维工作台 / 报告地址**：[https://zly258.github.io/P3dPyPad/](https://zly258.github.io/P3dPyPad/)

#### 分类统计

| 分类 | 目录 | 脚本数 | 覆盖范围 |
|---|---|---:|---|
| 法兰、盲板与垫片 | `01_flanges/` | 22 | `HG/T 20592`、`ASME B16.5` / `B16.47` / `B16.48` / `B16.20`、`NB/T 47023`、`ISO 2852`（367 档） |
| 管件与支管台 | `02_pipe_fittings/` | 28 | `GB/T 12459`、`GB/T 14383`、`GB/T 19326`、`SH/T 3408` 弯头、三通、四通、异径管、管帽（872 档） |
| 工业阀门 | `03_valves/` | 27 | 闸阀、截止阀、角阀、球阀、蝶阀、止回阀、刀闸阀、隔膜阀、旋塞阀、安全阀 PSV/先导式、疏水阀（336 档） |
| 过程仪表 | `04_instruments/` | 22 | 调节阀、流量计、液位计/变送器、压力/温度仪表 |
| 管道支吊架 | `05_supports/` | 19 | 管托、管卡、U 型螺栓、弹簧吊架、刚性吊杆、耳轴、导向架 |
| 化工工艺设备 | `06_equipment/` | 29 | 塔器、反应釜、换热器（`AES`/`BEM`/`BKU`）、储罐、离心/计量/多级泵、压缩机、容器 |
| 特种配管元件 | `07_specialty/` | 23 | 过滤器、视镜、膨胀节、阻火器、金属软管、呼吸阀、取样冷却器等 |
| **合计** | **`pyscripts/custom_scripts/`** | **170** | **170 份 CSV 规格表 / 1,876 档规格（1,431 档核实标准原表）** |

#### 数据格式与使用注意事项

- 全部非设备 CSV 均采用 Plant 3D / P3dPyPad 原生字段（`PartNumber`、`DN`、`DN2`、`DN3`、`EndType`、`EndType2`、`PressureClass`、`Facing`、`Schedule`、`Standard`、`SKEY`、`ShortDesc`、`LongDesc` + `@param` 几何参数列），单元格零内置逗号，可直接导入 Plant 3D Spec Editor 或通过 P3dPyPad 一键发布。
- **90° 角式阀门**（`VALVE_ANGLE_GLOBE`、`VALVE_SAFETY_PSV`、`VALVE_SAFETY_PILOT`）两端口互相垂直，放置时需连接在管道**开放端点**或**设备管嘴**上，不可直接插入连续直管中间。
