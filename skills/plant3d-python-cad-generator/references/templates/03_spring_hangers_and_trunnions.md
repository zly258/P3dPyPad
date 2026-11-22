# AutoCAD Plant 3D 原厂典范源码母版 —— 类别三：弹簧吊架、球面铰接吊架与耳轴支座类（`CSGH001`, `CSGH002`, `CSGF001`）

> **所属分册**：`references/templates/03_spring_hangers_and_trunnions.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别三：弹簧吊架、球面铰接吊架与耳轴支座类（`varmain/supportssub/`）

### 典范 10：`CSGH001` —— 恒力/可变弹簧整定吊架总成（Spring Hanger）
- **原厂路径**：`varmain/supportssub/csghsub/csgh001.pyc`
- **工程结构**：自下而上由 4 大模块串联构成（在局部 +Y 轴上顺序堆叠，最后 `.rotateZ(90.0)` 翻转为沿 -X 方向拉伸）：
  1. `o0`：底部双栓管夹 `CSGC002`。
  2. `o1a/o1b/o1c`：三明治交错耳板连接过渡段（长度 `HL1`）。
  3. `o2a/o2b/o2c`：弹簧罐体（下部 `CONE` 锥形过渡段 `HL21` + 中部 `CYLINDER` 主筒体 + 顶部 `CYLINDER` 法兰压盖 `HL22`）。
  4. `o3` + `o4a~o4d`：上部吊杆 `o3` 与顶部生根 U 型耳座销轴组件。

#### 原厂反编译源码与逐行几何注释
```python
def CSGH001(s, D=116.0, H=500.0, L=30.0, W=4.0, K=0.0, HL1=0.0, HL2=0.0,
            HL21=0.0, HL22=0.0, HD21=0.0, HD22=0.0, HD3=0.0, HT4=0.0,
            HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGH001', **kw):
    R1 = (D / 2.0)
    R2 = (R1 + W)
    if (K <= 0.0):    K = (D + (L * 2.0))
    W1 = (W * 3.0)
    L1 = ((K - D) / 2.0)
    oVal = (W / 10.0)
    if (HL1 <= 0.0):  HL1 = ((H - R1) / 5.0)
    if (HL2 <= 0.0):  HL2 = ((H - R1) / 3.0)
    if (HD21 <= 0.0): HD21 = D
    if (HD3 <= 0.0):  HD3 = (D / 10.0)

    # 模块 1：底部管夹 CSGC002
    o0 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90)

    # 模块 2：下部三片式连接耳板 o1a, o1b, o1c
    xL1 = (((HL1 - L1) + W) - oVal)
    xL2 = (HL1 - oVal)
    o1a = BOX(s, L=xL1, W=L, H=W).translate((W, ((((xL1 / 2.0) + R1) + L1) + oVal), 0.0))
    o1b = BOX(s, L=xL2, W=(L - (oVal * 2.0)), H=W).translate((0.0, ((((xL2 / 2.0) + R1) + W) + oVal), 0.0))
    o1c = BOX(s, L=xL1, W=L, H=W).translate(((-W), ((((xL1 / 2.0) + R1) + L1) + oVal), 0.0))

    # 模块 3：弹簧缸体（锥顶 o2a + 主圆筒 o2b + 顶盖法兰盘 o2c）
    cR1 = ((sqrt((pow(W1, 2.0) + pow(L, 2.0))) / 2.0) + oVal)
    if (HL21 <= 0.0): HL21 = ((HD21 / 2.0) - cR1)
    if (HL22 <= 0.0): HL22 = (HL2 / 10.0)
    if (HD22 <= 0.0): HD22 = (HD21 * 1.2)
    cR2 = (HD21 / 2.0)
    cR3 = (HD22 / 2.0)
    o2a = CONE(s, R1=cR1, R2=cR2, H=HL21, E=0.0).rotateX(-90.0).translate((0.0, ((R1 + W) + HL1), 0.0))
    o2b = CYLINDER(s, R=cR2, H=((HL2 - HL21) - HL22), O=0.0).rotateX(-90.0).translate((0.0, (((R1 + W) + HL1) + HL21), 0.0))
    o2c = CYLINDER(s, R=cR3, H=HL22, O=0.0).rotateX(90.0).translate((0.0, (((R1 + W) + HL1) + HL2), 0.0))

    # 模块 4：上部吊杆 o3 与生根 U 型吊耳 o4a~o4d
    cL3 = ((((H - R1) - W) - HL1) - HL2)
    o3 = CYLINDER(s, R=(HD3 / 2.0), H=cL3, O=0.0).rotateX(-90.0).translate((0.0, (((R1 + W) + HL1) + HL2), 0.0))
    if (HT4 <= 0.0): HT4 = W
    if (HL4 <= 0.0): HL4 = (HD3 + (HT4 * 3.0))
    if (HW4 <= 0.0): HW4 = HD3
    if (HH4 <= 0.0): HH4 = HD3
    xL1 = (HL4 + (HT4 * 2.0))
    xH1 = ((H - ((HH4 - HT4) / 2.0)) - HT4)
    o4a = BOX(s, L=HH4, W=HW4, H=HT4).translate((((HL4 / 2.0) - (HT4 / 2.0)), (H - (HH4 / 2.0)), 0.0))
    o4b = BOX(s, L=HH4, W=HW4, H=HT4).translate(((-((HL4 / 2.0) - (HT4 / 2.0))), (H - (HH4 / 2.0)), 0.0))
    o4c = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, (H - (HT4 / 2.0)), 0.0))
    o4d = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate(((xL1 / 2.0), xH1, 0.0))

    # 分组级联布尔并集
    for p in (o4c, o4b, o4a): o4d.uniteWith(p); p.erase()
    for p in (o2b, o2a):      o2c.uniteWith(p); p.erase()
    for p in (o1b, o1a):      o1c.uniteWith(p); p.erase()
    for p in (o3, o2c, o1c, o0): o4d.uniteWith(p); p.erase()

    o4d.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), ((-H), 0, 0))
```

---

### 典范 11：`CSGH002` —— `intersectWith` 球面交集与 `subtractFrom` 管孔切除吊架
- **原厂路径**：`varmain/supportssub/csghsub/csgh002.pyc`
- **工程亮点**：同时展示了三大 CSG 布尔运算（**交集 `intersectWith` + 并集 `uniteWith` + 差集 `subtractFrom`**）：
  - 先用圆柱 `o0a` 与球体 `o0b = SPHERE(s, R=mR1)` 求交集 `o0a.intersectWith(o0b)` 生成半球底壳；
  - 并入上部筒体、锥体、吊杆、顶耳后，最后用管道圆柱 `o0d` 执行 `o0a.subtractFrom(o0d)` 贯穿切出管道抱箍孔。

#### 原厂反编译源码与逐行几何注释
```python
def CSGH002(s, D=116.0, H=500.0, W=4.0, HL2=0.0, HL21=0.0, HL22=0.0,
            HD21=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGH002', **kw):
    R1 = (D / 2.0)
    if (HL2 <= 0.0):  HL2 = ((H - R1) / 2.0)
    if (HD21 <= 0.0): HD21 = (D * 0.66666666)
    if (HL21 <= 0.0): HL21 = ((HL2 - R1) * 0.66666666)
    if (HL22 <= 0.0): HL22 = ((HL2 - R1) * 0.15)
    if (HD3 <= 0.0):  HD3 = (D / 10.0)
    mR1 = (R1 + W)
    mR2 = (HD21 / 2.0)

    # 1. 半球形包络底壳：圆柱 o0a 与球体 o0b 求布尔交集 intersectWith
    o0a = CYLINDER(s, R=mR1, H=(mR1 * 2.0), O=0.0).rotateX(90.0).translate((0.0, mR1, 0.0))
    o0b = SPHERE(s, R=mR1)
    o0c = CYLINDER(s, R=mR1, H=(HL2 - HL21), O=0.0).rotateX(-90.0)
    # o0d: 被包裹管道的切割圆柱（沿 Z 轴贯穿）
    o0d = CYLINDER(s, R=R1, H=(mR1 * 4.0), O=0.0).rotateZ(90.0).translate((0.0, 0.0, (-(mR1 * 2.0))))
    o0e = CONE(s, R1=mR1, R2=mR2, H=(HL21 - HL22), E=0.0).rotateX(-90.0).translate((0.0, (HL2 - HL21), 0.0))
    xH = (HL22 / 3.0)
    o0f = CYLINDER(s, R=mR2, H=xH, O=0.0).rotateX(90.0).translate((0.0, (HL2 - (xH * 2.0)), 0.0))
    o0g = CYLINDER(s, R=mR2, H=xH, O=0.0).rotateX(90.0).translate((0.0, HL2, 0.0))

    cL3 = (H - R1)
    o3 = CYLINDER(s, R=(HD3 / 2.0), H=cL3, O=0.0).rotateX(-90.0).translate((0.0, R1, 0.0))
    if (HT4 <= 0.0): HT4 = W
    if (HL4 <= 0.0): HL4 = (HD3 + (HT4 * 3.0))
    if (HW4 <= 0.0): HW4 = HD3
    if (HH4 <= 0.0): HH4 = HD3
    xL1 = (HL4 + (HT4 * 2.0))
    xH1 = ((H - ((HH4 - HT4) / 2.0)) - HT4)
    o4a = BOX(s, L=HH4, W=HW4, H=HT4).translate((((HL4 / 2.0) - (HT4 / 2.0)), (H - (HH4 / 2.0)), 0.0))
    o4b = BOX(s, L=HH4, W=HW4, H=HT4).translate(((-((HL4 / 2.0) - (HT4 / 2.0))), (H - (HH4 / 2.0)), 0.0))
    o4c = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, (H - (HT4 / 2.0)), 0.0))
    o4d = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate(((xL1 / 2.0), xH1, 0.0))

    # 2. 三大布尔运算联合执行：先交集 -> 再并集 -> 最后减去管道孔 o0d
    o0a.intersectWith(o0b); o0b.erase()
    for part in (o0c, o0e, o0f, o0g, o4d, o4c, o4b, o4a, o3):
        o0a.uniteWith(part); part.erase()
    o0a.subtractFrom(o0d); o0d.erase()

    o0a.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), ((-H), 0, 0))
```

---

### 典范 12：`CSGF001` —— 调用 `CSGCutOut` 自适应切除主管/弯头相贯马鞍口的耳轴支腿
- **原厂路径**：`varmain/supportssub/csgfsub/csgf001.pyc`
- **工程亮点**：展示了假管支腿（Dummy Leg / Adjustable Stanchion）如何调用 `var_basic.CSGCutOut(s, o1, D, kw)`，根据宿主是直管还是弯头（通过 `kw` 中的 ` ElbowRadius` 等上下文参数）自动裁切支腿顶部的马鞍相贯面！

#### 原厂反编译源码与逐行几何注释
```python
def CSGF001(s, D=114.3, L=500.0, AL=0.0, MD=0.0, MH=0.0, MW=0.0,
            SL=250.0, SW=200.0, ST=10.0, IL=0.0, ID='CSGF001', **kw):
    if (L <= 0.0):  L = (defaultPipeLength * 2.0)
    OF = getThickness(D=D, OF=0.0, Ever=1, mustCalc=True)
    if (AL <= 0.0): AL = (L / 3.0)
    if (MD <= 0.0): MD = (D - (OF * 4.0))
    if (SW <= 0.0): SW = SL
    R = (D / 2.0)
    cL = (L - AL) + (IL if AL > 0.0 else 0.0)

    # 1. 上部耳轴假管段 o1 + 下部可调六角头螺柱 o2 + 调节螺母 o3/o4 + 法兰垫圈 o5 + 底板 o6
    o1 = CYLINDER(s, R=(D / 2.0), H=cL, O=0.0).translate((0.0, 0.0, ((-L) + AL)))
    o2 = CBOLT6_001(s, D=MD, L=AL, W=MW, H=MH, P=1).rotateY(-90.0).translate((0.0, 0.0, (-L)))
    o3 = CNUT6_001(s, D=MD, W=MW, H=MH).rotateY(90.0).translate((0.0, 0.0, ((-L) + AL)))
    if (MH <= 0.0):
        MH = abs((o3.pointAt(1).z() - o3.pointAt(0).z()))
    o4 = None
    if ((MH * 3.0) < (AL - ST)):
        o4 = CNUT6_001(s, D=MD, W=MW, H=MH).rotateY(90.0).rotateZ(90.0).translate(o3.pointAt(1))
    o5 = CYLINDER(s, R=(R + (OF * 4.0)), H=OF, O=0.0).translate((0.0, 0.0, ((-L) + AL)))
    o6 = None
    if (SL > 0.0) and (SW > 0.0) and (ST > 0.0):
        o6 = BOX(s, L=SL, H=SW, W=ST).translate((0.0, 0.0, (-(L - (ST / 2.0)))))
        o2.translate((0.0, 0.0, ST))

    for part in (o2, o3, o4, o5, o6):
        if part:
            o1.uniteWith(part); part.erase()

    # 2. 核心：调用 var_basic.CSGCutOut 自动切除顶部与主管/弯头相交的马鞍口
    CSGCutOut(s, o1, D, kw)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, (-L)))
```

---
