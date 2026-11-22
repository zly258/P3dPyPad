# -*- coding: utf-8 -*-
"""AutoCAD Plant 3D 全自动无人值守批量测试与异常分析总调度器 (Unattended Test Runner)。

核心能力：
1. 自动探测当前系统安装的 AutoCAD Plant 3D (2019~2026)；
2. 启动 Win32 模态阻塞弹窗自动拦截看门狗 (ModalWatchdog)，静默放行所有异常、修复与代理弹窗；
3. 自动拉起或连接 AutoCAD Plant 3D 进程并确保插件自启动加载；
4. 自动下发 `PYBATCH_RUN` 进行构件脚本全量建模、着色渲染与单图出图（默认四视图拼图）；
5. 自动捕获每一个失败脚本的完整 Python 异常堆栈、出错文件与具体行号，输出结构化报告；
6. 支持作为独立 CLI 运行，或作为 Python API 供外部 AI Agent / Skill 自动化调用。
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Set

# 将当前脚本目录与工程根目录加入模块搜索路径
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
if CUR_DIR not in sys.path:
    sys.path.insert(0, CUR_DIR)


def find_repo_root() -> str:
    """自底向上动态探寻工程根目录 (包含 plant3d_occ 或 pyscripts 目录)。"""
    cur = os.path.abspath(__file__)
    for _ in range(6):
        cur = os.path.dirname(cur)
        if os.path.isdir(os.path.join(cur, "plant3d_occ")) or os.path.isdir(os.path.join(cur, "pyscripts")):
            return cur
    cwd = os.getcwd()
    if os.path.isdir(os.path.join(cwd, "plant3d_occ")):
        return cwd
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


REPO_ROOT = find_repo_root()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from modal_watchdog import ModalWatchdog
except ImportError:
    try:
        from .modal_watchdog import ModalWatchdog
    except ImportError:
        from tools.autocad_runner.modal_watchdog import ModalWatchdog


def find_autocad_plant3d_exe() -> Optional[str]:
    """探测本机安装的 AutoCAD Plant 3D 主程序路径 (acad.exe)。"""
    env_acad = os.environ.get("CAD_EXE_PATH")
    if env_acad and os.path.isfile(env_acad):
        return env_acad

    candidates = [
        r"C:\Program Files\Autodesk\AutoCAD 2019\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2024\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2023\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2022\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2021\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2020\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2025\acad.exe",
        r"C:\Program Files\Autodesk\AutoCAD 2026\acad.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


def configure_autocad_security_bypass(repo_root: str, verbose: bool = True):
    """在 Windows 注册表中将 AutoCAD 全版本 SECURELOAD 设置为 0，并将插件与工程目录加入 TRUSTEDPATHS。
    
    彻底杜绝启动时弹出「安全性 - 未签名的可执行文件 / 是否加载此插件」的模态阻塞对话框。
    """
    import winreg
    try:
        base_key = r"Software\Autodesk\AutoCAD"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_key) as acad_key:
            num_versions = winreg.QueryInfoKey(acad_key)[0]
            for i in range(num_versions):
                ver_name = winreg.EnumKey(acad_key, i)
                try:
                    ver_path = f"{base_key}\\{ver_name}"
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ver_path) as ver_key:
                        num_prods = winreg.QueryInfoKey(ver_key)[0]
                        for j in range(num_prods):
                            prod_name = winreg.EnumKey(ver_key, j)
                            profiles_path = f"{ver_path}\\{prod_name}\\Profiles"
                            try:
                                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, profiles_path) as prof_root:
                                    num_profs = winreg.QueryInfoKey(prof_root)[0]
                                    for k in range(num_profs):
                                        prof_name = winreg.EnumKey(prof_root, k)
                                        vars_path = f"{profiles_path}\\{prof_name}\\Variables"
                                        try:
                                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, vars_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as vars_key:
                                                # 1. 设置 SECURELOAD = 0 (完全关闭未签名警告)
                                                winreg.SetValueEx(vars_key, "SECURELOAD", 0, winreg.REG_SZ, "0")
                                                # 2. 将插件目录与工程目录加入可信路径 TRUSTEDPATHS
                                                curr_trusted = ""
                                                try:
                                                    curr_trusted, _ = winreg.QueryValueEx(vars_key, "TRUSTEDPATHS")
                                                except FileNotFoundError:
                                                    pass
                                                plugin_bundle = r"C:\ProgramData\Autodesk\ApplicationPlugins\..."
                                                ws_path = f"{repo_root}\\..."
                                                new_parts = [p for p in curr_trusted.split(";") if p.strip()]
                                                changed = False
                                                for p_add in (plugin_bundle, ws_path):
                                                    if p_add not in new_parts:
                                                        new_parts.append(p_add)
                                                        changed = True
                                                if changed:
                                                    new_trusted = ";".join(new_parts)
                                                    winreg.SetValueEx(vars_key, "TRUSTEDPATHS", 0, winreg.REG_SZ, new_trusted)
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                except Exception:
                    pass
        if verbose:
            print("[调度器] 已在 Windows 注册表中配置 AutoCAD 安全信任策略 (SECURELOAD=0，信任 ApplicationPlugins 与工程路径)")
    except Exception as e:
        if verbose:
            print(f"[调度器] 配置注册表安全信任策略时发生异常 (非致命): {e}")


def run_unattended_test(
    scripts_dir: Optional[str] = None,
    output_dir: Optional[str] = None,
    close_after: bool = False,
    timeout_seconds: int = 600,
    show_cad_window: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """执行完整的无人值守 Plant 3D 批量测试流水线。

    返回测试结果字典：
    {
        "ok": bool,
        "total": int,
        "success_count": int,
        "fail_count": int,
        "duration_seconds": float,
        "report_txt": str,
        "report_json": str,
        "failures": list,
        "results": list
    }
    """
    if not scripts_dir:
        def_scripts = os.path.join(REPO_ROOT, "pyscripts", "custom_scripts")
        scripts_dir = def_scripts if os.path.isdir(def_scripts) else os.path.join(REPO_ROOT, "pyscripts")

    scripts_dir = os.path.abspath(scripts_dir)
    if not os.path.isdir(scripts_dir):
        raise FileNotFoundError(f"指定的脚本目录不存在: {scripts_dir}")

    if not output_dir:
        output_dir = os.path.join(REPO_ROOT, "test_output")
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    flag_path = os.path.join(output_dir, "unattended_done.flag")
    json_path = os.path.join(output_dir, "batch_report.json")

    # 清理历史标志文件
    for p in (flag_path, json_path):
        if os.path.isfile(p):
            try:
                os.remove(p)
            except OSError:
                pass

    acad_exe = find_autocad_plant3d_exe()
    if not acad_exe:
        raise RuntimeError("未在当前机器上检测到 AutoCAD Plant 3D 安装 (未找到 acad.exe)")

    if verbose:
        print("=" * 65)
        print("【AutoCAD Plant 3D 无人值守自动化测试流水线】")
        print("=" * 65)
        print(f"• Plant 3D 路径 : {acad_exe}")
        print(f"• 构件脚本目录 : {scripts_dir}")
        print(f"• 出图与报告目录: {output_dir}")
        print(f"• 超时时限     : {timeout_seconds} 秒")
        print(f"• 结束后退出 CAD: {'是' if close_after else '否'}")
        print("-" * 65)

    # 0. 自动配置 AutoCAD 注册表安全绕行，免去未签名 DLL 弹窗阻塞
    configure_autocad_security_bypass(REPO_ROOT, verbose=verbose)

    # 写入共享配置至临时目录，保证 C# 插件无论从 COM 还是脚本启动均能精准读取目录
    import tempfile
    cfg_path = os.path.join(tempfile.gettempdir(), "p3d_batch_cfg.txt")
    with open(cfg_path, "w", encoding="utf-8") as fp:
        fp.write(f"{scripts_dir}\n{output_dir}\n")

    # 1. 生成 AutoCAD 自动化批处理脚本 (.scr)
    scr_path = os.path.join(output_dir, "unattended_batch.scr")
    src_esc = scripts_dir.replace("\\", "/")
    out_esc = output_dir.replace("\\", "/")

    scr_lines = [
        '(vl-load-com)',
        '(setvar "SECURELOAD" 0)',
        '(setvar "FILEDIA" 0)',
        '(setvar "CMDDIA" 0)',
        '(vla-put-graphicswinmodelbackgrndcolor (vla-get-display (vla-get-preferences (vlax-get-acad-object))) 16777215)',
        f'(setenv "P3D_BATCH_SRC" "{src_esc}")',
        f'(setenv "P3D_BATCH_OUT" "{out_esc}")',
        '(command "netload" "C:/ProgramData/Autodesk/ApplicationPlugins/P3dPyPad.bundle/Contents/P3dPyPad.dll")',
        "PYBATCH_RUN",
    ]
    if close_after:
        scr_lines.append('(vla-put-saved (vla-get-activedocument (vlax-get-acad-object)) :vlax-true)')
        scr_lines.append('(vla-quit (vlax-get-acad-object))')

    with open(scr_path, "w", encoding="utf-8") as fp:
        fp.write("\r\n".join(scr_lines) + "\r\n")

    # 2. 启动模态阻塞守护看门狗
    watchdog = ModalWatchdog(verbose=verbose)
    watchdog.start()

    acad_app = None
    launched_proc = None

    try:
        # 3. 尝试通过 COM 获取已运行的 AutoCAD；若未运行则通过 /b 脚本无头拉起
        import win32com.client
        try:
            acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
            if verbose:
                print(f"[调度器] 成功连接至现有的 AutoCAD 进程 (版本: {acad_app.Version})")
        except Exception:
            acad_app = None

        if acad_app is not None:
            try:
                doc = getattr(acad_app, "ActiveDocument", None)
                if doc is None or not getattr(doc, "Name", None):
                    doc = acad_app.Documents.Add()
                if show_cad_window:
                    acad_app.Visible = True
                time.sleep(1.0)
                if verbose:
                    print("[调度器] 正在向运行中的 AutoCAD 下发自动化测试指令...")
                doc.SendCommand("PYBATCH_RUN\n")
            except Exception as e_com:
                if verbose:
                    print(f"[调度器] 现有 AutoCAD COM 通信失败 ({e_com})，回退到重新启动...")
                acad_app = None

        if acad_app is None:
            if verbose:
                print(f"[调度器] 正在通过 AutoCAD 自动化脚本启动 Plant 3D 宿主进程 (执行 /b {os.path.basename(scr_path)})...")
            cmd = [acad_exe, "/product", "PLNT3D", "/b", scr_path]
            cad_env = os.environ.copy()
            cad_env["P3D_BATCH_SRC"] = scripts_dir
            cad_env["P3D_BATCH_OUT"] = output_dir
            launched_proc = subprocess.Popen(cmd, env=cad_env)
            watchdog.add_target_pid(launched_proc.pid)

        # 4. 轮询监控测试完成信号 (unattended_done.flag)
        if verbose:
            print("[调度器] 测试任务进行中，看门狗持续监控模态阻塞弹窗...")

        t_wait_start = time.time()
        completed = False

        while time.time() - t_wait_start < timeout_seconds:
            if os.path.isfile(flag_path):
                completed = True
                break
            if launched_proc and launched_proc.poll() is not None:
                if os.path.isfile(flag_path):
                    completed = True
                break
            time.sleep(1.0)

        if not completed:
            raise TimeoutError(f"批量测试执行超时 (已耗时 {timeout_seconds} 秒仍未收到完成标志)")

        # 5. 解析测试产物与错误报告
        report_data = {}
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as fp:
                report_data = json.load(fp)

        # 打印清晰的终端控制台分析
        total = report_data.get("total", 0)
        success_cnt = report_data.get("success", 0)
        fail_cnt = report_data.get("failed", 0)
        duration_s = report_data.get("duration_seconds", 0.0)
        failures = [r for r in report_data.get("results", []) if not r.get("success")]

        if verbose:
            print("\n" + "=" * 65)
            print("【AutoCAD Plant 3D 无人值守测试执行结果分析】")
            print("=" * 65)
            print(f"• 构件脚本总数 : {total}")
            print(f"• 建模成功数   : {success_cnt}")
            print(f"• 建模失败数   : {fail_cnt}")
            print(f"• 总执行耗时   : {duration_s:.1f} 秒")
            print(f"• 结构化报告   : {json_path}")

            if fail_cnt > 0:
                print("\n" + "-" * 65)
                print(f"【失败构件明细与异常原因诊断 (共 {fail_cnt} 项)】")
                print("-" * 65)
                for f_item in failures:
                    s_name = f_item.get("script_name")
                    err = f_item.get("error", "").strip()
                    first_err_line = err.split("\n")[0] if err else "未知错误"
                    print(f"❌ [{s_name}]")
                    print(f"   原因: {first_err_line}")
                    # 打印真实异常关键行
                    for line in err.split("\n"):
                        if any(k in line for k in ("Error:", "Exception:", "File \"", "line ")):
                            print(f"   > {line.strip()}")
                    print()
            else:
                print("\n🎉 恭喜！当前目录下全部构件均 100% 通过 Plant 3D 真实建模与单图出图！")

        return {
            "ok": fail_cnt == 0,
            "total": total,
            "success_count": success_cnt,
            "fail_count": fail_cnt,
            "duration_seconds": duration_s,
            "report_json": json_path,
            "failures": failures,
            "results": report_data.get("results", []),
        }

    finally:
        # 停止弹窗看门狗
        watchdog.stop()

        if close_after:
            if verbose:
                print("[调度器] 正在安全退出 AutoCAD Plant 3D 进程...")
            try:
                import win32com.client
                app = acad_app
                if not app:
                    try:
                        app = win32com.client.GetActiveObject("AutoCAD.Application")
                    except Exception:
                        pass
                if app:
                    try:
                        app.ActiveDocument.Saved = True
                    except Exception:
                        pass
                    app.Quit()
            except Exception:
                pass

            if launched_proc and launched_proc.poll() is None:
                try:
                    launched_proc.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    if verbose:
                        print("[调度器] AutoCAD 未在预定时限内退出，执行终止放行...")
                    launched_proc.terminate()
                    try:
                        launched_proc.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        launched_proc.kill()


def main():
    parser = argparse.ArgumentParser(description="AutoCAD Plant 3D Unattended Batch Runner")
    parser.add_argument("--scripts-dir", "-s", default="", help="待测试脚本根目录")
    parser.add_argument("--output-dir", "-o", default="", help="批量测试截图与测试报告输出目录")
    parser.add_argument("--close-after", action="store_true", help="测试完成后自动关闭 AutoCAD")
    parser.add_argument("--timeout", type=int, default=600, help="总体超时时间 (秒)")
    args = parser.parse_args()

    try:
        res = run_unattended_test(
            scripts_dir=args.scripts_dir,
            output_dir=args.output_dir,
            close_after=args.close_after,
            timeout_seconds=args.timeout,
        )
        sys.exit(0 if res.get("ok") else 1)
    except Exception as exc:
        print(f"\n[错误] 无人值守测试执行失败: {exc}")
        sys.exit(2)


if __name__ == "__main__":
    main()
