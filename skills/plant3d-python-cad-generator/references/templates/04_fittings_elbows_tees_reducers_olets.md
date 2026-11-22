# AutoCAD Plant 3D 原厂典范源码母版 —— 类别四：复杂管件类（`CPBD`, `CPTS`, `CPTY`, `CPJREL`, `CPNO`）

> **所属分册**：`references/templates/04_fittings_elbows_tees_reducers_olets.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别四：复杂管件类（带支座弯头 / 斜三通 / Y型三通 / 偏心大小头 / 弯头支管台）

### 典范 13：`CPBD` —— 带 6 种底座形态的变径带支座弯头（Base Elbow）
- **原厂路径**：`varmain/arcsub/cpbdsub/cpbd.pyc`
- **工程亮点**：
  1. **防自交铁律**：`if R <= D / 2.0: R = D / 2.0 + 0.0001`，并传入半径 `D / 2.0` 调用 `ARC3D2`。
  2. **多形态支座切换（`DFT = 1~5`）**：支持双T型钢背靠背十字柱（`DFT=1`）、圆管立柱+圆法兰底板（`DFT=2`）、圆管立柱+方底板（`DFT=3`）、圆锥台支座（`DFT=4`）、方锥台支座（`DFT=5`）。
  3. **先并外轮廓、后减弯管内孔**：将支座 `oD1` 并入弯头外壳 `o0` 后，再用内径 `ARC3D2(s, D=O1/2.0, D2=O2/2.0, R=R, A=A)` 一次性贯通挖孔，保证支座插入弯头内部的部分被干净切除！

#### 原厂反编译源码与逐行几何注释
```python
def CPBD(s, D=114.3, D2=0.0, R=175.0, A=90.0, DFH=0.0, DFD=0.0, DFT=0, OF=-1.0, ID='CPBD', **kw):
    # 1. 弯曲半径防自交保护（铁律：R 必须大于管半径 D/2）
    if (R <= (D / 2.0)):
        R = ((D / 2.0) + 0.0001)
    if (D2 <= 0.0):
        D2 = D

    # 2. 创建外径变径弯头实体 o0，并通过 CPB_CalcPts 提取弯头关键特征点
    o0 = ARC3D2(s, D=(D / 2.0), D2=(D2 / 2.0), R=R, A=A)
    Pts = CPB_CalcPts(o0, A, None, None)
    OF = getThickness(D=D, OF=OF)
    arc3d2TMP = CYLINDER(s, R=((D * 0.01) / 2.0), H=(R * 0.01)).rotateY(-90).translate(Pts[8])
    arc3d2TMP.uniteWith(o0); o0.erase()
    o0 = arc3d2TMP

    # 3. 计算弯头外弧面至支座底面的几何截距 sPY 与立柱高 sH
    if (DFH <= 0.0): DFH = (D + D2)
    if (DFD <= 0.0): DFD = D
    xR = (D2 / 2.0) if (D2 <= D) else (D / 2.0)
    sPY = (sqrt((pow((R + xR), 2.0) - pow((R * tan((asRadiants(A) / 2.0))), 2.0))) - R)
    sH = (DFH - sPY)
    sT = (DFD * 0.1)
    stH = (DFD / 2.0) if (DFD <= (xR * 2.0)) else xR

    # 4. 按 DFT 枚举构建 5 种不同结构型式的弯头底座 oD1 / oD2
    oD1 = oD2 = None
    if (DFT == 1):  # 双 T 型钢组合十字筋板底座 + 方形底板
        stT2 = (sT / 2.0)
        stH = sqrt((pow(stH, 2.0) - pow((sT / 2.0), 2.0)))
        sPX = (sqrt((pow((R + xR), 2.0) - pow(((R * tan((asRadiants(A) / 2.0))) + stH), 2.0))) - R)
        oD1 = CSTE_T(s, H=(stH + stT2), W=(stH * 2.0), L=(DFH - sPX), T=sT).translate((0, ((stH / 2.0) - (stT2 / 2.0)), (-DFH)))
        oD3 = CSTE_T(s, H=((stH + stT2) + sPX), W=(stH * 2.0), L=(DFH - sPX), T=sT).translate((0, ((stH / 2.0) - (stT2 / 2.0)), (-DFH))).rotateZ(180.0)
        oD2 = BOX(s, L=DFD, W=DFD, H=sT).rotateX(-90).rotateY(-90).translate((0.0, 0.0, (-(DFH - (sT / 2.0)))))
        oD2.uniteWith(oD1); oD1.erase()
        oD1 = oD2; oD2 = oD3
    elif (DFT == 2):  # 圆柱立柱 + 圆底板
        oD1 = CYLINDER(s, R=(sT / 2.0), H=(sH + (sT / 2.0))).translate((0.0, 0.0, (((sT / 2.0) - sH) - sPY)))
        oD2 = CYLINDER(s, R=(DFD / 2.0), H=sT).rotateX(180.0).translate((0, 0, (-(DFH - sT))))
    elif (DFT == 3):  # 圆柱立柱 + 方底板
        oD1 = CYLINDER(s, R=(sT / 2.0), H=(sH + (sT / 2.0))).translate((0.0, 0.0, (((sT / 2.0) - sH) - sPY)))
        oD2 = BOX(s, L=DFD, W=DFD, H=sT).rotateX(-90).rotateY(-90).translate((0.0, 0.0, (-(DFH - (sT / 2.0)))))
    elif (DFT == 4):  # 圆锥底座
        oD1 = CONE(s, R1=(DFD / 2.0), R2=0.0, H=sH).translate((0, 0, ((-sH) - sPY)))
    elif (DFT == 5):  # 方锥底座
        oD1 = PYRAMID(s, L=DFD, W=DFD, H=sH).translate((0, 0, ((-sH) - sPY)))

    if oD2:
        oD1.uniteWith(oD2); oD2.erase()
    if oD1:
        oD1.rotateX(-90.0)
        o0.uniteWith(oD1); oD1.erase()

    # 5. 最后一步统一减去内孔弯管 o1，自动清除支座伸入管腔内的多余实体
    if (OF > 0.0):
        O1 = getInsideDiameter(D=D, OF=OF)
        O2 = getInsideDiameter(D=D2, OF=OF)
        o1 = ARC3D2(s, D=(O1 / 2.0), D2=(O2 / 2.0), R=R, A=A)
        o0.subtractFrom(o1); o1.erase()

    s.setPoint(Pts[4], Pts[6], 0.0)
    s.setPoint(Pts[5], Pts[7], 0.0)
```

---

### 典范 14：`CPTS` —— 任意支管倾角、变径过渡、内外壳一次差集斜三通（Lateral Tee）
- **原厂路径**：`varmain/teesub/cptssub/cpts.pyc`
- **工程亮点**：展示多通管件的黄金建模法则——**绝不分别给主管和支管单独挖孔（会导致主管壁挡死支管通道），而是先构建实心外表面合集 `o0 = o0 ∪ o1`，再构建实心内表面芯模合集 `o3 = o3 ∪ o4`，最后执行一次 `o0.subtractFrom(o3)` 贯通三向流道**；并使用 `mTransform().rotateZ(asRadiants(A))` 计算斜支管端口坐标与法向向量。

#### 原厂反编译源码与逐行几何注释
```python
def CPTS(s, D1=114.3, D2=114.3, D3=114.3, L1=105.0, L2=105.0, L3=95.0, A=90.0, OF=-1.0, ID='CPTS', **kw):
    I1 = float(kw.get('I1', 0.0))
    I2 = float(kw.get('I2', 0.0))
    I3 = float(kw.get('I3', 0.0))
    if (D2 == 0.0): D2 = D1
    if (D3 == 0.0): D3 = D1
    if (L2 == 0.0): L2 = L1
    if (L3 == 0.0): L3 = L1
    if (A == 0.0):  A = 90.0

    R1, R2, R3 = (D1 / 2.0), (D2 / 2.0), (D3 / 2.0)
    # 1. 计算三端内半径 O1, O2, O3
    Drill = 1
    if (OF > 0.0):
        O1 = ((D1 / 2.0) - OF) if ((D1 / 2.0) - OF) > 0.0 else (CON_OF_DIV(D1) / 2.0)
        O2 = ((D2 / 2.0) - OF) if ((D2 / 2.0) - OF) > 0.0 else (CON_OF_DIV(D2) / 2.0)
        O3 = ((D3 / 2.0) - OF) if ((D3 / 2.0) - OF) > 0.0 else (CON_OF_DIV(D3) / 2.0)
    elif (OF == -1):
        O1, O2, O3 = (CON_OF_DIV(D1) / 2.0), (CON_OF_DIV(D2) / 2.0), (CON_OF_DIV(D3) / 2.0)
    else:
        O1 = O2 = O3 = 0.0
        Drill = None

    # 2. 主管段外壳 o0 与内芯 o3（等径用 CYLINDER，异径用 CONE）
    if (D1 == D2):
        o0 = CYLINDER(s, R=R1, H=(L1 + L2), O=0.0).rotateY(270).translate((L2, 0, 0))
        if Drill:
            o3 = CYLINDER(s, R=O1, H=(L1 + L2), O=0.0).rotateY(270).translate((L2, 0, 0))
    else:
        o0 = CONE(s, R1=R1, R2=R2, H=(L1 + L2), E=0.0).rotateY(90).translate(((-L1), 0, 0))
        if Drill:
            o3 = CONE(s, R1=O1, R2=O2, H=(L1 + L2), E=0.0).rotateY(90).translate(((-L1), 0, 0))

    # 3. 支管段外壳 o1 与内芯 o4（绕 Z 轴偏转 A - 90°）
    A = (A - 90.0)
    if (D3 <= D1) and (D3 <= D2):
        o1 = CYLINDER(s, R=R3, H=L3, O=0.0).rotateX(270).rotateZ(A)
        if Drill:
            o4 = CYLINDER(s, R=O3, H=L3, O=0.0).rotateX(270).rotateZ(A)
    else:
        # 当支管直径大于主管时，根部采用 CONE 锥台平滑过渡
        L4 = (min(D1, D2) / 2.0)
        o1 = CYLINDER(s, R=(D3 / 2.0), H=(L3 - L4), O=0.0).rotateX(270).translate((0, L4, 0)).rotateZ(A)
        o2 = CONE(s, R1=L4, R2=(D3 / 2.0), H=L4, E=0.0).rotateX(-90).rotateZ(A)
        o1.uniteWith(o2); o2.erase()
        if Drill:
            O4 = O2 if (D1 > D2) else O1
            o4 = CYLINDER(s, R=O3, H=(L3 - L4), O=0.0).rotateX(270).translate((0, L4, 0)).rotateZ(A)
            o5 = CONE(s, R1=O4, R2=O3, H=L4, E=0.0).rotateX(-90).rotateZ(A)
            o4.uniteWith(o5); o5.erase()

    # 4. 外壳合并、内芯合并、最后一次差集贯通三通内腔
    o0.uniteWith(o1); o1.erase()
    if Drill:
        o3.uniteWith(o4); o4.erase()
        o0.subtractFrom(o3); o3.erase()

    # 5. 使用齐次变换矩阵计算斜支管端口 3 的坐标与外法向向量
    pP3 = (mTransform().rotateZ(asRadiants(A)) * mPoint(0, (L3 + I3), 0))
    pD3 = (mTransform().rotateZ(asRadiants(A)) * mVector(0, 1, 0))
    s.setPoint((((-L1) - I1), 0, 0), (-1, 0, 0))
    s.setPoint(((L2 + I2), 0, 0), (1, 0, 0))
    s.setPoint(pP3, pD3)
```

---

### 典范 15：`CPTY` —— 双支管对称分叉与根部防穿刺裁切 Y 型三通（True Wye）
- **原厂路径**：`varmain/teesub/cptysub/cpty.pyc`
- **工程亮点**：两根分叉支管分别绕 Z 轴旋转 `-A/2.0` 与 `+A/2.0`；更精妙的是第 1080~1086 行的**大夹角根部防溢出保护**：当分叉角 `A` 较大且主管段 `L1` 较短时，两侧斜支管的根部圆柱脚跟会凸出主管端面 `X = -L1`，原厂通过计算 `oL` 并在 `X = -L1` 处用 `o6` 切平端面！

#### 原厂反编译源码与逐行几何注释
```python
def CPTY(s, D1=114.3, D2=0.0, D3=0.0, L1=105.0, L2=0.0, L3=0.0, A=90.0, OF=-1.0, ID='CPTY', **kw):
    I1 = float(kw.get('I1', 0.0))
    I2 = float(kw.get('I2', 0.0))
    I3 = float(kw.get('I3', 0.0))
    if (D2 == 0.0): D2 = D1
    if (D3 == 0.0): D3 = D2
    if (L2 == 0.0): L2 = L1
    if (L3 == 0.0): L3 = L2
    if (A == 0.0):  A = 90.0

    OF = getThickness(D=D1, OF=OF, Ever=1)
    R1, R2, R3 = (D1 / 2.0), (D2 / 2.0), (D3 / 2.0)
    Drill = True
    if (OF > 0.0):
        O1 = (getInsideDiameter(D1, OF) / 2.0) or CON_OF_DIV(R1)
        O2 = (getInsideDiameter(D2, OF) / 2.0) or CON_OF_DIV(R2)
        O3 = (getInsideDiameter(D3, OF) / 2.0) or CON_OF_DIV(R3)
    else:
        O1 = O2 = O3 = 0.0
        Drill = False

    # 1. 入口主管段 o0 (沿 -X) + 右下分叉支管 o1 (-A/2) + 右上分叉支管 o2 (+A/2)
    o0 = CYLINDER(s, R=R1, H=L1, O=0.0).rotateY(270)
    if Drill:
        o3 = CYLINDER(s, R=O1, H=L1, O=0.0).rotateY(270)

    if (D2 == D1):
        o1 = CYLINDER(s, R=R2, H=L2, O=0.0).rotateY(90).rotateZ((0.0 - (A / 2.0)))
        if Drill: o4 = CYLINDER(s, R=O2, H=L2, O=0.0).rotateY(90).rotateZ((0.0 - (A / 2.0)))
    else:
        o1 = CONE(s, R1=R1, R2=R2, H=L2, E=0.0).rotateY(90).rotateZ((0.0 - (A / 2.0)))
        if Drill: o4 = CONE(s, R1=O1, R2=O2, H=L2, E=0.0).rotateY(90).rotateZ((0.0 - (A / 2.0)))

    if (D3 == D1):
        o2 = CYLINDER(s, R=R3, H=L3, O=0.0).rotateY(90).rotateZ((A / 2.0))
        if Drill: o5 = CYLINDER(s, R=O3, H=L3, O=0.0).rotateY(90).rotateZ((A / 2.0))
    else:
        o2 = CONE(s, R1=R1, R2=R3, H=L3, E=0.0).rotateY(90).rotateZ((A / 2.0))
        if Drill: o5 = CONE(s, R1=O1, R2=O3, H=L3, E=0.0).rotateY(90).rotateZ((A / 2.0))

    # 2. 外壳并集与三向内芯差集
    o1.uniteWith(o2); o2.erase()
    o0.uniteWith(o1); o1.erase()
    if Drill:
        o4.uniteWith(o5); o5.erase()
        o3.uniteWith(o4); o4.erase()
        o0.subtractFrom(o3); o3.erase()

    # 3. 根部防溢出保护：若分叉管脚跟投影长 oL > L1，则切平 X = -L1 左侧多余部分
    oL = sqrt((pow(R1, 2.0) - pow((R1 * cos(asRadiants((A / 2.0)))), 2.0)))
    if (oL > L1):
        o6 = CYLINDER(s, R=R1, H=(oL * 2.0), O=0.0).rotateY(-90.0).translate(((-L1), 0.0, 0.0))
        o0.subtractFrom(o6); o6.erase()

    # 4. 三个连接端口设置
    pP2 = (mTransform().rotateZ(asRadiants((0.0 - (A / 2.0)))) * mPoint((L2 + I2), 0, 0))
    pD2 = (mTransform().rotateZ(asRadiants((0.0 - (A / 2.0)))) * mVector(1, 0, 0))
    pP3 = (mTransform().rotateZ(asRadiants((A / 2.0))) * mPoint((L3 + I3), 0, 0))
    pD3 = (mTransform().rotateZ(asRadiants((A / 2.0))) * mVector(1, 0, 0))
    s.setPoint((((-L1) - I1), 0, 0), (-1, 0, 0))
    s.setPoint(pP2, pD2)
    s.setPoint(pP3, pD3)
```

---

### 典范 16：`CPJREL` —— 含左右直管段与偏心锥段的偏心大小头（Eccentric Reducer）
- **原厂路径**：`varmain/reducersub/cpjrelsub/cpjrel.pyc`
- **工程亮点**：
  1. 缺省偏心距 `E = (D1/2.0) - (D2/2.0)`，即工程标准的**底平（Flat on Bottom）或顶平偏心对齐**。
  2. 采用原生空心圆柱 `CYLINDER(s, R=D1/2.0, H=LL, O=DI1/2.0)` 构建左直段 `oI1` 与右直段 `oI2`（小端Z向偏移 `-E`），无需额外布尔差集。

#### 原厂反编译源码与逐行几何注释
```python
def CPJREL(s, D1=114.3, D2=60.3, L=210.0, E=0.0, LL=0.0, LR=0.0, OF=-1.0, ID='CPJREL', **kw):
    # 1. 缺省偏心距 E = R1 - R2（保证大端与小端切线平齐）
    if (E == 0.0):
        E = ((D1 / 2.0) - (D2 / 2.0))
    if (LL == 0.0) and (LR == 0.0):
        LL = (L / 3.0)
        LR = LL
    elif (LL == 0.0):
        LL = ((L - LR) / 2.0)
    elif (LR == 0.0):
        LR = ((L - LL) / 2.0)

    OF = getThickness(D1, OF=OF)
    noLeft = 1 if (LL == -2) else 0
    noRight = 1 if (LR == -2) else 0
    if noLeft:  LL = 0.0
    if noRight: LR = 0.0
    LM = (L - (LL + LR))
    if (OF == 0.0): OF = -1

    # 2. 中部偏心圆台段 o0（调用 CPJRE）
    o0 = CPJRE(s, D1=D1, D2=D2, L=LM, E=E, OF=OF).translate((LL, 0, 0))
    oTMP = CYLINDER(s, R=(D1 / 2.0), H=0.001, O=((D1 - 1.0) / 2.0)).rotateY(90).translate((LL, 0, 0))
    oTMP.uniteWith(o0); o0.erase()

    # 3. 左侧大径直管段 oI1（中心在 Z = 0）与右侧小径直管段 oI2（中心在 Z = -E）
    if (noLeft == 0):
        DI1 = getInsideDiameter(D=D1, OF=OF, Ever=1)
        oI1 = CYLINDER(s, R=(D1 / 2.0), H=LL, O=(DI1 / 2.0)).rotateY(270).translate((LL, 0, 0))
        oTMP.uniteWith(oI1); oI1.erase()
    if (noRight == 0):
        DI2 = getInsideDiameter(D=D2, OF=OF, Ever=1)
        oI2 = CYLINDER(s, R=(D2 / 2.0), H=LR, O=(DI2 / 2.0)).rotateY(90).translate(((L - LR), 0, (-E)))
        oTMP.uniteWith(oI2); oI2.erase()

    # 4. 端口 1 在 (0, 0, 0) 朝 -X，端口 2 在 (L, 0, -E) 朝 +X
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, (-E)), (1, 0, 0))
```

---

### 典范 17：`CPNO` —— `ARC3D` + `setTransformationMatrix` 齐次变换弯管支管台
- **原厂路径**：`varmain/weldentsub/cpnosub/cpno.pyc`
- **工程亮点**：展示了 `o1.pointAt(1)`、`o1.directionAt(1)` 与 `t1 = mTransform().translate(...)`、`o1.setTransformationMatrix(t1)` 的高阶矩阵变换协同用法，以及如何用被接主管圆柱 `o3` 切出支管台底部精确贴合主管外壁的马鞍口（`o1.subtractFrom(o3)`）。

#### 原厂反编译源码与逐行几何注释
```python
def CPNO(s, D=114.3, R=300.0, L=100.0, D2=0.0, A=90.0, OF=-1.0, ID='CPNO', **kw):
    vC = CPNO_util(D=D, D2=D2, OF=OF, L=L, R=R, A=A)
    R1 = (vC[0] / 2.0)  # 支管外半径
    R2 = (vC[1] / 2.0)  # 主管外半径

    # 1. 创建弯管主体 o1 并查询其末端特征点 pointAt(1)
    o1 = ARC3D(s, D=R1, R=vC[6], A=vC[2])
    p2 = o1.pointAt(1)
    yMove = (R2 - R1)
    extLen = (vC[7] - vC[6])
    xMove = (0.0 - p2.x())
    if (extLen < 0.0):
        yMove = (vC[7] - p2.y())
        xL = L
        xMove = ((0.0 - p2.x()) - (xL * cos(asRadiants(vC[2]))))
        yMove = ((vC[7] - p2.y()) - (xL - (xL * sin(asRadiants(vC[2])))))

    # 2. 构造齐次平移矩阵 t1 并直接赋给实体 o1，同时用 t1 * o1.pointAt(1) 同步变换特征点
    t1 = mTransform().translate((xMove, yMove, 0.0))
    o1.setTransformationMatrix(t1)
    pA1o = mPoint(0, 0, 0)
    pD1 = mVector(0, -1, 0)
    pA2o = (t1 * o1.pointAt(1))
    pD2 = o1.directionAt(1)

    if (vC[6] < vC[7]):
        o2 = CYLINDER(s, R=R1, H=extLen, O=0.0).rotateX(270.0).rotateZ((90.0 - A)).translate(pA2o)
        o1.uniteWith(o2); o2.erase()

    # 3. 减去支管内孔弯管 d1 + d2
    if vC[5]:
        d1 = ARC3D(s, D=(R1 - vC[4]), R=vC[6], A=vC[2])
        d1.setTransformationMatrix(t1)
        if (vC[6] < vC[7]):
            d2 = CYLINDER(s, R=(R1 - vC[4]), H=extLen, O=0.0).rotateX(270.0).rotateZ((90.0 - A)).translate(pA2o)
            d1.uniteWith(d2); d2.erase()
        o1.subtractFrom(d1); d1.erase()

    # 4. 用主管外径圆柱 o3 切除支管台根部，形成马鞍面
    o3 = CYLINDER(s, R=R2, H=(vC[6] * 2.0), O=0.0).rotateY(270).translate((vC[6], 0, 0))
    if (vC[7] < vC[6]):
        o4 = BOX(s, H=(vC[6] * 2.0), W=(vC[0] * 2.0), L=vC[6]).translate(((vC[6] / 2.0), (-(vC[6] / 2.0)), 0.0))
        o3.uniteWith(o4); o4.erase()
    o1.subtractFrom(o3); o3.erase()

    pA2 = mPoint((-(L * cos(asRadiants(vC[2])))), ((L * sin(asRadiants(vC[2]))) + (vC[1] / 2.0)), 0.0)
    s.setPoint(pA1o, pD1)
    s.setPoint(pA2, pD2)
```

---
