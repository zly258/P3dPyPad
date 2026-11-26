# 化工行业 AutoCAD Plant 3D 参数化元件库（170 套 Plant 3D 原生规范版）

- **构件总数**：170 套（全部通过 `plant3d_occ` 几何/端口校验 `170/170 PASS`，并通过 Plant 3D 目录解析 `inspect_script` 0 告警验证）
- **总规格行数**：1876 档（其中逐行核实标准原表 **1431 档**）
- **Plant 3D 原生 CSV 数据格式**：全部非设备 CSV 均已标准化为 Plant 3D / P3dPyPad 原生字段（`PartNumber`, `DN`, `DN2`, `DN3`, `EndType`, `EndType2`, `PressureClass`, `Facing`, `Schedule`, `Standard`, `SKEY`, `ShortDesc`, `LongDesc` + `@param` 几何参数列），单元格零内置逗号，可直接用于 `P3dPyPad` 一键写入 `.acat/.pcat/.pspc` 或导入 Plant 3D Spec Editor。
- **本次核心升级**：
  1. **管件（02_pipe_fittings，28 套）**：872 档（847 档核实标准表），异径件全面映射标准 `DN2`/`DN3` 端口口径。
  2. **阀门（03_valves，27 套）**：由 114 档扩充至 **336 档**（259 档逐行核实自 ASME B16.10 CL150/300/600 与 API 609 Cat A）。
  3. **法兰、盲板与垫片（01_flanges，22 套）**：由 193 档扩充至 **367 档**（325 档核实标准表，新增 HG/T 20592 PN40 全口径、ASME B16.48 8字/插板盲板 CL150/300、ASME B16.20 缠绕垫与 RTJ 八角环垫）。
  4. **非标设备（06_equipment，29 套）**：每套仅保留 1 行默认外形模板；修正 `EQ_TANK_STAIR_PLATFORM` 名称与护栏连续结构；明显区分 `EQ_HEAT_EXCHANGER_AES`（前端可拆平盖+吊盖旋臂+加大浮头外头盖）与 `EQ_HEAT_EXCHANGER_BEM`（对称整体封头+轴向端头接管+壳体中部波纹膨胀节）。
