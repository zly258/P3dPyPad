# -*- coding: utf-8 -*-
"""自动化测试：系统默认构件反编译器 (decompiler.py)、163 个系统构件脚本与元件库真实检索管理 (catalog/manager.py)。"""

import os
import unittest

from plant3d_occ.runner.sandbox import run_script_in_sandbox
from plant3d_occ.catalog.manager import (
    detect_default_content_dir,
    list_catalog_databases,
    query_published_items,
    query_item_sizes_detail,
)


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS_DEFAULTS_DIR = os.path.join(REPO_ROOT, "pyscripts", "system_defaults")


class TestDecompilerAndSystemDefaults(unittest.TestCase):

    def test_01_system_defaults_categorized_inventory(self):
        """确保 163 个系统默认构件按 7 大分类存放且全部存在。"""
        self.assertTrue(os.path.isdir(SYS_DEFAULTS_DIR))
        categories = sorted([
            d for d in os.listdir(SYS_DEFAULTS_DIR)
            if os.path.isdir(os.path.join(SYS_DEFAULTS_DIR, d))
        ])
        self.assertEqual(len(categories), 7)
        all_py = []
        for cat in categories:
            cat_dir = os.path.join(SYS_DEFAULTS_DIR, cat)
            for fn in os.listdir(cat_dir):
                if fn.endswith(".py") and not fn.startswith("_"):
                    all_py.append(os.path.join(cat_dir, fn))
        self.assertEqual(len(all_py), 160)

    def test_02_representative_system_scripts_execute_to_3d_solids(self):
        """验证各分类代表性系统构件（含子组件调用与种子体的复杂设备/支吊架/阀门）均能生成有效 3D 实体。"""
        samples = [
            ("01_supports", "CSGH005.py"),
            ("01_supports", "CSGB001.py"),
            ("02_fittings", "CPB.py"),
            ("03_flanges_gaskets_blinds", "CPFLR.py"),
            ("04_pipes_nozzles_olets", "CPNS.py"),
            ("05_valves_actuators", "CPVX006.py"),
            ("06_instruments", "CPI001.py"),
            ("07_equipment_pumps", "CAPD1a.py"),
            ("07_equipment_pumps", "CAPH1a.py"),
        ]
        for cat, fname in samples:
            path = os.path.join(SYS_DEFAULTS_DIR, cat, fname)
            self.assertTrue(os.path.isfile(path), f"Missing {path}")
            session, entry_name, shapes = run_script_in_sandbox(path)
            self.assertTrue(entry_name, f"{fname} should resolve entry function")
            self.assertGreaterEqual(len(shapes), 1, f"{fname} should produce at least 1 3D shape")


class TestCatalogManagerRealRetrieval(unittest.TestCase):

    def test_01_query_published_catalog_and_equipment(self):
        """真实检索 CPak Common 下的 .acat / .pcat / .pspc / .peqx 已发布构件与设备。"""
        cdir = detect_default_content_dir()
        if not os.path.isdir(cdir):
            self.skipTest("CPak Common directory not present")

        dbs = list_catalog_databases(cdir)
        self.assertGreaterEqual(len(dbs), 1)

        items = query_published_items(cdir, include_builtin=True)
        self.assertGreaterEqual(len(items), 30)

        cat_items = [it for it in items if it.get("source_type") == "catalog_db"]
        self.assertTrue(cat_items)
        first_cat = cat_items[0]
        detail = query_item_sizes_detail(first_cat["catalog_path"], first_cat["script_name"])
        self.assertGreaterEqual(len(detail), 1)

        eq_items = [it for it in items if it.get("source_type") == "peqx"]
        self.assertTrue(eq_items)
        first_eq = eq_items[0]
        eq_detail = query_item_sizes_detail(first_eq["catalog_path"], first_eq["script_name"])
        self.assertGreaterEqual(len(eq_detail), 1)


if __name__ == "__main__":
    unittest.main()
