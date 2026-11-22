# WPF 界面离屏渲染与遮挡检查

不启动 AutoCAD，把插件里每个 `Window` 渲染成 PNG，并自动诊断控件遮挡、截断、下拉弹层被裁等问题。

## 为什么要单独做一个工具

这些窗口的代码后置直接引用了 AutoCAD 托管类型（`Autodesk.AutoCAD.*`），
普通的「截图看一下」很难覆盖真实交互态：

- **下拉弹层是独立顶层窗口**（`Popup`），不在窗口视觉树里，整屏截图会被其它程序干扰；
- **窗口最小宽度**下才暴露的溢出，正常尺寸看不出来；
- **表格列头**被压缩后只剩一个字，肉眼容易忽略。

所以工具直接遍历可视树做几何断言，而不是靠肉眼看图。

## 用法

```bash
# 先构建插件本体
dotnet build src/P3dPyPad/P3dPyPad.csproj

# 构建渲染工具
dotnet build tools/render/RenderWpfViews.csproj

# acdbmgd/acmgd 是混合模式程序集，加载时需要能解析到同目录的本地库，
# 因此把 AutoCAD 安装目录加进 PATH 再运行
export PATH="/c/Program Files/Autodesk/AutoCAD 2019:$PATH"
./build/bin/Debug/RenderWpfViews.exe --out .render-out
```

可选参数：

| 参数 | 说明 |
|---|---|
| `--out DIR` | 输出目录，默认 `.render-out` |
| `--scale N` | 渲染倍率，默认 `1.0`；`1.5` 可模拟高 DPI 下的取整误差 |

## 产物

```
.render-out/
  <Window>.png                    窗口默认尺寸截图
  <Window>.minwidth.png           窗口拉到 MinWidth 时的截图
  <Window>.<Combo>.dropdown.png   单个 ComboBox 展开后的弹层截图
  report.json                     诊断结果
```

`report.json` 每个窗口包含：

| 字段 | 含义 |
|---|---|
| `issues` | 默认尺寸下的遮挡/截断问题 |
| `minWidthIssues` | 最小宽度下的同类问题 |
| `dropDowns[]` | 每个下拉的项数、弹层实际高度、所需高度、是否被压缩、是否可滚动 |
| `bottomEdgePlacements[]` | 翻转判定及其几何依据（`below` / `above`） |

## 诊断项

| 类型 | 含义 |
|---|---|
| `OUT_OF_WINDOW` | 控件跑出窗口内容区 |
| `OVERFLOWS_PARENT` | 超出直接父容器（`WrapPanel`/`StackPanel` 默认不裁剪，溢出部分会被遮挡或看不见） |
| `CLIPPED_BY_ANCESTOR` | 被带 `ClipToBounds` 的祖先裁掉 |
| `OVERLAP` | 两个可交互控件重叠面积超过 15% |
| `DROPDOWN_OFFSCREEN` | 弹层越出屏幕工作区 |
| `DROPDOWN_ASSIST_INACTIVE` | 下拉没有挂上自动翻转行为 |
| `DROPDOWN_PLACEMENT_MISMATCH` | 翻转方向与几何事实不符 |
| `FLIP_LOGIC_ERROR` | 翻转判定自检失败（贴近底边应向上、靠顶部应向下） |

`DataGridColumnHeadersPresenter` 内部的横向溢出属于表格滚动预期行为，不计入缺陷。

## 相关修复记录

本轮通过该工具定位并修复的问题：

1. **ComboBox 内部的 `ToggleButton` 继承隐式样式 `Height=36`**
   箭头按钮撑在 28px 高的下拉框里纵向溢出 8px，压住下一行控件——
   这是「下拉框被挡住」的真正根因。模板内显式 `Height="Auto"` + `MinHeight/MinWidth=0` 解决。
2. **弹层固定 `Placement="Bottom"`**
   靠近屏幕底边时列表向下长出可视区被裁。新增 `ComboBoxAssist`
   （`DropDownOpened` 时按屏幕工作区判断，必要时翻到上方并收紧高度）。
3. **`BatchTestWindow` 工具栏横向溢出**
   左侧快捷目录组把右侧「一键发布 / 在单件测试中打开选中项 / 打开出图目录」挤出窗口，
   最后一个按钮只剩半个字。改为整条工具栏 `WrapPanel` + 组内不可拆分。
4. **`Loc.BatchAddToSpecBtn` 等 3 个本地化键缺失**
   主按钮内容为空，界面上只剩一个空白色块；表头显示空白。
5. **`CatalogManagerWindow` 表头被截断**
   `规格数`→`规`、`公称直径范围`整列消失。加宽列 + `MinWidth` 兜底，
   表头模板改 `TextBlock` 以支持省略号，并挂 `ToolTip` 保证全文可读。
6. **目标等级库下拉与按钮重叠**
   单行布局在窄窗口下把下拉压到 60 多像素并与按钮重叠，改为两行布局。
