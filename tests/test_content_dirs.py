# -*- coding: utf-8 -*-
"""PLANTCONTENTFOLDER 应能列出本机各版本的 CPak Common。"""
import os
import sys
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from plant3d_occ.catalog.content_dirs import list_cpak_common_dirs, to_cpak_common


class TestContentDirs(unittest.TestCase):
    def test_content_root_becomes_cpak_common(self):
        root = r"C:\AutoCAD Plant 3D 2019 Content"
        if not os.path.isdir(os.path.join(root, "CPak Common")):
            self.skipTest("本机没有 2019 Content")
        self.assertTrue(to_cpak_common(root + "\\").lower().endswith("cpak common"))
        self.assertTrue(to_cpak_common(os.path.join(root, "CPak Common")).lower().endswith("cpak common"))

    def test_registry_lists_installed_versions(self):
        found = list_cpak_common_dirs()
        paths = [item["path"].lower() for item in found]
        if not any("2019" in path or "2026" in path for path in paths):
            self.skipTest("注册表里没有 Plant Content")
        self.assertEqual(len(paths), len(set(paths)))
        for item in found:
            self.assertTrue(os.path.isdir(item["path"]), item["path"])
            self.assertIn("cpak common", item["path"].lower())


if __name__ == "__main__":
    unittest.main()
