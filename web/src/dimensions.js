// -*- coding: utf-8 -*-
/**
 * AutoCAD Plant 3D 轴测尺寸标注生成与渲染管线
 * 严格对齐 plant3d_occ/catalog/preview.py 与 plant3d_occ/core/session.py 原生标准：
 * - 提取真实脚本注册的 setLinearDimension 标注点与端口 Pipe Diameter (D)
 * - 自动计算外伸引导方向 (ext_dir)、阶梯分层避让 (tier_step) 与尺寸界线过冲量 (overshoot)
 * - 45° CAD 工程斜短划线 (Architectural Tick) 消除箭头歧义
 * - 纯白描边带光晕的高清参数字母标签 Sprite，防止与实体模型重叠
 * - 原点端口小方框标记 □ (Port 0 Marker)
 */

import * as THREE from 'three';

/**
 * 清理参数名标签，剔除后缀与辅助说明
 * @param {string} value 
 * @returns {string}
 */
export function cleanDimensionLabel(value) {
  let text = String(value || '').trim();
  if (!text || text.startsWith('#')) return '';
  for (const sep of ['=', ':', '：']) {
    if (text.includes(sep)) {
      text = text.split(sep)[0].trim();
    }
  }
  text = text.replace(/\s*[（(]\s*[-+]?\d+(?:\.\d+)?\s*(?:mm)?\s*[）)]\s*$/i, '').trim();
  if (text.startsWith('总长') || text.startsWith('总高') || text.startsWith('总宽')) {
    return '';
  }
  return text;
}

/**
 * 计算与测量方向 (p2 - p1) 垂直且朝构件包围盒外侧的引导线引出方向
 */
export function chooseDefaultExtDir(p1, p2, bmin, bmax) {
  const vec = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
  const vlen = Math.hypot(vec[0], vec[1], vec[2]);
  if (vlen < 1e-6) return [0, -1, 0];

  const m_dir = [vec[0] / vlen, vec[1] / vlen, vec[2] / vlen];
  const span = [
    Math.max(bmax[0] - bmin[0], 1.0),
    Math.max(bmax[1] - bmin[1], 1.0),
    Math.max(bmax[2] - bmin[2], 1.0)
  ];
  const center = [
    0.5 * (bmin[0] + bmax[0]),
    0.5 * (bmin[1] + bmax[1]),
    0.5 * (bmin[2] + bmax[2])
  ];
  const mid = [
    0.5 * (p1[0] + p2[0]),
    0.5 * (p1[1] + p2[1]),
    0.5 * (p1[2] + p2[2])
  ];

  // Case 1: 沿 Z 轴的垂直测量
  if (Math.abs(m_dir[2]) > 0.75) {
    if (span[0] > 1.45 * span[1]) {
      return mid[0] <= center[0] + 0.15 * span[0] ? [-1, 0, 0] : [1, 0, 0];
    }
    return mid[1] <= center[1] + 0.15 * span[1] ? [0, -1, 0] : [0, 1, 0];
  }

  // Case 2: 沿 X 轴的测量
  if (Math.abs(m_dir[0]) > 0.75) {
    if (mid[2] >= center[2] + 0.1 * span[2]) {
      return [0, 0, 1];
    }
    if (mid[2] <= bmin[2] + 0.25 * span[2]) {
      return span[2] > span[0] * 0.4 ? [0, -1, 0] : [0, 0, -1];
    }
    return [0, -1, 0];
  }

  // Case 3: 沿 Y 轴的测量
  if (Math.abs(m_dir[1]) > 0.75) {
    if (mid[2] >= center[2] + 0.15 * span[2]) {
      return [0, 0, 1];
    }
    return mid[0] >= center[0] ? [1, 0, 0] : [-1, 0, 0];
  }

  // 默认正交投影
  let cand = [
    m_dir[1] * 0 - m_dir[2] * 1,
    m_dir[2] * 0 - m_dir[0] * 0,
    m_dir[0] * 1 - m_dir[1] * 0
  ];
  let clen = Math.hypot(cand[0], cand[1], cand[2]);
  if (clen < 1e-3) {
    cand = [0, 1, 0];
  } else {
    cand = [cand[0] / clen, cand[1] / clen, cand[2] / clen];
  }
  return cand;
}

/**
 * 提取并构建三维轴测标注原始规格 (严格对照 plant3d_occ build_3d_dimension_specs)
 */
export function build3dDimensionSpecs(session, paramsMeta = [], callValues = {}, bounds, maxDims = 40) {
  const bmin = bounds ? [bounds.min.x, bounds.min.y, bounds.min.z] : [-50, -50, -50];
  const bmax = bounds ? [bounds.max.x, bounds.max.y, bounds.max.z] : [50, 50, 50];
  const span = [
    Math.max(bmax[0] - bmin[0], 1.0),
    Math.max(bmax[1] - bmin[1], 1.0),
    Math.max(bmax[2] - bmin[2], 1.0)
  ];

  const dims = [];
  const usedLabels = new Set();

  // 1. 优先读取脚本显式注册的 setLinearDimension
  if (session && session.dimensions && session.dimensions.length > 0) {
    for (const g of session.dimensions) {
      const name = cleanDimensionLabel(g.name);
      if (!name || usedLabels.has(name)) continue;
      const p1 = g.p1;
      const p2 = g.p2;
      const dist = Math.hypot(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]);
      if (dist < 0.5) continue;

      const item = {
        label: name,
        p1: [...p1],
        p2: [...p2],
        kind: 'linear',
        style: g.style || 'linear'
      };
      if (g.ext_dir) item.ext_dir = [...g.ext_dir];
      dims.push(item);
      usedLabels.add(name);
    }
  }

  // 收集参数名列表
  const paramNames = [];
  for (const p of paramsMeta) {
    if (p && p.name) paramNames.push(p.name);
  }
  for (const k of Object.keys(callValues)) {
    if (!paramNames.includes(k)) paramNames.push(k);
  }
  const filteredParams = paramNames.filter(p => p !== 'ID' && p !== 's' && p !== 'kw');

  // 2. 若脚本未显式标注外径 D，自动在端口 0 (Port 0) 测量管径 D
  for (const dName of ['D', 'D_VESSEL', 'D_CASE']) {
    if (filteredParams.includes(dName) && !usedLabels.has(dName) && dims.length < maxDims) {
      let dVal = Number(callValues[dName]);
      if (isNaN(dVal) || dVal <= 1.0) {
        dVal = Math.min(span[0], span[1]) * 0.45;
      }
      const rVal = dVal * 0.5;
      let p0 = [0, 0, 0];
      let d0 = [0, 1, 0];
      if (session && session.ports && session.ports.length > 0) {
        p0 = [...session.ports[0].point];
        if (session.ports[0].direction) d0 = [...session.ports[0].direction];
      }

      if (span[2] >= dVal * 0.9 && bmin[2] <= p0[2] - rVal * 0.5 && bmax[2] >= p0[2] + rVal * 0.5) {
        dims.push({
          label: dName,
          p1: [p0[0], p0[1], p0[2] - rVal],
          p2: [p0[0], p0[1], p0[2] + rVal],
          kind: 'diameter_z',
          style: 'linear'
        });
      } else {
        const axis = Math.abs(d0[1]) > 0.6 ? [1, 0, 0] : [0, 1, 0];
        dims.push({
          label: dName,
          p1: [p0[0] - axis[0] * rVal, p0[1] - axis[1] * rVal, p0[2] - axis[2] * rVal],
          p2: [p0[0] + axis[0] * rVal, p0[1] + axis[1] * rVal, p0[2] + axis[2] * rVal],
          kind: 'diameter_xy',
          style: 'linear'
        });
      }
      usedLabels.add(dName);
      break;
    }
  }

  return dims.slice(0, maxDims);
}

/**
 * 求解三维尺寸标注几何 (引出线、阶梯避让分层、端点短划线)
 */
export function resolve3dDimensionGeometry(bounds, rawDims) {
  if (!rawDims || rawDims.length === 0) return { resolved: [], framingPoints: [] };

  const bmin = bounds ? [bounds.min.x, bounds.min.y, bounds.min.z] : [-50, -50, -50];
  const bmax = bounds ? [bounds.max.x, bounds.max.y, bounds.max.z] : [50, 50, 50];
  const span = [
    Math.max(bmax[0] - bmin[0], 10.0),
    Math.max(bmax[1] - bmin[1], 10.0),
    Math.max(bmax[2] - bmin[2], 10.0)
  ];
  const charSize = Math.max(span[0], span[1], span[2]);

  const work = [];
  for (let idx = 0; idx < rawDims.length; idx++) {
    const d = rawDims[idx];
    let p1 = [...d.p1];
    let p2 = [...d.p2];
    const vec = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
    const segLen = Math.hypot(vec[0], vec[1], vec[2]);
    if (segLen < 0.5) continue;

    let m_dir = [vec[0] / segLen, vec[1] / segLen, vec[2] / segLen];
    if (m_dir[2] < -0.5 || (Math.abs(m_dir[2]) <= 0.5 && m_dir[0] < -0.5) || (Math.abs(m_dir[2]) <= 0.5 && Math.abs(m_dir[0]) <= 0.5 && m_dir[1] < -0.5)) {
      const tmp = p1; p1 = p2; p2 = tmp;
      m_dir = [-m_dir[0], -m_dir[1], -m_dir[2]];
    }

    let ext_dir;
    if (d.ext_dir) {
      const dot = d.ext_dir[0] * m_dir[0] + d.ext_dir[1] * m_dir[1] + d.ext_dir[2] * m_dir[2];
      const proj = [
        d.ext_dir[0] - dot * m_dir[0],
        d.ext_dir[1] - dot * m_dir[1],
        d.ext_dir[2] - dot * m_dir[2]
      ];
      const nExt = Math.hypot(proj[0], proj[1], proj[2]);
      ext_dir = nExt > 1e-6 ? [proj[0] / nExt, proj[1] / nExt, proj[2] / nExt] : chooseDefaultExtDir(p1, p2, bmin, bmax);
    } else {
      ext_dir = chooseDefaultExtDir(p1, p2, bmin, bmax);
    }

    const t1 = p1[0] * m_dir[0] + p1[1] * m_dir[1] + p1[2] * m_dir[2];
    const t2 = p2[0] * m_dir[0] + p2[1] * m_dir[1] + p2[2] * m_dir[2];
    const tMin = Math.min(t1, t2);
    const tMax = Math.max(t1, t2);

    const gKey = [
      Math.round(m_dir[0] * 4), Math.round(m_dir[1] * 4), Math.round(m_dir[2] * 4),
      Math.round(ext_dir[0] * 4), Math.round(ext_dir[1] * 4), Math.round(ext_dir[2] * 4)
    ].join('_');

    work.push({
      origIdx: idx,
      label: d.label,
      p1,
      p2,
      m_dir,
      ext_dir,
      tMin,
      tMax,
      span: tMax - tMin,
      gKey,
      style: d.style || 'linear'
    });
  }

  // 分组平行尺寸
  const groups = {};
  for (const item of work) {
    if (!groups[item.gKey]) groups[item.gKey] = [];
    groups[item.gKey].push(item);
  }

  const baseClear = Math.max(18.0, 0.135 * charSize);
  const tierStep = Math.max(24.0, 0.155 * charSize);

  const resolved = [];
  const framingPoints = [];

  for (const gItems of Object.values(groups)) {
    const gSorted = [...gItems].sort((a, b) => a.span - b.span || a.tMin - b.tMin);
    const tiers = [];

    for (const item of gSorted) {
      let placed = false;
      for (const tierList of tiers) {
        let overlaps = false;
        for (const existing of tierList) {
          const overlap = Math.min(item.tMax, existing.tMax) - Math.max(item.tMin, existing.tMin);
          if (overlap > 1.5) {
            overlaps = true;
            break;
          }
        }
        if (!overlaps) {
          tierList.push(item);
          placed = true;
          break;
        }
      }
      if (!placed) {
        tiers.push([item]);
      }
    }

    const m_dir = gSorted[0].m_dir;
    const ext_dir = gSorted[0].ext_dir;
    let prevTargetProj = -1e18;

    for (let tierIdx = 0; tierIdx < tiers.length; tierIdx++) {
      const tierList = tiers[tierIdx];
      let anchorExtMax = -1e18;
      for (const x of tierList) {
        const d1 = x.p1[0] * ext_dir[0] + x.p1[1] * ext_dir[1] + x.p1[2] * ext_dir[2];
        const d2 = x.p2[0] * ext_dir[0] + x.p2[1] * ext_dir[1] + x.p2[2] * ext_dir[2];
        anchorExtMax = Math.max(anchorExtMax, d1, d2);
      }

      let targetProj;
      if (tierList.every(x => x.style === 'leader_ext')) {
        targetProj = anchorExtMax + Math.max(18.0, 0.14 * charSize);
      } else {
        const baseRef = anchorExtMax;
        targetProj = Math.max(baseRef + baseClear + tierIdx * tierStep, prevTargetProj + tierStep);
        prevTargetProj = targetProj;
      }

      for (const x of tierList) {
        const p1 = x.p1;
        const p2 = x.p2;
        const proj1 = p1[0] * ext_dir[0] + p1[1] * ext_dir[1] + p1[2] * ext_dir[2];
        const proj2 = p2[0] * ext_dir[0] + p2[1] * ext_dir[1] + p2[2] * ext_dir[2];

        const d1 = [
          p1[0] + ext_dir[0] * (targetProj - proj1),
          p1[1] + ext_dir[1] * (targetProj - proj1),
          p1[2] + ext_dir[2] * (targetProj - proj1)
        ];
        const d2 = [
          p2[0] + ext_dir[0] * (targetProj - proj2),
          p2[1] + ext_dir[1] * (targetProj - proj2),
          p2[2] + ext_dir[2] * (targetProj - proj2)
        ];

        const overshoot = Math.max(8.0, 0.045 * charSize);
        const w1_end = [
          d1[0] + ext_dir[0] * overshoot,
          d1[1] + ext_dir[1] * overshoot,
          d1[2] + ext_dir[2] * overshoot
        ];
        const w2_end = [
          d2[0] + ext_dir[0] * overshoot,
          d2[1] + ext_dir[1] * overshoot,
          d2[2] + ext_dir[2] * overshoot
        ];

        const resItem = {
          ...x,
          d1,
          d2,
          w1_end,
          w2_end,
          tierIdx
        };
        resolved.push(resItem);

        framingPoints.push(p1, p2, d1, d2, w1_end, w2_end);
      }
    }
  }

  resolved.sort((a, b) => a.origIdx - b.origIdx);
  return { resolved, framingPoints };
}

/**
 * 绘制高清晰度参数字母 Sprite 纹理 (带白色防遮挡外发光描边)
 */
function createTextSprite(text, fontSize = 28) {
  const canvas = document.createElement('canvas');
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = `bold ${fontSize}px "Roboto", "Noto Sans SC", sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  // 4px 白色全向描边光晕 (Halo) 确保无论背景是模型网格还是纯白都能清晰可读
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.96)';
  ctx.lineWidth = 5;
  ctx.lineJoin = 'round';
  ctx.strokeText(text, cx, cy);

  // 核心深色工程字体
  ctx.fillStyle = '#0f172a';
  ctx.fillText(text, cx, cy);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;

  const material = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthTest: false,
    depthWrite: false
  });

  const sprite = new THREE.Sprite(material);
  sprite.renderOrder = 999;
  return sprite;
}

/**
 * 创建 Three.js 三维尺寸标注组合对象 (CAD 45° 斜短划线 + 轴测引出线 + 字母标签)
 */
export function create3dDimensionsObject(session, paramsMeta, callValues, bounds) {
  const rawDims = build3dDimensionSpecs(session, paramsMeta, callValues, bounds);
  const { resolved, framingPoints } = resolve3dDimensionGeometry(bounds, rawDims);

  const group = new THREE.Group();
  group.name = 'CAD_DIMENSIONS_GROUP';

  if (!resolved || resolved.length === 0) {
    return { dimensionGroup: group, framingPoints: [] };
  }

  const bmin = bounds ? [bounds.min.x, bounds.min.y, bounds.min.z] : [-50, -50, -50];
  const bmax = bounds ? [bounds.max.x, bounds.max.y, bounds.max.z] : [50, 50, 50];
  const charSize = Math.max(bmax[0] - bmin[0], bmax[1] - bmin[1], bmax[2] - bmin[2], 10.0);
  const tickLen = Math.max(10.0, 0.055 * charSize);

  // 1. 统一构建所有线段缓冲区 (尺寸线 + 见证引出线 + 45° 斜短划线)
  const linePositions = [];

  for (const d of resolved) {
    const p1 = d.p1;
    const p2 = d.p2;
    const d1 = d.d1;
    const d2 = d.d2;
    const w1 = d.w1_end;
    const w2 = d.w2_end;
    const m_dir = d.m_dir;
    const ext_dir = d.ext_dir;

    // 见证引出线 1 (p1 -> w1)
    linePositions.push(p1[0], p1[1], p1[2], w1[0], w1[1], w1[2]);
    // 见证引出线 2 (p2 -> w2)
    linePositions.push(p2[0], p2[1], p2[2], w2[0], w2[1], w2[2]);
    // 尺寸线 (d1 -> d2)
    linePositions.push(d1[0], d1[1], d1[2], d2[0], d2[1], d2[2]);

    // 45° CAD 工程斜短划线 (Architectural Tick)
    // 矢量为沿 (m_dir + ext_dir) 方向的 45 度短划线
    const tv = [
      m_dir[0] + ext_dir[0],
      m_dir[1] + ext_dir[1],
      m_dir[2] + ext_dir[2]
    ];
    const tvLen = Math.hypot(tv[0], tv[1], tv[2]);
    const normTv = tvLen > 1e-4 ? [tv[0] / tvLen, tv[1] / tvLen, tv[2] / tvLen] : [1, 0, 0];
    const halfTick = tickLen * 0.5;

    // 端点 1 短划线
    linePositions.push(
      d1[0] - normTv[0] * halfTick, d1[1] - normTv[1] * halfTick, d1[2] - normTv[2] * halfTick,
      d1[0] + normTv[0] * halfTick, d1[1] + normTv[1] * halfTick, d1[2] + normTv[2] * halfTick
    );
    // 端点 2 短划线
    linePositions.push(
      d2[0] - normTv[0] * halfTick, d2[1] - normTv[1] * halfTick, d2[2] - normTv[2] * halfTick,
      d2[0] + normTv[0] * halfTick, d2[1] + normTv[1] * halfTick, d2[2] + normTv[2] * halfTick
    );

    // 2. 放置参数文字 Sprite (在尺寸线中点稍外侧)
    const mid = [
      0.5 * (d1[0] + d2[0]) + ext_dir[0] * (0.04 * charSize),
      0.5 * (d1[1] + d2[1]) + ext_dir[1] * (0.04 * charSize),
      0.5 * (d1[2] + d2[2]) + ext_dir[2] * (0.04 * charSize)
    ];

    const sprite = createTextSprite(d.label);
    const spriteSize = Math.max(16.0, 0.12 * charSize);
    sprite.scale.set(spriteSize, spriteSize, 1);
    sprite.position.set(mid[0], mid[1], mid[2]);
    group.add(sprite);
  }

  // 构建 LineSegments
  const geom = new THREE.BufferGeometry();
  geom.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
  const mat = new THREE.LineBasicMaterial({
    color: 0x1e293b,
    linewidth: 1.5,
    depthTest: false,
    depthWrite: false
  });
  const lineSegments = new THREE.LineSegments(geom, mat);
  lineSegments.renderOrder = 998;
  group.add(lineSegments);

  // 3. 绘制端口 0 (Port 0) 小方框定位标记 (匹配 Plant 3D 官方出图习惯)
  if (session && session.ports && session.ports.length > 0) {
    const p0 = session.ports[0].point;
    const markerBox = new THREE.BoxGeometry(tickLen * 0.45, tickLen * 0.45, tickLen * 0.45);
    const markerEdges = new THREE.EdgesGeometry(markerBox);
    const markerMat = new THREE.LineBasicMaterial({ color: 0x0f172a, depthTest: false });
    const markerLine = new THREE.LineSegments(markerEdges, markerMat);
    markerLine.position.set(p0[0], p0[1], p0[2]);
    markerLine.renderOrder = 999;
    group.add(markerLine);
  }

  return { dimensionGroup: group, framingPoints };
}
