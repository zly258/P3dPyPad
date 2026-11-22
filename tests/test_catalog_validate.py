# -*- coding: utf-8 -*-
"""发布前校验与设备打包的测试。

校验部分只用 OCC 沙箱，不需要 AutoCAD；设备打包是纯 zip/XML，可离线断言。
"""

import io
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import test_catalog_publish as helper
from plant3d_occ.catalog import equipment, validate
from plant3d_occ.catalog.model import inspect_script
from plant3d_occ.catalog.publish import publish_scripts

SCRIPTS_CUSTOM = os.path.join(pkg_root, "pyscripts", "custom_scripts")
SCRIPTS = SCRIPTS_CUSTOM if os.path.isdir(SCRIPTS_CUSTOM) else os.path.join(pkg_root, "pyscripts")
GATE = os.path.join(SCRIPTS, "05_supports", "SUPPORT_BEAM_BOLTED_HANGER.py")
LB = os.path.join(SCRIPTS, "05_supports", "SUPPORT_PIPE_CLAMP.py")
VALVE = os.path.join(SCRIPTS, "03_valves", "VALVE_GATE.py")
VESSEL = os.path.join(SCRIPTS, "06_equipment", "EQUIPMENT_VERTICAL_VESSEL.py")

# 两块互不相连的方块：用来验证"多实体"能被抓出来
SPLIT_SCRIPT = '''# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.custom import *

@activate(Group="Support", TooltipShort="断开测试", LengthUnit="mm", Ports=1)
@param(D=LENGTH, TooltipShort="外径")
def SPLIT_BODY(s, D=100.0, **kw):
    a = BOX(s, L=50.0, W=50.0, H=50.0).translate((0.0, 0.0, -500.0))
    b = BOX(s, L=50.0, W=50.0, H=50.0).translate((0.0, 0.0, 500.0))
    a.uniteWith(b)
    b.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
'''

# 端口写到了模型外面（典型的"把截面中心当基准"错法）
PORT_FAR_SCRIPT = '''# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.custom import *

@activate(Group="Valve", TooltipShort="端口跑偏测试", LengthUnit="mm", Ports=2)
@param(D=LENGTH, TooltipShort="外径")
def PORT_FAR(s, D=100.0, **kw):
    b = CYLINDER(s, R=D / 2.0, H=200.0, O=0.0).rotateY(90.0)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((5000.0, 0, 0), (1, 0, 0))
'''


def write_script(folder, name, source):
    """写一份测试脚本 + 同名预设表（进元件库要求两者齐全）。"""
    script = os.path.join(folder, name + ".py")
    io.open(script, "w", encoding="utf-8").write(source)
    io.open(os.path.join(folder, name + ".csv"), "w", encoding="utf-8").write(
        u"规格名,D\nrow1,100.0\n")
    return script


class TestValidation(unittest.TestCase):

    def test_real_scripts_pass(self):
        for path in (GATE, LB, VALVE, VESSEL):
            result = validate.validate_script(path)
            self.assertTrue(result["ok"], os.path.basename(path) + " 应通过：" + str(result["issues"]))
            self.assertEqual(result["solids"], 1)
            self.assertGreaterEqual(result["ports"], 1)

    def test_disconnected_bodies_are_rejected(self):
        tmp = tempfile.mkdtemp(prefix="val_")
        try:
            path = write_script(tmp, "SPLIT_BODY", SPLIT_SCRIPT)
            result = validate.validate_script(path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["solids"], 2)
            self.assertTrue(any("不相连" in issue for issue in result["issues"]),
                            result["issues"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_port_outside_model_is_rejected(self):
        tmp = tempfile.mkdtemp(prefix="val_")
        try:
            path = write_script(tmp, "PORT_FAR", PORT_FAR_SCRIPT)
            result = validate.validate_script(path)
            self.assertFalse(result["ok"])
            self.assertTrue(any("之外" in issue for issue in result["issues"]), result["issues"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_support_ports_are_not_required_to_be_inside_steel(self):
        """支吊架端口在管道中心线上，本来就落在型钢外面，不能算错。"""
        result = validate.validate_script(LB)
        self.assertTrue(result["ok"])
        self.assertFalse(any("之外" in issue for issue in result["issues"]))

    def test_unpublishable_group_is_reported(self):
        """P3D_ 前缀的基准脚本不进元件库，发布时必须报"不可发布"。"""
        tmp = tempfile.mkdtemp(prefix="bench_")
        try:
            bench = os.path.join(tmp, "P3D_BENCH.py")
            io.open(bench, "w", encoding="utf-8").write(
                u"# -*- coding: utf-8 -*-\n"
                u"from varmain.primitiv import *\n"
                u"from varmain.custom import *\n\n"
                u"@activate(Group=\"Support\", TooltipShort=\"bench\", LengthUnit=\"mm\", Ports=1)\n"
                u"def P3D_BENCH(s, **kw):\n"
                u"    BOX(s, L=100.0, W=100.0, H=100.0)\n"
                u"    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))\n")
            result = validate.validate_script(bench)
            self.assertFalse(result["ok"])
            self.assertTrue(any("不可发布" in issue for issue in result["issues"]))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestEquipmentPackaging(unittest.TestCase):

    def test_parse_script_reads_groups_and_params(self):
        info = equipment.parse_script(VESSEL)
        self.assertEqual(info["name"], "EQUIPMENT_VERTICAL_VESSEL")
        self.assertEqual(info["group"], "Equipment")
        self.assertEqual(info["ports"], 3)
        self.assertEqual(info["length_unit"], "mm")
        self.assertTrue(info["tooltip"])

        main = info["groups"][0]
        names = [item[0] for item in main[1]]
        self.assertIn("D_BODY", names)
        # 默认值要从 def 签名里取到，而不是写死的 0
        defaults = dict((n, d) for n, _t, d, _tip in main[1])
        self.assertEqual(defaults["D_BODY"], "800")

    def test_build_peqx_produces_valid_package(self):
        tmp = tempfile.mkdtemp(prefix="peqx_")
        try:
            path = os.path.join(tmp, "VESSEL.peqx")
            built = equipment.build_peqx(VESSEL, path)
            self.assertTrue(os.path.isfile(path))

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                self.assertIn("[Content_Types].xml", names)
                self.assertIn("content/EquipmentType.xml", names)
                self.assertIn("_rels/.rels", names)

                xml = archive.read("content/EquipmentType.xml").decode("utf-8")
                self.assertIn('Name="%s"' % built["name"], xml)
                self.assertIn('Type="C"', xml)
                self.assertIn('SubType="V"', xml)
                self.assertIn("PartType=", xml)
                self.assertIn("GUID=\"{", xml)
                self.assertIn("<Nozzles>", xml)
                self.assertIn(built["info"]["tooltip"], xml)
                # 参数类型映射：LENGTH→d、LENGTH0→d0
                self.assertIn('Name="D_BODY" DefaultValue="800" Type="d"', xml)
                # STRING 参数在 peqx 里没有对应类型，应被跳过
                self.assertNotIn('Name="ID"', xml)

                rels = archive.read("_rels/.rels").decode("utf-8")
                self.assertIn("Plant/Equipment/EquipmentType", rels)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_guid_is_stable_per_script(self):
        info = equipment.parse_script(VESSEL)
        first = equipment.build_equipment_xml(info)
        second = equipment.build_equipment_xml(info)
        self.assertEqual(first, second, "同一脚本每次打包的 GUID 必须一致")
        other = dict(info, name="SOMETHING_ELSE")
        self.assertNotEqual(equipment.build_equipment_xml(other), first)

    def test_equipment_group_is_routed_to_peqx_not_catalog(self):
        job = inspect_script(VESSEL)
        self.assertIsNone(job["skip_reason"])
        self.assertEqual(job["domain"], "equipment")
        self.assertTrue(job["params"])
        self.assertEqual(job["sizes"], [], "设备不靠预设表")


class TestPublishWithValidation(unittest.TestCase):

    def setUp(self):
        if not helper.plant_content_available():
            self.skipTest("本机没有可读的 Plant 3D 内容库，跳过发布测试")
        self.tmp = tempfile.mkdtemp(prefix="pub_")
        self.plant_root, self.content = helper.build_isolated_library(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_equipment_publish_writes_peqx_and_script(self):
        results = publish_scripts([VESSEL], content_dir=self.content, plant_root=self.plant_root,
                                  write_preview=False)
        self.assertEqual(results[0].status, "published", results[0].message)

        peqx = os.path.join(self.content, "equipment", "EQUIPMENT_VERTICAL_VESSEL.peqx")
        self.assertTrue(os.path.isfile(peqx), "设备必须生成 .peqx")
        copied = os.path.join(self.content, "CustomScripts", "EQUIPMENT_VERTICAL_VESSEL.py")
        self.assertTrue(os.path.isfile(copied), "脚本要复制到 CustomScripts")

    def test_broken_script_is_not_published(self):
        broken = write_script(self.tmp, "SPLIT_BODY", SPLIT_SCRIPT)
        results = publish_scripts([broken], content_dir=self.content, plant_root=self.plant_root,
                                  write_preview=False)
        self.assertEqual(results[0].status, "failed")
        self.assertIn("校验不通过", results[0].message)
        self.assertFalse(os.path.isfile(os.path.join(self.content, "CustomScripts", "SPLIT_BODY.py")),
                         "校验没过就不该往库里写任何东西")

    def test_validation_can_be_skipped_explicitly(self):
        broken = write_script(self.tmp, "SPLIT_BODY", SPLIT_SCRIPT)
        results = publish_scripts([broken], content_dir=self.content, plant_root=self.plant_root,
                                  write_preview=False, validate=False)
        self.assertEqual(results[0].status, "published",
                         "显式关掉校验时应照旧发布（并自行承担风险）")


class TestDualCatalogAndDevloop(unittest.TestCase):
    """支吊架要同时写公制与英制两个 .acat；devloop 一轮 = 校验 + 发布。"""

    def setUp(self):
        if not helper.plant_content_available():
            self.skipTest("本机没有可读的 Plant 3D 内容库")
        self.tmp = tempfile.mkdtemp(prefix="dual_")
        self.plant_root, self.content = helper.build_isolated_library(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def _rows(path, stem):
        import sqlite3
        if not os.path.isfile(path):
            return 0
        con = sqlite3.connect(path)
        try:
            return con.execute(
                "SELECT COUNT(*) FROM EngineeringItems WHERE ContentGeometryTemplate LIKE ?",
                ("%" + stem + "%",)).fetchone()[0]
        finally:
            con.close()

    def test_support_goes_into_both_catalogs(self):
        results = publish_scripts([GATE], content_dir=self.content, plant_root=self.plant_root,
                                  write_preview=False)
        self.assertEqual(results[0].status, "published", results[0].message)

        metric = os.path.join(self.content, "SUPPORTS Catalog metric.acat")
        imperial = os.path.join(self.content, "SUPPORTS Catalog.acat")
        self.assertEqual(self._rows(metric, "SUPPORT_BEAM_BOLTED_HANGER"), 5)
        self.assertEqual(self._rows(imperial, "SUPPORT_BEAM_BOLTED_HANGER"), 5,
                         "英制/通用支吊架库也要写一份")

    def test_equipment_peqx_carries_a_preview_image(self):
        results = publish_scripts([VESSEL], content_dir=self.content, plant_root=self.plant_root,
                                  write_preview=True)
        self.assertEqual(results[0].status, "published", results[0].message)

        peqx = os.path.join(self.content, "equipment", "EQUIPMENT_VERTICAL_VESSEL.peqx")
        with zipfile.ZipFile(peqx) as archive:
            previews = [n for n in archive.namelist() if n.startswith("preview/")]
            self.assertTrue(previews, "应带一张 200×200 预览图")
            rels = archive.read("_rels/.rels").decode("utf-8")
            self.assertIn("Plant/Equipment/Preview", rels)
            self.assertIn(previews[0], rels)

    def test_devloop_run_once_validates_then_publishes(self):
        from plant3d_occ import devloop

        ok, summary = devloop.run_once(GATE, content=self.content, plant_root=self.plant_root,
                                       validate=True)
        self.assertTrue(ok, summary)
        self.assertIn("published", summary)

    def test_devloop_dry_run_writes_nothing(self):
        from plant3d_occ import devloop

        before = os.path.isdir(os.path.join(self.content, "SUPPORTS Catalog", "200"))
        ok, summary = devloop.run_once(GATE, content=self.content, plant_root=self.plant_root,
                                       validate=True, dry_run=True)
        self.assertTrue(ok, summary)
        self.assertIn("干跑", summary)
        self.assertEqual(before, os.path.isdir(os.path.join(self.content, "SUPPORTS Catalog", "200")))

    def test_devloop_refuses_broken_script(self):
        from plant3d_occ import devloop

        broken = write_script(self.tmp, "SPLIT_BODY", SPLIT_SCRIPT)
        ok, summary = devloop.run_once(broken, content=self.content, plant_root=self.plant_root,
                                       validate=True)
        self.assertFalse(ok)
        self.assertIn("校验不通过", summary)


if __name__ == "__main__":
    unittest.main()
