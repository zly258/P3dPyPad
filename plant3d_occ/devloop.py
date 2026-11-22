# -*- coding: utf-8 -*-
"""改脚本 → 校验 → 发布 的自动循环（配合 Plant 3D 的"重启才生效"）。

Plant 3D 加载脚本后不会释放，改完必须 PLANTREGISTERCUSTOMSCRIPTS 再重启
（PD1746 明确说明）。所以开发循环是：

    改 .py / .csv → 本工具自动校验+发布 → 手动（或 --restart-acad）重启 Plant 3D
                                         → 在图形里 TESTACPSCRIPT 看结果

用法：

    python -m plant3d_occ.devloop pyscripts/05_supports/SUPPORT_GATE_FRAME.py
    python -m plant3d_occ.devloop <脚本> --once            # 只跑一轮（可放进编辑器快捷键）
    python -m plant3d_occ.devloop <脚本> --no-validate     # 跳过模型校验直接发布
    python -m plant3d_occ.devloop <脚本> --restart-acad "C:\\...\\acad.exe"

只监视，不发布（干跑）：--dry-run
"""

from __future__ import print_function

import argparse
import os
import subprocess
import sys
import time

def _stamp(path):
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _watched_files(script):
    """脚本 + 同名 CSV（预设表改了也要重新发布）。"""
    base = os.path.splitext(script)[0]
    files = [script]
    for ext in (".csv",):
        candidate = base + ext
        if os.path.isfile(candidate):
            files.append(candidate)
    return files


def _mtime_map(files):
    return dict((f, _stamp(f)) for f in files)


def run_once(script, content=None, plant_root=None, validate=True, dry_run=False,
             restart_acad=None, write_preview=False):
    """校验 + 发布一轮。返回 (ok, 摘要行)。"""
    from .catalog.model import inspect_script
    from .catalog.publish import publish_scripts

    job = inspect_script(script)
    label = os.path.basename(script)
    if job.get("skip_reason"):
        return False, "跳过 %s：%s" % (label, job["skip_reason"])

    if validate:
        from .catalog.validate import validate_script
        check = validate_script(script)
        if not check["ok"]:
            return False, "校验不通过 %s：%s" % (label, "；".join(check["issues"]))

    if dry_run:
        return True, "干跑通过 %s（未写入库）" % label

    results = publish_scripts([script], content_dir=content, plant_root=plant_root,
                              write_preview=write_preview, validate=False)
    ok = bool(results) and results[0].status == "published"
    summary = results[0].status + " " + label + "：" + results[0].message.split("。")[0]

    if ok and restart_acad:
        try:
            subprocess.Popen([restart_acad])
            summary += "；已启动 AutoCAD，等它完全起来后重新打开图形"
        except Exception as exc:            # noqa: BLE001
            summary += "；启动 AutoCAD 失败：" + str(exc)
    return ok, summary


def watch(script, interval=2.0, on_cycle=None, **kwargs):
    """盯着文件变化，每变一次跑一轮。Ctrl+C 退出。"""
    files = _watched_files(script)
    seen = _mtime_map(files)
    print(u"监视 %s（Ctrl+C 退出）" % "、".join(os.path.basename(f) for f in files))

    ok, summary = run_once(script, **kwargs)
    print(_prefix(ok) + summary)
    if on_cycle:
        on_cycle(ok, summary)

    while True:
        time.sleep(interval)
        current = _mtime_map(files)
        if current == seen:
            continue
        seen = current
        print(u"\n[%s] 检测到改动，重新校验并发布…" % time.strftime("%H:%M:%S"))
        ok, summary = run_once(script, **kwargs)
        print(_prefix(ok) + summary)
        if ok:
            print(u"   → 到 Plant 3D 里执行 PLANTREGISTERCUSTOMSCRIPTS，重启后用 "
                  u"TESTACPSCRIPT 验证（脚本名：%s）" % os.path.splitext(os.path.basename(script))[0])
        if on_cycle:
            on_cycle(ok, summary)


def _prefix(ok):
    return u"[通过] " if ok else u"[失败] "


def _main(argv=None):
    parser = argparse.ArgumentParser(description=u"脚本开发循环：改文件 → 校验 → 发布（→ 重启 CAD）")
    parser.add_argument("script", help=u"要监视的 .py 脚本")
    parser.add_argument("--interval", type=float, default=2.0, help=u"轮询间隔秒数（默认 2）")
    parser.add_argument("--once", action="store_true", help=u"只跑一轮就退出")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help=u"只校验，不写库")
    parser.add_argument("--no-validate", dest="no_validate", action="store_true",
                        help=u"跳过模型校验")
    parser.add_argument("--content", default=None, help=u"CPak Common 目录")
    parser.add_argument("--plant-root", default=None, help=u"Plant 内容包根目录")
    parser.add_argument("--restart-acad", dest="restart_acad", default=None,
                        help=u"发布成功后启动这个 AutoCAD 可执行文件")
    parser.add_argument("--preview", action="store_true", help=u"同时生成元件库预览图（较慢）")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.script):
        print(u"找不到脚本：%s" % args.script)
        return 2

    kwargs = dict(content=args.content, plant_root=args.plant_root,
                  validate=not args.no_validate, dry_run=args.dry_run,
                  restart_acad=args.restart_acad, write_preview=args.preview)

    if args.once:
        ok, summary = run_once(args.script, **kwargs)
        print(_prefix(ok) + summary)
        return 0 if ok else 1

    try:
        watch(args.script, interval=args.interval, **kwargs)
    except KeyboardInterrupt:
        print(u"\n已停止。")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
