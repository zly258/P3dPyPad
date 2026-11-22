# AutoCAD Plant 3D 原厂典范源码母版 —— 类别六：非标设备支耳、弧形补强板与天圆地方过渡件（`EQLUG`/`CSGP`/`BENDROUNDEDPLATE`, `CADAPT_SQ2RO`）

> **所属分册**：`references/templates/06_equipment_lugs_and_transitions.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别六：非标设备部件、容器支耳与天圆地方过渡件（`eqfactory` & `divsub`）

### 典范 20A：`EQLUG` + `CSGP` —— 贴合塔器外壁圆弧垫板的双筋板容器悬挂支耳
- **原厂路径**：`varmain/eqfactory.pyc`
- **工程亮点**：
  - 容器悬挂支耳（Vessel Lifting / Support Lug）不仅要生成水平承重底板 `o1` 与两块斜切三角筋板 `o2, o3`（用旋转 `ALPHA2` 的切刀块 `o4` 切除斜边），还要生成紧贴直径 `DA` 容器筒体曲面的**圆角弧形背衬垫板 `BENDROUNDEDPLATE`**，并用容器筒体圆柱 `o3 = CYLINDER(s, R=DA/2, H=H3)` 切平所有筋板与底板伸入设备内部的部分！

#### 原厂反编译源码与逐行几何注释
```python
def CSGP(s, DA=1000.0, S2=7.5, H1=200.0, H2=192.0, H3=250.0, E=160.0, F=140.0,
         G=125.0, K=25.0, R=32.0, S1=8.0, T1=125.0, T2=20.0, ID='CSGP', **kw):
    # 1. 计算容器筒体直径 DA 对应的弧长张角 ALPHA、弦长 SEHNE 与拱高 H / H4
    ALPHA = ((180 * H1) / ((pi * DA) / 2))
    SEHNE = (((sin((((ALPHA / 2) * pi) / 180)) * DA) / 2) * 2)
    H = ((DA / 2) - (sqrt(((4 * pow((DA / 2), 2)) - pow(SEHNE, 2))) / 2))
    H4 = (((DA / 2) + S2) - (sqrt(((4 * pow(((DA / 2) + S2), 2)) - pow(G, 2))) / 2))

    # 2. 计算三角加强筋板斜边倾角 ALPHA2 与切刀定位偏移 X, Y
    L1 = sqrt((pow((T1 - T2), 2) + pow((H2 - 20), 2)))
    ALPHA2 = ((acos(((H2 - 20) / L1)) * 180) / pi)
    L2 = (L1 / sqrt(2))
    X = (sin((((45 - ALPHA2) * pi) / 180)) * L2)
    Y = (cos((((45 - ALPHA2) * pi) / 180)) * L2)

    # 3. 支耳底板 o1 + 左右双立筋板 o2, o3（用倾斜切刀块 o4 切出梯形斜边）
    o1 = BOX(s, L=E, W=((F + S2) + H), H=S1).rotateY(90).translate((((((-F) - S2) + H) / 2), 0, (S1 / 2)))
    o2 = BOX(s, L=S1, W=T1, H=H2).rotateY(90).translate((((((-T1) / 2) - S2) + H4), ((G / 2) - (S1 / 2)), ((+S1) + (H2 / 2))))
    o3 = BOX(s, L=S1, W=T1, H=H2).rotateY(90).translate((((((-T1) / 2) - S2) + H4), (((-G) / 2) + (S1 / 2)), ((+S1) + (H2 / 2))))

    for gusset in (o2, o3):
        o4 = BOX(s, L=L1, W=G, H=L1).rotateY(90).rotateZ(90).rotateY(ALPHA2).translate((((((-S2) + H4) - T1) - X), 0, ((Y + 20) + S1)))
        gusset.subtractFrom(o4)
        o4.erase()
        o1.uniteWith(gusset)
        gusset.erase()

    # 4. 叠加贴合容器外壁的圆角弧形补强板 BENDROUNDEDPLATE，并用容器圆柱 o3 削平内侧
    o2 = BENDROUNDEDPLATE(s, DA=DA, S=S2, H=H3, LB=H1, R=R).translate((0, 0, (-K))) if (S2 > 0.0) else None
    o3 = CYLINDER(s, R=(DA / 2), H=H3, O=0).translate(((DA / 2), 0, (-K)))
    o1.subtractFrom(o3); o3.erase()
    if o2:
        o1.uniteWith(o2); o2.erase()

def EQLUG(s, D=1000.0, H=200.0, ID='CGSP1', **kw):
    CSGP(s, DA=D, S2=(H * 0.05), H1=H, H2=(H * 0.7), H3=H, E=(H * 0.8), F=(H * 0.7),
         G=(H * 0.6), K=(H * 0.1), R=(H * 0.1), S1=(H * 0.05), T1=(H * 0.7), T2=(H * 0.1)).rotateZ(180)
    s.setPoint((0, 0, 0), (0, -1, 0))
    s.setPoint((((-(((-H) * 0.7) - (H * 0.05))) / 2.0), 0, 0), (0, 0, -1))
```

---

### 典范 20B：`CADAPT_SQ2RO` + `CADAPT_SQ2SQ_Sub` —— 任意偏心“天圆地方”过渡件
- **原厂路径**：`varmain/divsub/cadapt_sq2ro.pyc` & `varmain/divsub/cadapt_sq2sq.pyc`
- **工程亮点**：当 `ROUNDRECT` 原生体素无法满足双轴同时偏心（`OL, OW`）且带壁厚翻边（`FB1, FB2, OF`）的复杂通风/烟风煤管道过渡件时，原厂展示了惊艳的**偏心圆台与偏心四棱台布尔求交（`intersectWith`）+ 内外包络相减抽壳算法**：
  1. `CADAPT_SQ2SQ_Sub`：先创建一个包容整个偏心范围的大长方体 `o0`，再用 4 个按 `atan2(CH, xl)` 倾角旋转的切刀长方体 `os1, os2, os3, os4` 削去四面斜坡，得到精确的双轴偏心四棱台；
  2. `CADAPT_SQ2RO_Sub`：创建一个底圆外接于底矩形（`RB = sqrt(LL^2 + LW^2)/2`）、顶圆半径为 `R`、偏心距为 `RE = sqrt(OL^2 + OW^2)` 的偏心圆台 `o1 = CONE(...)`，与外切偏心四棱台 `o2 = CADAPT_SQ2SQ_Sub(...)` 执行 **`o1.intersectWith(o2)`**，直接生成任意双轴偏心的实心天圆地方！
  3. `CADAPT_SQ2RO`：用外层实心天圆地方 `o1` 减去尺寸缩小 `2*OF` 的内层天圆地方 `s1`，瞬间完成均匀壁厚抽壳！

#### 原厂反编译源码与逐行几何注释
```python
def CADAPT_SQ2RO_Sub(s, LL=715.0, LW=700.0, R=225.0, OL=919.19, OW=698.28, H=2515.45, ID='CADAPT_SQ2RO_Sub', **kw):
    TL = (R * 2.0)
    TW = (R * 2.0)
    # 1. 底圆半径 RB 取底部矩形 (LL x LW) 的外接圆半径，确保底面完全覆盖矩形四角
    RB = (sqrt((pow(LL, 2.0) + pow(LW, 2.0))) / 2.0)
    RA = (90.0 - asDegrees(atan2(OL, OW)))
    RE = sqrt((pow(OL, 2.0) + pow(OW, 2.0)))

    # 2. 偏心圆锥台 o1 与偏心方锥台 o2 求布尔交集 intersectWith -> 形成任意偏心天圆地方实心体
    o1 = CONE(s, R1=RB, R2=R, H=H, E=RE).rotateZ(RA)
    o2 = CADAPT_SQ2SQ_Sub(s, LL=LL, LW=LW, TL=TL, TW=TW, OL=OL, OW=OW, H=H)
    o1.intersectWith(o2)
    o2.erase()
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setPoint((OL, OW, H), (0.0, 0.0, 1.0))

def CADAPT_SQ2RO(s, LL=715.0, LW=700.0, R=225.0, OL=919.19, OW=698.28, H=2515.45, OF=5.0, FB1=25.0, FB2=15.0, ID='CADAPT_SQ2RO', **kw):
    # 1. 构建外表面实心体 o1 并提取两端端口
    o1 = CADAPT_SQ2RO_Sub(s, LL=LL, LW=LW, R=R, OL=OL, OW=OW, H=H)
    p1, d1 = o1.pointAt(0), o1.directionAt(0)
    p2, d2 = o1.pointAt(1), o1.directionAt(1)
    oTMP = CYLINDER(s, R=(defaultTolerance / 2.0), H=defaultTolerance, O=0)
    oTMP.uniteWith(o1); o1.erase()

    # 2. 叠加方口法兰翻边 o2、圆口法兰翻边 o3，并减去缩进壁厚 OF 的内芯 s1 完成抽壳
    if (OF > 0):
        if (FB1 > 0.0):
            dFB1 = (FB1 * 2.0)
            o2 = BOX(s, L=(LL + dFB1), W=(LW + dFB1), H=OF).rotateX(-90).rotateY(-90).translate((0.0, 0.0, (OF / 2.0))).translate(p1)
            oTMP.uniteWith(o2); o2.erase()
        if (FB2 > 0.0):
            o3 = CYLINDER(s, R=(R + FB2), H=OF).translate((0.0, 0.0, (-OF))).translate(p2)
            oTMP.uniteWith(o3); o3.erase()
        dOF = (OF * 2.0)
        s1 = CADAPT_SQ2RO_Sub(s, LL=(LL - dOF), LW=(LW - dOF), R=(R - OF), OL=OL, OW=OW, H=H)
        oTMP.subtractFrom(s1); s1.erase()

    s.setPoint(p1, d1)
    s.setPoint(p2, d2)
```
