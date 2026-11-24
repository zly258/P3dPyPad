# AutoCAD Plant 3D Parametric Component Design & Testing Toolkit (P3dPyPad)

<p align="center">
  <img src="docs/images/app_icon.png" alt="P3dPyPad Icon" width="96" height="96" />
</p>

<p align="center">
  <a href="README.md"><b>简体中文</b></a> | <a href="README_EN.md"><b>English</b></a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPLv3-blue.svg" alt="License: GPL v3" /></a>
  <a href="https://zly258.github.io/P3dPyPad/"><img src="https://img.shields.io/badge/Live_Demo-GitHub_Pages-blue?style=flat&logo=github" alt="Live Demo on GitHub Pages" /></a>
  <img src="https://img.shields.io/badge/AutoCAD_Plant_3D-2019~2026-brightgreen.svg" alt="Plant 3D Compatibility" />
  <img src="https://img.shields.io/badge/.NET_Framework-4.7.2~4.8-purple.svg" alt=".NET Framework" />
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%20OCC%207.7+-yellow.svg" alt="Python & PyOCC" />
  <img src="https://img.shields.io/badge/Web-OpenCASCADE%20WASM%20%7C%20Three.js-blue.svg" alt="WebAssembly & Three.js" />
  <img src="https://img.shields.io/badge/Node.js-18+-success.svg" alt="Node.js 18+" />
  <a href="https://github.com/zly258"><img src="https://img.shields.io/badge/Author-zly258-orange.svg" alt="Author GitHub" /></a>
  <a href="https://ifdian.net/order/create?user_id=3db8e630e6dc11f1b37452540025c377"><img src="https://img.shields.io/badge/Sponsor-Afdian-946ce6.svg" alt="Sponsor on Afdian" /></a>
</p>

A high-performance, engineering-grade toolkit for **AutoCAD Plant 3D (2019 ~ 2026)**, integrating **parametric component design, real-time hot reload debugging, automated batch verification, a standalone desktop PyOCC offline simulation studio, and a WebAssembly in-browser 3D modeling workbench**.

Architected and developed with end-to-end assistance from **Google Gemini 4** under test-driven development (TDD). Integrates **490+ industrial-grade parametric component scripts** and released as open source under the GNU GPL v3 License. Contributions and discussions from piping designers and CAD developers worldwide are warmly welcome!

---

## 🌟 Key Highlights

- ⚡ **Millisecond Hot Reload (Zero CAD Restart)**: Eliminates the tedious need to restart AutoCAD Plant 3D after every script edit. Powered by in-memory dynamic proxies and the `PnP3dACPAdapter.arx` adapter, press `F5` to instantly regenerate and replace 3D solids in the active CAD viewport.
- 📐 **PyOCC 1:1 Offline Geometric Topology Alignment**: Complete reverse engineering and alignment with native Plant 3D primitives (Box, Cylinder, Cone, Torus, CSTE_* structural profiles, fasteners, etc.). Perform 100% accurate solid modeling in a standalone Python 3 + OpenCASCADE environment without launching CAD.
- 🌐 **WebAssembly Offline 3D Simulation & Preview Studio (`web/`)**: A zero-dependency Node.js and static browser studio powered by OpenCASCADE 8.0.1 WASM (`occt.js` / `libcascade`) and Three.js. Paste or edit Python component scripts online, simulate 3D B-Rep solids in milliseconds, and export presentation-grade dual PNG isometric preview snapshots.
- ☀️ **100% Crisp Engineering Light Theme**: Clean, distraction-free CAD light theme aligned with `/wpf-ui-style`, completely eliminating dark mode eye strain. Features high-contrast deep charcoal edge lines (Slate-900) for crystal-clear geometry contours.
- 📐 **Dual-Mode Isometric Snapshots & Clean 3D Viewport**: Interactive 3D scene remains completely clean with zero floating dimension clutter. Clicking "生成预览图" generates two presentation-quality exports: **① Clean Isometric View** (pure solid) and **② Annotated Isometric View** (with 45° architectural ticks, offset witness lines, and haloed parameter label sprites), with instant modal tab switching and batch downloads.
- ⏳ **Seamless Loading Feedback**: Real-time loading overlays and status badges across WASM kernel boot, script loading, CAD modeling, and dual-mode snapshot rendering.
- 🖥️ **Orthographic Projection & Professional CAD Controls**: True orthographic projection (`OrthographicCamera`) eliminating perspective distortion; OrbitControls with damping disabled (`enableDamping = false`, stop-on-release CAD feel); zero viewport grid; expandable bottom multi-line console log with timestamps and status tags.
- 🔤 **Modern Google Fonts Typography**: Fully integrated with modern Google Fonts (`Inter`, `Noto Sans SC`, and developer-grade `JetBrains Mono`) across all interface elements, code editors, and dimension labels.
- 🌍 **Native Bilingual Support (Chinese & English i18n)**: Seamless language switcher (`[中文] [English]`) in the header bar, instantly translating app titles, buttons, categorized dropdowns, dimensional parameters, console logs, and snapshot dialogs without page reloads, with automatic LocalStorage preference persistence.
- 📚 **Full 490+ Component Catalog Discovery & Real-Time Filtering**: Dynamic categorized catalog of all 494 industrial scripts from `pyscripts/` (fittings, flanges, valves, instruments, power supports CD/ZD, chemical supports HG/T, equipment). Instant sub-second keyword search.
- 🎨 **Minimalist Text-First CAD UI**: Clean, distraction-free aesthetic with strictly zero decorative icons or emojis, aligned with desktop CAD toolbars and engineering conventions.
- 🔗 **GitHub Pages Instant Live Demo**: Accessible anywhere at [https://zly258.github.io/P3dPyPad/](https://zly258.github.io/P3dPyPad/).
- 📦 **490+ AI Industrial Script Asset Library**: Covers piping components, flanges, valves, instruments, process equipment, and comprehensive pipe supports/hangers (National Power Standard CD/ZD 2010, Chemical Industry Standard HG/T 21629), 100% verified with B-Rep single-connected topology.
- 📊 **Automatic Co-Located CSV Spec Discovery**: Automatically pairs scripts with co-located `.csv` specification tables (e.g., `VALVE_GATE.csv`). Dropdown selector enables instant multi-size filtering without tedious manual path configuration.
- 🏷️ **Smart 3D Isometric Dimensioning**: The PyOCC workbench features an automated offscreen dimensioning engine with 45° architectural ticks (eliminating arrow direction ambiguity), collinear chain dimension grouping, and multi-tier baseline stacking.
- 🔄 **End-to-End Catalog & SQLite Lifecycle**: One-click generation of `.acat/.pcat` component catalogs, `.peqx` equipment templates, and direct SQLite `.pspc` spec management with safe member deletion and zero orphaned data.
- 🚀 **Streamlined Packaging & Out-of-the-Box Setup**: Automated InnoSetup installers (~1.85 MB for plugin, ~155 MB for full workbench) deploying directly to the system add-in directory for clean, zero-pollution loading.
- ☁️ **GitHub Pages Automated CI/CD Deployment**: Equipped with `.github/workflows/pages.yml` to automatically build and deploy the Web studio to GitHub Pages on push.

---

## 🏗️ Dual-End Collaborative Architecture

The toolkit adopts a decoupled **dual-end collaborative architecture**:

```mermaid
flowchart TD
    subgraph CAD_Host ["AutoCAD Plant 3D Host (C# / .NET / WPF)"]
        Ribbon["Native Ribbon Tab\n(PYPAD / PYBATCH / PYLANG / PYABOUT)"]
        HotReload["Zero-Restart Hot Reload Core\n(DEV_PROXY.py -> PnP3dACPAdapter.arx)"]
        PadWin["Single-Script Pad\n(Minimal Toolbar + AvalonEdit + Auto CSV)"]
        BatchWin["Batch Test Runner\n(Recursive Scan + Isometric Capture + Diagnostics)"]
        Ribbon --> HotReload
        HotReload --> PadWin
        HotReload --> BatchWin
    end

    subgraph OCC_Standalone ["PyOCC Standalone Workbench (Python 3 / OpenCASCADE / PySide6)"]
        MainGUI["3-Column Interactive Studio\n(Script Tree + Dynamic Property Grid + 3D Viewport)"]
        BRepKernel["1:1 Primitive & CSG Engine\n(Box/Cylinder/Torus/CSTE Profiles/Fasteners)"]
        AutoPreview["Offscreen Rendering & Smart Dimensioning\n(Shaded + Edge Lines + 45° Architectural Ticks)"]
        CatalogEngine["Catalog & Spec Database Engine\n(.acat/.pcat Publish + .peqx Equipment + SQLite)"]
        MainGUI --> BRepKernel
        BRepKernel --> AutoPreview
        AutoPreview --> CatalogEngine
    end

    subgraph Shared_Assets ["Shared Assets & CAD Agent Skills (pyscripts / skills)"]
        AI_Skill["skills/plant3d-python-cad-generator\n(Dual-End Compatible Code Generation Agent)"]
        ScriptsLib["334+ Parametric Component Assets\n(Fittings/Flanges/Valves/Instruments/Equipment/ZD/HGT)"]
        AI_Skill --> ScriptsLib
    end

    Shared_Assets --> CAD_Host
    Shared_Assets --> OCC_Standalone
```

---

## 🖥️ Core Modules & Capabilities

### 1. Single Component Script Pad (`PYPAD`)

**Role**: Rapid interactive debugging for parametric component developers.
- **Minimalist Single-Row Toolbar**: Compact and distraction-free with Reload, Save (`Ctrl+S`), Execute (`F5`), Clear Log, and Close buttons;
- **Co-Located CSV Discovery**: Automatically detects and loads matching `.csv` spec files in the same directory (e.g., `VALVE_GATE.csv`);
- **AvalonEdit Syntax Highlighting**: Professional Python syntax coloring, line numbers, and instant shortcut saving;
- **Sub-Second F5 Redraw**: Direct invocation via `PnP3dACPAdapter.arx` instantly updates the 3D entity on the drawing canvas.

![Script Pad](docs/images/01_csharp_script_pad.png)

---

### 2. Automated Batch Test Runner (`PYBATCH`)

**Role**: Automated batch simulation and quality inspection across dozens or hundreds of scripts.
- **Recursive Directory Scan**: Traverses all `.py` component scripts in any selected directory with one click;
- **Automatic Isometric Capture**: Generates standardized isometric shaded images for every component to a designated output folder;
- **In-Depth Diagnostics**: Double-click list items to preview screenshots in the system image viewer; right-click to inspect and copy full Python stack traces;
- **Unattended CLI & LISP Entry**: Accessible via `PYBATCH_RUN` command line and LISP interfaces for continuous integration and AI Agent orchestration.

![Batch Test Runner](docs/images/02_csharp_batch_test.png)

---

### 3. PyOCC Standalone Offline Workbench

**Role**: Standalone Python 3 environment running independently of AutoCAD, powered by the OpenCASCADE C++ B-Rep kernel.
- **3-Column Industrial UI**:
  - **Left**: Hierarchical script catalog with real-time keyword filtering;
  - **Center**: Dynamic property grid for live parameter manipulation + collapsible Python code editor;
  - **Right**: `SafeQtViewer3d` interactive 3D viewport featuring 8 standard engineering view angles and 4 display styles (Shaded, Shaded with Edges, Wireframe, Hidden Line);
- **Zero AutoCAD Dependency**: Test component geometry and adjust dimensions on any computer without needing an AutoCAD license.

![Python OCC Workbench](docs/images/04_python_workbench.png)

---

### 4. Smart 3D Isometric Dimensioning & Offscreen Rendering

**Role**: High-precision drafting engine driven by `plant3d_occ/catalog/preview.py`.
- **Shaded + Edge Lines**: Pure white background with grey shaded faces and crisp black silhouette outlines matching Plant 3D's native aesthetic;
- **45° Architectural Ticks**: Replaces conventional arrows with 45° ticks to eliminate visual ambiguity in isometric views;
- **Intelligent Stacking & Avoidance**: Extracts parametric boundary grips, automatically clusters collinear dimensions, and creates multi-tier baselines.

| 3D Shaded + Edge Silhouette | 3D Isometric Dimensioned Drawing |
|:---:|:---:|
| ![Shaded Preview](docs/images/05_exact_hlr_preview.png) | *(Dynamically rendered from parameters)* |

---

### 5. Catalog Publishing & Database Management

- **Publish Components**: Directly writes to `.acat/.pcat` SQLite databases, generating `<Script>.xml` and `variants.map` metadata;
- **Publish Equipment**: Explicitly specifies PartType / PartSubType to package `.peqx` templates with one click;
- **Spec Database Management**: Inspects CPak Common SQLite databases to view PnPID, ND, OD, and geometric parameters, supporting safe membership-based deletion without orphaned entries.

| Publish Component | Publish Equipment | Catalog Manager |
|:---:|:---:|:---:|
| ![Publish Component](docs/images/06_publish_component.png) | ![Publish Equipment](docs/images/07_publish_equipment.png) | ![Catalog Manager](docs/images/08_catalog_manager.png) |

---

## 📂 Repository Directory Structure

```text
P3dPyPad/
├── .github/workflows/               # GitHub Actions CI/CD workflows
│   └── pages.yml                    # Automated GitHub Pages static build & deployment
├── installer/                       # Installer packaging & automated deployment
│   ├── output/                      # Release artifact directory
│   │   └── P3dPyPad-Setup-v1.0.0.exe# Standalone plugin setup (~1.85 MB)
│   ├── PackageContents.xml          # AutoCAD Autoloader manifest
│   ├── P3dPyPad.iss                 # InnoSetup project script
│   └── Publish-PluginExe.ps1        # PowerShell automated build script
├── plant3d_occ/                     # PyOCC standalone offline workbench (Python 3 + PySide6)
│   ├── core/                        # Session, topological entity & geometry math
│   ├── gui/                         # PySide6 UI components & theme system
│   ├── primitives/                  # 1:1 aligned native & extended primitives
│   ├── renderer/                    # Shaded edge renderer & 45° tick dimensioning
│   ├── catalog/                     # Catalog publisher & SQLite database engine
│   └── main.py                      # Standalone application entry point
├── pyscripts/                       # 490+ AI industrial component scripts
│   ├── custom_scripts/              # Curated fittings/flanges/valves/instruments/equipment
│   ├── supports/                    # Standard pipe support libraries (CD/ZD 2010, HG/T 21629)
│   └── system_defaults/             # Clean scripts distilled from original variants.zip
├── skills/                          # AI Agent modeling skill (plant3d-python-cad-generator)
├── src/P3dPyPad/                    # AutoCAD in-process C# plugin source
│   ├── App/                         # Plugin entry & Ribbon builder
│   ├── Core/                        # Script parser, hot-reload runner & i18n
│   └── Views/                       # Script pad, batch tester & about dialogs
├── tests/                           # Unit tests & topological regression suites
├── web/                             # WebAssembly offline 3D simulation studio (Node.js / occt.js)
│   ├── public/                      # Static WASM, Three.js modules & offline script mirror
│   │   ├── libs/                    # occt.js (OpenCASCADE 8.0.1 WASM) & Three.js
│   │   ├── pyscripts/               # 490+ component script offline mirror
│   │   └── pyscripts_manifest.json  # Component catalog categorization & search index
│   ├── src/                         # Frontend application source
│   │   ├── app.js                   # Viewport controls, state & event bindings (Minimal MD)
│   │   ├── kernel.js                # OpenCASCADE WASM modeling & B-Rep mesher
│   │   ├── transpiler.js            # Python primitive transpiler & @param sandbox
│   │   ├── presets.js               # Preset fallback catalog
│   │   └── style.css                # Minimalist Material Design styling (zero icons)
│   ├── index.html                   # Web studio entry point
│   ├── server.js                    # Zero-dependency native Node.js static dev server
│   ├── sync_pyscripts.js            # pyscripts mirror syncer and manifest generator
│   └── package.json                 # Web studio Node.js package manifest
├── package.json                     # Root project execution scripts (npm start / npm run dev)
├── LICENSE                          # GNU GPL v3 License
├── README.md                        # Official documentation (Chinese)
└── README_EN.md                     # Official documentation (English)
```

---

## 🚀 Three Packaging & Deployment Options

This project offers **three deployment packages** tailored to diverse workflow requirements:

| Package Type | Asset Filename | Size | Included Contents & Use Case |
|:---|:---|:---:|:---|
| **1. Standalone Plugin Setup**<br>*(For CAD-Only Users)* | [`P3dPyPad-Plugin-Setup-v1.0.0.exe`](installer/output/P3dPyPad-Plugin-Setup-v1.0.0.exe) | **1.85 MB** | • Installs in-process AutoCAD Plant 3D plugin only<br>• Deploys to `ApplicationPlugins\P3dPyPad.bundle`<br>• Injects `DEV_PROXY.py` singleton hot-reload shell<br>• Auto-loads on CAD launch, ultra-lightweight |
| **2. Standalone PyOCC Workbench**<br>*(For Offline Modelers)* | `Plant3dOcc-Setup-v1.0.0.exe`<br>`Plant3dOcc-v1.0.0-Portable-x64.zip` | **155 MB**<br>*(Unpacked: 728 MB)* | • Bundles complete OpenCASCADE C++ kernel + Python 3 runtime<br>• Available as desktop setup or portable zero-install zip<br>• Designed for offline 3D modeling, 45° dimensioning, and catalog authoring |
| **3. All-In-One Dual Setup**<br>*(Recommended for Full Environment)* | `P3dPyPad-AllInOne-Setup-v1.0.0.exe` | **155.2 MB** | • **All-in-one unified installer**: sets up both the CAD plugin and PyOCC desktop workbench<br>• Supports custom component selection in the setup wizard |

### Quick Build Commands:
```powershell
# Build standalone AutoCAD plugin installer (1.85 MB)
pwsh -File installer/Publish-PluginExe.ps1

# Build standalone PyOCC workbench (portable ZIP + setup EXE)
pwsh -File installer/Publish-OccExe.ps1

# Build all three release packages at once
pwsh -File installer/Publish-Release.ps1
```

### 3. Running the PyOCC Offline Workbench (Python Desktop)
In an environment with Python 3.10+, PySide6, and PythonOCC-Core:
```bash
# Launch the offline workbench
python plant3d_occ/main.py

# Or directly open a specific component script
python plant3d_occ/main.py pyscripts/custom_scripts/03_valves/VALVE_GATE.py
```

### 4. Running the Web Offline 3D Studio (Node.js / Browser)
Zero-dependency local server with the full 490+ script catalog and OpenCASCADE WASM:

- 🌐 **GitHub Pages Live Demo**: [https://zly258.github.io/P3dPyPad/](https://zly258.github.io/P3dPyPad/) (Zero installation, accessible directly in any modern browser)
- 💻 **Local Execution**:
```bash
# Option 1: Start directly from the repository root
npm start

# Option 2: Start from the web directory
cd web
npm start    # or: node server.js

# Open in browser: http://localhost:3000
```
> **Key Capabilities**:
> - **☀️ 100% Crisp Engineering Light Theme**: Clean white and slate-50 styling with high-contrast deep charcoal contours (Slate-900).
> - **🔍 490+ Script Catalog**: Select any component from categorized dropdown or type keywords in the search bar (e.g. "ELBOW", "VALVE", "FLANGE").
> - **⚡ Live Editing & Execution**: Edit Python code or tweak `@param` fields, press F5 or click "运行 (F5)" for sub-second 3D B-Rep rendering with loading animations.
> - **📐 Dual-Mode Isometric Snapshots**: Interactive 3D scene stays clutter-free; clicking "生成预览图" generates both a clean isometric PNG and an annotated isometric PNG (with 45° architectural ticks and haloed parameter label sprites).
> - **☁️ GitHub Pages CI/CD**: Built-in `.github/workflows/pages.yml` continuously deploys the static site to GitHub Pages on push.

### 5. Running Regression Tests
```bash
# Run unit test suite
python -m unittest discover -s tests -p "test_*.py"

# Run full topological stitching validation across all pipe supports
python tests/test_all_supports.py
```

---

## 📜 Script Development & Compatibility Rules

To guarantee flawless execution across both **Plant 3D native environment (Python 2.7)** and **PyOCC offline environment (Python 3.x)**, adhere to the following rules:

### 1. UTF-8 Encoding Declaration
Every script must declare encoding within the first 7 lines:
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

### 2. Dimensioning Function Signature
`setLinearDimension` strictly takes 3 positional arguments (code, start_point, end_point). Keyword arguments are prohibited:
```python
# Correct signature: exactly 3 positional arguments
s.setLinearDimension("L", (0.0, 0.0, -r_flange), (L, 0.0, -r_flange))
```

---

## 🤝 Open Source License & Community

- **License**: Released under the [GNU GPL v3 (GPL-3.0)](LICENSE) license — free to use, study, and modify; any derivative works distributed based on this project must also be open-sourced under GPL v3.
- **Sponsor / Donate**: If this project helps your workflow, feel free to support the author via [Afdian](https://ifdian.net/order/create?user_id=3db8e630e6dc11f1b37452540025c377).
- **Author & GitHub**: [zly258 (zhangly1403)](https://github.com/zly258)
- **Acknowledgments**: Gratefully acknowledging Google DeepMind Gemini 4 for its pivotal role throughout architecture design, geometric algorithms, and code generation.
- Issues and Pull Requests are warmly encouraged as we work together to advance and standardize the plant design parametric modeling ecosystem!
