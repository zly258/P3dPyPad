# AutoCAD Plant 3D 参数化构件设计与测试工具箱 (P3dPyPad)

<p align="center">
  <img src="docs/images/app_icon.png" alt="P3dPyPad Icon" width="96" height="96" />
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
  <img src="https://img.shields.io/badge/AutoCAD_Plant_3D-2019~2026-brightgreen.svg" alt="Plant 3D Compatibility" />
  <img src="https://img.shields.io/badge/.NET_Framework-4.7.2~4.8-purple.svg" alt=".NET Framework" />
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%20OCC%207.7+-yellow.svg" alt="Python & PyOCC" />
  <a href="https://github.com/zly258"><img src="https://img.shields.io/badge/Author-zly258-orange.svg" alt="Author GitHub" /></a>
</p>

一套专为 **AutoCAD Plant 3D (2019 ~ 2026)** 深度定制的高性能、工程级**参数化构件设计、实时热更新调试、全自动批量测试与 PyOCC 离线仿真工作台**。

本项目依托 **Google Gemini 4** 全程辅助架构设计与自动化测试驱动开发完成。全项目集成了 **334+ 个工业级参数化构件脚本资产**，并已开源发布。欢迎各位管道工程设计师、CAD 二次开发工程师交流与共建！

---

## 🌟 核心亮点概览

- ⚡ **毫秒级热更新（免重启 CAD）**：彻底摆脱传统修改脚本需反复重启 AutoCAD 的痛点，基于动态内存代理与 `PnP3dACPAdapter.arx` 适配器，按 `F5` 键毫秒级在图面生成并替换 3D 实体。
- 📐 **PyOCC 1:1 脱机几何拓扑对齐**：完整逆向并对齐 Plant 3D 原生几何原语（Box, Cylinder, Cone, Torus, CSTE_* 型钢等），无需启动庞大的 CAD 即可在 Python 3 + OpenCASCADE 独立端进行 100% 精确的实体建模仿真。
- 📦 **334+ AI 工业级脚本资产库**：涵盖管道管件、法兰、阀门、仪表、工艺设备及海量批量支吊架（CD/ZD 2010 电力标准、HG/T 21629 化工管架），100% 通过几何连续性与单连通拓扑校验。
- 📊 **规格表同目录自动识别**：脚本测试时自动关联同目录下同名 `.csv` 规格预设表，下拉框即时过滤选型，无需手动指定繁琐路径。
- 🏷️ **智能 3D 轴测尺寸标注**：PyOCC 独立端内置离屏自动标注算法，支持真实参数握点读取、共线链式分组、基线防重叠与国际标准的 45° 建筑斜短划线（Architectural Tick）尺寸标注。
- 🔄 **发布与库管理全链路闭环**：一键生成 `.acat/.pcat` 元件库、注册设备模板包（`.peqx`），直连 SQLite 等级库（`.pspc`）穿透式增删管理，杜绝多余垃圾数据残留。
- 🚀 **极简打包与即装即用**：自带自动化 InnoSetup 安装程序（体积仅 1.85 MB），一键安装至系统插件目录，启动 CAD 自动加载，零侵入无残留。

---

## 🏗️ 双端协同架构体系

本项目采用**双端分工协同**的解耦设计架构：

```mermaid
flowchart TD
    subgraph CAD_Host ["AutoCAD Plant 3D 宿主端 (C# / .NET / WPF)"]
        Ribbon["原生 Ribbon 功能区\n(PYPAD / PYBATCH / PYLANG / PYABOUT)"]
        HotReload["免重启热更新内核\n(DEV_PROXY.py -> PnP3dACPAdapter.arx)"]
        PadWin["单件脚本测试器\n(极简顶部工具条 + AvalonEdit + 自动关联CSV)"]
        BatchWin["批量全自动测试器\n(递归扫描 + 轴测图生成 + 诊断报告)"]
        Ribbon --> HotReload
        HotReload --> PadWin
        HotReload --> BatchWin
    end

    subgraph OCC_Standalone ["PyOCC 独立工作台 (Python 3 / OpenCASCADE / PySide6)"]
        MainGUI["三栏交互工作台\n(中文脚本树 + 属性网格 + 3D交互视口)"]
        BRepKernel["1:1 原语与布尔引擎\n(对齐Box/Cylinder/Torus/CSTE型钢/紧固件)"]
        AutoPreview["离屏渲染与智能标注\n(着色加边线 + 45°斜短划线尺寸标注)"]
        CatalogEngine["元件库与等级库管理\n(.acat/.pcat发布 + .peqx设备 + SQLite)"]
        MainGUI --> BRepKernel
        BRepKernel --> AutoPreview
        AutoPreview --> CatalogEngine
    end

    subgraph Shared_Assets ["共享脚本资产与 AI 智能体 (pyscripts / skills)"]
        AI_Skill["skills/plant3d-python-cad-generator\n(双端兼容代码生成专家)"]
        ScriptsLib["334+ 构件脚本资产\n(管件/法兰/阀门/仪表/设备/电力ZD/化工HGT)"]
        AI_Skill --> ScriptsLib
    end

    Shared_Assets --> CAD_Host
    Shared_Assets --> OCC_Standalone
```

---

## 🖥️ 核心功能展示与深度解析

### 1. 单件构件脚本测试器 (`PYPAD`)

**功能定位**：面向参数化构件开发者的快速调试测试器。
- **单行极简工具条**：界面整洁紧凑，顶部集成「重新加载」、「保存 (Ctrl+S)」、「执行 (F5)」、「清空日志」及「退出」；
- **同名 CSV 自动识别**：脚本加载时，自动探测并加载同目录下同名 `.csv` 规格数据表（如 `VALVE_GATE.csv`），无需多余配置；
- **AvalonEdit 实时高亮**：专业 Python 语法高亮与行号显示，支持快捷键即时存盘；
- **F5 毫秒级重绘**：通过 `PnP3dACPAdapter.arx` 适配器驱动脚本建模，图面瞬时生成或替换 3D 构件实体。

![单件构件脚本测试器](docs/images/01_csharp_script_pad.png)

---

### 2. 构件全自动批量测试器 (`PYBATCH`)

**功能定位**：对几十至上百个构件脚本进行全自动批量仿真验证与质量巡检。
- **全目录递归扫描**：一键遍历指定目录下的所有 `.py` 脚本；
- **自动轴测图出图**：每个构件自动生成标准轴测着色图，保存至指定测试输出目录；
- **深度故障排查**：双击列表行即调用系统图像查看器预览，右键可查看并复制完整的 Python 异常堆栈日志；
- **无人值守自动化**：提供 `PYBATCH_RUN` 命令行与 LISP 入口，可由自动化脚本及 AI Agent 直接调度。

![构件全自动批量测试器](docs/images/02_csharp_batch_test.png)

---

### 3. PyOCC 独立离线构件设计工作台

**功能定位**：脱离 AutoCAD 运行的纯 Python 3 离线工作台，基于 OpenCASCADE C++ 几何拓扑内核构建。
- **三栏工业布局**：
  - **左栏**：中文目录树，自动提取脚本顶部中文注释，显示格式为 `中文名称 (文件名.py)`，支持即时关键字过滤；
  - **中栏**：参数动态解析网格 + 可折叠 Python 代码编辑器；
  - **右栏**：`SafeQtViewer3d` 交互式 3D 视口，集成 8 大标准工程视角与 4 种显示样式（着色、边线、线框、隐藏线）；
- **免 CAD 环境依赖**：无需安装庞大的 AutoCAD 即可快速进行构件外形验证与尺寸微调。

![Python OCC 独立构件工作台](docs/images/04_python_workbench.png)

---

### 4. 智能 3D 轴测尺寸标注与离屏渲染

**功能定位**：由 `plant3d_occ/catalog/preview.py` 驱动的高精度出图引擎。
- **着色 + 边线渲染**：纯白底色、灰色着色面与黑色拓扑轮廓线，与 Plant 3D 原生视口风格完美匹配；
- **45° 建筑斜短划线标注**：尺寸线端点统一采用 45° 斜短划线（Architectural Tick），摒弃传统箭头带来的视线混淆；
- **智能分层与避让**：自动提取真实参数握点，实现链式尺寸共线合并与基线分级展开。

| 纯 3D 外形着色 + 边线图 | 外形 + 轴测真实尺寸斜线标注图 |
|:---:|:---:|
| ![着色加边线图预览](docs/images/05_exact_hlr_preview.png) | *(自动读取参数动态渲染)* |

---

### 5. 发布中心与数据库管理闭环

- **发布构件**：直接写入 `.acat/.pcat` SQLite 元件库，自动生成 `<Script>.xml`、`variants.map` 等关联元数据；
- **发布设备**：显式指定设备大类与子类（PartType / PartSubType），一键生成 `.peqx` 模板包；
- **等级库管理**：穿透式检索 CPak Common 数据库，直观查看规格明细（PnPID、ND、OD、几何参数定义），支持按实际成员资格安全删除，无残留垃圾项。

| 发布构件 | 发布设备 | 元件库管理 |
|:---:|:---:|:---:|
| ![发布构件](docs/images/06_publish_component.png) | ![发布设备](docs/images/07_publish_equipment.png) | ![元件库管理](docs/images/08_catalog_manager.png) |

---

## 📂 项目工程目录

```text
P3dPyPad/
├── installer/                       # 安装程序打包与自动部署
│   ├── output/                      # 发布产物目录
│   │   └── P3dPyPad-Setup-v1.0.0.exe# [重要] 插件独立安装程序 (约 1.85 MB)
│   ├── PackageContents.xml          # AutoCAD Autoloader 自动加载清单
│   ├── P3dPyPad.iss                 # InnoSetup 打包脚本工程
│   └── Publish-PluginExe.ps1        # PowerShell 自动化打包脚本
├── plant3d_occ/                     # PyOCC 独立离线构件设计工作台
│   ├── core/                        # 会话、拓扑实体与几何数学库
│   ├── gui/                         # PySide6 界面组件与样式系统
│   ├── primitives/                  # 1:1 对齐 Plant 3D 的原生及扩展体素库
│   ├── renderer/                    # 着色边线渲染与智能斜线标注引擎
│   ├── catalog/                     # 元件库发布与 SQLite 管理引擎
│   └── main.py                      # 独立端主程序启动入口
├── pyscripts/                       # 334+ AI 工业级构件脚本资产
│   ├── custom_scripts/              # 92 个管件/法兰/阀门/仪表/支吊架/设备典范脚本
│   ├── supports/                    # 批量支吊架标准库 (CD/ZD 2010 电力、HG/T 21629 化工)
│   └── system_defaults/             # 从原厂 variants.zip 反编译的 160 个纯净脚本
├── skills/                          # AI 智能体生成技能 (Agentic Prompt & Rules)
├── src/P3dPyPad/                    # AutoCAD C# 进程内插件源码
│   ├── App/                         # 插件入口与 Ribbon 构建
│   ├── Core/                        # 脚本解析器、热更新运行器与双语切换
│   └── Views/                       # 单件测试器、批量测试器与关于窗口
├── tests/                           # 单元测试与拓扑回归测试套件 (100% 通过)
├── LICENSE                          # MIT 开源许可证
└── README.md                        # 项目官方中文文档
```

---

## 🚀 三种安装发布模式

本项目提供 **三种不同形态的发布包**，满足不同场景的使用需求：

| 发布包类型 | 产物文件名 | 体积 | 包含内容与适用场景 |
|:---|:---|:---:|:---|
| **1. 插件独立安装包**<br>*(推荐仅用 CAD 者)* | [`P3dPyPad-Plugin-Setup-v1.0.0.exe`](installer/output/P3dPyPad-Plugin-Setup-v1.0.0.exe)<br>*(别名 P3dPyPad-Setup-v1.0.0.exe)* | **1.85 MB** | • 仅安装 AutoCAD Plant 3D 进程内插件<br>• 自动部署至 `ApplicationPlugins\P3dPyPad.bundle`<br>• 注入单件热更新外壳 `DEV_PROXY.py`<br>• 启动 CAD 自动自加载，极速轻量 |
| **2. PyOCC 独立工作台**<br>*(推荐脱机设计者)* | `Plant3dOcc-Setup-v1.0.0.exe`<br>`Plant3dOcc-v1.0.0-Portable-x64.zip` | **155 MB**<br>*(解压 728 MB)* | • 包含完整 OpenCASCADE C++ 几何内核 + Python 3 运行时<br>• 提供独立桌面快捷方式安装包与纯绿色解压即用 zip<br>• 适合脱离 AutoCAD 离线造型、出图标注与元件库管理 |
| **3. 双端全功能二合一包**<br>*(推荐完整环境者)* | `P3dPyPad-AllInOne-Setup-v1.0.0.exe` | **155.2 MB** | • **二合一完整安装程序**：同时包含 CAD 插件与 PyOCC 桌面工作台<br>• 安装向导支持组件勾选自定义安装，一步搞定双端协同环境 |

### 快速上手命令：
```powershell
# 仅打包 AutoCAD 插件独立安装包 (1.85 MB)
pwsh -File installer/Publish-PluginExe.ps1

# 仅打包 PyOCC 独立工作台 (绿色版 ZIP + 安装包 EXE)
pwsh -File installer/Publish-OccExe.ps1

# 一键打包全部三种类型发布包
pwsh -File installer/Publish-Release.ps1
```

### 3. 运行 PyOCC 离线设计工作台
在具备 Python 3.10+、PySide6 及 PythonOCC-Core 的环境中运行：
```bash
# 启动离线工作台
python plant3d_occ/main.py

# 或直接打开指定构件脚本
python plant3d_occ/main.py pyscripts/custom_scripts/03_valves/VALVE_GATE.py
```

### 4. 运行全量回归测试
```bash
# 运行完整单元测试套件
python -m unittest discover -s tests -p "test_*.py"

# 运行支吊架全量实体拓扑缝合校验 (确保单一实体无缝连通)
python tests/test_all_supports.py
```

---

## 📜 构件脚本开发防乱码与编写规范

为了确保脚本在 **Plant 3D 原生环境 (Python 2.7)** 与 **PyOCC 离线端 (Python 3.x)** 双向平滑运行，请遵循以下规范：

### 1. 编码头声明
每个构件脚本必须置于前 7 行内声明：
```python
# -*- coding: utf-8 -*-
#coding=utf-8
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass
```

### 2. 尺寸标注函数规则
`setLinearDimension` 严格使用 3 个位置参数（代号, 起点坐标, 终点坐标），禁止使用任何关键字参数：
```python
# 正确写法：严格 3 个位置参数
s.setLinearDimension("L", (0.0, 0.0, -r_flange), (L, 0.0, -r_flange))
```

---

## 🤝 开源协议与交流共建

- **开源协议**：本项目基于 [MIT License](LICENSE) 许可开源发布，允许自由使用、修改及商用。
- **作者与主页**：[zly258 (zhangly1403)](https://github.com/zly258)
- **致谢**：感谢 Google DeepMind Gemini 4 在全流程开发、几何算法实现与代码重构中提供的强劲辅助。
- 欢迎提交 Issue 与 Pull Request，共同推动工厂设计三维参数化构件生态的标准化与现代化！
