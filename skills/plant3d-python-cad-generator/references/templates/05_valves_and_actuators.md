# AutoCAD Plant 3D 原厂典范源码母版 —— 类别五：阀门与执行机构总成类（`CPVA003513` + `CPVX513`, `CPVI013000`）

> **所属分册**：`references/templates/05_valves_and_actuators.md`（检索自 `references/templates/00_templates_index.md`）

---

## 类别五：阀门与执行机构总成类（`varmain/valvsub/`）

### 典范 18：`CPVA003513` + `CPVX513` —— 带气动薄膜执行机构与侧装手轮的三通/角阀总成
- **原厂路径**：`varmain/valvsub/cpva003sub/cpva003513sub/cpva003513.pyc` & `varmain/valvsub/cpvxsub/cpvx513.pyc`
- **工程亮点**：
  1. **封头高度自省**：`CPVX513` 创建 `oTH = ELLIPSOIDHEAD(s, R=D/2.0)` 后，调用 `vTH = oTH.parameters()['H']` 动态读取 C++ 内核计算出的标准椭球封头高度！
  2. **多级子件拼装与端口继承**：`CPVA003513` 调用阀体子脚本 `oV = CPVA003000(...)` 与执行机构子脚本 `oA = CPVX513(...)`，直接通过 `s.setPoint(oV.pointAt(0), oV.directionAt(0), vC[40])` 继承阀体端口，再用 `oTMP` 种子圆柱将阀体与执行机构合并，最后调用 `CPVA003000_Drill` 贯穿挖出阀体内流道。

#### 原厂反编译源码与逐行几何注释
```python
# --- 子部件 1：气动薄膜执行机构 + 侧装手轮 CPVX513 ---
def CPVX513(s, D=225.0, L=345.0, HD=225.0, HL=150.0, HP=300.0, HA1=0.0, HA2=0.0, ID='CPVX513', **kw):
    # 1. 创建顶部薄膜室椭球封头 oTH，并通过 .parameters()['H'] 内省获取封头高度 vTH
    oTH = ELLIPSOIDHEAD(s, R=(D / 2.0))
    vT = oTH.parameters()
    vTH = vT['H']
    oTH.translate((0, 0, (L - vTH)))

    # 2. 创建下部倒锥形支架体 oC1 与侧装手轮子件 oC2 (CPVX002)
    oC1 = CONE(s, R1=(D / 2.0), R2=0.0, H=(L - vTH)).rotateY(180).translate((0, 0, (L - vTH)))
    if (HD <= 0.0): HD = D
    if (HL <= 0.0): HL = (D * 0.75)
    if (HP <= 0.0): HP = (L * 0.75)
    oC2 = CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY((-HA2)).rotateZ((90.0 - HA1)).translate((0.0, 0.0, HP))

    oTH.uniteWith(oC1); oC1.erase()
    oTH.uniteWith(oC2); oC2.erase()

# --- 主部件 2：角阀/三通阀体 + 执行机构总成 CPVA003513 ---
def CPVA003513(s, D1=114.3, D2=0.0, L1=175.0, L2=0.0, H1=220.0, H2=0.0,
               W1=0.0, W2=0.0, HB=220.0, WB=240.0, LB=260.0, A=0.0, OF=-1.0,
               B1=22.0, B2=0.0, DA=225.0, HA=345.0, A1=90.0, A2=90.0, P=0,
               HD=225.0, HL=150.0, HP=300.0, HA1=0.0, HA2=0.0, ID='CPVA003513', **kw):
    vC = CPVA003CORRV(D1=D1, D2=D2, L1=L1, L2=L2, H1=H1, H2=H2, B1=B1, B2=B2,
                      W1=W1, W2=W2, LB=LB, WB=WB, HB=HB, A=A, OF=OF, L3=0.0, L4=0.0, I1=None, I2=None)
    aC = CPVA003CORRA(A=vC[11], P=P, L=vC[33], W=vC[34], H=vC[35], M=0)

    # 1. 实例化阀体 oV 与顶部执行机构 oA
    oV = CPVA003000(s, D1=vC[0], D2=vC[1], L1=vC[8], L2=vC[9], LB=vC[33], WB=vC[34], HB=vC[35],
                    H1=vC[4], H2=vC[5], B1=vC[29], B2=vC[30], W1=vC[38], W2=vC[39], A=vC[11], OF=vC[18])
    oA = CPVX513(s, D=DA, L=(HA - aC[2]), HD=HD, HL=HL, HP=(HP - aC[2]), HA1=HA1, HA2=HA2).rotateX((90.0 - A2)).rotateY((90.0 - A1))
    oA.translate((0, 0, aC[2])).rotateX(aC[0]).rotateZ(aC[1])

    # 2. 直接内省继承 oV 阀体的两个法兰端口坐标与法向向量
    s.setPoint(oV.pointAt(0), oV.directionAt(0), vC[40])
    s.setPoint(oV.pointAt(1), oV.directionAt(1), vC[41])

    # 3. 种子圆柱 oTMP 合并阀体与执行机构，最后减去阀体内流道 oC7
    oTMP = CYLINDER(s, R=0.01, H=0.01, O=0.0)
    oTMP.uniteWith(oV); oV.erase()
    oTMP.uniteWith(oA); oA.erase()
    if (vC[18] > 0.0):
        oC7 = CPVA003000_Drill(s, D1=vC[0], D2=vC[1], OF=vC[18], L1=vC[2], L2=vC[3], A=vC[10])
        oTMP.subtractFrom(oC7); oC7.erase()
```

---

### 典范 19：`CPVI013000` —— `ELLIPSOIDSEGMENT` 鼓形阀体与双端 `CPFBO` 法兰拼装阀
- **原厂路径**：`varmain/valvsub/cpvi013sub/cpvi013000sub/cpvi013000.pyc`
- **工程亮点**：使用 `ELLIPSOIDSEGMENT(s, RX=..., RY=..., A1=360.0, A2=0.0, A3=0.0, A4=180.0)` 构建全周完整的橄榄形/椭球形流线阀腔 `oC1`，两端合并 `CPFBO` 法兰盘 `oF1, oF2`，最后用 `CPVI013000_Drill` 挖穿流道。

#### 原厂反编译源码与逐行几何注释
```python
def CPVI013000(s, D1=114.3, D2=0.0, L=350.0, LS=0.0, H1=220.0, H2=0.0,
               W1=0.0, W2=0.0, OF=-1.0, B1=22.0, B2=0.0, ID='CPVI013000', **kw):
    vC = CPVI013CORRV(D1=D1, D2=D2, L=L, LS=LS, H1=H1, H2=H2, B1=B1, B2=B2,
                      W1=W1, W2=W2, OF=OF, L1=0.0, L2=0.0, I1=None, I2=None)
    # 1. 左右两端法兰盘 CPFBO
    oF1 = CPFBO(s, L=vC[30], D=vC[36], W=vC[37]).rotateX(vC[34]) if (vC[30] > 0.0) else None
    oF2 = CPFBO(s, L=vC[31], D=vC[38], W=vC[39]).rotateX(vC[35]).translate((((vC[3] + vC[4]) + vC[30]), 0, 0)) if (vC[31] > 0.0) else None

    # 2. 中部完整椭球阀体 (A1=360°, A3=0°~A4=180°)
    oC1 = ELLIPSOIDSEGMENT(s, RX=(vC[42] / 2.0), RY=vC[41], A1=360.0, A2=0.0, A3=0.0, A4=180.0).translate(((vC[30] + (vC[42] / 2.0)), 0.0, 0.0))
    if oF1:
        oC1.uniteWith(oF1); oF1.erase()
    if oF2:
        oC1.uniteWith(oF2); oF2.erase()

    # 3. 减去阀体内部锥形过渡流道
    if (vC[17] > 0.0):
        oC5 = CPVI013000_Drill(s, D1=vC[0], D2=vC[1], L1=vC[3], L2=vC[4], H1=vC[36], H2=vC[38], OF=vC[17]).translate((vC[30], 0.0, 0.0))
        oC1.subtractFrom(oC5); oC5.erase()

    s.setPoint(vC[11], vC[12], vC[34])
    s.setPoint(vC[13], vC[14], vC[35])
```

---
