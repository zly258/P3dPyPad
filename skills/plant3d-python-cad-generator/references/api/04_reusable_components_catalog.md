# AutoCAD Plant 3D 原厂可复用组件全量目录与参数物理含义手册（`04_reusable_components_catalog.md`）

> **数据来源**：基于 `variants.zip` 22 个子目录 5,698 个核心 `.pyc` 模块 AST 静态扫描整理。涵盖公共型钢、紧固件、支吊架、弯头、三通、大小头、法兰、阀门、执行机构与非标设备组件的名称、所在模块、功能说明及参数物理含义。

---

## 一、 原厂内置可复用组件源码总表（Component Reference Catalog）

以下汇总 `variants.zip` 全部 22 个子目录中的核心可复用母版组件、模块导入路径、组件工程含义、完整参数签名及参数物理意义：

### 5.1 支吊架组件库 (`varmain.supportssub.*`)

| 组件函数名 | 模块导入路径 (`from ... import *`) | 组件工程名称与几何特征 | 完整参数列表与物理意义 |
| :--- | :--- | :--- | :--- |
| **`CSGB000`** | `varmain.supportssub.csgbsub.csgb000` | 基础T型滑托（含底板、腹板、可选垫板） | `D` 管外径, `SL` 管托长, `SW` 底板宽, `ST` 板厚, `SH` 管底至底板高, `HL/HW/HH` 底部垫板长/宽/高 |
| **`CSGB001`** | `varmain.supportssub.csgbsub.csgb001` | 双管卡T型管托（T型滑托 + 前后双 `CSGC002` 管卡） | `D` 管外径, `L` 管卡宽, `W` 管卡厚, `K` 管卡总长, `SL/SW/ST` 管托长/宽/厚, `SH` 管心至底面高, `E` 管卡边距, `HL/HW/HH` 垫板尺寸 |
| **`CSGB002`** | `varmain.supportssub.csgbsub.csgb002` | 双腹板H型鞍座管托（双立板间距 `SD` + 双管卡） | 在 `CSGB001` 基础上增加 `SD`（双腹板间距） |
| **`CSGB003`** | `varmain.supportssub.csgbsub.csgb003` | 带侧向限位挡块的滑动管托 | 同 `CSGB001`，底板两侧带限位翼板 |
| **`CSGB004`** | `varmain.supportssub.csgbsub.csgb004` | 带前后筋板与腹板减重孔的鞍式管托 | `D` 管外径, `SL/SW/ST` 管托长/宽/厚, `SH` 管底至底板高, `SE` 筋板边距, `SC` 减重八角孔切角尺寸, `P` 是否带端板 (`0/1`), `HL/HW/HH` 垫板 |
| **`CSGB005`** | `varmain.supportssub.csgbsub.csgb005` | U型螺栓固定鞍式管托 | `D` 管外径, `SL/SW/ST/SH/SE/SC` 鞍座参数, `BH` U型螺栓深, `CD` 螺栓杆径, `BL` 横担宽, `P` 端板标志, `C` U型螺栓数量 (`1` 或 `2`) |
| **`CSGB006`** | `varmain.supportssub.csgbsub.csgb006` | U型螺栓简易T型管托 | `D, SL, SW, ST, SH, BL, CD, P, C`（无腹板减重孔） |
| **`CSGB007`** | `varmain.supportssub.csgbsub.csgb007` | 导轨式底座滑托（带底部槽道） | `D, SL, SW, ST, SH, HW, LL, LW` |
| **`CSGB008`** / **`009`** | `varmain.supportssub.csgbsub.csgb008` | 宽幅抱箍管托 / 双抱箍焊接管托 | `D` 管外径, `L` 抱箍长, `W` 抱箍厚, `K` 耳板跨距, `SL/SW/ST/SH` 支座尺寸 |
| **`CSGB010`** / **`011`** | `varmain.supportssub.csgbsub.csgb010` | 弧形板焊接鞍座（带包角 `E` 与底板 `BL/BW/BH`） | `D` 管外径, `L/W/K` 管卡尺寸, `SL/SW/ST/SM/SD` 鞍板参数, `E` 包角(度), `SH` 高度(`011`), `BL/BW/BH` 底板 |
| **`CSGB012`** | `varmain.supportssub.csgbsub.csgb012` | 多向十字翼板保冷/保温管托 | `D, L, W, K, SL, SW, ST, SH`, `TI` 翼板位掩码 (`1/2/4/8`), `CS` 管卡模式 |
| **`CSGB013`** | `varmain.supportssub.csgbsub.csgb013` | 扇形多筋板保冷护壳管托 | `D` 管外径, `T` 保温厚, `L` 护壳长, `A` 扇形包角(`120°`), `TW` 板厚, `N` 径向筋板数量 |
| **`CSGC000`** | `varmain.supportssub.csgcsub.csgc000` | U型螺栓组件（含圆环抱箍、双螺杆、横担板、双螺母） | `D` 管外径, `L` 伸出长, `W` 螺杆直径, `BL/BW/BH` 横担长/宽/高, `MW/MH/MD` 螺母宽/高/位置 |
| **`CSGC001`** | `varmain.supportssub.csgcsub.csgc001` | 扁钢欧姆型（$\Omega$ 型）管卡（带底板） | `D` 管外径, `L` 扁钢宽, `W` 扁钢厚, `K` 总跨宽, `BL/BW/BH` 底座长/宽/高 |
| **`CSGC002`** | `varmain.supportssub.csgcsub.csgc002` | 标准双耳对夹扁钢管卡（最常用子组件） | `D` 管外径, `L` 扁钢宽, `W` 扁钢厚, `K` 双耳总跨距 |
| **`CSGC003`** | `varmain.supportssub.csgcsub.csgc003` | 带立柱吊耳的双螺栓管夹 | `D` 管外径, `L` 管卡宽, `W` 管卡厚, `K` 下耳跨距, `H` 上吊耳高度 |
| **`CSGC004`** | `varmain.supportssub.csgcsub.csgc004` | 带六角减振块/加强套的管夹 | 在 `CSGC003` 基础上增加 `M1`（六角块厚）、`M2`（六角块高） |
| **`CSGC005`** | `varmain.supportssub.csgcsub.csgc005` | 立管承重双耳管卡（不对称或加宽耳板 `K1, K2`） | `D` 管外径, `L` 管卡宽, `W` 管卡厚, `K1` 上翼宽, `K2` 下翼宽 |
| **`CSGD001`** | `varmain.supportssub.csgdsub.csgd001` | 直管段假管支座（Dummy Leg，溶接于弯头） | `D` 假管外径, `L` 假管长, `OF` 壁厚, `IL` 插入余量（另有 `_F_`, `_MJ`, `_OF`, `_OM`, `_PL` 端口变体） |
| **`CSGE001`~`004`** | `varmain.supportssub.csgesub.csge001` | 型钢悬臂架/L型托臂/角钢斜撑组合支架 | `D` 管外径, `L` 立柱高, `LS/WS/BL/BW/BH` 管卡参数, `WT/HT/TT` T型钢立柱, `WL/HL/TL/LL` L角钢横担, `NO/NL/NW/NT` 筋板, `SL/SW/ST` 底板 |
| **`CSGF001`~`004`** | `varmain.supportssub.csgfsub.csgf001` | 可调螺纹立柱支座 / 变径套筒支腿（带 `CSGCutOut` 马鞍口） | `D` 支腿管径, `L` 总高, `AL` 螺杆段长, `MD/MH/MW` 调节螺母尺寸, `SL/SW/ST` 底板尺寸, `**kw` 传入 `OD/OR/OO` 自动切马鞍口 |
| **`CSGH001`~`009`** | `varmain.supportssub.csghsub.csgh001` | 弹簧吊架、花兰螺丝吊杆、单/双滚轮悬吊架家族 | `D` 管外径, `H` 悬吊总高, `L/W/K` 管卡尺寸, `HL1` 吊耳高, `HL2/HD21/HD22` 弹簧缸/花兰螺丝尺寸, `HD3` 吊杆直径, `HT4/HL4/HW4/HH4` 顶部生根耳座尺寸 |
| **`CSGR000`~`008`** | `varmain.supportssub.csgrsub.csgr000` | 滚轮管托家族（单滚轮、双滚轮、带底座/可调螺杆/V型轮） | `D` 管外径, `RD` 滚轮外径, `RL` 滚轮长, `RDI` 滚轮内轴径, `RLI` 中部平段长, `RTYPE` 滚轮截面类型(`0~3`), `DOUBROLL` 双排滚轮标志(`0/1`), `H` 支座高 |
| **`CSGT001`~`002`** | `varmain.supportssub.csgtsub.csgt001` | 双吊杆横担门式吊架（Trapeze Hanger） | `L` 双吊杆中心距, `W` 横担宽, `K` 横担高, `O` 横担两端悬挑长, `H1/H2` 左右吊杆高度, `HD3` 吊杆直径, `HT4/HL4/HW4/HH4` 顶部生根座 |

### 5.2 弯头、法兰、三通、四通、大小头、支管台、阀门与设备组件库

| 类别子目录 | 核心组件函数名与模块路径 | 组件工程说明 | 核心参数物理意义 |
| :--- | :--- | :--- | :--- |
| **弯头 (`arcsub`)** | `CPB` (`varmain.arcsub.cpbsub.cpb`)<br>`CPBD` (`varmain.arcsub.cpbdsub.cpbd`)<br>`CPBE` (`varmain.arcsub.cpbesub.cpbe`)<br>`CPBN` (`varmain.arcsub.cpbnsub.cpbn`)<br>`CPBP` (`varmain.arcsub.cpbpsub.cpbp`)<br>`CPBS` (`varmain.arcsub.cpbssub.cpbs`)<br>`CPBT` (`varmain.arcsub.cpbtsub.cpbt`) | `CPB` 标准/变径弯头（带直段 `L1, L2`）<br>`CPBD` 带底脚支座弯头（Base Elbow，`DFT=0~5` 支持圆管/方管/圆锥/四棱锥支座）<br>`CPBE` 双承口弯头<br>`CPBN` 带接管嘴弯头（Side Outlet Elbow）<br>`CPBP` 长半径直段弯管<br>`CPBS` 虾米腰焊接弯头（`S` 节数）<br>`CPBT` 带直段虾米腰弯头 | `D` 端1外径, `D2` 端2外径, `R` 弯曲半径, `A` 弯曲角(度), `L1/L2` 两端直段长, `OF` 壁厚, `S` 虾米腰节数, `DFH/DFD/DFT` 底脚高/底板宽/支座类型, `ND/NL` 背部接管外径/长度 |
| **法兰与人孔 (`flangesub`)** | `CPFWR` (`varmain.flangesub.cpfwr`)<br>`CPFWO` (`varmain.flangesub.cpfwo`)<br>`CPFWRI` (`varmain.flangesub.cpfwri`)<br>`CPFLR` / `CPFLO` (`cpflr` / `cpflo`)<br>`CPFBR` / `CPFBO` (`cpfbr` / `cpfbo`)<br>`CMANHOLE` (`varmain.flangesub.manhole`) | `CPFWR` 对焊法兰（Weld Neck）<br>`CPFWO` 椭圆对焊法兰（带 `W`）<br>`CPFWRI` 带内衬环对焊法兰<br>`CPFLR`/`CPFLO` 松套/平焊法兰<br>`CPFBR`/`CPFBO` 盲板法兰（圆形/椭圆形）<br>`CMANHOLE` 圆形/长圆形人孔（`W>0` 时为长圆形跑道截面） | `D1` 法兰外径, `D2` 管外径, `D3` 颈部根部外径, `L` 法兰总高, `B` 法兰盘厚, `W` 椭圆法兰短轴宽（或人孔跑道直线段宽）, `OF` 壁厚 |
| **三通 (`teesub`)** | `CPTS` (`varmain.teesub.cptssub.cpts`)<br>`CPTY` (`varmain.teesub.cptysub.cpty`)<br>`CPTB` (`varmain.teesub.cptbsub.cptb`)<br>`CPTC` (`varmain.teesub.cptcsub.cptc`)<br>`CPTE` (`varmain.teesub.cptesub.cpte`)<br>`CPTP` / `CPTR` (`cptpsub` / `cptrsub`)<br>`CPTSD` (`varmain.teesub.cptsdsub.cptsd`)<br>`CPTSE` (`varmain.teesub.cptsesub.cptse`)<br>`CPTW` (`varmain.teesub.cptwsub.cptw`) | `CPTS` 标准正三通/斜三通（含变径锥颈）<br>`CPTY` Y型对称/非对称分叉三通（裤衩三通）<br>`CPTB` 弯头三通（Swept Tee）<br>`CPTC` 双弯头汇流三通<br>`CPTE` 拔制三通<br>`CPTP`/`CPTR` 鸭嘴兽式偏置支管三通<br>`CPTSD` 带底脚支座三通<br>`CPTSE` 偏心异径三通（带偏心距 `E`） | `D1` 主管左端外径, `D2` 主管右端外径, `D3` 支管外径, `L1` 左端至中心长, `L2` 右端至中心长, `L3` 支管端至中心长, `A` 支管夹角(度，默认 `90°`), `E` 偏心距, `OF` 壁厚 |
| **四通 (`crosssub`)** | `CPXT` (`varmain.crosssub.cpxtsub.cpxt`)<br>`CPXX` (`varmain.crosssub.cpxxsub.cpxx`)<br>`CPXL` / `CPXP` / `CPXR` / `CPXV` / `CPXY` | `CPXT` 标准正四通/异径四通<br>`CPXX` 斜四通（带角度 `A`）<br>`CPXL`/`CPXP`/`CPXR`/`CPXV`/`CPXY` 排水/暖通多向弯角四通 | `D1, D2` 主管外径, `D3, D4` 两侧支管外径, `L1, L2, L3, L4` 四端中心距, `A/A1/A2` 支管夹角, `H3/H4/R3/R4` 支管偏置高度与弯曲半径 |
| **大小头 (`reducersub`)** | `CPJRC` (`varmain.reducersub.cpjrcsub.cpjrc`)<br>`CPJRCL` (`varmain.reducersub.cpjrclsub.cpjrcl`)<br>`CPJRE` (`varmain.reducersub.cpjresub.cpjre`)<br>`CPJREL` (`varmain.reducersub.cpjrelsub.cpjrel`) | `CPJRC` 同心大小头（Concentric Reducer）<br>`CPJRCL` 带两端直管段的同心大小头<br>`CPJRE` 偏心大小头（Eccentric Reducer）<br>`CPJREL` 带两端直管段的偏心大小头 | `D1` 大端外径, `D2` 小端外径, `L` 总长度, `LL` 大端直段长, `LR` 小端直段长, `E` 偏心距（`E=0` 时自动取 `(D1-D2)/2` 实现平底/平顶对齐）, `OF` 壁厚 |
| **支管台 (`weldentsub`)** | `CPNL` (`varmain.weldentsub.cpnlsub.cpnl`)<br>`CPNS` (`varmain.weldentsub.cpnssub.cpns`)<br>`CPNO` (`varmain.weldentsub.cpnosub.cpno`)<br>`CPNE` (`varmain.weldentsub.cpnesub.cpne`)<br>`CPNI` / `CPNIT` (`cpnisub`)<br>`CPMV` / `CPMW` (`cpmvsub` / `cpmwsub`) | `CPNL` 焊接支管台（Weldolet / Threadolet / Sockolet）<br>`CPNS` 斜接支管台（Latrolet，带倾角 `A`）<br>`CPNO` 弯头支管台（Elbolet，带弯头半径 `R`）<br>`CPNE` 偏心支管台<br>`CPNI`/`CPNIT` 球面点占位接管嘴（Stub-in）<br>`CPMV`/`CPMW` 补强圈（Reinforcing Pad）/ 焊缝环 | `D` 支管外径, `D2` 主管外径, `L` 支管台高度, `W` 根部鞍座宽, `A` 倾斜角(度), `R` 弯头曲率半径, `OF` 壁厚 |
| **阀门与执行机构 (`valvsub`)** | `VALVE` / `VALVE3` / `ANGLEVALVE` / `WHEEL` (`varmain.valve`)<br>`CPVA000`~`128` (`varmain.valvsub.cpva*`)<br>`CPVI000`~`256` (`varmain.valvsub.cpvi*`)<br>`CPV3000`~`128` (`varmain.valvsub.cpv3*`)<br>`CPV4000`~`128` (`varmain.valvsub.cpv4*`)<br>`CPVX001`~`513` (`varmain.valvsub.cpvxsub.*`) | `CPVA*` 角阀（Angle Valves）与安全阀（`CPVR001`）<br>`CPVI*` 直通双端口阀（闸阀、截止阀、球阀、蝶阀、隔膜阀 `CPVI013`、止回阀）<br>`CPV3*` 三通阀，`CPV4*` 四通阀<br>`CPVX*` 独立执行机构库（`001/004/008` 手柄扳手、`002/003` 手轮、`006/007` 带支架手轮、`016~021` 齿轮箱执行机构、`064/065` 电动执行机构、`512/513` 气动薄膜执行机构） | 阀体参数：`D1/D2/D3/D4` 端口管径, `L/L1/L2/L3` 阀体长, `H1/H2` 法兰外径, `B1/B2` 法兰厚, `HB/WB/LB` 阀盖尺寸；<br>执行机构参数：`DA/D` 执行器直径, `HA/L/H` 执行器总高, `HD/HL/HP` 侧置手轮直径/伸出长/高度, `HA1/HA2` 手轮偏转角 |
| **过滤器 (`filtersub`)** | `CPSY001` / `CPSY002` (`varmain.filtersub.cpsysub.*`)<br>`CPSA*` / `CPSI*` / `CPSO*` / `CPSR*` | `CPSY*` Y型过滤器（Y-Strainer）<br>`CPSA*` 角式过滤器，`CPSI*` 直通篮式过滤器，`CPSO*` 偏置过滤器，`CPSR*` 双筒过滤器 | `D1, D2` 进出口管径, `L` 总长, `LS` 滤筒偏置距, `DS/D3` 滤筒外径, `H/H3` 滤筒长, `A` Y型支筒倾角, `H1/B1` 法兰外径/厚度 |
| **盲板、管帽、垫片、管箍 (`blindsub`, `capsub`, `gasketsub`, `couplingsub`)** | `CPIBL` / `CPIBP` (`varmain.blindsub.*`)<br>`CPC` (`varmain.capsub.cpc`)<br>`CPMGO` / `CPMGP` / `CPMGR` (`gasketsub`)<br>`CCOUPLING` / `CPJB` / `CPJH` / `CPJHS` (`couplingsub`) | `CPIBL` 8字盲板（Spectacle Blind）<br>`CPIBP` 插板盲板（Paddle Blind，带手柄）<br>`CPC` 管帽（`DISP=0/1/2` 平盖，`DISP=3` 碟形封头带三肋板）<br>`CPJH`/`CPJHS` 哈夫节/卡箍活接头 | `D/D1` 外径, `L` 长度/厚度, `W` 手柄宽/中心距, `H` 手柄长, `BD` 泄放孔径, `DISP` 显示样式枚举 |
| **矩形风管与天圆地方 (`squareconduitssub`, `divsub`)** | `CSQKZ` (直风管), `CSQKK*` (虾米腰/圆弧矩形弯头), `CSQRK*` (矩形变径), `CSQTK*` (矩形三通), `CSQCZK*` (矩形四通), `CSQMTRS*` / `CADAPT_SQ2RO` (天圆地方), `CADAPT_SQ2SQ` (方变方偏心过渡) | 完整的矩形通风/烟风煤管道系统与方圆偏心过渡件（支持导流叶片与法兰边 `TO`, `FB1`, `FB2`） | `W, H` 矩形截面宽×高, `W2, H2` 变径端宽×高, `LL, LW` 下口长宽, `TL, TW` 上口长宽, `OL, OW` X/Y向偏心距, `R` 圆口半径, `OF` 壁厚 |
| **非标设备与机泵 (`eqfactory`, `pumpsub`, `cylinderstacksub`)** | `EQCYLINDER`, `EQCONE`, `EQELLIPSOIDHEAD`, `EQTORISPHERICHEAD`, `EQROUNDRECT`, `EQBOX`, `EQPYRAMID`, `EQLUG`, `CSGP`, `BENDROUNDEDPLATE`, `EQ_ACC_BODYFLANGE`, `EQ_ACC_STIFFENINGRING` (`varmain.eqfactory`)<br>`EQPUMP1`, `EQPUMP2`, `CAPB1a`, `CAPD1a`, `CAPH1a`, `CAPI1a`, `CAPS1a` (`varmain.pumpsub.*`)<br>`CYLSTACK002`~`208` (`varmain.cylinderstacksub.*`) | 塔器/容器筒体、封头、加强圈、设备法兰、带弧形垫板折弯圆角的设备支耳/吊耳 (`CSGP`)、卧式/立式离心泵（含底座、蜗壳、轴承箱 `CBEAR001`、电机 `CAPMOT001`）、多阶同心/六角柱段组合件 (`CYLSTACK*`) | 详见第四份交付文档 `04_canonical_component_templates.md` 逐行源码解析 |
