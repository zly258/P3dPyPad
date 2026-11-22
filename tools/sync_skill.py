# -*- coding: utf-8 -*-
"""Plant 3D Skill 自动化构建、脚本打包与多级分发同步工具 (Skill Packager & Sync Tool)。

功能：
1. 将项目内已验证的工具链 (autocad_runner、occ_verify) 自动打包同步至
   `skills/plant3d-python-cad-generator/scripts/`，保证 Skill 纯自包含 (Self-contained)；
2. 自动同步发布至当前项目 `.zcode/skills/`，使当前项目 ZCode 会话即时识别；
3. 自动同步发布至用户全局 `~/.zcode/skills/` 与 `~/.agents/skills/`，
   使用户在任意文件夹或全新工程均可无缝使用该 Skill。

用法：
    python tools/sync_skill.py
    python tools/sync_skill.py --project-only
    python tools/sync_skill.py --global-only
"""

import argparse
import os
import shutil
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_SOURCE_DIR = os.path.join(REPO_ROOT, "skills", "plant3d-python-cad-generator")


def ensure_skill_scripts_bundle(verbose: bool = True):
    """将项目内的运行与验证工具自动打包到 Skill 自包含目录 (scripts/)。"""
    scripts_dest = os.path.join(SKILL_SOURCE_DIR, "scripts")
    os.makedirs(scripts_dest, exist_ok=True)

    # 1. 写入 scripts/__init__.py
    init_file = os.path.join(scripts_dest, "__init__.py")
    if not os.path.isfile(init_file):
        with open(init_file, "w", encoding="utf-8") as fp:
            fp.write("# -*- coding: utf-8 -*-\n")

    # 2. 需要打包进 Skill 的核心脚本清单
    mappings = [
        (os.path.join(REPO_ROOT, "tools", "autocad_runner", "modal_watchdog.py"), "modal_watchdog.py"),
        (os.path.join(REPO_ROOT, "tools", "autocad_runner", "unattended_runner.py"), "unattended_runner.py"),
        (os.path.join(REPO_ROOT, "tools", "occ_verify", "verify_primitives.py"), "verify_primitives.py"),
        (os.path.join(REPO_ROOT, "tools", "occ_verify", "verify_shapes.py"), "verify_shapes.py"),
    ]

    for src_path, dest_name in mappings:
        if not os.path.isfile(src_path):
            if verbose:
                print(f"[警告] 源文件不存在，跳过: {src_path}")
            continue
        dest_path = os.path.join(scripts_dest, dest_name)
        shutil.copy2(src_path, dest_path)
        if verbose:
            print(f"  • 打包脚本 -> {os.path.relpath(dest_path, REPO_ROOT)}")


def sync_directory(src: str, dst: str, verbose: bool = True):
    """完整镜像同步目录内容。"""
    if not os.path.isdir(src):
        raise FileNotFoundError(f"源目录不存在: {src}")

    os.makedirs(dst, exist_ok=True)

    # 递归拷贝所有文件与子目录（排除 __pycache__）
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        rel_dir = os.path.relpath(root, src)
        target_dir = os.path.join(dst, rel_dir) if rel_dir != "." else dst
        os.makedirs(target_dir, exist_ok=True)

        for fn in files:
            if fn.endswith((".pyc", ".tmp")):
                continue
            s_file = os.path.join(root, fn)
            d_file = os.path.join(target_dir, fn)
            shutil.copy2(s_file, d_file)


def deploy_skill(project_sync: bool = True, global_sync: bool = True, verbose: bool = True):
    """执行多级分发部署。"""
    if verbose:
        print("=" * 65)
        print("【Plant 3D Skill 自动化打包与分发流水线】")
        print("=" * 65)
        print(f"• Skill 源码目录: {SKILL_SOURCE_DIR}")

    # 第一步：打包自包含 scripts
    if verbose:
        print("\n[阶段 1] 正在打包核心执行与守护脚本至 Skill 内部...")
    ensure_skill_scripts_bundle(verbose=verbose)

    # 第二步：同步到当前项目 .zcode/skills/
    if project_sync:
        proj_zcode_skill = os.path.join(REPO_ROOT, ".zcode", "skills", "plant3d-python-cad-generator")
        if verbose:
            print(f"\n[阶段 2] 正在同步至项目级技能目录: {proj_zcode_skill}...")
        sync_directory(SKILL_SOURCE_DIR, proj_zcode_skill, verbose=verbose)
        if verbose:
            print("  ✓ 项目级技能已就绪 (ZCode 当前项目即时可用)")

    # 第三步：同步到全局用户目录 (~/.zcode/skills/ & ~/.agents/skills/)
    if global_sync:
        user_home = os.path.expanduser("~")
        global_targets = [
            os.path.join(user_home, ".zcode", "skills", "plant3d-python-cad-generator"),
            os.path.join(user_home, ".agents", "skills", "plant3d-python-cad-generator"),
        ]
        if verbose:
            print("\n[阶段 3] 正在同步至全局用户技能目录...")
        for g_tgt in global_targets:
            sync_directory(SKILL_SOURCE_DIR, g_tgt, verbose=verbose)
            if verbose:
                print(f"  ✓ 全局技能已就绪: {g_tgt}")

    if verbose:
        print("\n" + "=" * 65)
        print("🎉 Plant 3D 专家技能全量同步完成！")
        print("现在可以在任何 ZCode 对话中通过输入 /plant3d-python-cad-generator 直接调用。")
        print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Plant 3D Skill Packager and Sync Tool")
    parser.add_argument("--project-only", action="store_true", help="仅同步至项目级 .zcode/skills")
    parser.add_argument("--global-only", action="store_true", help="仅同步至用户全局 ~/.zcode/skills")
    args = parser.parse_args()

    proj = not args.global_only
    glob = not args.project_only

    deploy_skill(project_sync=proj, global_sync=glob, verbose=True)


if __name__ == "__main__":
    main()
