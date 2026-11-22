# -*- coding: utf-8 -*-
"""Plant 3D OCC 支吊架全量自动化测试套件 (自定义支吊架 + 标准模板 + 核心 UI 组件)。"""

import os
import sys
import glob
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import script_fixtures
from plant3d_occ.runner.sandbox import run_script_in_sandbox
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Core.TopExp import TopExp_Explorer

class TestSupportsAutomated(unittest.TestCase):

    def _count_solids(self, shapes):
        cnt = 0
        for b in shapes:
            shape = b.shape if hasattr(b, 'shape') else b
            exp = TopExp_Explorer(shape, TopAbs_SOLID)
            while exp.More():
                cnt += 1
                exp.Next()
        return cnt

    def test_01_custom_batch_supports(self):
        """自动化测试：批量自定义支吊架脚本。
        
        验证指标：
        1. 0 脚本报错或崩溃（通过 aqa.math 模拟环境）；
        2. 每个脚本均生成有效 3D 几何实体；
        3. 每个构件均为 100% 单一连通实体（solids == 1，消除浮空/切线分裂错误）；
        4. 正确注册管道端口与拉伸尺寸握点。
        """
        files = script_fixtures.zd_scripts()
        if not files:
            self.skipTest("批量自定义脚本未提供，跳过分册建模测试")
        self.assertGreater(len(files), 50, f"电力脚本数量异常偏少，实际找到 {len(files)}")

        failed = []
        split_solids = []
        missing_ports = []

        for p in files:
            name = os.path.splitext(os.path.basename(p))[0]
            try:
                s, entry, shapes = run_script_in_sandbox(p)
                if not shapes:
                    failed.append((name, "未产生任何 3D 实体"))
                    continue
                cnt = self._count_solids(shapes)
                if cnt != 1 or len(shapes) != 1:
                    split_solids.append((name, len(shapes), cnt))
                if not s.ports:
                    missing_ports.append(name)
            except Exception as e:
                failed.append((name, f"运行时异常: {e}"))

        self.assertEqual(len(failed), 0, f"电力脚本运行失败列表: {failed}")
        self.assertEqual(len(split_solids), 0, f"存在未融合单一实体的构件: {split_solids}")
        self.assertEqual(len(missing_ports), 0, f"缺失端口定义的构件: {missing_ports}")

    def test_02_hgt_21629_chemical_supports(self):
        """自动化测试：化工 HG/T 21629-2021 全类别 265 个参数化管架脚本。
        
        验证指标：
        1. 0 脚本崩溃；
        2. 每个脚本均生成 100% 单一连通拓扑实体；
        3. 严格注册端口与线性标注握点。
        """
        files = script_fixtures.hg_scripts()
        if not files:
            self.skipTest("化工脚本库已移除，跳过分册建模测试")
        self.assertGreater(len(files), 150, f"化工管架脚本数量异常偏少，实际找到 {len(files)}")

        failed = []
        split_solids = []
        missing_ports = []

        for p in files:
            name = os.path.splitext(os.path.basename(p))[0]
            try:
                s, entry, shapes = run_script_in_sandbox(p)
                if not shapes:
                    failed.append((name, "未产生任何 3D 实体"))
                    continue
                cnt = self._count_solids(shapes)
                if cnt != 1 or len(shapes) != 1:
                    split_solids.append((name, len(shapes), cnt))
                if not s.ports:
                    missing_ports.append(name)
            except Exception as e:
                failed.append((name, f"运行时异常: {e}"))

        self.assertEqual(len(failed), 0, f"化工脚本运行失败列表: {failed}")
        self.assertEqual(len(split_solids), 0, f"存在未融合单一实体的管架: {split_solids}")
        self.assertEqual(len(missing_ports), 0, f"缺失端口定义的管架: {missing_ports}")

    def test_03_root_templates(self):
        """自动化测试：pyscripts 根目录工业典范模板构件。"""
        files = script_fixtures.template_scripts()
        if not files:
            self.skipTest("工业模板脚本已移除，跳过模板建模测试")

        failed = []
        for p in sorted(files):
            name = os.path.splitext(os.path.basename(p))[0]
            try:
                s, entry, shapes = run_script_in_sandbox(p)
                if not shapes:
                    failed.append((name, "未产生任何 3D 实体"))
            except Exception as e:
                failed.append((name, str(e)))

        self.assertEqual(len(failed), 0, f"工业模板构件异常: {failed}")

    def test_04_ui_cleanliness_and_widgets(self):
        """自动化测试：UI 去样式后各组件行为与接口完整性。"""
        gui_dir = os.path.join(pkg_root, 'plant3d_occ', 'gui')
        for py_file in glob.glob(os.path.join(gui_dir, '*.py')):
            if os.path.basename(py_file) == 'theme.py':
                continue
            with open(py_file, encoding='utf-8') as f:
                content = f.read()
            self.assertNotIn('.setStyleSheet(', content, f"{os.path.basename(py_file)} 仍含有 setStyleSheet 调用！")
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            self.skipTest("PySide6 未安装（无头环境仅执行静态 UI 样式检查）")

        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        from plant3d_occ.gui.property_grid import PropertyGridWidget
        from plant3d_occ.gui.file_tree import FileTreeWidget

        # 1. 验证 PropertyGridWidget
        grid = PropertyGridWidget()
        test_params = [
            {'name': 'D', 'type': 'LENGTH', 'default': '114.3', 'tooltip': '管外径'},
            {'name': 'H', 'type': 'LENGTH', 'default': '120.0', 'tooltip': '中心高'},
        ]
        grid.load_parameters(test_params)
        vals = grid.get_values()
        self.assertEqual(vals.get('D'), '114.3')
        self.assertEqual(vals.get('H'), '120.0')

        # 别名赋值测试
        grid.set_values({'OD': '168.3', 'SUPPORT_H': '200.0'})
        vals = grid.get_values()
        self.assertEqual(vals.get('D'), '168.3')

        # 还原默认测试
        grid.reset_defaults()
        vals = grid.get_values()
        self.assertEqual(vals.get('D'), '114.3')

        # 2. 验证 FileTreeWidget
        tree = FileTreeWidget()
        tree.load_directory(script_fixtures.SCRIPTS_ROOT)
        if script_fixtures.all_scripts():
            self.assertGreater(tree.tree.topLevelItemCount(), 0,
                               "脚本目录非空时文件树应有条目")

        # 3. 验证无硬编码 setStyleSheet 残留（排除 theme.py 本身）
        gui_dir = os.path.join(pkg_root, 'plant3d_occ', 'gui')
        for py_file in glob.glob(os.path.join(gui_dir, '*.py')):
            if os.path.basename(py_file) == 'theme.py':
                continue
            with open(py_file, encoding='utf-8') as f:
                content = f.read()
            self.assertNotIn('.setStyleSheet(', content, f"{os.path.basename(py_file)} 仍含有 setStyleSheet 调用！")

if __name__ == '__main__':
    unittest.main()
