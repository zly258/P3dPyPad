# -*- coding: utf-8 -*-
import os
import sys
import argparse
import time

if __package__ is None or __package__ == "":
    pkg_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if pkg_root not in sys.path:
        sys.path.insert(0, pkg_root)
    from plant3d_occ.runner.sandbox import run_script_in_sandbox
    from plant3d_occ.renderer.offscreen import render_occt_viewer
else:
    from .sandbox import run_script_in_sandbox
    from ..renderer.offscreen import render_occt_viewer

def visual_check(script_path, output_png=None, param_overrides=None, show_gui=True, mode="both"):
    """加载指定 Plant 3D 脚本，通过 OCC 内核仿真建模并输出原生 OCCT 渲染大图 / 交互式 3D 窗口。"""
    t0 = time.time()
    if not os.path.exists(script_path):
        print(f"Error: 脚本文件不存在: {script_path}")
        return False

    if output_png is None:
        base, _ = os.path.splitext(script_path)
        output_png = base + "_check.png"

    print(f"[OCC 仿真器] 正在加载并执行脚本: {os.path.basename(script_path)}...")
    session, entry_name, shapes = run_script_in_sandbox(script_path, param_overrides)
    t_calc = time.time() - t0

    print(f"[OCC 仿真器] CSG 拓扑构建完成，生成 {len(shapes)} 个有效实体 (耗时: {t_calc*1000:.1f}ms)")
    if not shapes:
        print("Error: 脚本执行后未产生任何有效 3D 实体！")
        return False

    title = f"AutoCAD Plant 3D 真实外形离线检验: {entry_name}"
    ok = render_occt_viewer(shapes, output_png_path=output_png, show_gui=show_gui, title=title, render_mode=mode)

    if ok:
        print(f"[OCC 仿真器] 渲染完成！截图文件: {output_png} (总耗时: {(time.time() - t0)*1000:.1f}ms)")
        return output_png
    else:
        print("Error: 渲染失败！")
        return False

def main():
    parser = argparse.ArgumentParser(description="Plant 3D OCC 离线仿真与真实外形检验渲染工具")
    parser.add_argument("script", help="待检验的 Plant 3D 参数化 Python 脚本路径 (.py)")
    parser.add_argument("-o", "--out", help="输出渲染图片路径 (.png)", default=None)
    parser.add_argument("-p", "--param", action="append", help="覆盖参数，格式 KEY=VALUE", default=[])
    parser.add_argument("--gui", action="store_true", default=None, help="启动交互式 3D GUI 视口窗口 (已居中)")
    parser.add_argument("--no-gui", "--not-gui", action="store_true", dest="no_gui", help="仅静默导出高清渲染图板，不弹窗")
    parser.add_argument("--mode", choices=["shaded", "hlr", "both"], default="both", help="视图渲染模式 (默认: both 多视图标注图板)")

    args = parser.parse_args()
    param_dict = {}
    for p in args.param:
        if "=" in p:
            k, v = p.split("=", 1)
            param_dict[k.strip()] = v.strip()

    show_gui = False if args.no_gui else True
    result = visual_check(args.script, args.out, param_dict, show_gui=show_gui, mode=args.mode)
    if not result:
        sys.exit(1)

if __name__ == "__main__":
    main()
