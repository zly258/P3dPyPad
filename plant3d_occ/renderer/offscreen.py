# -*- coding: utf-8 -*-
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont


def _make_steel_color():
    from OCC.Core.Quantity import Quantity_NOC_GRAY50, Quantity_Color
    try:
        return Quantity_Color(Quantity_NOC_GRAY50)
    except Exception:
        return Quantity_Color((0.55, 0.62, 0.70))


def _disable_face_boundaries(display):
    """主色不带边线：关闭面边界线并提升曲面细化精度，禁止出现网格化棱线。"""
    try:
        ctx = getattr(display, "Context", None)
        if ctx is not None and hasattr(ctx, "DefaultDrawer"):
            drawer = ctx.DefaultDrawer()
            if hasattr(drawer, "SetFaceBoundaryDraw"):
                drawer.SetFaceBoundaryDraw(False)
            if hasattr(drawer, "SetDeviationCoefficient"):
                drawer.SetDeviationCoefficient(0.002)
            if hasattr(drawer, "SetDeviationAngle"):
                drawer.SetDeviationAngle(0.2)
    except Exception:
        pass


def render_occt_viewer(shapes, output_png_path=None, show_gui=True, title="Plant 3D OCCT 3D Viewer", render_mode="shaded"):
    """使用 OpenCASCADE (OCCT) 3D 渲染引擎进行平滑无边线着色渲染与交互式查看。"""
    from OCC.Display.SimpleGui import init_display

    valid_shapes = []
    for s in shapes:
        shape = s.shape if hasattr(s, "shape") else s
        if shape is not None and not shape.IsNull():
            valid_shapes.append(shape)

    if not valid_shapes:
        print("[OCCT] 警告: 未找到任何有效 3D 实体！")
        return False

    display, start_display, _add_menu, _add_function_to_menu = init_display(backend_str="pyside6")
    _disable_face_boundaries(display)

    steel_gray = _make_steel_color()
    for shape in valid_shapes:
        display.DisplayShape(shape, update=False, color=steel_gray, transparency=0.0)

    try:
        win = getattr(display, "parent", None)
        if win:
            win.setWindowTitle(title)
            screen = win.screen().availableGeometry()
            win_w = min(1180, screen.width() - 80)
            win_h = min(780, screen.height() - 80)
            win.resize(win_w, win_h)
            pos_x = (screen.width() - win_w) // 2
            pos_y = (screen.height() - win_h) // 2
            win.move(max(0, pos_x), max(0, pos_y))
    except Exception:
        pass

    display.SetModeShaded()
    _disable_face_boundaries(display)
    display.View_Iso()
    display.FitAll()

    if output_png_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
        export_multiview_composite(display, output_png_path, title, render_mode)
        print(f"[OCCT] 标准四视图合成检验大图已生成: {output_png_path}")

    if show_gui:
        start_display()

    return True


def export_multiview_composite(display, output_path, title, mode="shaded"):
    """抓取四个标准工程视角并拼接为无边线平滑着色四视图大图。"""
    temp_dir = tempfile.gettempdir()
    view_files = []

    views = [
        (display.View_Iso, "1. 东南等轴测视图 (SE Isometric)", "iso"),
        (display.View_Front, "2. 正视图 (Front View - XZ 向)", "front"),
        (display.View_Top, "3. 俯视图 (Top View - XY 向)", "top"),
        (display.View_Right, "4. 右侧视图 (Right View - YZ 向)", "right"),
    ]

    display.SetModeShaded()
    _disable_face_boundaries(display)
    for view_func, label, tag in views:
        view_func()
        display.FitAll()
        tmp_img = os.path.join(temp_dir, f"occt_tmp_{tag}.png")
        display.View.Dump(tmp_img)
        view_files.append((tmp_img, label))

    sub_imgs = [Image.open(f) for f, _ in view_files]
    sw, sh = sub_imgs[0].size
    target_sw = min(sw, 720)
    target_sh = int(sh * (target_sw / float(sw)))
    resized_imgs = [img.resize((target_sw, target_sh), Image.Resampling.LANCZOS) for img in sub_imgs]

    pad = 12
    header_h = 44
    label_h = 24

    total_w = target_sw * 2 + pad * 3
    total_h = header_h + (target_sh + label_h + pad) * 2 + pad

    canvas = Image.new("RGB", (total_w, total_h), color=(245, 247, 250))
    draw = ImageDraw.Draw(canvas)

    title_font = None
    label_font = None
    font_candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for f_candidate in font_candidates:
        if os.path.exists(f_candidate):
            try:
                title_font = ImageFont.truetype(f_candidate, 16)
                label_font = ImageFont.truetype(f_candidate, 12)
                break
            except Exception:
                pass
    if title_font is None:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    draw.rectangle([0, 0, total_w, header_h], fill=(38, 50, 56))
    draw.text((pad + 4, 12), title + " [AutoCAD Plant 3D vs OCCT 多视图检验图板]", fill=(255, 255, 255), font=title_font)

    positions = [
        (pad, header_h + pad),
        (pad * 2 + target_sw, header_h + pad),
        (pad, header_h + pad * 2 + target_sh + label_h),
        (pad * 2 + target_sw, header_h + pad * 2 + target_sh + label_h),
    ]

    for idx, (img, (pos_x, pos_y)) in enumerate(zip(resized_imgs, positions)):
        label = view_files[idx][1]
        draw.rectangle([pos_x, pos_y, pos_x + target_sw, pos_y + label_h], fill=(225, 230, 235))
        draw.text((pos_x + 8, pos_y + 4), label, fill=(33, 43, 54), font=label_font)
        canvas.paste(img, (pos_x, pos_y + label_h))
        draw.rectangle([pos_x, pos_y, pos_x + target_sw, pos_y + label_h + target_sh], outline=(180, 190, 200), width=1)

    canvas.save(output_path, quality=95)

    for f, _ in view_files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception:
            pass
