# AutoCAD Plant 3D 装饰器、连接端口与动态握点规范 (`03_decorators_ports_and_grips.md`)

> **数据源基准**：
> 1. 原厂反编译字节码：`variants.zip` -> `varmain/custom.pyc`（`PLANTREGISTERCUSTOMSCRIPTS` 注册器与 XML 元数据生成引擎核心实现）、`aqa/varmap/varindex.pyc`（`variants.map` 哈希索引引擎）及 49 个含 `setLinearDimension` 的原厂支吊架脚本。
> 2. 官方技术白皮书：`PD4214-L` (Pages 2, 32, 38–47) 与 `PD1746` (Pages 4–14)。

---

## 一、 装饰器语法规范与元数据注册引擎原理 (`varmain/custom.py`)

AutoCAD Plant 3D 存在两套并行的组件激活与元数据注册机制：
1. **现代装饰器机制（`from varmain.custom import *`）**：用于 `CPak Common\CustomScripts\` 下的用户自定义脚本，通过 `@activate`、`@group`、`@param`、`@enum` 声明元数据，由 `PLANTREGISTERCUSTOMSCRIPTS` 命令调用 `varmain.custom.dumpAll()` 自动生成 `<SCRIPT>.xml`、`variants.xml`、`ScriptGroup.xml` 和 `variants.map`。
2. **传统底层数据库绑定机制（`varmain.primitiv.activate`）**：用于 `variants.zip` 内置的 40,763 个原厂脚本，在函数定义末尾调用 `activate(FUNC, """[Type AQA-V...] ...""", "@VarDataDefault0")`。

### 1.1 `varmain/custom.py` 完整反编译源码与底层机制

```python
import varmain.primitiv as varmain
import sys as _sys
import os as _os
import imp as _imp
import codecs as _codecs

# 参数类型枚举常量
ANGLE = 1
BOOL = 2
ENUM = 3
INT = 4
LENGTH = 5
LENGTH0 = 6
STRING = 7

_collect = False
_scripts = {}

# 未显式声明 @param 时，根据函数默认参数值的 Python 类型自动推断 Plant 3D 参数类型
_autotypes = {
    type(0.0): LENGTH0,
    type(0): INT,
    type(True): BOOL,
    type(''): STRING,
    type(u''): STRING,
}

_typeStrings = [None, 'ANGLE', 'BOOL', 'ENUM', 'INT', 'LENGTH', 'LENGTH0', 'STRING']
```

> **从 `custom.pyc` 反编译揭示的三大底层铁律**：
> 1. **为什么 `@activate` 必须写在最顶层（第一行装饰器）？**
>    在 Python 中，装饰器按**自下而上（Bottom-Up）**顺序执行：`@enum` 与 `@param` 先把参数追加到 `md.ParamGroups[0]` 列表中，最后顶层的 `@activate.__call__(func)` 执行，将 `md.ParamGroups.reverse()`、`grp.Parameters.reverse()`、`p.EnumValues.reverse()` 翻转回书写顺序，并调用 `varmain.primitiv.activate(func)` 完成 C++ 注册！若把 `@activate` 写在 `@param` 下面，所有 `@param` 将在 `@activate` 之后执行，导致生成的 XML 丢失参数默认值！
> 2. **为什么 `s` 之后的所有参数都必须有默认值？**
>    在 `activate.__call__` 内部，提取参数默认值的源码为：
>    ```python
>    dfl = func.func_defaults
>    d = dict(map(None, func.func_code.co_varnames[1 : 1 + len(dfl)], dfl))
>    ```
>    它直接从 `co_varnames[1]`（即跳过第 0 个参数 `s`）开始按切片长度 `len(dfl)` 截取参数名并与 `func_defaults` 配对！**如果 `s` 之后有任何一个参数没有写默认值，切片就会发生错位，导致所有参数的默认值张冠李戴！**
> 3. **为什么装饰器支持无括号 `@activate` 和带括号 `@activate(...)`？**
>    `activate.__new__` 检查第一个参数 `Group` 是否 `callable(Group)`：若直接写 `@activate`，`Group` 就是被装饰的函数本身；若写 `@activate(Group="Support", ...)`，则返回实例并调用 `__call__(func)`。

---

### 1.2 四大装饰器完整属性字典

#### （1）`@activate(...)` —— 组件级元数据声明（必须作为第 1 个装饰器）
```python
@activate(
    Group="Support",
    FirstPortEndtypes="",
    Ports="1",
    TooltipShort="T-Slide Shoe Support",
    TooltipLong="Parametric T-Type Sliding Pipe Shoe with Ribs",
    ThumbnailImage="CustomShoe_200.png",
    ParamDimImage="CustomShoe_Dim.png",
    SCEditDimImage="CustomShoe_SCE.png",
    Language="en",
    LengthUnit="mm"
)
```

| 属性名 | XML 映射属性 (`<Script>`) | 必填/可选 | 合法取值与工程含义 |
| :--- | :--- | :--- | :--- |
| **`Group`** | `ScriptGroup.xml -> <Group>` | **必填** | Plant 3D 元件等级库分类名（合法枚举值见下表 1.3） |
| **`Ports`** | `ConnPortNum="..."` | 强烈建议 | 连接端口数量字符串：`"0"`（纯设备）、`"1"`（支吊架/盲板/管帽/支管台）、`"2"`（直管/法兰/弯头/大小头/双通阀）、`"3"`（三通/三通阀/Y型过滤器）、`"4"`（四通/四通阀） |
| **`TooltipShort`** | `variants.xml -> <ToolTipShortColl>` | **必填** | 组件简短显示名称（在 Spec Editor 与工具选项板中显示） |
| **`TooltipLong`** | `variants.xml -> <ToolTipLongColl>` | **必填** | 组件详细功能描述 |
| **`LengthUnit`** | `LengthUnit="..."` | **必填** | 脚本默认尺寸单位：`"mm"`（公制毫米）或 `"in"`（英制英寸） |
| **`FirstPortEndtypes`** | `ScriptGroup.xml -> <FirstPortEndtypes>` | 可选 | 首端口连接端型过滤码，如 `"BV"`, `"PL"`, `"FL"`, `"THD"`, `"SW"`, `"WF"`（支吊架留空或省略） |
| **`ThumbnailImage`** | `Img="..."` | 可选 | 缩略图文件名（也可通过 `PlantSnapShot` 生成 `<ScriptName>_200.png` / `_64.png` / `_32.png` 自动识别） |
| **`ParamDimImage`** | `SizingImg="..."` | 可选 | 模型端参数尺寸标注示意图文件名 |
| **`SCEditDimImage`** | `SCESizingImg="..."` | 可选 | Spec/Catalog Editor 端参数尺寸示意图文件名 |
| **`Language`** | 内部语言标记 | 可选 | 如 `"en"`、`"zh-CN"`、`"de"` |

#### （2）合法的 `Group` 枚举值全表（1.3）

| `Group` 枚举值 | 对应的 Plant 3D 工程构件大类 | 典型端口数 (`Ports`) |
| :--- | :--- | :--- |
| **`"Support"`** | **管道支吊架**（管托、管卡、弹簧吊架、龙门架、耳轴、滚轮架；唯有设为 `"Support"` 才能被 Plant 3D Pipe Supports 模块识别并吸附管道） | `"1"` |
| **`"Elbow"`** | 弯头、弯管、虾米腰弯头、带支座弯头 | `"2"` |
| **`"Flange"`** | 对焊法兰、平焊法兰、松套法兰、盲板法兰、人孔 | `"1"` 或 `"2"` |
| **`"Tee"`** | 等径三通、异径三通、斜三通、Y型三通、弯头三通 | `"3"` |
| **`"Cross"`** | 正四通、斜四通、异径四通 | `"4"` |
| **`"Reducer"`** | 同心大小头、偏心大小头、天圆地方过渡件 | `"2"` |
| **`"Valve"`** / **`"ValveBody"`** | 闸阀、截止阀、球阀、蝶阀、止回阀、隔膜阀、安全阀、三通/四通调节阀 | `"2"`, `"3"`, `"4"` |
| **`"Actuator"`** | 手轮、手柄、伞齿轮箱、气动薄膜执行器、电动执行器、活塞执行器 | `"0"` 或 `"1"` |
| **`"Olet"`** | 支管台（Weldolet, Sockolet, Threadolet, Latrolet, Elbolet）、补强圈 | `"1"` 或 `"2"` |
| **`"Pipe"`** | 直管段、波纹膨胀节、软管 | `"2"` |
| **`"Cap"`** / **`"Blind"`** | 管帽、封头、8字盲板、插板盲板 | `"1"` 或 `"2"` |
| **`"Coupling"`** / **`"Gasket"`** | 管箍、活接头、哈夫节、法兰垫片 | `"2"` |
| **`"Filter"`** / **`"Instrument"`** | Y型过滤器、篮式过滤器、流量计、压力表、视镜 | `"1"`, `"2"`, `"3"` |
| **`"Vessel"`** / **`"Equipment"`** / **`"Pump"`** | 容器裙座、支耳、鞍座、封头、筒体、离心泵（配合 `.peqx` 设备模板打包） | `"0"`, `"1"`, `"2"` |

#### （3）`@group(...)`、`@param(...)`、`@enum(...)` 参数类型与映射表

```python
@group("MainDimensions", TooltipLong="Primary geometric dimensions")
# 写法 A（推荐简写）：直接以 参数名=类型常量 传入
@param(D=LENGTH, TooltipShort="Pipe Outer Diameter", TooltipLong="Nominal Pipe OD", Ask4Dist=False)
@param(H=LENGTH, TooltipShort="Support Height", TooltipLong="Centerline to baseplate bottom", Ask4Dist=True)
@param(OF=LENGTH0, TooltipShort="Wall Thickness", TooltipLong="Wall thickness (0 for solid)")
# 写法 B（完整关键字）：
@param(Name="K", Type=ENUM, TooltipShort="Rib Option", TooltipLong="Stiffener rib configuration")
@enum(0, "Without Stiffener Ribs")
@enum(1, "Single Side Rib")
@enum(2, "Double Side Ribs")
```

| Python 装饰器类型常量 | 内部整型值 | XML 输出 `Type` 字符串 | `.peqx` `EquipmentType.xml` 类型码 | 取值约束与工程用途详解 |
| :--- | :--- | :--- | :--- | :--- |
| **`LENGTH`** | `5` | `"LENGTH"` | `d` | **严格大于 0 的长度尺寸（`> 0`）**，支持公英制单位自动换算（如管外径 `D`、总长 `L`、高度 `H`） |
| **`LENGTH0`** | `6` | `"LENGTH0"` | `d0` / `d-` | **允许等于 0 或负数的长度/偏移量**（如壁厚 `OF=0.0` 或 `-1.0`、偏心距 `E=0.0`、可选垫板厚 `HH=0.0`） |
| **`ANGLE`** | `1` | `"ANGLE"` | `a` | **角度值（单位：度 Degrees）**，如弯头角度 `A=90.0`、斜三通支管角 `A=45.0` |
| **`INT`** | `4` | `"INT"` | `r` | **无量纲整数**，如虾米腰节数 `S=4`、筋板数量 `N=3`、开关标志 `P=1` |
| **`BOOL`** | `2` | `"BOOL"` | `b` | **布尔值（`True` / `False` 或 `1` / `0`）** |
| **`ENUM`** | `3` | `"ENUM"` | `List` / `Combo` | **枚举下拉选项**，其后必须紧跟一个或多个 `@enum(Value, TooltipLong)` 声明 |
| **`STRING`** | `7` | `"STRING"` | `s` | **字符串参数**，如公称直径标识 `DN="100"`、部件 ID `ID="CSGB001"` |
| *(注：标准脚本中无 `FLOAT` 常量)* | — | — | `r` | **重要提示**：`varmain/custom.py` 中**没有导出 `FLOAT` 常量**！所有带小数的尺寸均应声明为 `LENGTH` 或 `LENGTH0`，角度声明为 `ANGLE`；原厂底层 `dbtype` 字符串中浮点型写作 `DOUBLE` |

---

### 1.3 解析器死线规则（Parser Hard Constraints）

1. **装饰器与 `def` 之间严禁出现空行或 `#` 注释行**：
   - 从第一行 `@activate(...)` 开始，经过所有的 `@group(...)`、`@param(...)`、`@enum(...)`，直到 `def FUNC_NAME(s, ..., **kw):` 这一行，**中间必须连续紧挨，绝对不能插入任何空行或 `#` 注释**！否则 `PLANTREGISTERCUSTOMSCRIPTS` 解析器在部分版本中会中断装饰器链。
2. **AutoCAD Plant 3D (Python 2.7) 中文 Unicode 铁律（消除 UnicodeDecodeError）**：
   - Plant 3D 官方运行时运行在内嵌的 Python 2.7 环境下。**所有包含中文字符的字符串字面量（装饰器中 `TooltipShort`、`TooltipLong`、分组描述、参数默认值、代码中的中文提示等）必须显式添加 `u` 前缀**（如 `TooltipShort=u"90度对焊弯头"`，`TooltipLong=u"长半径弯头描述"`，`ID=u"ELBOW_90-DN100"`）；
   - 严禁使用普通字节串 `"中文"`，否则当宿主 C++ 读取或字符串拼接格式化时，会默认调用 ascii 解码并瞬间抛出 `UnicodeDecodeError: 'ascii' codec can't decode byte ...` 导致脚本注册失败或崩溃！
   - 文件第 1 行严格声明 `# -*- coding: utf-8 -*-`，并在导入前加入标准兼容头：
     ```python
     # -*- coding: utf-8 -*-
     import sys
     try:
         reload(sys)
         sys.setdefaultencoding('utf-8')
     except (NameError, AttributeError):
         pass
     ```
3. **文件编码必须是 UTF-8 无 BOM（`utf-8` without BOM）且使用标准 4 空格缩进**：
   - 切勿混用 Tab 与空格缩进；虽然 `custom.py` 输出 `.xml` 时使用 `utf_8_sig`，但输入的 `.py` 源码文件若带 BOM 头可能导致 `imp.load_source` 在首行报 `SyntaxError`。
4. **文件名、主函数名与 `ID` 默认值三者必须完全一致（推荐全大写）**：
   - 例如文件名为 `CUSTOM_SHOE.py`，则主函数必须定义为 `def CUSTOM_SHOE(s, D=114.3, ..., ID=u'CUSTOM_SHOE', **kw):`。
5. **函数签名必须以 `(s, ...)` 开头，以 `**kw` 结尾，且所有中间参数均赋予浮点数/整数默认值**：
   - Plant 3D 会在调用脚本时通过 `**kw` 传入诸如 `OD`（母管外径）、`OR`（母管弯曲半径）、`OO`（方向码）、`PartFamilyLongDesc` 等上下文参数，若缺少 `**kw` 会直接抛出 `TypeError: got an unexpected keyword argument`！

---
