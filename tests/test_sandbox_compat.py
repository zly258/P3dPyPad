# -*- coding: utf-8 -*-
"""沙箱兼容性测试：Python 2 脚本头、varmain.divsub 子库、入口函数识别。

这三条都是为了让**未经修改的原厂存量脚本**能直接在离线 PyOCC 里跑起来。
以前这类脚本会在第一行或 import 处就失败。
"""

import os
import sys
import tempfile
import textwrap
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from plant3d_occ.runner.sandbox import execute_script_source, run_script_in_sandbox

# 典型原厂脚本头：Python 2 才有的两行 + divsub 导入
PY2_HEADER = textwrap.dedent(
    """\
    #coding=utf-8
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    from varmain.divsub.cnut6_001 import *
    from varmain.divsub.divutil import *

    from aqa.math import *
    from varmain.primitiv import *
    from varmain.var_basic import *
    from varmain.custom import *
    """
)

BODY = textwrap.dedent(
    """\

    @activate(Group="Support", TooltipShort="门形支撑", Ports="1")
    @group("MainDimensions")
    @param(D=LENGTH, TooltipLong="管径")
    @param(H=LENGTH, TooltipLong="高度")

    def gate_part(s, D=114.3, H=600.0, **kw):
        beam = BOX(s, L=H, W=40.0, H=40.0).translate((0, 0, 0))
        nut = NUT_BOLT_HEAD_6_001(s, W=20.0, H=10.0).translate((H / 2.0, 0, -25.0))
        beam.uniteWith(nut)
        nut.erase()
        s.setPoint((0, 0, 0), (0, 1, 0))
        s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
    """
)


class TestSandboxCompatibility(unittest.TestCase):

    def _write(self, text, name="gate_part.py"):
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".py", prefix=name.replace(".py", "_"), encoding="utf-8", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_python2_header_no_longer_breaks(self):
        """reload(sys) / sys.setdefaultencoding 是 py2 专用，不该让脚本直接崩。"""
        path = self._write(PY2_HEADER + BODY)
        session, entry, shapes = run_script_in_sandbox(path)
        self.assertEqual(entry, "gate_part")
        self.assertTrue(shapes, "应生成实体")
        self.assertGreaterEqual(len(session.ports), 1)

    def test_divsub_imports_resolve(self):
        """varmain.divsub.{divutil,cnut6_001} 必须能 import 到紧固件。"""
        code = PY2_HEADER + textwrap.dedent(
            """\

            @activate(Group="Support", Ports="1")
            def nut_only(s, **kw):
                nut = NUT_BOLT_HEAD_6_001(s, W=20.0, H=10.0)
                s.setPoint((0, 0, 0), (0, 1, 0))
            """
        )
        session, entry, shapes = run_script_in_sandbox(self._write(code))
        self.assertEqual(entry, "nut_only")
        self.assertTrue(shapes)

    def test_entry_found_by_activate_not_filename(self):
        """文件名与函数名不一致时，应靠 @activate 认出入口，而不是猜错。"""
        code = PY2_HEADER + BODY
        path = self._write(code, name="totally_different_name.py")
        session, entry, shapes = run_script_in_sandbox(path)
        self.assertEqual(entry, "gate_part",
                         "应通过 @activate 找到入口，而不是按文件名/大写字母猜")

    def test_helper_function_is_not_mistaken_for_entry(self):
        """脚本里既有入口又有子函数时，不能被大写子函数抢走。"""
        code = PY2_HEADER + BODY + textwrap.dedent(
            """\

            def ZZZ_Helper(s):
                return None
            """
        )
        session, entry, shapes = run_script_in_sandbox(self._write(code))
        self.assertEqual(entry, "gate_part")

    def test_execute_script_source_is_the_shared_entry(self):
        """GUI 与文件沙箱共用这一个函数，必须自己就把 py2 头与入口都处理好。"""
        globals_, entry = execute_script_source(
            PY2_HEADER + BODY, filename_hint="不相干的名字", origin="<test>")
        self.assertEqual(entry, "gate_part")
        self.assertTrue(callable(globals_["gate_part"]))
        self.assertIn("NUT_BOLT_HEAD_6_001", globals_)

    def test_execute_script_source_reports_no_entry(self):
        _globals, entry = execute_script_source("x = 1", origin="<test>")
        self.assertIsNone(entry)

    def test_divsub_primitives_build_valid_solids(self):
        """紧固件子库本身要能产出有效实体，而不是空壳。"""
        from OCC.Core.TopExp import TopExp_Explorer
        from OCC.Core.TopAbs import TopAbs_SOLID
        from plant3d_occ.primitives.divsub import (
            NUT_BOLT_HEAD_6_001, CNUT6_001, CBOLT6_001, CBOLT_001)
        from plant3d_occ.renderer.mesher import extract_mesh_and_bounds

        cases = [
            (NUT_BOLT_HEAD_6_001, dict(W=20.0, H=10.0)),
            (CNUT6_001, dict(D=12.0)),
            (CBOLT6_001, dict(D=12.0, L=40.0)),
            (CBOLT_001, dict(D=12.0, L=40.0)),
        ]
        for factory, kwargs in cases:
            body = factory(None, **kwargs)
            count = 0
            explorer = TopExp_Explorer(body.shape, TopAbs_SOLID)
            while explorer.More():
                count += 1
                explorer.Next()
            self.assertEqual(count, 1, "%s 应产出单一实体" % factory.__name__)

            triangles, bounds = extract_mesh_and_bounds([body])
            self.assertGreaterEqual(len(triangles), 20, "%s 面片过少" % factory.__name__)
            self.assertLess(bounds[0], bounds[3], "%s 包围盒无效" % factory.__name__)

    def test_bolt_axis_follows_x_and_starts_at_origin(self):
        """文档约定：紧固件沿 +X 且占据 [0, H]。"""
        from plant3d_occ.primitives.divsub import NUT_BOLT_HEAD_6_001
        from plant3d_occ.renderer.mesher import extract_mesh_and_bounds

        body = NUT_BOLT_HEAD_6_001(None, W=20.0, H=10.0)
        _triangles, (xmin, _ymin, _zmin, xmax, _ymax, _zmax) = extract_mesh_and_bounds([body])
        self.assertAlmostEqual(xmin, 0.0, delta=0.5)
        self.assertAlmostEqual(xmax, 10.0, delta=0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
