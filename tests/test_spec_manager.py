# -*- coding: utf-8 -*-
"""自动化测试：AutoCAD Plant 3D 项目目录解析、等级库生成、构件添加到等级库与外部编辑器探测。"""

import os
import shutil
import sqlite3
import tempfile
import unittest
import zipfile

from plant3d_occ.catalog.manager import (
    add_catalog_item_to_spec,
    create_project_spec,
    detect_specs_editor_path,
    list_project_specs,
    query_item_spec_membership,
    remove_item_from_spec,
    resolve_project_and_spec_dir,
)


class TestProjectSpecManager(unittest.TestCase):

    def test_01_resolve_project_and_spec_dir(self):
        """验证输入项目根目录或等级库工作表时能准确推导配对路径。"""
        # 1. 真实存在的中文版 Plant 3D 项目目录
        proj_root = r"D:\zTEMP\Project 1"
        if os.path.isdir(proj_root):
            p_dir, ps_dir = resolve_project_and_spec_dir(proj_root)
            self.assertEqual(os.path.normpath(p_dir).lower(), os.path.normpath(proj_root).lower())
            self.assertTrue(os.path.basename(ps_dir) in ("等级库工作表", "Spec Sheets"))

            # 直接输入 等级库工作表 子目录
            p_dir2, ps_dir2 = resolve_project_and_spec_dir(ps_dir)
            self.assertEqual(os.path.normpath(p_dir2).lower(), os.path.normpath(proj_root).lower())
            self.assertEqual(os.path.normpath(ps_dir2).lower(), os.path.normpath(ps_dir).lower())

        # 2. 模拟英文版 Spec Sheets 项目结构
        with tempfile.TemporaryDirectory() as tmp:
            spec_sheets = os.path.join(tmp, "Spec Sheets")
            os.makedirs(spec_sheets)
            p_dir, ps_dir = resolve_project_and_spec_dir(tmp)
            self.assertEqual(os.path.normpath(p_dir), os.path.normpath(tmp))
            self.assertEqual(os.path.normpath(ps_dir), os.path.normpath(spec_sheets))

            # 逆向：输入 Spec Sheets
            p_dir2, ps_dir2 = resolve_project_and_spec_dir(spec_sheets)
            self.assertEqual(os.path.normpath(p_dir2), os.path.normpath(tmp))
            self.assertEqual(os.path.normpath(ps_dir2), os.path.normpath(spec_sheets))

    def test_02_detect_specs_editor_path(self):
        """验证能准确探测到本机安装的 SpecsAndCatalogsEditor.exe 路径。"""
        path = detect_specs_editor_path()
        if os.path.isfile(r"C:\Program Files\Autodesk\AutoCAD 2019\PLNT3D\SpecsAndCatalogsEditor.exe"):
            self.assertTrue(os.path.isfile(path))
            self.assertTrue(path.lower().endswith("specsandcatalogseditor.exe"))

    def test_03_list_project_specs(self):
        """验证能够正确列出项目目录下的等级库并解析零件数和配对 pspx。"""
        proj_spec_dir = r"D:\zTEMP\Project 1\等级库工作表"
        if not os.path.isdir(proj_spec_dir):
            self.skipTest("未检测到本地项目等级库工作表，跳过真实扫描测试")

        specs = list_project_specs(proj_spec_dir)
        self.assertGreaterEqual(len(specs), 5)
        cs150 = next((s for s in specs if s["file"].lower() == "cs150.pspc"), None)
        self.assertIsNotNone(cs150)
        self.assertTrue(cs150["has_pspx"])
        self.assertGreater(cs150["part_count"], 0)

    def test_04_create_and_manage_spec_in_isolated_dir(self):
        """在完全隔离的临时目录中测试新建等级库 (.pspc + .pspx) 及元数据初始化。"""
        donor_source = r"D:\zTEMP\Project 1\等级库工作表\CS150.pspc"
        if not os.path.isfile(donor_source):
            self.skipTest("缺少基准等级库 CS150.pspc，跳过新建等级库测试")

        with tempfile.TemporaryDirectory() as tmp_spec_dir:
            res = create_project_spec(
                tmp_spec_dir,
                "CUSTOM_SPEC_01",
                donor_spec_path=donor_source,
                description="Custom Petrochem Spec 01",
                include_pipe=False,
            )
            self.assertTrue(res["ok"])
            self.assertEqual(res["spec_file"], "CUSTOM_SPEC_01.pspc")
            self.assertTrue(os.path.isfile(res["spec_path"]))
            self.assertTrue(os.path.isfile(res["pspx_path"]))

            # 验证新生成的 .pspc 是一个纯净的空等级库且描述正确
            con = sqlite3.connect(res["spec_path"])
            cur = con.cursor()
            cur.execute("SELECT Name, Description, Type FROM RepositoryDescriptor LIMIT 1")
            name, desc, rtype = cur.fetchone()
            self.assertEqual(name, "CUSTOM_SPEC_01")
            self.assertEqual(desc, "Custom Petrochem Spec 01")
            self.assertEqual(rtype, "Autodesk.ProcessPower.PartsRepository.Specification.PipePartSpecification")

            cur.execute("SELECT COUNT(*) FROM EngineeringItems")
            count = cur.fetchone()[0]
            self.assertEqual(count, 0, "新建的等级库应当清空旧零件规格行")
            con.close()

            # 验证配套的 .pspx 内部指向正确的 .pspc
            with zipfile.ZipFile(res["pspx_path"], "r") as zf:
                rels_content = None
                for n in zf.namelist():
                    if n.replace("\\", "/").endswith("_rels/.rels"):
                        rels_content = zf.read(n).decode("utf-8")
                        break
                self.assertIsNotNone(rels_content)
                self.assertIn('Target="CUSTOM_SPEC_01.pspc"', rels_content)

    def test_05_add_and_remove_item_from_spec(self):
        """测试将构件从源元件库添加到等级库，验证多端口关系、CatalogId、规格行，并测试移除。"""
        donor_source = r"D:\zTEMP\Project 1\等级库工作表\CS150.pspc"
        cat_source = r"D:\zTEMP\Project 1\等级库工作表\CS150.pspc"  # CS150 自身也是一个包含丰富零件的 PartsRepository
        if not os.path.isfile(donor_source):
            self.skipTest("缺少 CS150.pspc，跳过添加/移除测试")

        # 找到一个在 CS150 中存在的构件模板名
        con_src = sqlite3.connect(cat_source)
        cur_src = con_src.cursor()
        cur_src.execute(
            "SELECT ContentGeometryTemplate, COUNT(*) FROM EngineeringItems "
            "WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != '' "
            "GROUP BY ContentGeometryTemplate ORDER BY COUNT(*) DESC LIMIT 1"
        )
        row = cur_src.fetchone()
        con_src.close()
        if not row:
            self.skipTest("源库中无有效构件")

        sample_template, expected_count = row[0], row[1]

        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. 创建干净的目标等级库
            spec_info = create_project_spec(tmp_dir, "MY_TARGET_SPEC", donor_spec_path=donor_source)
            target_pspc = spec_info["spec_path"]

            # 2. 将构件添加到目标等级库
            res_add = add_catalog_item_to_spec(cat_source, target_pspc, sample_template)
            self.assertTrue(res_add["ok"])
            self.assertEqual(res_add["added_rows"], expected_count)

            # 3. 验证目标等级库中写入的数据完整性 (包含 CatalogId, PartFamilyId, 多端口)
            con_tgt = sqlite3.connect(target_pspc)
            cur_tgt = con_tgt.cursor()
            cur_tgt.execute(
                "SELECT COUNT(*), MIN(CatalogId), MIN(PartFamilyId) FROM EngineeringItems "
                "WHERE UPPER(ContentGeometryTemplate)=UPPER(?)",
                (sample_template,),
            )
            cnt, cat_id, fam_id = cur_tgt.fetchone()
            self.assertEqual(cnt, expected_count)
            self.assertTrue(bool(cat_id))
            self.assertTrue(bool(fam_id))

            # Plant 端口约定：没有 S0；S1 在零件行上，PartPort 只存 S2 及以后。
            cur_tgt.execute(
                "SELECT PortName, ConnectionPortCount FROM EngineeringItems "
                "WHERE UPPER(ContentGeometryTemplate)=UPPER(?)",
                (sample_template,),
            )
            declared = cur_tgt.fetchall()
            self.assertTrue(declared)
            self.assertTrue(all((row[0] or "S1") == "S1" for row in declared))
            cur_tgt.execute(
                "SELECT pp.Name, COUNT(*) FROM PartPort pp "
                "JOIN EngineeringItems e ON e.PnPID=pp.Part "
                "WHERE UPPER(e.ContentGeometryTemplate)=UPPER(?) GROUP BY pp.Name",
                (sample_template,),
            )
            names = {row[0]: row[1] for row in cur_tgt.fetchall()}
            self.assertNotIn("S0", names)
            self.assertNotIn("S1", names)
            con_tgt.close()

            # 4. 验证成员资格查询
            memberships = query_item_spec_membership(tmp_dir, sample_template)
            self.assertEqual(len(memberships), 1)
            self.assertEqual(memberships[0]["file"], "MY_TARGET_SPEC.pspc")
            self.assertEqual(memberships[0]["count"], expected_count)

            # 5. 验证从目标等级库移除
            res_rm = remove_item_from_spec(target_pspc, sample_template)
            self.assertTrue(res_rm["ok"])
            self.assertEqual(res_rm["removed_rows"], expected_count)

            # 验证已清空
            memberships_after = query_item_spec_membership(tmp_dir, sample_template)
            self.assertEqual(len(memberships_after), 0)


if __name__ == "__main__":
    unittest.main()
