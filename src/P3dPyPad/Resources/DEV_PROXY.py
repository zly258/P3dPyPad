# -*- coding: utf-8 -*-
#coding=utf-8
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass
# Fixed shell. The pad writes a complete script to dev_core.pyinc and this
# function executes it. REV exists only to bust the block cache.
from aqa.math import *
from varmain.primitiv import *
from varmain.custom import *
import os
import traceback


class _SafeSessionProxy(object):
    """透明代理会话对象，拦截对 setLinearDimension 的多余或关键字参数调用，防止 C++ 底层报 takes no keyword arguments。"""
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        val = getattr(self._target, name)
        if name == "setLinearDimension" and callable(val):
            def _safe_set_linear_dim(*args, **kwargs):
                try:
                    return val(*args[:3])
                except Exception:
                    pass
            return _safe_set_linear_dim
        return val

@activate(Group="Support", TooltipShort="Dev HotReload Proxy", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(REV=LENGTH0, TooltipShort="Reload counter. Do not use in geometry.")
def DEV_PROXY(s, REV=0.0, **kw):
    here = os.path.dirname(os.path.abspath(__file__))
    core_path = os.path.join(here, "dev_core.pyinc")
    log_path = os.path.join(here, "dev_reload.log")

    def _log(text):
        try:
            f = open(log_path, "wb")
            try:
                if isinstance(text, unicode):
                    data = text.encode("utf-8")
                else:
                    data = text
                f.write(data)
            finally:
                f.close()
        except Exception:
            pass
        try:
            print(text)
        except Exception:
            pass

    try:
        f = open(core_path, "rb")
        try:
            source = f.read()
        finally:
            f.close()
        if source.startswith("\xef\xbb\xbf"):
            source = source[3:]
        code = compile(source, core_path, "exec")
        ctx = globals().copy()
        ctx["__file__"] = core_path
        ctx["__name__"] = "dev_core"
        exec code in ctx
        fn = ctx.get("ACP_DEV_BUILD")
        if fn is None:
            raise RuntimeError("dev_core.pyinc has no ACP_DEV_BUILD")
        fn(s)
        _log("OK mtime=%s REV=%s %s" % (os.path.getmtime(core_path), REV, core_path))
    except Exception:
        err = traceback.format_exc()
        _log(err)
        raise
