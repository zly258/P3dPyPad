# -*- coding: utf-8 -*-
"""固定库名不能覆盖，自建名称可以。"""
import os
import sys
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from plant3d_occ.catalog.destinations import (
    catalog_filename,
    locked_catalog_reason,
    locked_spec_reason,
    spec_filename,
)
from plant3d_occ.catalog.publish import _support_spec_override


class TestDestinations(unittest.TestCase):
    def test_locked_names_are_recognized(self):
        self.assertIn("PipeSupportsSpec", locked_spec_reason("PipeSupportsSpec.pspc"))
        self.assertIn("NOZZLE", locked_catalog_reason("NOZZLE Catalog.acat"))
        self.assertIn("PlaceHolder", locked_spec_reason("PlaceHolder Metric.pspc"))
        self.assertEqual(locked_spec_reason("JC-E1-10-H.pspc"), "")
        self.assertEqual(locked_catalog_reason("ZD Piping.pcat"), "")

    def test_custom_names_pass_and_locked_names_fail(self):
        filename, stem = catalog_filename("ZD Piping")
        self.assertEqual(filename, "ZD Piping.pcat")
        self.assertEqual(stem, "ZD Piping")
        filename, stem = spec_filename("JC-E1-10-H.pspc")
        self.assertEqual((filename, stem), ("JC-E1-10-H.pspc", "JC-E1-10-H"))
        filename, stem = spec_filename("PipeSupports")
        self.assertEqual((filename, stem), ("PipeSupports.pspc", "PipeSupports"))
        with self.assertRaises(ValueError):
            catalog_filename("NOZZLE Catalog")
        with self.assertRaises(ValueError):
            spec_filename("PipeSupportsSpec")
        with self.assertRaises(ValueError):
            catalog_filename("bad/name")

    def test_support_spec_override_is_not_configurable(self):
        self.assertIsNone(_support_spec_override())


if __name__ == "__main__":
    unittest.main()
