# -*- coding: utf-8 -*-
"""发布入口：自动写入元件库 (.acat/.pcat) 与等级库 (.pspc/.pspx) 或设备包 (.peqx)，
自动复制脚本并生成 CustomScripts 注册元数据 (<Script>.xml, variants.map, ScriptGroup.xml)，
自动通过 PyOCC 离屏渲染轴测预览图 (640/200/64/32)：支吊架和设备带参数尺寸标注，
管件、阀门和仪表仅生成着色轴测图。
"""
import os

from . import custom_xml, equipment
from .model import inspect_script, needs_dimension_annotation
from .preview import (
    close_display,
    grab_family_pngs,
    open_offscreen_display,
    render_custom_script_previews,
)
from .store import PLANT_CONTENT, LibrarySession, copy_script, preview_paths

REGISTER_HINT = "请在 Plant 3D 中执行 PLANTREGISTERCUSTOMSCRIPTS，然后重新打开。"


class PublishResult(object):
    def __init__(self, script, status, message, catalog=""):
        self.script = script
        self.status = status
        self.message = message
        self.catalog = catalog


def _support_spec_override():
    """读取用户配置里的支吊架等级文件名（如 PipeSupports.pspc），未配置时返回 None 用原厂默认。"""
    return _fixed_spec_override("support_spec")


def _instrument_spec_override():
    """读取用户配置里的仪表等级文件名，未配置时返回 None 用原厂默认 Instrumentation Metric.pspc。

    仪表等级是固定的：不允许用户随意指定其他等级，仪表永远进仪表库。
    """
    return _fixed_spec_override("instrument_spec")


def _fixed_spec_override(cfg_key):
    """按配置键读取固定等级文件名（仅接受 .pspc），未配置时返回 None。"""
    import json
    cfg_file = os.path.expanduser("~/.plant3d_occ_catalog_config.json")
    try:
        if os.path.isfile(cfg_file):
            with open(cfg_file, "r", encoding="utf-8") as fp:
                name = (json.load(fp) or {}).get(cfg_key) or ""
            name = name.strip()
            if name and name.lower().endswith(".pspc"):
                return name
    except Exception:
        pass
    return None


def _ensure_support_spec_available(content_dir, spec_name, on_progress=None):
    """确保配置的固定等级（支吊架/仪表）在 CPak Common 里存在。

    项目自建等级（如 PipeSupports.pspc）通常只存在于项目的"等级库工作表"目录。
    首次发布时从项目目录原样拷贝（连同 .pspx），保留其中全部既有构件，
    之后每次发布都在这份拷贝上追加。
    """
    dest = os.path.join(content_dir, spec_name)
    if os.path.isfile(dest):
        return dest
    import json
    cfg_file = os.path.expanduser("~/.plant3d_occ_catalog_config.json")
    ps_dir = ""
    try:
        if os.path.isfile(cfg_file):
            with open(cfg_file, "r", encoding="utf-8") as fp:
                ps_dir = (json.load(fp) or {}).get("project_spec_dir") or ""
    except Exception:
        pass
    import glob as _glob
    if not ps_dir or not os.path.isdir(ps_dir):
        return dest
    src = os.path.join(ps_dir, spec_name)
    if os.path.isfile(src) and os.path.getsize(src) > 0:
        import shutil
        shutil.copy2(src, dest)
        src_pspx = os.path.splitext(src)[0] + ".pspx"
        if os.path.isfile(src_pspx):
            shutil.copy2(src_pspx, os.path.splitext(dest)[0] + ".pspx")
        _tell(on_progress, "已从项目等级库工作表复制 %s (%.0f KB) 到 CPak Common" % (
            spec_name, os.path.getsize(dest) / 1024.0))
    return dest


def publish_scripts(
    paths,
    content_dir=None,
    plant_root=None,
    display=None,
    write_preview=True,
    on_progress=None,
    validate=True,
    auto_generate_sizes=True,
    equipment_type=None,
    include_equipment=True,
):
    """把若干脚本写入元件库和等级库（设备则生成 .peqx），并自动生成带字母标注的轴测预览图与注册元数据。

    equipment_type：可选 (PartType, PartSubType) 二元组，只对设备脚本生效，
    用于在设备发布时由用户显式指定设备类型；传 None 时按脚本 Group 自动推断。
    include_equipment：是否允许处理设备脚本（生成 .peqx）。发布构件页传 False
    ——设备与构件分链路发布，设备脚本一律在「发布设备」页处理，绝不写元件库。
    支吊架等级文件名由配置 support_spec 决定（默认 PipeSupportsSpec.pspc，
    用户可改成 PipeSupports.pspc 等任意项目等级）；仪表等级由 instrument_spec
    决定（默认 Instrumentation Metric.pspc）。这两个等级是固定的，发布时不
    跟随界面上的"目标项目等级库"下拉；管件/阀门才写入用户自选等级。
    """
    plant_root = plant_root or PLANT_CONTENT
    if content_dir is None:
        content_dir = os.path.join(plant_root, "CPak Common")
    if content_dir:
        try:
            os.makedirs(content_dir, exist_ok=True)
        except OSError as exc:
            _tell(on_progress, "无法创建内容目录 %s：%s" % (content_dir, exc))
    # 支吊架与仪表等级是固定的（分别由 support_spec / instrument_spec 决定），
    # 不随用户在界面上选的"目标项目等级库"变化；管件/阀门才走用户自选等级。
    support_spec = _support_spec_override()
    if support_spec:
        try:
            _ensure_support_spec_available(content_dir, support_spec, on_progress)
        except Exception as exc:
            _tell(on_progress, "准备支吊架等级库失败（继续发布）：" + str(exc))
    instrument_spec = _instrument_spec_override()
    if instrument_spec:
        try:
            _ensure_support_spec_available(content_dir, instrument_spec, on_progress)
        except Exception as exc:
            _tell(on_progress, "准备仪表等级库失败（继续发布）：" + str(exc))
    preview_display = display
    owns_preview_display = False
    if write_preview and preview_display is None:
        # 预览统一使用着色+边线离屏视口。离屏 OpenGL 上下文只能在进程主线程
        # 创建，因此 GUI 发布链路固定通过 QProcess 在独立子进程里执行这里；
        # 子进程崩溃也不会带走主程序。
        try:
            preview_display = open_offscreen_display()
            owns_preview_display = True
        except Exception as exc:
            _tell(on_progress, "离屏预览视口创建失败，本次跳过预览图：" + str(exc))

    results = []
    sessions = {}
    try:
        for path in paths:
            job = inspect_script(path, auto_generate_sizes=auto_generate_sizes)
            # 没有同名 CSV 时自动生成一份默认预设表（按 def 签名默认值 + 标准管径
            # 系列推导），不再整体跳过——只有连参数都解析不出的脚本才真正不可发布。
            if job["skip_reason"] == "没有同名 CSV" and auto_generate_sizes:
                try:
                    from .model import ensure_script_csv
                    generated = ensure_script_csv(path)
                    if generated and os.path.isfile(generated):
                        _tell(on_progress, "已自动生成预设表 %s（按脚本默认值推导）"
                              % os.path.basename(generated))
                        job = inspect_script(path, auto_generate_sizes=auto_generate_sizes)
                except Exception as exc:
                    _tell(on_progress, "自动生成 %s.csv 失败：%s" % (job["stem"], exc))
            if job["skip_reason"]:
                results.append(PublishResult(path, "skipped", job["skip_reason"]))
                _tell(on_progress, "跳过 %s：%s" % (job["stem"], job["skip_reason"]))
                continue
            # 防御性分流：设备脚本走 .peqx 专属分支；若 publish_scripts 被外部
            # 以 include_equipment=False 调用（发布构件页），设备脚本一律跳过，
            # 避免设备被误写进管道/仪表元件库。
            if job["domain"] == "equipment" and not include_equipment:
                results.append(PublishResult(path, "skipped", "设备脚本请在「发布设备」页发布 (.peqx)"))
                _tell(on_progress, "跳过 %s：设备脚本请在「发布设备」页发布" % job["stem"])
                continue
            if validate:
                from .validate import validate_script
                check = validate_script(path)
                if not check["ok"]:
                    detail = u"；".join(check["issues"])
                    results.append(PublishResult(path, "failed", u"校验不通过：" + detail))
                    _tell(on_progress, "校验不通过 %s：%s" % (job["stem"], detail))
                    continue

            custom_scripts_dir = os.path.join(content_dir, "CustomScripts")

            if job["domain"] == "equipment":
                try:
                    copied = copy_script(content_dir, job["path"])
                    custom_xml.write_custom_script_metadata(custom_scripts_dir, job)
                    peqx_path = os.path.join(content_dir, "equipment", job["stem"] + ".peqx")
                    preview = None
                    if write_preview:
                        try:
                            preview = _render_equipment_preview(preview_display, job, custom_scripts_dir)
                        except Exception as exc:
                            _tell(on_progress, "预览图生成失败：" + str(exc))
                    built = equipment.build_peqx(
                        job["path"], peqx_path, preview_png=preview,
                        display_name=job.get("tooltip_short"),
                        part_type=(equipment_type[0] if equipment_type else None),
                        part_sub_type=(equipment_type[1] if equipment_type else None),
                    )
                    note = "已生成设备模板 %s（%s/%s）。脚本已复制到 %s" % (
                        built["path"], built["part_type"], built["part_sub_type"], copied
                    )
                    if built.get("preview"):
                        note += "。预览图 " + built["preview"]
                    if not job["params"]:
                        note += "。注意：脚本没有 @param，设备对话框里将没有可调参数"
                    results.append(PublishResult(job["path"], "published", note, "equipment"))
                    _tell(on_progress, "完成 " + job["stem"] + "（设备模板）")
                except Exception as exc:
                    results.append(PublishResult(job["path"], "failed", str(exc)))
                    _tell(on_progress, "失败 %s：%s" % (job["stem"], exc))
                continue

            try:
                session = sessions.get(job["domain"])
                if session is None:
                    # 等级固定分流：支吊架→support_spec，仪表→instrument_spec，
                    # 其余（管件/阀门）用领域默认 CustomParts Metric.pspc
                    spec_override = None
                    if job["domain"] == "support":
                        spec_override = support_spec
                    elif job["domain"] == "instrumentation":
                        spec_override = instrument_spec
                    session = LibrarySession(
                        content_dir, plant_root, job["domain"],
                        spec_file_override=spec_override,
                    )
                    session.open()
                    sessions[job["domain"]] = session
                    _tell(on_progress, "已准备 " + session.info["catalog_name"]
                          + " -> " + os.path.basename(session.spec_path))
                session.mark()
                try:
                    family = session.write_family(job)
                    session.release()
                except Exception:
                    session.undo()
                    raise
                copied = copy_script(content_dir, job["path"])
                custom_xml.write_custom_script_metadata(custom_scripts_dir, job)
                extra = _publish_extra_catalogs(job, content_dir, plant_root, on_progress)
                note = "已写入 %s，%d 个尺寸。脚本已复制到 %s" % (
                    session.info["catalog_name"], len(job["sizes"]), copied,
                )
                if extra:
                    note += "；同时写入 " + "、".join(extra)
                if job["warnings"]:
                    note += "。" + "。".join(job["warnings"])
                if write_preview:
                    try:
                        _render(preview_display, job, content_dir, session.info["catalog_file"], family)
                        if needs_dimension_annotation(job):
                            note += "。预览图已生成（含轴测参数尺寸标注）"
                        else:
                            note += "。预览图已生成（轴测着色图）"
                    except Exception as exc:
                        note += "。预览图失败: " + str(exc)
                elif write_preview:
                    note += "。未生成预览图"
                results.append(PublishResult(path, "published", note, session.info["catalog_name"]))
                _tell(on_progress, "完成 %s" % job["stem"])
            except Exception as exc:
                results.append(PublishResult(path, "failed", str(exc)))
                _tell(on_progress, "失败 %s：%s" % (job["stem"], exc))
    finally:
        for session in sessions.values():
            session.close()
        if owns_preview_display and preview_display is not None:
            close_display(preview_display)
    if any(item.status == "published" for item in results):
        _tell(on_progress, REGISTER_HINT)
    return results


def _publish_extra_catalogs(job, content_dir, plant_root, on_progress=None):
    """把同一个族再写进该域的额外元件库。"""
    try:
        from .store import domain_info
        info = domain_info(job["domain"])
    except Exception:  # noqa: BLE001
        return []

    written = []
    for extra in info.get("extra_catalogs") or []:
        target_name = extra.get("catalog_file")
        try:
            merged = dict(info)
            merged.update(extra)
            merged["catalog_only"] = True

            target = os.path.join(content_dir, target_name)
            candidates = [
                target,
                os.path.join(content_dir, target_name),
                os.path.join(plant_root, target_name),
                os.path.join(plant_root, "CPak Common", target_name),
                os.path.join(PLANT_CONTENT, target_name),
                os.path.join(PLANT_CONTENT, "CPak Common", target_name),
            ]
            donor = next((c for c in candidates if os.path.isfile(c)), None)
            if donor is None:
                raise RuntimeError("找不到用于追加的模板库：" + str(target_name))
            if not os.path.isfile(target):
                import shutil
                shutil.copy2(donor, target)

            session = LibrarySession(content_dir, plant_root, job["domain"])
            session.info = merged
            session.catalog_path = target
            session.catalog_donor = donor
            session.open()
            try:
                session.mark()
                try:
                    session.write_family(job)
                    session.release()
                except Exception:
                    session.undo()
                    raise
            finally:
                session.close()
            written.append(merged.get("catalog_name") or target_name)
            _tell(on_progress, "已同步写入 " + str(target_name))
        except Exception as exc:  # noqa: BLE001
            _tell(on_progress, "额外库写入失败 %s：%s" % (target_name, exc))
    return written


def _render_equipment_preview(display, job, custom_scripts_dir=None):
    """设备模板的主显示图（200×200，带轴测参数尺寸标注），打包进 peqx 的 preview/ 目录。"""
    import tempfile
    from ..runner.sandbox import run_script_in_sandbox

    annotate = needs_dimension_annotation(job)
    size = (job.get("sizes") or [None])[0]
    params = dict(size.get("call") or {}) if size else dict(job.get("defaults") or {})
    session, _name, shapes = run_script_in_sandbox(job["path"], params)
    handle, path = tempfile.mkstemp(suffix=".png")
    os.close(handle)
    grab_family_pngs(
        display,
        shapes,
        {200: path},
        session=session,
        params_meta=job.get("params_meta") or job.get("params"),
        call_values=params,
        annotate=annotate,
    )
    if not (os.path.isfile(path) and os.path.getsize(path) > 0):
        try:
            os.remove(path)
        except OSError:
            pass
        return None
    if custom_scripts_dir:
        render_custom_script_previews(
            display,
            shapes,
            custom_scripts_dir,
            job["stem"],
            session=session,
            params_meta=job.get("params_meta") or job.get("params"),
            call_values=params,
            annotate=annotate,
        )
    return path


def _render(display, job, content_dir, catalog_file, family):
    from ..runner.sandbox import run_script_in_sandbox
    annotate = needs_dimension_annotation(job)
    size = job["sizes"][len(job["sizes"]) // 2]
    session, _name, shapes = run_script_in_sandbox(job["path"], size["call"])
    paths = preview_paths(content_dir, catalog_file, job["image"], family)
    grab_family_pngs(
        display,
        shapes,
        paths,
        session=session,
        params_meta=job.get("params_meta") or job.get("params"),
        call_values=size["call"],
        annotate=annotate,
    )
    custom_scripts_dir = os.path.join(content_dir, "CustomScripts")
    render_custom_script_previews(
        display,
        shapes,
        custom_scripts_dir,
        job["stem"],
        session=session,
        params_meta=job.get("params_meta") or job.get("params"),
        call_values=size["call"],
        annotate=annotate,
    )


def _tell(callback, message):
    if callback is not None:
        callback(message)


def _main():
    import argparse
    import sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)
    parser = argparse.ArgumentParser(description="把构件脚本发布到 Plant 3D 元件库和等级库（自动生成带参数标注轴测预览图）")
    parser.add_argument("scripts", nargs="+")
    parser.add_argument("--content", default=None, help="CPak Common 目录")
    parser.add_argument("--plant-root", default=PLANT_CONTENT)
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--auto-sizes", action="store_true", help="缺少 CSV 时自动按函数默认值生成尺寸表")
    args = parser.parse_args()
    results = publish_scripts(
        args.scripts,
        content_dir=args.content,
        plant_root=args.plant_root,
        write_preview=not args.no_preview,
        auto_generate_sizes=args.auto_sizes,
        on_progress=lambda text: sys.stdout.write(text + "\n"),
    )
    failed = 0
    for item in results:
        sys.stdout.write("%s  %s  %s\n" % (item.status, os.path.basename(item.script), item.message))
        if item.status == "failed":
            failed += 1
    if any(item.status == "published" for item in results):
        sys.stdout.write(REGISTER_HINT + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
