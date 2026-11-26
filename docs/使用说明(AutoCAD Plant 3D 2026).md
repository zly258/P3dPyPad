# AutoCAD Plant 3D 2026 化工元件库与等级库使用说明（v1.1.0）

本成品包包含完整的 **化工元件库 (`ChemicalPlant170.pcat`)**、**项目等级库 (`ChemicalPlant170.pspc` / `.pspx`)** 以及 **参数化自定义脚本 (`CustomScripts`, 170+ 套化工阀门/管件/法兰/仪表/支吊架/特种件/设备)**，解压后即可直接在 **AutoCAD Plant 3D 2026** 中使用。

---

## 一、 压缩包目录结构

```text
ChemicalPlant170-Plant3D2026-v1.1.0/
├── 使用说明(AutoCAD Plant 3D 2026).md          # 本文档
├── CPak Common/                                # 元件库与自定义脚本
│   ├── ChemicalPlant170.pcat                   # 化工元件库数据库
│   ├── ChemicalPlant170/                       # 元件预览缩略图 (32/64/200/640)
│   └── CustomScripts/                          # 全部参数化 Python 脚本与配置
└── Spec Sheets (等级库工作表)/                  # 项目等级库
    ├── ChemicalPlant170.pspc                   # 等级库主数据库
    └── ChemicalPlant170.pspx                   # 等级库打包外壳文件
```

---

## 二、 安装步骤（AutoCAD Plant 3D 2026）

### 第 1 步：关闭 AutoCAD Plant 3D 2026
部署元件库和脚本前，请先退出所有正在运行的 AutoCAD Plant 3D 进程。

### 第 2 步：部署元件库与 CustomScripts
打开本机的 Plant 3D 2026 公共内容目录（默认路径）：
```text
C:\AutoCAD Plant 3D 2026 Content\CPak Common\
```
将压缩包内 **`CPak Common/`** 文件夹下的所有内容复制到上述目录中（如提示文件已存在，建议先备份原目录后选择覆盖/合并）：
- `ChemicalPlant170.pcat`
- `ChemicalPlant170\` 文件夹
- `CustomScripts\` 文件夹

> **注意**：如果你的 Plant 3D 内容目录被修改到了其他盘符（可通过系统命令行 `PLANTCONTENTLOCATION` 或注册表查看），请复制到对应的 `CPak Common\` 目录。

### 第 3 步：部署项目等级库（Spec Sheets）
将压缩包内 **`Spec Sheets (等级库工作表)/`** 文件夹下的两个文件：
- `ChemicalPlant170.pspc`
- `ChemicalPlant170.pspx`

复制到你的 Plant 3D 项目根目录下的 **`Spec Sheets`**（中文版默认叫 **`等级库工作表`**）文件夹中，例如：
```text
C:\Users\<用户名>\Documents\<你的项目名>\等级库工作表\
```

### 第 4 步：注册自定义脚本（关键步骤）
1. 启动 **AutoCAD Plant 3D 2026** 并打开你的项目。
2. 在 AutoCAD 命令行输入以下命令并回车：
   ```text
   PLANTREGISTERCUSTOMSCRIPTS
   ```
3. 等待命令行提示脚本编译与注册完成（通常数秒内完成）。
4. 重启 AutoCAD Plant 3D 2026（确保工具选项板与图标缓存刷新）。

---

## 三、 在项目中使用

1. **切换当前等级库**：在 Plant 3D 顶部功能区或“等级库与元件库管理器”中，将当前等级切换为 **`ChemicalPlant170`**。
2. **动态工具选项板**：切换到 **`ChemicalPlant170`** 后，右侧“动态工具选项板”会自动加载分类好的管件、法兰、阀门、仪表、支吊架与特种件，点击即可布管放置。
3. **规格编辑器二次调整**：如需扩充或微调某类阀门/管件的壁厚、压力等级或长描述，可用 **AutoCAD Plant 3D 2026 规格编辑器（Spec Editor）** 直接打开 `ChemicalPlant170.pspc` 和 `ChemicalPlant170.pcat`。

---

## 四、 常见问题与注意事项（必读）

### 1. 放置「90° 角式截止阀 / 放料阀」或「安全阀 PSV」时报错“无法连接不平行的端口”
- **原因**：`VALVE_ANGLE_GLOBE`（90度角式截止阀/放料阀）、`VALVE_SAFETY_PSV`（弹簧全启式安全阀）及 `VALVE_SAFETY_PILOT`（先导式安全阀）的两个端口呈 **90° 垂直关系**。
  若直接将它们拖到一根**连续直管的中间（捕捉“最近点”）**，Plant 3D 会试图打断直管并要求两个断口（180° 平行反向）同时接上阀门，从而必然触发“无法连接不平行的端口”错误。
- **正确做法**：
  - 将 90° 角阀/安全阀接到**管道的开放端点（Endpoint）**、**设备管嘴（Nozzle）**上，或先删除已有 90° 弯头露出两个开放管口后再放置并旋转对齐。
  - 接上第一端后，点击另一端蓝色 `+` 号即可沿 90° 方向继续布管。

### 2. 找不到工具选项板中的新增元件
- 请确认已执行 `PLANTREGISTERCUSTOMSCRIPTS` 并重启了 Plant 3D 2026。
- 请确认 `ChemicalPlant170.pspc` 和 `ChemicalPlant170.pspx` 已同时放在当前项目的 `等级库工作表`（`Spec Sheets`）目录中。
