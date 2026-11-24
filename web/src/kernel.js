// -*- coding: utf-8 -*-
/**
 * AutoCAD Plant 3D 核心几何造型内核 (OpenCASCADE.js / libcascade WebAssembly 驱动)
 * 适配 Plant 3D 原生几何原语 (BOX, CYLINDER, CONE, TORUS, ARC3D, SPHERE 等)
 * 支持布尔运算 (uniteWith, subtractFrom, intersectWith)、空间刚体变换与高保真网格剖分
 */

import { createInstance } from '../public/libcascade/init.single.js';

let oc = null;
let ocPromise = null;

/**
 * 异步初始化 OpenCASCADE (单线程离线版 libcascade)
 */
export async function initOpenCascade(onProgress) {
  if (oc) return oc;
  if (!ocPromise) {
    ocPromise = (async () => {
      if (onProgress) onProgress('正在加载 OpenCASCADE 几何造型内核 (WASM)...');
      const instance = await createInstance({
        locateFile: (file, prefix = '') => {
          if (file.endsWith('.wasm')) {
            return new URL('../public/libcascade/opencascade_single.wasm', import.meta.url).href;
          }
          return `${prefix}${file}`;
        }
      });
      oc = instance;
      return oc;
    })();
  }
  return ocPromise;
}

export function getOC() {
  if (!oc) throw new Error('OpenCASCADE 内核尚未初始化完成，请稍候！');
  return oc;
}

/**
 * Plant 3D 造型会话类 (Session)
 * 记录几何实体集合、端口数据 (Ports) 与工程标注点 (Dimensions)
 */
export class OccSession {
  constructor() {
    this.bodies = [];
    this.ports = [];
    this.dimensions = [];
    this.grips = this.dimensions;
    this.endpoints = null;
    this.color = null;
  }

  /**
   * 注册管道连接端口 (Port)
   * @param {[number, number, number]} pt 端口原点三维坐标
   * @param {[number, number, number]} dir 端口法向矢量 (朝外)
   */
  setPoint(pt, dir = [0, 0, 1]) {
    this.ports.push({
      point: [Number(pt[0]), Number(pt[1]), Number(pt[2])],
      direction: [Number(dir[0]), Number(dir[1]), Number(dir[2])]
    });
  }

  /**
   * 注册线性尺寸标注
   * @param {string} name 标注参数名称 (如 "R", "D", "L")
   * @param {[number, number, number]} p1 起点
   * @param {[number, number, number]} p2 终点
   * @param {[number, number, number]|null} ext_dir 引导线引出方向
   * @param {string|null} style 标注样式 (如 "linear", "leader_ext")
   */
  setLinearDimension(name, p1, p2, ext_dir = null, style = null) {
    const dim = {
      name: String(name),
      p1: [Number(p1[0]), Number(p1[1]), Number(p1[2])],
      p2: [Number(p2[0]), Number(p2[1]), Number(p2[2])],
      ext_dir: ext_dir ? [Number(ext_dir[0]), Number(ext_dir[1]), Number(ext_dir[2])] : null,
      style: style ? String(style) : 'linear'
    };
    this.dimensions.push(dim);
  }

  /**
   * 注册构件端点信息
   */
  setEndpoints(pt1, pt2) {
    this.endpoints = {
      pt1: [Number(pt1[0]), Number(pt1[1]), Number(pt1[2])],
      pt2: [Number(pt2[0]), Number(pt2[1]), Number(pt2[2])]
    };
  }

  /**
   * 设置构件显示颜色
   */
  setColor(color) {
    this.color = color;
  }

  /**
   * 清除会话中未被擦除的有效实体
   */
  getActiveBodies() {
    return this.bodies.filter(b => !b.erased && b.shape && !b.shape.IsNull());
  }

  /**
   * 合并所有存活实体为单个复合实体
   */
  getMergedShape() {
    const active = this.getActiveBodies();
    if (active.length === 0) return null;
    if (active.length === 1) return active[0].shape;

    let res = active[0].shape;
    for (let i = 1; i < active.length; i++) {
      res = fuseShapes(res, active[i].shape);
    }
    return res;
  }
}

/**
 * Plant 3D 几何实体封装类 (OccBody)
 * 封装 TopoDS_Shape 并提供与 Plant 3D 原生完全一致的方法链
 */
export class OccBody {
  constructor(session, shape, params = {}) {
    this.session = session;
    this.shape = shape;
    this.params = { ...params };
    this.erased = false;
    this.color = '#388bfd';
    if (session && session.bodies) {
      session.bodies.push(this);
    }
  }

  /**
   * 沿 X 轴旋转指定角度 (角度制)
   */
  rotateX(deg) {
    if (this.erased || !this.shape || Math.abs(deg) < 1e-6) return this;
    const rad = (deg * Math.PI) / 180.0;
    const trsf = new oc.gp_Trsf();
    const ax = new oc.gp_Ax1(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(1, 0, 0));
    trsf.SetRotation(ax, rad);
    this.shape = new oc.BRepBuilderAPI_Transform(this.shape, trsf, true).Shape();
    return this;
  }

  /**
   * 沿 Y 轴旋转指定角度 (角度制)
   */
  rotateY(deg) {
    if (this.erased || !this.shape || Math.abs(deg) < 1e-6) return this;
    const rad = (deg * Math.PI) / 180.0;
    const trsf = new oc.gp_Trsf();
    const ax = new oc.gp_Ax1(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 1, 0));
    trsf.SetRotation(ax, rad);
    this.shape = new oc.BRepBuilderAPI_Transform(this.shape, trsf, true).Shape();
    return this;
  }

  /**
   * 沿 Z 轴旋转指定角度 (角度制)
   */
  rotateZ(deg) {
    if (this.erased || !this.shape || Math.abs(deg) < 1e-6) return this;
    const rad = (deg * Math.PI) / 180.0;
    const trsf = new oc.gp_Trsf();
    const ax = new oc.gp_Ax1(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 0, 1));
    trsf.SetRotation(ax, rad);
    this.shape = new oc.BRepBuilderAPI_Transform(this.shape, trsf, true).Shape();
    return this;
  }

  /**
   * 空间平移向量
   * @param {[number, number, number]|number} dx 
   * @param {number} [dy=0] 
   * @param {number} [dz=0] 
   */
  translate(dx, dy = 0, dz = 0) {
    if (this.erased || !this.shape) return this;
    let x = 0, y = 0, z = 0;
    if (Array.isArray(dx) || (typeof dx === 'object' && dx !== null && 0 in dx)) {
      x = Number(dx[0] || 0);
      y = Number(dx[1] || 0);
      z = Number(dx[2] || 0);
    } else {
      x = Number(dx || 0);
      y = Number(dy || 0);
      z = Number(dz || 0);
    }
    if (Math.abs(x) < 1e-6 && Math.abs(y) < 1e-6 && Math.abs(z) < 1e-6) return this;

    const trsf = new oc.gp_Trsf();
    trsf.SetTranslation(new oc.gp_Vec(x, y, z));
    this.shape = new oc.BRepBuilderAPI_Transform(this.shape, trsf, true).Shape();
    return this;
  }

  /**
   * 等比缩放
   */
  scale(factor) {
    if (this.erased || !this.shape || Math.abs(factor - 1.0) < 1e-6) return this;
    const trsf = new oc.gp_Trsf();
    trsf.SetScale(new oc.gp_Pnt(0, 0, 0), Number(factor));
    this.shape = new oc.BRepBuilderAPI_Transform(this.shape, trsf, true).Shape();
    return this;
  }

  /**
   * 空间三轴缩放 (支持非等比)
   */
  scaleXYZ(sx, sy, sz) {
    if (this.erased || !this.shape) return this;
    if (Math.abs(sx - sy) < 1e-6 && Math.abs(sy - sz) < 1e-6) {
      return this.scale(sx);
    }
    const gpGTrsf = new oc.gp_GTrsf();
    const mat = new oc.gp_Mat(
      Number(sx), 0, 0,
      0, Number(sy), 0,
      0, 0, Number(sz)
    );
    gpGTrsf.SetVectorialPart(mat);
    this.shape = new oc.BRepBuilderAPI_GTransform(this.shape, gpGTrsf, true).Shape();
    return this;
  }

  /**
   * 布尔求并运算 (Union / Fuse)
   */
  uniteWith(other) {
    if (this.erased || !this.shape) return this;
    const otherShape = other instanceof OccBody ? other.shape : other;
    if (!otherShape || otherShape.IsNull()) return this;
    this.shape = fuseShapes(this.shape, otherShape);
    return this;
  }

  /**
   * 布尔求差运算 (Subtract / Cut)
   */
  subtractFrom(other) {
    if (this.erased || !this.shape) return this;
    const toolShape = other instanceof OccBody ? other.shape : other;
    if (!toolShape || toolShape.IsNull()) return this;
    this.shape = cutShapes(this.shape, toolShape);
    return this;
  }

  /**
   * 布尔求交运算 (Intersect / Common)
   */
  intersectWith(other) {
    if (this.erased || !this.shape) return this;
    const otherShape = other instanceof OccBody ? other.shape : other;
    if (!otherShape || otherShape.IsNull()) return this;
    this.shape = commonShapes(this.shape, otherShape);
    return this;
  }

  /**
   * 擦除标记 (用于临时布尔操作工具体)
   */
  erase() {
    this.erased = true;
    return this;
  }

  /**
   * 设置实体颜色
   */
  setColor(hex) {
    this.color = hex;
    return this;
  }
}

/**
 * OpenCASCADE 底层布尔合并
 */
export function fuseShapes(s1, s2) {
  const fuse = new oc.BRepAlgoAPI_Fuse(s1, s2);
  fuse.Build();
  if (fuse.IsDone()) {
    return fuse.Shape();
  }
  return s1;
}

/**
 * OpenCASCADE 底层布尔求差
 */
export function cutShapes(s1, s2) {
  const cut = new oc.BRepAlgoAPI_Cut(s1, s2);
  cut.Build();
  if (cut.IsDone()) {
    return cut.Shape();
  }
  return s1;
}

/**
 * OpenCASCADE 底层布尔求交
 */
export function commonShapes(s1, s2) {
  const common = new oc.BRepAlgoAPI_Common(s1, s2);
  common.Build();
  if (common.IsDone()) {
    return common.Shape();
  }
  return s1;
}

// ============================================================================
// Plant 3D 原生几何原语构造函数 (varmain.primitiv / varmain.custom)
// ============================================================================

/**
 * Plant 3D 长方体 (BOX)
 */
export function BOX(s, L = 100.0, W = 100.0, H = 100.0, kw = {}) {
  if (typeof L === 'object' && L !== null) {
    kw = L;
    L = kw.L;
    W = kw.W;
    H = kw.H;
  }
  const lVal = Math.max(1e-3, Number(L ?? 100.0));
  const wVal = Math.max(1e-3, Number(W ?? 100.0));
  const hVal = Math.max(1e-3, Number(H ?? 100.0));

  const p1 = new oc.gp_Pnt(-hVal / 2.0, -lVal / 2.0, -wVal / 2.0);
  const p2 = new oc.gp_Pnt(hVal / 2.0, lVal / 2.0, wVal / 2.0);
  const shape = new oc.BRepPrimAPI_MakeBox(p1, p2).Shape();
  return new OccBody(s, shape, { L: lVal, W: wVal, H: hVal });
}

/**
 * Plant 3D 角原点长方体 (CORNERBOX)
 * 放置最小角点于 (0, 0, 0)，沿 X 轴延伸 [0, L]，沿 Y 轴延伸 [0, W]，沿 Z 轴延伸 [0, H]
 */
export function CORNERBOX(s, ...args) {
  let L = 300.0, W = 200.0, H = 100.0;
  if (args.length > 0 && typeof args[0] === 'object' && !Array.isArray(args[0])) {
    const kw = args[0];
    if (kw.L !== undefined) L = Number(kw.L);
    if (kw.W !== undefined) W = Number(kw.W);
    if (kw.H !== undefined) H = Number(kw.H);
  } else {
    if (args[0] !== undefined) L = Number(args[0]);
    if (args[1] !== undefined) W = Number(args[1]);
    if (args[2] !== undefined) H = Number(args[2]);
  }
  return BOX(s, L, W, H).rotateX(-90).rotateY(-90).translate([L / 2.0, W / 2.0, H / 2.0]);
}

/**
 * Plant 3D 圆柱体 (CYLINDER)
 */
export function CYLINDER(s, ...args) {
  let R = 0, R1 = 0, R2 = 0, H = 0, O = 0;
  let kw = {};

  if (args.length > 0 && typeof args[args.length - 1] === 'object' && !Array.isArray(args[args.length - 1])) {
    kw = args.pop();
  }

  if (args.length === 2) {
    R = Number(args[0]);
    H = Number(args[1]);
  } else if (args.length === 3) {
    R = Number(args[0]);
    H = Number(args[1]);
    O = Number(args[2]);
  } else if (args.length >= 4) {
    R1 = Number(args[0]);
    R2 = Number(args[1]);
    H = Number(args[2]);
    O = Number(args[3]);
  }

  if (kw.R !== undefined) R = Number(kw.R);
  if (kw.R1 !== undefined) R1 = Number(kw.R1);
  if (kw.R2 !== undefined) R2 = Number(kw.R2);
  if (kw.H !== undefined) H = Number(kw.H);
  if (kw.O !== undefined) O = Number(kw.O);

  if (R <= 0 && R1 > 0) R = R1;
  R = Math.max(1e-3, R);
  H = Math.max(1e-3, H);
  O = Math.max(0, O);

  const ax = new oc.gp_Ax2(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 0, 1));
  let shape = new oc.BRepPrimAPI_MakeCylinder(ax, R, H).Shape();

  if (O > 1e-4 && O < R - 1e-4) {
    const axCut = new oc.gp_Ax2(new oc.gp_Pnt(0, 0, -0.5), new oc.gp_Dir(0, 0, 1));
    const bore = new oc.BRepPrimAPI_MakeCylinder(axCut, O, H + 1.0).Shape();
    shape = cutShapes(shape, bore);
  }

  return new OccBody(s, shape, { R, H, O });
}

/**
 * Plant 3D 圆台/圆锥体 (CONE)
 */
export function CONE(s, R1 = 50.0, R2 = 25.0, H = 100.0, E = 0.0, kw = {}) {
  if (typeof R1 === 'object') { kw = R1; R1 = kw.R1; R2 = kw.R2; H = kw.H; E = kw.E; }
  let r1Val = Math.max(0.0, Number(R1 ?? 50.0));
  let r2Val = Math.max(0.0, Number(R2 ?? 25.0));
  const hVal = Math.max(1e-3, Number(H ?? 100.0));
  const eVal = Number(E ?? 0.0);

  if (r1Val < 1e-4 && r2Val < 1e-4) r1Val = 1e-3;

  const ax = new oc.gp_Ax2(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 0, 1));
  let shape = null;

  if (Math.abs(eVal) > 1e-4) {
    const axB = new oc.gp_Ax2(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 0, 1));
    const axT = new oc.gp_Ax2(new oc.gp_Pnt(eVal, 0, hVal), new oc.gp_Dir(0, 0, 1));
    const wb = new oc.BRepBuilderAPI_MakeWire(new oc.BRepBuilderAPI_MakeEdge(new oc.gp_Circ(axB, Math.max(0.05, r1Val))).Edge()).Wire();
    const wt = new oc.BRepBuilderAPI_MakeWire(new oc.BRepBuilderAPI_MakeEdge(new oc.gp_Circ(axT, Math.max(0.05, r2Val))).Edge()).Wire();
    const loft = new oc.BRepOffsetAPI_ThruSections(true, true);
    loft.AddWire(wb);
    loft.AddWire(wt);
    loft.Build();
    shape = loft.Shape();
  } else if (Math.abs(r1Val - r2Val) < 1e-4) {
    shape = new oc.BRepPrimAPI_MakeCylinder(ax, Math.max(r1Val, 1e-3), hVal).Shape();
  } else {
    shape = new oc.BRepPrimAPI_MakeCone(ax, r1Val, r2Val, hVal).Shape();
  }

  return new OccBody(s, shape, { R1: r1Val, R2: r2Val, H: hVal, E: eVal });
}

/**
 * Plant 3D 圆环体 (TORUS)
 */
export function TORUS(s, R1 = 100.0, R2 = 15.0, kw = {}) {
  if (typeof R1 === 'object') { kw = R1; R1 = kw.R1; R2 = kw.R2; }
  let r1Val = Math.max(1e-3, Number(R1 ?? 100.0));
  let r2Val = Math.max(1e-3, Number(R2 ?? 15.0));
  if (r1Val <= r2Val) r1Val = r2Val + 1e-3;

  const ax = new oc.gp_Ax2(new oc.gp_Pnt(0, 0, 0), new oc.gp_Dir(0, 0, 1));
  const shape = new oc.BRepPrimAPI_MakeTorus(ax, r1Val, r2Val).Shape();
  return new OccBody(s, shape, { R1: r1Val, R2: r2Val });
}

/**
 * Plant 3D 空间平滑空间圆弧弯头 (ARC3D / ARC3D2)
 */
export function ARC3D2(s, D = 25.0, D2 = 0.0, R = 100.0, A = 90.0, kw = {}) {
  if (typeof D === 'object') { kw = D; D = kw.D; D2 = kw.D2; R = kw.R; A = kw.A; }
  const r1 = Math.max(1e-3, Number(D ?? 25.0));
  const r2 = D2 && Number(D2) > 1e-4 ? Number(D2) : r1;
  const rMajor = Math.max(Math.max(r1, r2) + 1e-3, Number(R ?? 100.0));
  const angleDeg = Math.max(1.0, Math.min(180.0, Number(A ?? 90.0)));
  const rad = (angleDeg * Math.PI) / 180.0;

  let mX = 0, cx = 0, cy = 0;
  if (Math.abs(angleDeg - 180.0) < 1e-4) {
    mX = rMajor;
    cx = rMajor;
    cy = rMajor;
  } else {
    mX = rMajor * Math.tan(rad / 2.0);
    cx = mX;
    cy = rMajor;
  }

  const startAng = (-90.0 - angleDeg) * (Math.PI / 180.0);
  const vx = new oc.gp_Dir(Math.cos(startAng), Math.sin(startAng), 0.0);
  const ax = new oc.gp_Ax2(new oc.gp_Pnt(cx, cy, 0.0), new oc.gp_Dir(0.0, 0.0, 1.0), vx);

  let shape = null;
  if (Math.abs(r1 - r2) < 1e-4) {
    shape = new oc.BRepPrimAPI_MakeTorus(ax, rMajor, r1, rad).Shape();
  } else {
    const loft = new oc.BRepOffsetAPI_ThruSections(true, false);
    const steps = 16;
    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      const u = t * rad;
      const ru = r1 + t * (r2 - r1);
      const cu = Math.cos(u), su = Math.sin(u);
      const loc = ax.Location();
      const vz = ax.Direction();
      const vxDir = ax.XDirection();
      const vyX = vz.Y() * vxDir.Z() - vz.Z() * vxDir.Y();
      const vyY = vz.Z() * vxDir.X() - vz.X() * vxDir.Z();
      const vyZ = vz.X() * vxDir.Y() - vz.Y() * vxDir.X();

      const radialX = cu * vxDir.X() + su * vyX;
      const radialY = cu * vxDir.Y() + su * vyY;
      const radialZ = cu * vxDir.Z() + su * vyZ;
      const tangX = -su * vxDir.X() + cu * vyX;
      const tangY = -su * vxDir.Y() + cu * vyY;
      const tangZ = -su * vxDir.Z() + cu * vyZ;

      const cPt = new oc.gp_Pnt(
        loc.X() + rMajor * radialX,
        loc.Y() + rMajor * radialY,
        loc.Z() + rMajor * radialZ
      );
      const cAx = new oc.gp_Ax2(cPt, new oc.gp_Dir(tangX, tangY, tangZ), new oc.gp_Dir(radialX, radialY, radialZ));
      const w = new oc.BRepBuilderAPI_MakeWire(new oc.BRepBuilderAPI_MakeEdge(new oc.gp_Circ(cAx, Math.max(0.1, ru))).Edge()).Wire();
      loft.AddWire(w);
    }
    loft.Build();
    shape = loft.Shape();
  }

  return new OccBody(s, shape, { D: r1, D2: r2, R: rMajor, A: angleDeg });
}

export function ARC3D(s, D = 25.0, R = 100.0, A = 90.0, kw = {}) {
  return ARC3D2(s, D, D, R, A, kw);
}

/**
 * Plant 3D 完整球体 (SPHERE)
 */
export function SPHERE(s, R = 50.0, kw = {}) {
  if (typeof R === 'object') { kw = R; R = kw.R; }
  const rVal = Math.max(1e-3, Number(R ?? 50.0));
  const shape = new oc.BRepPrimAPI_MakeSphere(new oc.gp_Pnt(0, 0, 0), rVal).Shape();
  return new OccBody(s, shape, { R: rVal, H: 2.0 * rVal });
}

/**
 * Plant 3D 半球体 (HALFSPHERE)
 */
export function HALFSPHERE(s, R = 50.0, kw = {}) {
  if (typeof R === 'object') { kw = R; R = kw.R; }
  const rVal = Math.max(1e-3, Number(R ?? 50.0));
  const shape = new oc.BRepPrimAPI_MakeSphere(new oc.gp_Pnt(0, 0, 0), rVal, 0.0, Math.PI / 2.0).Shape();
  return new OccBody(s, shape, { R: rVal, H: rVal });
}

/**
 * Plant 3D 椭圆封头 (ELLIPSOIDHEAD)
 */
export function ELLIPSOIDHEAD(s, R = 50.0, H = null, kw = {}) {
  if (typeof R === 'object') { kw = R; R = kw.R; H = kw.H; }
  const rVal = Math.max(1e-3, Number(R ?? 50.0));
  const hReal = H !== null && Number(H) > 0 ? Number(H) : rVal * 0.5;

  const body = HALFSPHERE(s, rVal);
  const scaleZ = hReal / rVal;
  if (Math.abs(scaleZ - 1.0) > 1e-4) {
    body.scaleXYZ(1.0, 1.0, scaleZ);
  }
  body.params = { R: rVal, H: hReal };
  return body;
}

// ============================================================================
// 网格剖分与特征线框提取 (Three.js 渲染数据转换)
// ============================================================================

/**
 * 将 TopoDS_Shape 离散化剖分为用于 WebGL 渲染的顶点与面片数组
 * @param {TopoDS_Shape} shape OpenCASCADE 拓扑实体
 * @param {number} [deflection=0.5] 线性弦高离散公差 (mm)
 * @returns {{ positions: Float32Array, indices: Uint32Array, bbox: object, faceCount: number, triangleCount: number }}
 */
export function meshShape(shape, deflection = 0.5) {
  if (!shape || shape.IsNull()) {
    return null;
  }

  new oc.BRepMesh_IncrementalMesh(shape, deflection, false, 0.5, false);

  const vertices = [];
  const indices = [];

  let faceCount = 0;
  let triangleCount = 0;

  let minX = Infinity, minY = Infinity, minZ = Infinity;
  let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

  const exp = new oc.TopExp_Explorer(shape, oc.TopAbs_ShapeEnum.TopAbs_FACE, oc.TopAbs_ShapeEnum.TopAbs_SHAPE);
  while (exp.More()) {
    const face = oc.TopoDS.Face(exp.Current());
    const loc = new oc.TopLoc_Location();
    const tri = oc.BRep_Tool.Triangulation(face, loc, 0);

    if (tri) {
      faceCount++;
      const nbNodes = tri.NbNodes();
      const nbTriangles = tri.NbTriangles();
      const isReversed = face.Orientation() === 'TopAbs_REVERSED';
      const trsf = loc.Transformation();
      const hasTrsf = !loc.IsIdentity();

      const baseVertexIndex = vertices.length / 3;

      for (let i = 1; i <= nbNodes; i++) {
        let p = tri.Node(i);
        if (hasTrsf) {
          p = p.Transformed(trsf);
        }
        const px = p.X();
        const py = p.Y();
        const pz = p.Z();

        vertices.push(px, py, pz);

        if (px < minX) minX = px;
        if (py < minY) minY = py;
        if (pz < minZ) minZ = pz;
        if (px > maxX) maxX = px;
        if (py > maxY) maxY = py;
        if (pz > maxZ) maxZ = pz;
      }

      for (let i = 1; i <= nbTriangles; i++) {
        const t = tri.Triangle(i);
        const idx1 = baseVertexIndex + (t.Value(1) - 1);
        const idx2 = baseVertexIndex + (t.Value(2) - 1);
        const idx3 = baseVertexIndex + (t.Value(3) - 1);

        if (isReversed) {
          indices.push(idx1, idx3, idx2);
        } else {
          indices.push(idx1, idx2, idx3);
        }
        triangleCount++;
      }
    }
    exp.Next();
  }

  if (vertices.length === 0) {
    return null;
  }

  const bbox = {
    min: [minX, minY, minZ],
    max: [maxX, maxY, maxZ],
    size: [maxX - minX, maxY - minY, maxZ - minZ],
    center: [(minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2]
  };

  return {
    positions: new Float32Array(vertices),
    indices: new Uint32Array(indices),
    bbox,
    faceCount,
    triangleCount
  };
}
