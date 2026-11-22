# -*- coding: utf-8 -*-
"""AutoCAD Plant 3D Shaded + Edges Isometric Preview & 3D CAD Dimension Renderer.

Reproduces the official AutoCAD Plant 3D Catalog / Spec Editor isometric preview style:
- Pure white background (`#FFFFFF`) with shaded solid faces and crisp black feature edges.
- Isometric square pipe centerline origin marker (`□`) at `(0, 0, 0)`.
- Authentic 3D isometric black CAD dimensions:
  * 3D isometric extension (witness) lines projected along true CAD axes (`±X`, `±Y`, `±Z`)
    with standard gap and overshoot past the dimension line.
  * Automatic collinear chain grouping (e.g., `H` + `SH` + `OH`, or `b1` + `b2`) and
    baseline tier stacking (e.g., `D` -> `K` -> `H`) so dimension lines never collide.
  * Hollow acute CAD arrowheads (`ClosedBlank` style: white fill with black outline),
    automatically switching between internal arrows (wide spans) and external inward-pointing
    arrows with leader tails (narrow spans like `SH`, `OH`, `W`, `L`, `HD3`).
  * Isometric-aligned rotated bold black parameter labels (`D`, `K`, `H`, `W`, `L`, `HD3`, `SH`, `OH`, etc.)
    with enlarged, easy-to-read typography on both 640px and 200px catalog previews.
"""

from __future__ import annotations

import math
import os
import re
import tempfile
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    win_fonts = os.path.join(windir, "Fonts")
    candidates = [
        # 优先覆盖中文参数名，避免脚本里的中文标签渲染成方框。
        # 微软雅黑同时覆盖中英文，整张图观感也统一。
        os.path.join(win_fonts, "msyhbd.ttc" if bold else "msyh.ttc"),
        os.path.join(win_fonts, "msyhbd.ttf" if bold else "msyh.ttf"),
        os.path.join(win_fonts, "simhei.ttf"),
        os.path.join(win_fonts, "simsun.ttc"),
        os.path.join(win_fonts, "arialbd.ttf" if bold else "arial.ttf"),
        os.path.join(win_fonts, "calibrib.ttf" if bold else "calibri.ttf"),
        os.path.join(win_fonts, "segoeuib.ttf" if bold else "segoeui.ttf"),
        os.path.join(win_fonts, "tahomabd.ttf" if bold else "tahoma.ttf"),
        os.path.join(win_fonts, "msyhbd.ttc" if bold else "msyh.ttc"),
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _make_occ_color(r: float, g: float, b: float):
    from OCC.Core.Quantity import Quantity_Color
    try:
        from OCC.Core.Quantity import Quantity_TOC_RGB
        return Quantity_Color(float(r), float(g), float(b), Quantity_TOC_RGB)
    except (ImportError, TypeError):
        return Quantity_Color((float(r), float(g), float(b)))


def open_offscreen_display(style: str = "pyocc_shaded"):
    """Creates an offscreen 3D OCC viewer configured for PyOCC 3D Shaded + Edge + Dimension CAD preview."""
    from OCC.Display.OCCViewer import Viewer3d
    display = Viewer3d()
    display.Create()
    display.SetSize(800, 800)
    display.SetModeShaded()
    try:
        display.set_bg_gradient_color([255, 255, 255], [255, 255, 255])
    except Exception:
        pass
    try:
        from OCC.Core.Graphic3d import Graphic3d_TypeOfShadingModel_Phong
        display.View.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
    except Exception:
        pass
    try:
        if hasattr(display.View, "SetAntialiasingOn"):
            display.View.SetAntialiasingOn()
    except Exception:
        pass
    try:
        ctx = getattr(display, "Context", None)
        if ctx is not None and hasattr(ctx, "DefaultDrawer"):
            drawer = ctx.DefaultDrawer()
            if hasattr(drawer, "SetDeviationCoefficient"):
                drawer.SetDeviationCoefficient(0.0008)
            if hasattr(drawer, "SetDeviationAngle"):
                drawer.SetDeviationAngle(0.12)
            if hasattr(drawer, "SetFaceBoundaryDraw"):
                drawer.SetFaceBoundaryDraw(True)
            if hasattr(drawer, "FaceBoundaryAspect"):
                from OCC.Core.Quantity import Quantity_NOC_BLACK, Quantity_Color
                from OCC.Core.Aspect import Aspect_TOL_SOLID
                aspect = drawer.FaceBoundaryAspect()
                aspect.SetColor(Quantity_Color(Quantity_NOC_BLACK))
                aspect.SetWidth(1.0)
                aspect.SetTypeOfLine(Aspect_TOL_SOLID)
    except Exception:
        pass
    return display


def close_display(display):
    try:
        display.EraseAll()
    except Exception:
        pass


def _dump_view(display, path: str) -> None:
    if not display.View.Dump(path):
        raise RuntimeError("视口抓图失败")
    if not os.path.isfile(path) or os.path.getsize(path) < 100:
        raise RuntimeError("预览图为空")


def _square_around_part(image: Image.Image, pad: int = 26) -> Image.Image:
    """Crops the rendered image into a centered square around non-white pixels."""
    gray = image.convert("L")
    mask = gray.point(lambda pixel: 255 if pixel < 245 else 0)
    box = mask.getbbox()
    if not box:
        side = min(image.size)
        left = (image.width - side) // 2
        top = (image.height - side) // 2
        return image.crop((left, top, left + side, top + side))
    left, top, right, bottom = box
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width, right + pad)
    bottom = min(image.height, bottom + pad)
    side = max(right - left, bottom - top)
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
    half = side // 2
    left = max(0, center_x - half)
    top = max(0, center_y - half)
    right = min(image.width, left + side)
    bottom = min(image.height, top + side)
    left = max(0, right - side)
    top = max(0, bottom - side)
    return image.crop((left, top, right, bottom))


def _shapes_bounds(shapes) -> Tuple[np.ndarray, np.ndarray]:
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib

    box = Bnd_Box()
    for item in shapes:
        sh = item.shape if hasattr(item, "shape") else item
        if sh is not None and not sh.IsNull():
            brepbndlib.Add(sh, box)
    if box.IsVoid():
        return np.zeros(3), np.ones(3)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return np.array([xmin, ymin, zmin], dtype=np.float64), np.array([xmax, ymax, zmax], dtype=np.float64)


def _all_shape_verts(shapes) -> np.ndarray:
    v_list = []
    for item in shapes:
        sh = item.shape if hasattr(item, "shape") else item
        if sh is None or sh.IsNull():
            continue
        if hasattr(sh, "verts") and len(sh.verts) > 0:
            v_list.append(sh.verts)
        else:
            # Native C++ pythonocc-core TopoDS_Shape vertex extraction
            try:
                from OCC.Core.TopExp import TopExp_Explorer
                from OCC.Core.TopAbs import TopAbs_VERTEX
                from OCC.Core.BRep import BRep_Tool
                exp = TopExp_Explorer(sh, TopAbs_VERTEX)
                pts = []
                while exp.More():
                    vtx = exp.Current()
                    pnt = BRep_Tool.Pnt(vtx)
                    pts.append([pnt.X(), pnt.Y(), pnt.Z()])
                    exp.Next()
                if pts:
                    v_list.append(np.array(pts, dtype=np.float64))
            except Exception:
                pass
    bmin, bmax = _shapes_bounds(shapes)
    corners = np.array([
        [bmin[0], bmin[1], bmin[2]],
        [bmax[0], bmin[1], bmin[2]],
        [bmin[0], bmax[1], bmin[2]],
        [bmax[0], bmax[1], bmin[2]],
        [bmin[0], bmin[1], bmax[2]],
        [bmax[0], bmin[1], bmax[2]],
        [bmin[0], bmax[1], bmax[2]],
        [bmax[0], bmax[1], bmax[2]],
    ], dtype=np.float64)
    v_list.append(corners)
    return np.vstack(v_list)


def _project_3d_points(
    display,
    pts_arr: np.ndarray,
    width: int,
    height: int,
    margin: float = 0.12,
) -> np.ndarray:
    """Projects an `(N, 3)` array of 3D world points into `(N, 2)` 2D viewport pixel coordinates.
    Works seamlessly on both `occ_fallback.Viewer3d` and native C++ `OCC.Display.OCCViewer.Viewer3d`.
    """
    if hasattr(display, "project_points"):
        proj_2d, _ = display.project_points(pts_arr, width=width, height=height, margin=margin)
        return proj_2d
    view = getattr(display, "View", None)
    if view is not None and hasattr(view, "Convert"):
        out = np.zeros((len(pts_arr), 2), dtype=np.float64)
        for i, pt in enumerate(pts_arr):
            try:
                res = view.Convert(float(pt[0]), float(pt[1]), float(pt[2]))
                if isinstance(res, (tuple, list)) and len(res) >= 2:
                    out[i, 0] = float(res[0])
                    out[i, 1] = float(res[1])
            except Exception:
                pass
        return out
    return np.zeros((len(pts_arr), 2), dtype=np.float64)


def build_3d_dimension_specs(
    shapes,
    session=None,
    params_meta: Optional[Sequence[dict]] = None,
    call_values: Optional[dict] = None,
    max_dims: int = 40,
) -> List[dict]:
    """生成轴测尺寸 `{label, p1, p2, ext_dir, style}`。

    只使用脚本真实注册的线性尺寸和真实参数（如 D），不再合成
    “总长/总高/总宽”包围盒尺寸；标签只显示参数名，不附带具体数值。
    """
    bmin, bmax = _shapes_bounds(shapes)
    span = np.maximum(bmax - bmin, 1e-3)
    dims: List[dict] = []
    used_labels = set()

    # 1. Explicit grips from s.setLinearDimension(name, pt1, pt2, ext_dir=..., style=...)
    if session is not None and getattr(session, "grips", None):
        for g in session.grips:
            name = _clean_dimension_label(g.get("name"))
            if not name or name in used_labels:
                continue
            p1 = np.array(g["pt1"], dtype=np.float64)
            p2 = np.array(g["pt2"], dtype=np.float64)
            if np.linalg.norm(p2 - p1) < 0.5:
                continue
            item = {
                "label": name,
                "p1": p1,
                "p2": p2,
                "kind": "linear",
            }
            if g.get("ext_dir") is not None:
                item["ext_dir"] = np.array(g["ext_dir"], dtype=np.float64)
            if g.get("style") is not None:
                item["style"] = str(g["style"])
            dims.append(item)
            used_labels.add(name)

    param_names = []
    if params_meta:
        for pm in params_meta:
            if isinstance(pm, dict) and pm.get("name"):
                param_names.append(str(pm["name"]))
            elif isinstance(pm, (list, tuple)) and len(pm) > 0:
                param_names.append(str(pm[0]))
            elif isinstance(pm, str) and pm.strip():
                param_names.append(pm.strip())
    if call_values:
        for k in call_values.keys():
            if k not in param_names:
                param_names.append(str(k))
    param_names = [p for p in param_names if p not in ("ID", "s", "kw")]

    # 2. If the script didn't explicitly register D, add pipe diameter D at port 0
    for d_name in ("D", "D_VESSEL", "D_CASE"):
        if d_name in param_names and d_name not in used_labels and len(dims) < max_dims:
            d_val = None
            if call_values and d_name in call_values:
                try:
                    d_val = float(call_values[d_name])
                except Exception:
                    d_val = None
            if d_val is None or d_val <= 1.0:
                d_val = float(min(span[0], span[1]) * 0.45)
            r_val = d_val * 0.5
            p0 = np.zeros(3, dtype=np.float64)
            if session is not None and getattr(session, "ports", None):
                p0 = np.array(session.ports[0]["point"], dtype=np.float64)
            # Measure D vertically across Z at port 0 (matching Plant 3D clamp/support diagrams)
            if span[2] >= d_val * 0.9 and bmin[2] <= p0[2] - r_val * 0.5 and bmax[2] >= p0[2] + r_val * 0.5:
                dims.append({
                    "label": d_name,
                    "p1": p0 + np.array([0.0, 0.0, -r_val]),
                    "p2": p0 + np.array([0.0, 0.0, +r_val]),
                    "kind": "diameter_z",
                })
            else:
                d0 = np.array(session.ports[0]["dir"], dtype=np.float64) if (session and getattr(session, "ports", None)) else np.array([0.0, 1.0, 0.0])
                axis = np.array([1.0, 0.0, 0.0]) if abs(d0[1]) > 0.6 else np.array([0.0, 1.0, 0.0])
                dims.append({
                    "label": d_name,
                    "p1": p0 - axis * r_val,
                    "p2": p0 + axis * r_val,
                    "kind": "diameter_xy",
                })
            used_labels.add(d_name)
            break

    return dims[:max_dims]


def _clean_dimension_label(value) -> str:
    """只保留参数名：移除“=数值”/“:数值”后缀和概括性包络标签。"""
    text = str(value or "").strip()
    if not text or text.startswith("#"):
        return ""
    for separator in ("=", ":", "："):
        if separator in text:
            text = text.split(separator, 1)[0].strip()
    text = re.sub(
        r"\s*[（(]\s*[-+]?\d+(?:\.\d+)?\s*(?:mm)?\s*[）)]\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    if text.startswith(("总长", "总高", "总宽")):
        return ""
    return text


def _choose_default_ext_dir(
    p1: np.ndarray,
    p2: np.ndarray,
    bmin: np.ndarray,
    bmax: np.ndarray,
) -> np.ndarray:
    """Chooses an authentic 3D isometric extension direction perpendicular to (p2 - p1)."""
    vec = p2 - p1
    vlen = float(np.linalg.norm(vec))
    if vlen < 1e-6:
        return np.array([0.0, -1.0, 0.0])
    m_dir = vec / vlen
    span = np.maximum(bmax - bmin, 1.0)
    center = 0.5 * (bmin + bmax)
    mid = 0.5 * (p1 + p2)

    # Case 1: Vertical measurement (along Z)
    if abs(m_dir[2]) > 0.75:
        if span[0] > 1.45 * span[1]:
            if mid[0] <= center[0] + 0.15 * span[0]:
                return np.array([-1.0, 0.0, 0.0])
            return np.array([1.0, 0.0, 0.0])
        if mid[1] <= center[1] + 0.15 * span[1]:
            return np.array([0.0, -1.0, 0.0])
        return np.array([0.0, 1.0, 0.0])

    # Case 2: Measurement along X
    if abs(m_dir[0]) > 0.75:
        if mid[2] >= center[2] + 0.1 * span[2]:
            return np.array([0.0, 0.0, 1.0])
        if mid[2] <= bmin[2] + 0.25 * span[2]:
            return np.array([0.0, -1.0, 0.0]) if span[2] > span[0] * 0.4 else np.array([0.0, 0.0, -1.0])
        return np.array([0.0, -1.0, 0.0])

    # Case 3: Measurement along Y
    if abs(m_dir[1]) > 0.75:
        if mid[2] >= center[2] + 0.15 * span[2]:
            return np.array([0.0, 0.0, 1.0])
        if mid[0] >= center[0]:
            return np.array([1.0, 0.0, 0.0])
        return np.array([-1.0, 0.0, 0.0])

    cand = np.cross(m_dir, np.array([0.0, 1.0, 0.0]))
    if np.linalg.norm(cand) < 1e-3:
        cand = np.cross(m_dir, np.array([0.0, 0.0, 1.0]))
    return cand / max(np.linalg.norm(cand), 1e-6)


def resolve_3d_dimension_geometry(
    shapes,
    dims: Sequence[dict],
) -> Tuple[List[dict], np.ndarray]:
    """Computes exact 3D witness lines `(p1 -> d1, p2 -> d2)` with automatic collinear chain
    grouping (e.g. `H` + `SH` + `OH`, or `b1` + `b2`) and baseline tier stacking (`D` -> `K` -> `H`).

    Returns `(resolved_dims, extra_framing_pts_3d)`.
    """
    if not dims:
        return [], np.zeros((0, 3), dtype=np.float64)

    verts = _all_shape_verts(shapes)
    bmin, bmax = _shapes_bounds(shapes)
    span = np.maximum(bmax - bmin, 10.0)
    char_size = float(np.max(span))

    work = []
    for idx, d in enumerate(dims):
        p1 = np.array(d["p1"], dtype=np.float64)
        p2 = np.array(d["p2"], dtype=np.float64)
        vec = p2 - p1
        seg_len = float(np.linalg.norm(vec))
        if seg_len < 0.5:
            continue
        m_dir = vec / seg_len
        if m_dir[2] < -0.5 or (abs(m_dir[2]) <= 0.5 and m_dir[0] < -0.5) or (abs(m_dir[2]) <= 0.5 and abs(m_dir[0]) <= 0.5 and m_dir[1] < -0.5):
            p1, p2 = p2, p1
            m_dir = -m_dir

        if "ext_dir" in d and d["ext_dir"] is not None:
            ext_dir = np.array(d["ext_dir"], dtype=np.float64)
            ext_dir = ext_dir - np.dot(ext_dir, m_dir) * m_dir
            n_ext = np.linalg.norm(ext_dir)
            ext_dir = ext_dir / n_ext if n_ext > 1e-6 else _choose_default_ext_dir(p1, p2, bmin, bmax)
        else:
            ext_dir = _choose_default_ext_dir(p1, p2, bmin, bmax)

        t1 = float(np.dot(p1, m_dir))
        t2 = float(np.dot(p2, m_dir))
        t_min, t_max = min(t1, t2), max(t1, t2)

        g_key = (
            int(round(m_dir[0] * 4)), int(round(m_dir[1] * 4)), int(round(m_dir[2] * 4)),
            int(round(ext_dir[0] * 4)), int(round(ext_dir[1] * 4)), int(round(ext_dir[2] * 4)),
        )
        work.append({
            "orig_idx": idx,
            "label": str(d["label"]),
            "p1": p1,
            "p2": p2,
            "m_dir": m_dir,
            "ext_dir": ext_dir,
            "t_min": t_min,
            "t_max": t_max,
            "span": t_max - t_min,
            "g_key": g_key,
            "style": d.get("style", "linear"),
        })

    groups: Dict[tuple, List[dict]] = {}
    for item in work:
        groups.setdefault(item["g_key"], []).append(item)

    base_clear = max(18.0, 0.135 * char_size)
    tier_step = max(24.0, 0.155 * char_size)

    resolved: List[dict] = []
    framing_pts: List[np.ndarray] = []

    for g_items in groups.values():
        g_sorted = sorted(g_items, key=lambda x: (x["span"], x["t_min"]))
        tiers: List[List[dict]] = []

        for item in g_sorted:
            placed_in_tier = False
            for tier_list in tiers:
                overlaps = False
                for existing in tier_list:
                    overlap_len = min(item["t_max"], existing["t_max"]) - max(item["t_min"], existing["t_min"])
                    if overlap_len > 1.5:
                        overlaps = True
                        break
                if not overlaps:
                    tier_list.append(item)
                    placed_in_tier = True
                    break
            if not placed_in_tier:
                tiers.append([item])

        if len(tiers) >= 2:
            outer_tier = tiers[-1]
            changed = True
            while changed:
                changed = False
                for prev_tier in tiers[:-1]:
                    for cand in sorted(list(prev_tier), key=lambda c: c["t_min"]):
                        if all(min(cand["t_max"], x["t_max"]) - max(cand["t_min"], x["t_min"]) <= 1.5 for x in outer_tier):
                            adj_tol = max(25.0, 0.04 * char_size)
                            if any(abs(cand["t_min"] - x["t_max"]) <= adj_tol or abs(cand["t_max"] - x["t_min"]) <= adj_tol for x in outer_tier):
                                prev_tier.remove(cand)
                                outer_tier.append(cand)
                                changed = True
            tiers = [t for t in tiers if len(t) > 0]

        m_dir = g_sorted[0]["m_dir"]
        ext_dir = g_sorted[0]["ext_dir"]
        v_m = verts @ m_dir
        v_ext = verts @ ext_dir

        prev_target_proj = -1e18

        for tier_idx, tier_list in enumerate(tiers):
            t_low = min(x["t_min"] for x in tier_list) - 5.0
            t_high = max(x["t_max"] for x in tier_list) + 5.0
            mask = (v_m >= t_low) & (v_m <= t_high)
            part_ext_max = float(np.max(v_ext[mask])) if np.any(mask) else float(np.max(v_ext))
            anchor_ext_max = max(max(float(np.dot(x["p1"], ext_dir)), float(np.dot(x["p2"], ext_dir))) for x in tier_list)

            if all(x["style"] == "leader_ext" for x in tier_list):
                target_proj = anchor_ext_max + max(18.0, 0.14 * char_size)
            else:
                base_ref = max(anchor_ext_max, anchor_ext_max * 0.35 + part_ext_max * 0.65)
                if tier_idx == len(tiers) - 1 and len(tiers) > 1:
                    base_ref = max(base_ref, part_ext_max)
                target_proj = max(base_ref + base_clear + tier_idx * tier_step, prev_target_proj + tier_step)
                prev_target_proj = target_proj

            tier_sorted = sorted(tier_list, key=lambda item: item["t_min"])
            for s_idx, x in enumerate(tier_sorted):
                p1, p2 = x["p1"], x["p2"]
                eff_proj = target_proj
                if s_idx > 0 and x["span"] < 0.14 * char_size:
                    prev_x = tier_sorted[s_idx - 1]
                    if prev_x["span"] < 0.14 * char_size and abs(x["t_min"] - prev_x["t_max"]) < 5.0:
                        eff_proj = anchor_ext_max + 0.56 * (target_proj - anchor_ext_max)
                d1 = p1 + ext_dir * (eff_proj - float(np.dot(p1, ext_dir)))
                d2 = p2 + ext_dir * (eff_proj - float(np.dot(p2, ext_dir)))
                w1_end = p1 + ext_dir * (target_proj - float(np.dot(p1, ext_dir)))
                w2_end = p2 + ext_dir * (target_proj - float(np.dot(p2, ext_dir)))
                x_res = dict(x)
                x_res["d1"] = d1
                x_res["d2"] = d2
                x_res["w1_end"] = w1_end
                x_res["w2_end"] = w2_end
                x_res["tier_idx"] = tier_idx
                resolved.append(x_res)
                pad_ext = d1 + ext_dir * (0.11 * char_size)
                pad_ext2 = d2 + ext_dir * (0.11 * char_size)
                framing_pts.extend([p1, p2, d1, d2, pad_ext, pad_ext2])
                if x["style"] == "leader_ext":
                    framing_pts.append(d2 + ext_dir * (0.21 * char_size))

    resolved.sort(key=lambda x: x["orig_idx"])
    framing_arr = np.array(framing_pts, dtype=np.float64) if framing_pts else np.zeros((0, 3), dtype=np.float64)
    return resolved, framing_arr


def _draw_architectural_tick(
    draw: ImageDraw.ImageDraw,
    pt: Tuple[float, float],
    tick_len: float = 16.0,
    line_width: int = 2,
    color=(30, 41, 59),
) -> None:
    """绘制标准 CAD 工程 45° 尺寸界线斜短划线 (Architectural Tick)，彻底消除箭头反向歧义。"""
    x, y = pt
    half = tick_len * 0.5 * 0.7071
    p_start = (x - half, y + half)
    p_end = (x + half, y - half)
    draw.line([p_start, p_end], fill=color, width=line_width)


def _draw_hollow_cad_arrow(
    draw: ImageDraw.ImageDraw,
    tip: Tuple[float, float],
    direction: Tuple[float, float],
    length: float = 12.5,
    half_width: float = 3.2,
    line_width: int = 2,
) -> None:
    """兼容包装：直接绘制 45° 工程斜短划线。"""
    _draw_architectural_tick(draw, tip, tick_len=max(14.0, length), line_width=line_width)


def _draw_rotated_cad_text(
    base_img: Image.Image,
    text: str,
    center_xy: Tuple[float, float],
    angle_deg: float,
    font_size: int = 22,
) -> None:
    """Draws crisp anti-aliased bold black CAD text rotated to align with `angle_deg`."""
    while angle_deg <= -89.0:
        angle_deg += 180.0
    while angle_deg > 90.0:
        angle_deg -= 180.0

    # Render at 2x supersampling for crisp rotated glyph edges
    ss = 2
    font = _load_font(font_size * ss, bold=True)
    dummy = ImageDraw.Draw(base_img)
    bbox = dummy.textbbox((0, 0), text, font=font)
    tw = max(4, bbox[2] - bbox[0])
    th = max(4, bbox[3] - bbox[1])
    pad = 14 * ss
    cw, ch = tw + 2 * pad, th + 2 * pad

    txt_layer = Image.new("RGBA", (cw, ch), (255, 255, 255, 0))
    tdraw = ImageDraw.Draw(txt_layer)
    tx = pad - bbox[0]
    ty = pad - bbox[1]

    # Subtle 3px white halo under glyph strokes so larger letters remain crisp and never merge with witness lines
    for ox in (-3, -2, 0, 2, 3):
        for oy in (-3, -2, 0, 2, 3):
            if ox != 0 or oy != 0:
                tdraw.text((tx + ox, ty + oy), text, font=font, fill=(255, 255, 255, 235))
    # Draw bold stroke (with slight 1px reinforcement at 2x supersampling for extra clarity)
    tdraw.text((tx, ty), text, font=font, fill=(0, 0, 0, 255))
    tdraw.text((tx + 1, ty), text, font=font, fill=(0, 0, 0, 255))

    rot_layer = txt_layer.rotate(-angle_deg, resample=Image.BICUBIC, expand=True)
    rw, rh = max(2, rot_layer.width // ss), max(2, rot_layer.height // ss)
    rot_small = rot_layer.resize((rw, rh), resample=Image.LANCZOS)

    px = int(round(center_xy[0] - rw * 0.5))
    py = int(round(center_xy[1] - rh * 0.5))
    base_img.paste(rot_small, (px, py), rot_small)


def annotate_isometric_dimensions(
    image: Image.Image,
    display,
    resolved_dims: Sequence[dict],
    session=None,
    margin: float = 0.12,
    font_scale: float = 1.0,
) -> Image.Image:
    """Overlays authentic AutoCAD Plant 3D black isometric witness lines, hollow CAD arrowheads,
    origin square marker `□`, and rotated isometric parameter labels onto `image`.
    """
    out = image.copy().convert("RGB")
    W, H = out.size
    draw = ImageDraw.Draw(out)

    scale_ui = max(0.75, min(1.8, min(W, H) / 560.0))
    # Enlarged parameter letter size (24px+ bold on 640x640, even larger when font_scale > 1.0)
    font_size = max(17, int(round(20.5 * scale_ui * font_scale)))
    line_w = max(1, int(round(1.5 * scale_ui)))
    arrow_len = max(9.0, 12.8 * scale_ui)
    arrow_hw = max(2.4, 3.2 * scale_ui)
    gap_px = 2.8 * scale_ui
    overshoot_px = 7.5 * scale_ui

    # 1. Draw small square origin/pipe-center marker `□` at (0, 0, 0) (matching Plant 3D preview)
    origin_pt = np.array([[0.0, 0.0, 0.0]], dtype=np.float64)
    if session is not None and getattr(session, "ports", None):
        origin_pt = np.array([session.ports[0]["point"]], dtype=np.float64)
    orig_2d = _project_3d_points(display, origin_pt, width=W, height=H, margin=margin)
    ox, oy = float(orig_2d[0, 0]), float(orig_2d[0, 1])
    sq = max(2.8, 3.6 * scale_ui)
    if 0 <= ox < W and 0 <= oy < H:
        draw.rectangle([ox - sq, oy - sq, ox + sq, oy + sq], fill=(255, 255, 255), outline=(0, 0, 0), width=line_w)

    if not resolved_dims:
        return out

    # 2. Project all (p1, p2, d1, d2) 3D points into 2D screen coordinates
    pts_3d = []
    for d in resolved_dims:
        pts_3d.extend([d["p1"], d["p2"], d["d1"], d["d2"]])
    pts_arr = np.array(pts_3d, dtype=np.float64)
    proj_2d = _project_3d_points(display, pts_arr, width=W, height=H, margin=margin)

    for idx, d in enumerate(resolved_dims):
        p1 = proj_2d[4 * idx + 0]
        p2 = proj_2d[4 * idx + 1]
        d1 = proj_2d[4 * idx + 2]
        d2 = proj_2d[4 * idx + 3]

        dim_vec = d2 - d1
        seg_len = float(np.linalg.norm(dim_vec))
        if seg_len < 2.5:
            continue
        u_dir = dim_vec / seg_len
        dim_angle_deg = math.degrees(math.atan2(float(u_dir[1]), float(u_dir[0])))

        # Extension (witness) unit vector in 2D
        ew1 = d1 - p1
        ew2 = d2 - p2
        el1 = float(np.linalg.norm(ew1))
        el2 = float(np.linalg.norm(ew2))
        ext_u = (ew1 / el1) if el1 > 1e-3 else ((ew2 / el2) if el2 > 1e-3 else np.array([-u_dir[1], u_dir[0]]))
        ext_angle_deg = math.degrees(math.atan2(float(ext_u[1]), float(ext_u[0])))

        label = str(d["label"])
        style = d.get("style", "linear")
        lbl_font_size = font_size
        if len(label) > 4:
            lbl_font_size = max(13, int(round(font_size * (4.0 / len(label)) ** 0.45)))

        # Draw witness line 1 (p1 -> d1 + overshoot) and witness line 2 (p2 -> d2 + overshoot)
        for p_src, d_dst, elen in ((p1, d1, el1), (p2, d2, el2)):
            if elen > gap_px + 1.0:
                eu = (d_dst - p_src) / elen
                w_start = p_src + eu * gap_px
                extra_over = overshoot_px
                if style == "leader_ext" and d_dst is d2:
                    extra_over = overshoot_px + (len(label) * 13.0 * font_scale + 16.0) * scale_ui
                w_end = d_dst + eu * extra_over
                draw.line(
                    [(float(w_start[0]), float(w_start[1])), (float(w_end[0]), float(w_end[1]))],
                    fill=(0, 0, 0),
                    width=line_w,
                )

        # Draw dimension line, hollow CAD arrowheads, and rotated text label
        wide_threshold = 42.0 * scale_ui
        if seg_len >= wide_threshold and style != "leader_ext":
            line_start = d1 + u_dir * arrow_len
            line_end = d2 - u_dir * arrow_len
            draw.line(
                [(float(line_start[0]), float(line_start[1])), (float(line_end[0]), float(line_end[1]))],
                fill=(0, 0, 0),
                width=line_w,
            )
            _draw_hollow_cad_arrow(
                draw,
                (float(d1[0]), float(d1[1])),
                (-float(u_dir[0]), -float(u_dir[1])),
                length=arrow_len,
                half_width=arrow_hw,
                line_width=line_w,
            )
            _draw_hollow_cad_arrow(
                draw,
                (float(d2[0]), float(d2[1])),
                (float(u_dir[0]), float(u_dir[1])),
                length=arrow_len,
                half_width=arrow_hw,
                line_width=line_w,
            )
            mid = 0.5 * (d1 + d2)
            n_perp = np.array([-u_dir[1], u_dir[0]])
            if np.dot(n_perp, -ext_u) < 0:
                n_perp = -n_perp
            txt_pos = mid + n_perp * (11.0 * scale_ui)
            _draw_rotated_cad_text(out, label, (float(txt_pos[0]), float(txt_pos[1])), dim_angle_deg, font_size=lbl_font_size)
        else:
            draw.line(
                [(float(d1[0]), float(d1[1])), (float(d2[0]), float(d2[1]))],
                fill=(0, 0, 0),
                width=line_w,
            )
            tail_1 = d1 - u_dir * (arrow_len + 10.0 * scale_ui)
            tail_2 = d2 + u_dir * (arrow_len + 10.0 * scale_ui)
            if style == "tail_text":
                tail_2 = d2 + u_dir * (arrow_len + (len(label) * 13.0 * font_scale + 16.0) * scale_ui)
            draw.line([(float(d1[0]), float(d1[1])), (float(tail_1[0]), float(tail_1[1]))], fill=(0, 0, 0), width=line_w)
            draw.line([(float(d2[0]), float(d2[1])), (float(tail_2[0]), float(tail_2[1]))], fill=(0, 0, 0), width=line_w)

            _draw_hollow_cad_arrow(
                draw,
                (float(d1[0]), float(d1[1])),
                (float(u_dir[0]), float(u_dir[1])),
                length=arrow_len,
                half_width=arrow_hw,
                line_width=line_w,
            )
            _draw_hollow_cad_arrow(
                draw,
                (float(d2[0]), float(d2[1])),
                (-float(u_dir[0]), -float(u_dir[1])),
                length=arrow_len,
                half_width=arrow_hw,
                line_width=line_w,
            )

            if style == "leader_ext":
                w_perp = np.array([-ext_u[1], ext_u[0]])
                if w_perp[1] > 0:
                    w_perp = -w_perp
                txt_pos = d2 + ext_u * ((len(label) * 6.5 * font_scale + 12.0) * scale_ui) + w_perp * (12.5 * scale_ui * font_scale)
                _draw_rotated_cad_text(out, label, (float(txt_pos[0]), float(txt_pos[1])), ext_angle_deg, font_size=lbl_font_size)
            elif style == "tail_text":
                n_perp = np.array([-u_dir[1], u_dir[0]])
                if n_perp[1] > 0:
                    n_perp = -n_perp
                txt_pos = d2 + u_dir * (arrow_len + (len(label) * 6.5 * font_scale + 8.0) * scale_ui) + n_perp * (12.5 * scale_ui * font_scale)
                _draw_rotated_cad_text(out, label, (float(txt_pos[0]), float(txt_pos[1])), dim_angle_deg, font_size=lbl_font_size)
            else:
                mid = 0.5 * (d1 + d2)
                txt_pos = mid - ext_u * (15.5 * scale_ui * font_scale)
                _draw_rotated_cad_text(out, label, (float(txt_pos[0]), float(txt_pos[1])), dim_angle_deg, font_size=lbl_font_size)

    return out


def render_exact_hlr_family_pngs(
    shapes,
    size_paths: Dict[int, str],
    session=None,
    params_meta: Optional[Sequence[dict]] = None,
    call_values: Optional[dict] = None,
    render_size: int = 1200,
    clean_path: Optional[str] = None,
) -> bool:
    """使用 OpenCASCADE 高阶精确分析模式 HLRBRep_Algo 生成大图超清消隐线工程图：
    - 精确模式：提取全部可见边 (棱线、相切边界) 与外轮廓素线 (OutLineVCompound)（需要所有的线）
    - 严格消除隐藏不可见线段（看不到的不要）
    - 纯白 CAD 背景 + 高对比度深色专业工程线条
    - 正轴测标注真实尺寸，空心尖锐三角箭头与粗体带保护晕轮标注文字
    - 1200x1200 大分辨率输出，呈现极致清晰度
    """
    valid_shapes = []
    for s in shapes:
        sh = s.shape if hasattr(s, "shape") else s
        if sh is not None and not (hasattr(sh, "IsNull") and sh.IsNull()):
            valid_shapes.append(sh)
    if not valid_shapes:
        return False

    try:
        from OCC.Core.HLRAlgo import HLRAlgo_Projector
        from OCC.Core.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
        from OCC.Core.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Pnt2d
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_EDGE
        from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
    except Exception:
        return False

    try:
        # 标准东南等轴测视角：视线沿 (1, -1, 1) 射向原点
        view_dir = gp_Dir(1.0, -1.0, 1.0)
        x_dir = gp_Dir(1.0, 1.0, 0.0)
        ax2 = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), view_dir, x_dir)
        proj = HLRAlgo_Projector(ax2)

        hlr = HLRBRep_Algo()
        for sh in valid_shapes:
            hlr.Add(sh)
        hlr.Projector(proj)
        hlr.Update()
        hlr.Hide()

        to_shape = HLRBRep_HLRToShape(hlr)
        visible_compounds = [
            to_shape.VCompound(),
            to_shape.OutLineVCompound(),
            to_shape.Rg1LineVCompound()
        ]

        model_curves = []
        for comp in visible_compounds:
            if comp and not comp.IsNull():
                exp = TopExp_Explorer(comp, TopAbs_EDGE)
                while exp.More():
                    e = exp.Current()
                    adaptor = BRepAdaptor_Curve(e)
                    t0, t1 = adaptor.FirstParameter(), adaptor.LastParameter()
                    steps = 32
                    pts = []
                    for i in range(steps + 1):
                        t = t0 + (t1 - t0) * (i / float(steps))
                        p = adaptor.Value(t)
                        pts.append((p.X(), p.Y()))
                    if len(pts) >= 2:
                        model_curves.append(pts)
                    exp.Next()

        if not model_curves:
            return False

        # 提取 3D 尺寸标注并投影到二维平面
        raw_dims = build_3d_dimension_specs(
            valid_shapes,
            session=session,
            params_meta=params_meta,
            call_values=call_values,
            max_dims=40,
        )
        resolved_dims, _ = resolve_3d_dimension_geometry(valid_shapes, raw_dims)

        proj_dims = []
        for d in resolved_dims:
            p2d1, p2d2, d2d1, d2d2 = gp_Pnt2d(), gp_Pnt2d(), gp_Pnt2d(), gp_Pnt2d()
            proj.Project(gp_Pnt(float(d['p1'][0]), float(d['p1'][1]), float(d['p1'][2])), p2d1)
            proj.Project(gp_Pnt(float(d['p2'][0]), float(d['p2'][1]), float(d['p2'][2])), p2d2)
            proj.Project(gp_Pnt(float(d['d1'][0]), float(d['d1'][1]), float(d['d1'][2])), d2d1)
            proj.Project(gp_Pnt(float(d['d2'][0]), float(d['d2'][1]), float(d['d2'][2])), d2d2)
            proj_dims.append({
                'label': str(d['label']),
                'p1': (p2d1.X(), p2d1.Y()),
                'p2': (p2d2.X(), p2d2.Y()),
                'd1': (d2d1.X(), d2d1.Y()),
                'd2': (d2d2.X(), d2d2.Y()),
                'style': d.get('style', 'linear'),
            })

        # 计算纯外形图模型包络
        m_xs = [p[0] for l in model_curves for p in l]
        m_ys = [p[1] for l in model_curves for p in l]
        m_min_x, m_max_x = min(m_xs), max(m_xs)
        m_min_y, m_max_y = min(m_ys), max(m_ys)

        pad_clean = 90
        m_dx = max(1e-4, m_max_x - m_min_x)
        m_dy = max(1e-4, m_max_y - m_min_y)
        scale_clean = min((render_size - pad_clean * 2) / m_dx, (render_size - pad_clean * 2) / m_dy)
        cx_clean = (m_min_x + m_max_x) * 0.5
        cy_clean = (m_min_y + m_max_y) * 0.5

        def to_px_clean(x, y):
            return (render_size * 0.5 + (x - cx_clean) * scale_clean, render_size * 0.5 - (y - cy_clean) * scale_clean)

        # 1. 绘制高清 3D 外形精确 HLR 消隐线图 (无标注)
        clean_img = Image.new("RGB", (render_size, render_size), (255, 255, 255))
        draw_clean = ImageDraw.Draw(clean_img)
        for l in model_curves:
            px_pts = [to_px_clean(x, y) for x, y in l]
            for i in range(len(px_pts) - 1):
                draw_clean.line([px_pts[i], px_pts[i+1]], fill=(15, 23, 42), width=3)

        # 计算带标注图总包络
        all_xs = list(m_xs)
        all_ys = list(m_ys)
        for pd in proj_dims:
            for pt in [pd['p1'], pd['p2'], pd['d1'], pd['d2']]:
                all_xs.append(pt[0])
                all_ys.append(pt[1])

        a_min_x, a_max_x = min(all_xs), max(all_xs)
        a_min_y, a_max_y = min(all_ys), max(all_ys)
        pad_annot = 110
        a_dx = max(1e-4, a_max_x - a_min_x)
        a_dy = max(1e-4, a_max_y - a_min_y)
        scale_annot = min((render_size - pad_annot * 2) / a_dx, (render_size - pad_annot * 2) / a_dy)
        cx_annot = (a_min_x + a_max_x) * 0.5
        cy_annot = (a_min_y + a_max_y) * 0.5

        def to_px_annot(x, y):
            return (render_size * 0.5 + (x - cx_annot) * scale_annot, render_size * 0.5 - (y - cy_annot) * scale_annot)

        # 2. 绘制高清外形 + 轴测尺寸标注图
        annotated_img = Image.new("RGB", (render_size, render_size), (255, 255, 255))
        draw_annot = ImageDraw.Draw(annotated_img)

        # 绘制实体全部可见线条
        for l in model_curves:
            px_pts = [to_px_annot(x, y) for x, y in l]
            for i in range(len(px_pts) - 1):
                draw_annot.line([px_pts[i], px_pts[i+1]], fill=(15, 23, 42), width=3)

        # 绘制原点标记 □
        p2d_orig = gp_Pnt2d()
        orig_3d = (0.0, 0.0, 0.0)
        if session is not None and getattr(session, "ports", None):
            orig_3d = tuple(session.ports[0]["point"])
        proj.Project(gp_Pnt(float(orig_3d[0]), float(orig_3d[1]), float(orig_3d[2])), p2d_orig)
        ox, oy = to_px_annot(p2d_orig.X(), p2d_orig.Y())
        sq = 7.0
        if 0 <= ox < render_size and 0 <= oy < render_size:
            draw_annot.rectangle([ox - sq, oy - sq, ox + sq, oy + sq], fill=(255, 255, 255), outline=(15, 23, 42), width=2)

        # 绘制标注引线、尺寸线、箭头与文字
        line_w = 2
        arrow_len = 22.0
        arrow_hw = 6.0
        gap_px = 6.0
        overshoot_px = 16.0

        for pd in proj_dims:
            p1 = to_px_annot(*pd['p1'])
            p2 = to_px_annot(*pd['p2'])
            d1 = to_px_annot(*pd['d1'])
            d2 = to_px_annot(*pd['d2'])

            v_dim = np.array(d2) - np.array(d1)
            seg_len = float(np.linalg.norm(v_dim))
            if seg_len < 5.0:
                continue
            u_dir = v_dim / seg_len
            dim_angle = math.degrees(math.atan2(float(u_dir[1]), float(u_dir[0])))

            # 延伸引线 (带起点空隙与端部伸出)
            for p_src, d_dst in [(p1, d1), (p2, d2)]:
                v_ext = np.array(d_dst) - np.array(p_src)
                e_len = float(np.linalg.norm(v_ext))
                if e_len > gap_px + 2.0:
                    u_ext = v_ext / e_len
                    w_start = tuple(np.array(p_src) + u_ext * gap_px)
                    w_end = tuple(np.array(d_dst) + u_ext * overshoot_px)
                    draw_annot.line([w_start, w_end], fill=(30, 41, 59), width=line_w)

            draw_annot.line([d1, d2], fill=(30, 41, 59), width=line_w)
            _draw_architectural_tick(draw_annot, d1, tick_len=18.0, line_width=line_w)
            _draw_architectural_tick(draw_annot, d2, tick_len=18.0, line_width=line_w)

            label = str(pd['label'])
            mid_pt = tuple((np.array(d1) + np.array(d2)) * 0.5)
            font_size = 32 if len(label) <= 3 else (26 if len(label) <= 6 else 22)
            _draw_rotated_cad_text(annotated_img, label, mid_pt, dim_angle, font_size=font_size)

        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        for size, path in size_paths.items():
            folder = os.path.dirname(path)
            if folder and not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)
            sz = int(size)
            if sz >= 600:
                # 标注大图直接保存 1200x1200 极致清晰度
                annotated_img.save(path, "PNG")
            elif sz >= 200:
                annotated_img.resize((sz, sz), resample).save(path, "PNG")
            # 32/64 由 grab_family_pngs 用视口着色带边渲染图填充，这里跳过
        if clean_path:
            folder = os.path.dirname(clean_path)
            if folder and not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)
            clean_img.save(clean_path, "PNG")
        return True
    except Exception as exc:
        print("[HLR] 精确消隐线生成异常，回退至视口渲染:", exc)
        return False


def grab_family_pngs(
    display,
    shapes,
    size_paths: Dict[int, str],
    session=None,
    params_meta: Optional[Sequence[dict]] = None,
    call_values: Optional[dict] = None,
    annotate: bool = True,
    style: str = "pyocc_shaded",
    clean_path: Optional[str] = None,
) -> None:
    """Renders preview PNGs in the requested sizes using shaded faces + edges only.

    所有尺寸统一走离屏视口着色渲染（白底 + 灰色着色面 + 黑色面边界线），
    不再生成 HLR 消隐线图：
    - 32 / 64  ：无标注的着色带边缩略图
    - 200 / 640：annotate=True 时为着色带边 + 轴测尺寸标注，否则为纯着色轴测图
    - clean_path（可选）：无标注的着色带边图，供预览对话框展示

    display 必须是已创建的离屏视口。离屏 OpenGL 上下文只能在进程主线程
    创建，发布链路因此固定跑在独立发布子进程里。
    """
    if display is None:
        raise RuntimeError("着色+边线预览需要离屏视口 display")

    shaded_img = _render_shaded_edges_viewport(display, shapes)
    if shaded_img is None:
        raise RuntimeError("预览渲染失败")

    small_only = {k: v for k, v in size_paths.items() if int(k) in (32, 64)}
    big_only = {k: v for k, v in size_paths.items() if int(k) not in (32, 64)}
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")

    for size, path in small_only.items():
        folder = os.path.dirname(path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        shaded_img.resize((int(size), int(size)), resample).save(path, "PNG")

    if clean_path:
        folder = os.path.dirname(clean_path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        shaded_img.save(clean_path, "PNG")

    if big_only:
        _fallback_viewport_family(
            display,
            shapes,
            big_only,
            session=session,
            params_meta=params_meta,
            call_values=call_values,
            annotate=annotate,
        )


def _render_shaded_edges_viewport(display, shapes) -> Optional[Image.Image]:
    """视口渲染着色带边图：白底 + 灰色着色面 + 黑色面边界线，返回方形的 PIL Image。"""
    if display is None:
        return None
    display.EraseAll()
    display.SetModeShaded()
    try:
        display.set_bg_gradient_color([255, 255, 255], [255, 255, 255])
    except Exception:
        pass
    try:
        from OCC.Core.Graphic3d import Graphic3d_TypeOfShadingModel_Phong
        display.View.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
    except Exception:
        pass

    try:
        from OCC.Core.Quantity import Quantity_NOC_GRAY50, Quantity_NOC_BLACK, Quantity_Color
        from OCC.Core.Aspect import Aspect_TOL_SOLID
        color = Quantity_Color(Quantity_NOC_GRAY50)
        edge_color = Quantity_Color(Quantity_NOC_BLACK)
    except Exception:
        color = _make_occ_color(0.55, 0.60, 0.66)
        edge_color = None
        Aspect_TOL_SOLID = None

    drawn = 0
    for item in shapes:
        shape = item.shape if hasattr(item, "shape") else item
        if shape is None or shape.IsNull():
            continue
        ais_list = display.DisplayShape(shape, update=False, color=color, transparency=0.0)
        if ais_list and edge_color is not None:
            for ais in ais_list:
                try:
                    drw = ais.Attributes()
                    drw.SetFaceBoundaryDraw(True)
                    asp = drw.FaceBoundaryAspect()
                    asp.SetColor(edge_color)
                    asp.SetWidth(1.0)
                    if Aspect_TOL_SOLID is not None:
                        asp.SetTypeOfLine(Aspect_TOL_SOLID)
                    ais.SetAttributes(drw)
                except Exception:
                    pass
        drawn += 1
    if drawn == 0:
        raise RuntimeError("脚本没有生成实体")

    if hasattr(display, "SetExtraFramingPoints"):
        display.SetExtraFramingPoints(None, margin=0.14)
    display.SetSize(640, 640)
    display.View_Iso()
    display.FitAll()
    if hasattr(display, "Repaint"):
        display.Repaint()

    handle, tmp = tempfile.mkstemp(suffix=".png")
    os.close(handle)
    try:
        _dump_view(display, tmp)
        img = Image.open(tmp).convert("RGB")
        img.load()
        if img.size[0] < 8 or img.size[1] < 8:
            raise RuntimeError("预览抓图失败")
        return _square_around_part(img, pad=20)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _fallback_viewport_family(
    display,
    shapes,
    size_paths: Dict[int, str],
    session=None,
    params_meta=None,
    call_values=None,
    annotate: bool = True,
) -> None:
    """HLR 不可用时的完整视口回退：按 annotate 渲染标注或纯着色图。"""
    resolved_dims: List[dict] = []
    margin = 0.12
    if annotate:
        raw_dims = build_3d_dimension_specs(
            shapes,
            session=session,
            params_meta=params_meta,
            call_values=call_values,
            max_dims=40,
        )
        resolved_dims, framing_pts = resolve_3d_dimension_geometry(shapes, raw_dims)
        if hasattr(display, "SetExtraFramingPoints"):
            display.SetExtraFramingPoints(framing_pts, margin=margin)
    else:
        if hasattr(display, "SetExtraFramingPoints"):
            display.SetExtraFramingPoints(None, margin=0.14)

    display.SetSize(640, 640)
    display.View_Iso()
    display.FitAll()
    # On native C++ pythonocc-core, zoom out slightly when annotating so dimension lines around the model have room
    if annotate and not hasattr(display, "SetExtraFramingPoints"):
        try:
            if hasattr(display.View, "SetScale") and hasattr(display.View, "Scale"):
                display.View.SetScale(display.View.Scale() * 0.74)
        except Exception:
            pass
    if hasattr(display, "Repaint"):
        display.Repaint()

    handle, tmp = tempfile.mkstemp(suffix=".png")
    os.close(handle)
    try:
        _dump_view(display, tmp)
        raw_img = Image.open(tmp).convert("RGB")
        raw_img.load()
        width, height = raw_img.size
        if width < 8 or height < 8:
            raise RuntimeError("预览抓图失败")

        if annotate:
            annotated_img_640 = annotate_isometric_dimensions(
                raw_img,
                display,
                resolved_dims,
                session=session,
                margin=margin,
                font_scale=1.0,
            )
            annotated_img_200 = annotate_isometric_dimensions(
                raw_img,
                display,
                resolved_dims,
                session=session,
                margin=margin,
                font_scale=1.22,
            )
        else:
            annotated_img_640 = raw_img
            annotated_img_200 = raw_img
    finally:
        if hasattr(display, "SetExtraFramingPoints"):
            display.SetExtraFramingPoints(None, margin=0.14)
        try:
            os.remove(tmp)
        except OSError:
            pass

    square_annot = _square_around_part(annotated_img_640, pad=26)
    square_plain = _square_around_part(raw_img, pad=20)
    resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")

    for size, path in size_paths.items():
        folder = os.path.dirname(path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)
        if int(size) in (32, 64):
            src = square_plain
        elif annotate:
            src = square_annot
        else:
            src = square_plain
        picture = src.resize((int(size), int(size)), resample)
        picture.save(path, "PNG")


def render_custom_script_previews(
    display,
    shapes,
    custom_scripts_dir: str,
    stem: str,
    session=None,
    params_meta: Optional[Sequence[dict]] = None,
    call_values: Optional[dict] = None,
    style: str = "pyocc_shaded",
    clean_path: Optional[str] = None,
    annotate: bool = True,
) -> Dict[int, str]:
    """生成 `<stem>_640.png`、`<stem>_200.png`、`<stem>_64.png` 与
    `<stem>_32.png` 到 `CustomScripts/` 目录。不再生成 `_shape.png`。

    annotate=True 时 640/200 带轴测尺寸标注，适用于支吊架和设备；
    annotate=False 时所有尺寸均为纯着色轴测图，适用于管件、阀门和仪表。
    clean_path 非空时额外写出无标注的着色带边图（发布流程不使用）。
    """
    os.makedirs(custom_scripts_dir, exist_ok=True)
    paths = {
        640: os.path.join(custom_scripts_dir, f"{stem}_640.png"),
        200: os.path.join(custom_scripts_dir, f"{stem}_200.png"),
        64: os.path.join(custom_scripts_dir, f"{stem}_64.png"),
        32: os.path.join(custom_scripts_dir, f"{stem}_32.png"),
    }
    grab_family_pngs(
        display,
        shapes,
        paths,
        session=session,
        params_meta=params_meta,
        call_values=call_values,
        annotate=annotate,
        style=style,
        clean_path=clean_path,
    )
    return paths
