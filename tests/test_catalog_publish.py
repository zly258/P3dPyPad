# -*- coding: utf-8 -*-
"""元件库发布链路测试（catalog 模块 + 族预览图）。

设计原则：所有写入都发生在本测试自己创建的临时目录里。
只有在能读到本机 Plant 3D 内容库（donor 文件）时才会真的跑发布，
读不到就跳过——绝不向真实的 Plant 库写入任何东西。
"""

import glob
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import script_fixtures
from plant3d_occ.catalog.model import (
    inspect_script,
    iter_scripts,
    needs_dimension_annotation,
    stable_uuid,
)
from plant3d_occ.catalog.publish import publish_scripts
from plant3d_occ.catalog.store import PLANT_CONTENT, preview_paths

SCRIPTS_ROOT = script_fixtures.SCRIPTS_ROOT
HG_SCRIPTS = script_fixtures.hg_scripts()
P3D_SCRIPTS = sorted(glob.glob(os.path.join(SCRIPTS_ROOT, "**", "P3D_*.py"), recursive=True))

# 各域需要的 donor：建一份隔离的内容库要先把它们抄进临时目录。
_DONORS = {
    "plant": [
        (("CPak Common", "SUPPORTS Catalog metric.acat"), ("CPak Common", "SUPPORTS Catalog metric.acat")),
        (("CPak Common", "PipeSupportsSpec.pspc"), ("CPak Common", "PipeSupportsSpec.pspc")),
        (("CPak Common", "PipeSupportsSpec.pspx"), ("CPak Common", "PipeSupportsSpec.pspx")),
    ],
    "content": [
        ("CPak Common", "SUPPORTS Catalog metric.acat"),
        ("CPak Common", "PipeSupportsSpec.pspc"),
        ("CPak Common", "PipeSupportsSpec.pspx"),
    ],
}


def plant_content_available():
    for parts in _DONORS["content"]:
        if not os.path.isfile(os.path.join(PLANT_CONTENT, *parts)):
            return False
    return True


def build_isolated_library(root):
    """在 root 下造一份一次性内容库：plant/ 放 donor，content/ 放待写入的库。"""
    plant_root = os.path.join(root, "plant")
    content_dir = os.path.join(root, "content")
    os.makedirs(content_dir, exist_ok=True)
    for parts in _DONORS["content"]:
        src = os.path.join(PLANT_CONTENT, *parts)
        dst_dir = os.path.join(plant_root, parts[0])
        os.makedirs(dst_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(plant_root, *parts))
        # 支吊架域是 append 模式，目标库必须已存在
        shutil.copy2(src, os.path.join(content_dir, parts[1]))
    return plant_root, content_dir


class TestCatalogModel(unittest.TestCase):

    def test_iter_scripts_skips_dunder_and_pycache(self):
        files = list(iter_scripts(SCRIPTS_ROOT))
        if not files:
            self.skipTest("pyscripts 下没有脚本，跳过遍历测试")
        for path in files:
            self.assertTrue(path.endswith(".py"))
            self.assertNotIn("__pycache__", path)
            self.assertFalse(os.path.basename(path).startswith("_"))

    def test_stable_uuid_is_deterministic(self):
        self.assertEqual(stable_uuid("ZD_101"), stable_uuid("ZD_101"))
        self.assertNotEqual(stable_uuid("ZD_101"), stable_uuid("ZD_102"))

    def test_only_support_and_equipment_need_dimension_annotation(self):
        self.assertTrue(needs_dimension_annotation({"domain": "support"}))
        self.assertTrue(needs_dimension_annotation({"domain": "equipment"}))
        self.assertTrue(needs_dimension_annotation({"group": "Support"}))
        self.assertTrue(needs_dimension_annotation({"group": "Pump"}))
        self.assertFalse(needs_dimension_annotation({"domain": "piping"}))
        self.assertFalse(needs_dimension_annotation({"domain": "instrumentation"}))
        self.assertFalse(needs_dimension_annotation({}))

    def test_dimension_labels_only_use_real_parameters_without_values(self):
        import numpy as np
        from unittest import mock
        from plant3d_occ.catalog.preview import build_3d_dimension_specs

        class FakeSession:
            grips = [{"name": "H=600", "pt1": (0, 0, 0), "pt2": (0, 0, -600)}]
            ports = [{"point": (0, 0, 0), "dir": (1, 0, 0)}]

        bounds = (np.array([-50.0, -50.0, -600.0]), np.array([50.0, 50.0, 0.0]))
        with mock.patch(
            "plant3d_occ.catalog.preview._shapes_bounds",
            return_value=bounds,
        ):
            dims = build_3d_dimension_specs(
                [],
                session=FakeSession(),
                params_meta=["H", "D"],
                call_values={"H": 600.0, "D": 100.0},
            )

        labels = [item["label"] for item in dims]
        self.assertEqual(labels, ["H", "D"])
        for label in labels:
            self.assertNotIn("总长", label)
            self.assertNotIn("总高", label)
            self.assertNotIn("总宽", label)
            self.assertNotIn("=", label)

    def test_inspect_real_support_script(self):
        script = script_fixtures.first_publishable_script(group="Support")
        if not script:
            self.skipTest("没有可发布的支吊架脚本（脚本库已移除）")
        job = inspect_script(script)
        self.assertIsNone(job["skip_reason"], "应可发布: " + str(job["skip_reason"]))
        self.assertEqual(job["group"], "Support")
        self.assertEqual(job["domain"], "support")
        self.assertTrue(job["sizes"], "应从同名 CSV 读出尺寸表")
        self.assertTrue(job["params"], "应解析出 @param 参数")
        self.assertTrue(job["tooltip"], "应解析出 TooltipShort")

    def test_every_hgt_script_is_publishable_or_skipped_with_reason(self):
        """不允许有脚本被静默丢弃：可发布，或给出明确的跳过原因。

        结构钢（Group=Structure）按设计不进管道/支吊架元件库。
        """
        if not HG_SCRIPTS:
            self.skipTest("化工脚本库已移除，跳过批量可发布性检查")
        unexpected = []
        publishable = 0
        for path in HG_SCRIPTS:
            job = inspect_script(path)
            if job["skip_reason"]:
                if job["group"] in ("Structure", "Structural"):
                    continue
                unexpected.append((os.path.basename(path), job["group"], job["skip_reason"]))
            else:
                publishable += 1
        self.assertEqual(unexpected, [], "非结构钢脚本被意外跳过")
        self.assertGreater(publishable, 150, "可发布脚本数异常偏少")

    def test_baseline_script_is_skipped(self):
        if not P3D_SCRIPTS:
            self.skipTest("没有 P3D_ 基准脚本")
        self.assertIsNotNone(inspect_script(P3D_SCRIPTS[0])["skip_reason"])

    def test_script_without_activate_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "no_activate.py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("def make():\n    return 1\n")
            self.assertIsNotNone(inspect_script(path)["skip_reason"])

    def test_script_without_csv_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "lonely.py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    'def make():\n'
                    '    @activate(Group="Support", Ports=1, TooltipShort="测试")\n'
                    '    @param(D=LENGTH, Value=100.0)\n'
                    '    def _body(D):\n'
                    '        return None\n'
                )
            job = inspect_script(path)
            self.assertIsNotNone(job["skip_reason"])
            self.assertIn("CSV", job["skip_reason"])


class TestCatalogPublish(unittest.TestCase):
    """真正跑一次发布，但目标是临时目录里的库副本。"""

    def setUp(self):
        # 发布链路写的是 SUPPORTS 库，脚本必须同属 Support 大类
        self.script = script_fixtures.first_publishable_script(group="Support")
        if not self.script:
            self.skipTest("没有可发布的支吊架脚本（脚本库已移除）")
        if not plant_content_available():
            self.skipTest("本机没有可读的 Plant 3D 内容库，跳过发布测试")
        self.tmp = tempfile.mkdtemp(prefix="p3d_catalog_")
        self.plant_root, self.content_dir = build_isolated_library(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_preview_paths_shape(self):
        paths = preview_paths(self.content_dir, "SUPPORTS Catalog metric.acat",
                              "BasePlate", stable_uuid("x"))
        self.assertEqual(sorted(paths.keys()), [32, 64, 200, 640])
        for size, path in paths.items():
            self.assertIn(os.sep + str(size) + os.sep, path)
            self.assertTrue(path.endswith(".png"))

    def test_publish_writes_catalog_spec_and_script(self):
        script = self.script
        messages = []
        results = publish_scripts([script], content_dir=self.content_dir,
                                  plant_root=self.plant_root, write_preview=False,
                                  on_progress=messages.append)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].status, "published", results[0].message)

        catalog = os.path.join(self.content_dir, "SUPPORTS Catalog metric.acat")
        spec = os.path.join(self.content_dir, "PipeSupportsSpec.pspc")
        self.assertTrue(os.path.exists(catalog), "元件库应被创建")
        self.assertTrue(os.path.exists(spec), "等级库应被创建")

        con = sqlite3.connect(catalog)
        try:
            tables = [row[0] for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            self.assertGreater(len(tables), 0, "元件库应有数据表")
        finally:
            con.close()

        copied = os.path.join(self.content_dir, "CustomScripts", os.path.basename(script))
        self.assertTrue(os.path.exists(copied), "脚本应复制到 CustomScripts")
        self.assertTrue(any("PLANTREGISTERCUSTOMSCRIPTS" in text for text in messages),
                        "发布后应提示执行 PLANTREGISTERCUSTOMSCRIPTS")

    def test_republish_keeps_family_id(self):
        script = self.script
        first = stable_uuid(inspect_script(script)["stem"])
        for _ in range(2):
            results = publish_scripts([script], content_dir=self.content_dir,
                                      plant_root=self.plant_root, write_preview=False)
            self.assertEqual(results[0].status, "published", results[0].message)
        self.assertEqual(first, stable_uuid(inspect_script(script)["stem"]))

    def test_baseline_script_reports_skipped(self):
        if not P3D_SCRIPTS:
            self.skipTest("没有基准脚本")
        results = publish_scripts([P3D_SCRIPTS[0]], content_dir=self.content_dir,
                                  plant_root=self.plant_root, write_preview=False)
        self.assertEqual(results[0].status, "skipped")
        self.assertTrue(results[0].message)


class TestFamilyPreview(unittest.TestCase):
    """族预览图：离屏 OCC 着色+边线抓 640/200/64/32 四档。"""

    @classmethod
    def setUpClass(cls):
        cls.display = None
        cls.reason = ""
        try:
            from plant3d_occ.catalog.preview import open_offscreen_display
            cls.display = open_offscreen_display()
        except Exception as exc:  # 无 GL 的机器上跳过，不算失败
            cls.reason = str(exc)

    @classmethod
    def tearDownClass(cls):
        if cls.display is not None:
            from plant3d_occ.catalog.preview import close_display
            close_display(cls.display)

    def setUp(self):
        if self.display is None:
            self.skipTest("离屏视口不可用: " + self.reason)

    def test_square_crop_centers_part(self):
        from PIL import Image
        from plant3d_occ.catalog.preview import _square_around_part

        image = Image.new("RGB", (400, 300), (255, 255, 255))
        for x in range(20, 120):
            for y in range(30, 130):
                image.putpixel((x, y), (0, 0, 0))
        square = _square_around_part(image)
        self.assertEqual(square.width, square.height, "应裁成正方形")
        mask = square.convert("L").point(lambda pixel: 255 if pixel < 210 else 0)
        self.assertIsNotNone(mask.getbbox(), "裁剪后应仍包含零件像素")

    def test_square_crop_handles_blank_image(self):
        from PIL import Image
        from plant3d_occ.catalog.preview import _square_around_part

        square = _square_around_part(Image.new("RGB", (300, 200), (255, 255, 255)))
        self.assertEqual(square.width, square.height)

    def test_grab_writes_all_sizes(self):
        from PIL import Image
        from plant3d_occ.catalog.preview import grab_family_pngs
        from plant3d_occ.runner.sandbox import run_script_in_sandbox

        script = script_fixtures.first_publishable_script(group="Support")
        if not script:
            self.skipTest("没有可发布脚本（脚本库已移除）")
        job = inspect_script(script)
        if job["skip_reason"] or not job["sizes"]:
            self.skipTest("样板脚本不可发布，跳过预览抓图")

        size = job["sizes"][len(job["sizes"]) // 2]
        _session, _entry, shapes = run_script_in_sandbox(script, size["call"])
        self.assertTrue(shapes, "脚本应生成实体")

        with tempfile.TemporaryDirectory() as tmp:
            paths = preview_paths(tmp, "SUPPORTS Catalog metric.acat",
                                  job["image"], stable_uuid(job["stem"]))
            grab_family_pngs(self.display, shapes, paths)

            for pixels in (640, 200, 64, 32):
                path = paths[pixels]
                self.assertTrue(os.path.isfile(path), "应生成 %dpx 预览" % pixels)
                self.assertGreater(os.path.getsize(path), 100, "预览图不应为空")
                with Image.open(path) as image:
                    self.assertEqual(image.size, (pixels, pixels))
                    self.assertGreater(len(image.convert("RGB").getcolors(100000)), 1,
                                       "预览图是单色，零件没画上")

    def test_grab_rejects_empty_shapes(self):
        from plant3d_occ.catalog.preview import grab_family_pngs

        with tempfile.TemporaryDirectory() as tmp:
            paths = preview_paths(tmp, "x.acat", "img", stable_uuid("x"))
            with self.assertRaises(RuntimeError):
                grab_family_pngs(self.display, [], paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
