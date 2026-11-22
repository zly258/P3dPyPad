# AutoCAD Plant 3D 20 个工业级分类典范源码母版总索引（`00_templates_index.md`）

> **按需加载说明**：为避免单次加载超大文件阻塞上下文，20 个原厂反编译典范源码母版已按 **6 大工程类别** 拆分为 6 个独立的代码分册（每册仅 6~15 KB）。请根据当前开发的目标构件类型，仅加载对应的单个分册文件。

---

## 分册路由与 20 个典范母版速查表

| 分册文件路径 | 涵盖工程类别 | 包含的原厂典范脚本 | 核心几何技巧与适用场景 |
| :--- | :--- | :--- | :--- |
| **`references/templates/01_structural_frames_and_guides.md`** | **型钢支吊架框架与多向导向架类** | `CSGE001`, `CSGE002`, `CSGT001`, `CSGB012` | L型角钢+T型钢悬臂架、带管底鞍座弧面裁切腹板、`pointAt` 螺母高度运行时内省、双侧对称循环装配、`TI & 1/2/4/8` 位掩码四向翼板控制 |
| **`references/templates/02_shoes_clamps_and_rollers.md`** | **滑动管托、焊接鞍座、管卡与滚轮支座类** | `CSGB001`, `CSGB004`, `CSGC000`, `CSGC004`, `CSGR005` | 双抱箍T型管托、端板+腹板一次圆柱差集切鞍口、45° 旋转方块切八角减重孔、`TORUS` 半环裁切 U 型螺栓、3×60° `BOX` 拼正六角螺母、单/双排滚轮二维网格装配 |
| **`references/templates/03_spring_hangers_and_trunnions.md`** | **弹簧吊架、球面铰接吊架与耳轴支座类** | `CSGH001`, `CSGH002`, `CSGF001` | 三明治耳板+锥顶弹簧罐+顶部U型吊耳串联、`CYLINDER` ∩ `SPHERE`（`intersectWith`）球面铰接底壳、`var_basic.CSGCutOut` 自适应切直管/弯头相贯马鞍口 |
| **`references/templates/04_fittings_elbows_tees_reducers_olets.md`** | **复杂管件类（弯头/三通/大小头/管台）** | `CPBD`, `CPTS`, `CPTY`, `CPJREL`, `CPNO` | `ARC3D2` 防自交保护与 5 种弯头支座、斜三通/Y型三通“先并外壳再并内芯一次差集”、Y型三通大夹角脚跟防穿刺削平、偏心大小头、`setTransformationMatrix` 齐次矩阵变换 |
| **`references/templates/05_valves_and_actuators.md`** | **阀门与执行机构总成类** | `CPVA003513` + `CPVX513`, `CPVI013000` | `ELLIPSOIDHEAD.parameters()['H']` 封头高度内省、角阀阀体+气动薄膜执行机构+侧装手轮多级嵌套、`oV.pointAt/directionAt` 端口继承、`ELLIPSOIDSEGMENT` 鼓形阀腔 |
| **`references/templates/06_equipment_lugs_and_transitions.md`** | **非标设备支耳、弧形补强板与天圆地方** | `EQLUG` + `CSGP` + `BENDROUNDEDPLATE`, `CADAPT_SQ2RO` + `CADAPT_SQ2SQ_Sub` | 贴合容器筒体外壁的圆角弧形垫板与双筋板悬挂支耳、偏心圆台 `CONE` 与四面斜切偏心方台 `intersectWith` 求交 + 内外包络差集抽壳构造任意偏心“天圆地方” |
