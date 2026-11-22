# -*- coding: utf-8 -*-
"""AutoCAD Plant 3D 模态阻塞弹窗精准拦截与守护看门狗 (Modal Watchdog)。

采用纯 Windows Win32 底层 API (ctypes + user32.dll，零外部依赖)：
1. 实时后台监视 AutoCAD (acad.exe) 进程所弹出的模态阻塞对话框 (#32770)；
2. 严格按已知白名单与精准规则匹配，严防对文件选择、保存、参数设置等正常弹窗的误触误关：
   - 【未签名安全警告】(Security - Unsigned Executable) -> 精准点击「始终加载」或触发 Alt+A / CommandLink-1001；
   - 【.NET 未捕获异常】(Unhandled Exception) -> 精准点击「继续 (C)」保证 CAD 进程不挂起；
   - 【图形修复管理器】(Drawing Recovery Manager) -> 精准点击「关闭 (Close)」；
   - 【代理实体信息】(Proxy Information) -> 精准点击「确定 (OK)」；
   - 【缺失字体样式】(Missing Font / SHX) -> 精准点击「取消 / 忽略」；
   - 【客户错误报告】(CER) -> 精准点击「不发送 / 关闭」。
3. 对所有非明确阻塞场景（如“选择文件夹”、“打开文件”、“另存为”、“选项”、“图层”以及用户自定义窗口）
   实行严格白名单放行，绝对不进行任何点击或按键注入。
"""

import ctypes
import os
import sys
import threading
import time
from ctypes import wintypes
from typing import List, Optional, Set, Tuple

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
BM_CLICK = 0x00F5
WM_COMMAND = 0x0111
WM_KEYDOWN = 0x0100
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_MENU = 0x12  # Alt
VK_A = 0x41     # 'A'
VK_L = 0x4C     # 'L'
KEYEVENTF_KEYUP = 0x0002

# 严禁触碰的白名单关键字（文件对话框、设置面板、用户自定义窗体、主工作区）
WHITELIST_IGNORE_KEYWORDS = [
    "选择", "打开", "浏览", "另存为", "open", "browse", "save as", "save",
    "select folder", "select file", "options", "选项", "图层", "layer",
    "特性", "properties", "p3dpypad", "scriptpad", "batchtest", "about",
    "绘图", "drawing", "dwg", "命令行", "command line", "ribbon", "工作空间",
    "workspace", "自定义", "customize"
]


def _get_window_text(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value


def _get_class_name(hwnd: int) -> str:
    buff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buff, 256)
    return buff.value


def _get_window_pid(hwnd: int) -> int:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def _is_autocad_pid(pid: int) -> bool:
    """检查指定 PID 是否属于 AutoCAD 相关进程 (acad.exe / plnt3d 等)。"""
    if pid <= 0:
        return False
    try:
        h_proc = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h_proc:
            return False
        buff = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(1024)
        if kernel32.QueryFullProcessImageNameW(h_proc, 0, buff, ctypes.byref(size)):
            kernel32.CloseHandle(h_proc)
            img = buff.value.lower()
            return "acad" in img or "plant" in img or "plnt3d" in img
        kernel32.CloseHandle(h_proc)
    except Exception:
        pass
    return False


def _get_child_controls(hwnd: int) -> Tuple[List[Tuple[int, str, int]], List[str]]:
    """枚举子控件，返回 (按钮列表[(hwnd, text, id)], 静态文本内容列表[text])。"""
    buttons = []
    texts = []

    def enum_children_callback(child_hwnd, _lparam):
        c_cls = _get_class_name(child_hwnd)
        t = _get_window_text(child_hwnd).strip()
        if "button" in c_cls.lower():
            b_id = user32.GetDlgCtrlID(child_hwnd)
            buttons.append((child_hwnd, t, b_id))
        elif t and (c_cls in ("Static", "Edit", "DirectUIHWND") or "text" in c_cls.lower()):
            texts.append(t)
        return True

    user32.EnumChildWindows(hwnd, WNDENUMPROC(enum_children_callback), 0)
    return buttons, texts


class ModalWatchdog:
    """AutoCAD 模态弹窗精准监控与拦截守护器。"""

    def __init__(self, target_pids: Optional[Set[int]] = None, poll_interval: float = 0.35, verbose: bool = True):
        self.target_pids = set(target_pids or [])
        self.poll_interval = poll_interval
        self.verbose = verbose
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._handled_windows: Set[int] = set()

    def add_target_pid(self, pid: int):
        self.target_pids.add(pid)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="ModalWatchdogThread", daemon=True)
        self._thread.start()
        if self.verbose:
            print("[看门狗] AutoCAD 模态阻塞弹窗精准拦截守护线程已启动 (严格白名单保护机制已启用)...")

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self.verbose:
            print("[看门狗] 模态弹窗守护线程已安全停止。")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _run_loop(self):
        while not self._stop_event.is_set():
            try:
                self._scan_and_handle_dialogs()
            except Exception:
                pass
            time.sleep(self.poll_interval)

    def _scan_and_handle_dialogs(self):
        candidate_hwnds = []

        def enum_windows_callback(hwnd, _lparam):
            if not user32.IsWindow(hwnd) or not user32.IsWindowVisible(hwnd):
                return True
            cls_name = _get_class_name(hwnd)
            # 仅针对模态对话框类名 #32770
            if cls_name == "#32770":
                w_pid = _get_window_pid(hwnd)
                if not self.target_pids or w_pid in self.target_pids or _is_autocad_pid(w_pid):
                    candidate_hwnds.append((hwnd, cls_name, w_pid))
            return True

        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

        for hwnd, cls_name, w_pid in candidate_hwnds:
            if hwnd in self._handled_windows:
                continue
            title = _get_window_text(hwnd).strip()

            handled = self._try_dismiss_dialog_strictly(hwnd, title)
            if handled:
                self._handled_windows.add(hwnd)

    def _try_dismiss_dialog_strictly(self, hwnd: int, title: str) -> bool:
        """基于严格规则树判别并精准放行已知阻塞弹窗，对未知弹窗一律不触碰。"""
        lower_title = title.lower()

        # 1. 严格白名单过滤：凡命中文件选择、浏览、选项、特性、或用户窗体的，绝对不处理！
        if any(ign in lower_title for ign in WHITELIST_IGNORE_KEYWORDS):
            return False

        buttons, texts = _get_child_controls(hwnd)
        combined_text = (lower_title + " " + " ".join(t.lower() for t in texts)).strip()

        # -------------------------------------------------------------
        # 场景 1：未签名插件安全警告弹窗 (Security - Unsigned Executable)
        # -------------------------------------------------------------
        is_security_dlg = (
            ("安全" in lower_title and "未签名" in lower_title) or
            ("security" in lower_title and "unsigned" in lower_title) or
            ("文件加载" in lower_title and "安全" in lower_title) or
            ("file load" in lower_title and "security" in lower_title) or
            ("可执行文件" in combined_text and ("未签名" in combined_text or "unsigned" in combined_text))
        )
        if is_security_dlg:
            # 1.1 优先寻找 Win32「始终加载」或「加载一次」按钮
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "始终加载" in clean_btn or "always load" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准拦截【未签名安全弹窗】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True

            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "加载一次" in clean_btn or "load once" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准拦截【未签名安全弹窗】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True

            # 1.2 针对 DirectUI TaskDialog：下发 CommandLink-1001 或 Alt+A 始终加载
            user32.SetForegroundWindow(hwnd)
            time.sleep(0.06)
            for cmd_id in (1001, 2001, 101, 6, 1):
                user32.SendMessageW(hwnd, WM_COMMAND, cmd_id, 0)
            if not user32.IsWindowVisible(hwnd):
                if self.verbose:
                    print(f"[看门狗] 精准拦截【DirectUI安全弹窗】: \"{title}\" (已下发 CommandLink-1001 始终加载)")
                return True

            user32.keybd_event(VK_MENU, 0, 0, 0)
            user32.keybd_event(VK_A, 0, 0, 0)
            time.sleep(0.02)
            user32.keybd_event(VK_A, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.08)
            if not user32.IsWindowVisible(hwnd):
                if self.verbose:
                    print(f"[看门狗] 精准拦截【安全弹窗】: \"{title}\" (已触发 Alt+A 始终加载)")
                return True

            return False

        # -------------------------------------------------------------
        # 场景 2：发生未经处理的异常 (.NET Unhandled Exception)
        # -------------------------------------------------------------
        is_exception_dlg = (
            "发生未经处理的异常" in combined_text or
            "unhandled exception" in combined_text or
            "microsoft .net framework" in lower_title or
            ("autocad" in lower_title and any(k in combined_text for k in ("未经处理的异常", "exception has occurred")))
        )
        if is_exception_dlg:
            # 严格寻找「继续 (C)」/ Continue 按钮，严禁点击「退出」或盲点「确定」
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "继续" in clean_btn or "continue" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准拦截【未捕获异常弹窗】: \"{title}\" -> 已自动点击「{b_text}」保证进程不中断")
                    return True
            return False

        # -------------------------------------------------------------
        # 场景 3：图形修复管理器 (Drawing Recovery Manager)
        # -------------------------------------------------------------
        is_recovery_dlg = (
            "图形修复管理器" in lower_title or
            "drawing recovery manager" in lower_title or
            "图形修复" in lower_title
        )
        if is_recovery_dlg:
            # 严格寻找「关闭」按钮
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "关闭" in clean_btn or "close" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准放行【图形修复管理器】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True
            return False

        # -------------------------------------------------------------
        # 场景 4：代理实体信息 (Proxy Information)
        # -------------------------------------------------------------
        is_proxy_dlg = (
            "代理信息" in lower_title or
            "proxy information" in lower_title or
            ("代理对象" in combined_text and "未注册" in combined_text)
        )
        if is_proxy_dlg:
            # 严格寻找「确定」按钮
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if clean_btn in ("确定", "ok", "yes"):
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准放行【代理信息对话框】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True
            return False

        # -------------------------------------------------------------
        # 场景 5：缺失字体 / 指定字形 (Missing SHX Fonts)
        # -------------------------------------------------------------
        is_font_dlg = (
            "指定字形" in lower_title or
            "指定字体" in lower_title or
            "缺失字体" in lower_title or
            "missing shx" in lower_title
        )
        if is_font_dlg:
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "取消" in clean_btn or "cancel" in clean_btn or "忽略" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 精准放行【缺失字体对话框】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True
            return False

        # -------------------------------------------------------------
        # 场景 6：Autodesk 崩溃错误报告 (CER)
        # -------------------------------------------------------------
        is_cer_dlg = (
            "客户错误报告" in lower_title or
            "customer error report" in lower_title or
            "autodesk 错误报告" in lower_title
        )
        if is_cer_dlg:
            for b_hwnd, b_text, b_id in buttons:
                clean_btn = b_text.lower().replace("&", "").strip()
                if "不发送" in clean_btn or "取消" in clean_btn or "关闭" in clean_btn:
                    user32.SendMessageW(b_hwnd, BM_CLICK, 0, 0)
                    if self.verbose:
                        print(f"[看门狗] 静默关闭【CER崩溃报告】: \"{title}\" -> 已自动点击「{b_text}」")
                    return True
            return False

        # 其他任何未知对话框，一律不触碰、不点击、不发送按键！
        return False


if __name__ == "__main__":
    print("正在启动精确模态阻塞监控测试（按 Ctrl+C 退出）...")
    with ModalWatchdog(verbose=True) as wd:
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass
