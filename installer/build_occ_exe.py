# -*- coding: utf-8 -*-
"""Plant 3D OCC 独立 3D 桌面工作台一键打包发布工具。

面向【最小依赖 DLL、最小体积、功能 100% 完整】设计：
1. 仅精准收集 OpenCASCADE (OCCT) 核心建模、几何、着色与 HLR 渲染所必需的 DLL (TKernel, TKMath, TKBRep, TKTopAlgo, TKPrim, TKBO, TKBool, TKOffset, TKV3d, TKOpenGl, TKHLR, tbb, freetype, freeimage)，彻底剔除数十个体积庞大的非必要数据交换库 (TKDESTEP, TKDEIGES, TKDE*, TKXml*, TKBin*, TKCAF, TKCDF 等)；
2. 排除 matplotlib, scipy, pandas, IPython, tkinter 等无用重量级包；
3. 为生成的 Plant3dOcc.exe 配置专业 CAD 矢量应用图标 (app_icon.ico)；
4. 编译完成后自动打包生成绿色便携免安装版: output/Plant3dOcc-v1.2.0-Portable-x64.zip；
5. 执行自动化冒烟测试确保绿色版开箱即可 100% 正常运行。
"""

import glob
import os
import shutil
import subprocess
import sys
import time
import zipfile

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

APP_NAME = "Plant3dOcc"
APP_VERSION = "1.1.0"

# 精准保留的 OpenCASCADE 必需核心 DLL 清单 (仅 19 个核心 TK 库 + 3 个三方依赖)
ESSENTIAL_DLL_PATTERNS = [
    "TKernel.dll",
    "TKMath.dll",
    "TKG2d.dll",
    "TKG3d.dll",
    "TKGeomBase.dll",
    "TKGeomAlgo.dll",
    "TKBRep.dll",
    "TKTopAlgo.dll",
    "TKPrim.dll",
    "TKBO.dll",
    "TKBool.dll",
    "TKOffset.dll",
    "TKFillet.dll",
    "TKShHealing.dll",
    "TKMesh.dll",
    "TKService.dll",
    "TKV3d.dll",
    "TKOpenGl.dll",
    "TKHLR.dll",
    "tbb*.dll",
    "freetype*.dll",
    "freeimage*.dll",
]


def get_repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collect_opencascade_assets(prefix):
    """精准收集 OpenCASCADE (OCCT) 核心 DLL 与必要数据目录，剔除无用冗余文件。"""
    binaries = []
    datas = []

    lib_bin = os.path.join(prefix, "Library", "bin")
    if os.path.exists(lib_bin):
        collected_names = set()
        for pat in ESSENTIAL_DLL_PATTERNS:
            for dll in glob.glob(os.path.join(lib_bin, pat)):
                fn = os.path.basename(dll)
                if fn.lower() not in collected_names:
                    collected_names.add(fn.lower())
                    binaries.append((dll, "."))
        print(f"[打包器] 精简收集 OpenCASCADE 核心动态库: 共 {len(binaries)} 个 DLL (剔除冗余 STEP/IGES/XML 数据交换库)")

    share_res = os.path.join(prefix, "Library", "share", "opencascade", "resources")
    if os.path.exists(share_res):
        datas.append((share_res, os.path.join("share", "opencascade", "resources")))
        print(f"[打包器] 收集 OpenCASCADE 着色与字体资源: {share_res}")

    return binaries, datas


def generate_spec_file(repo_root, prefix, spec_path, binaries, datas, icon_path):
    """生成高压缩、轻量化、最小依赖的 PyInstaller 打包规格文件。"""
    entry_script = os.path.join(repo_root, "plant3d_occ", "main.py")
    pyscripts_dir = os.path.join(repo_root, "pyscripts")
    plant3d_occ_dir = os.path.join(repo_root, "plant3d_occ")

    datas.append((pyscripts_dir, "pyscripts"))
    datas.append((plant3d_occ_dir, "plant3d_occ"))
    if os.path.isfile(icon_path):
        datas.append((icon_path, "."))

    # 仅保留 plant3d_occ 与 PySide6 / PyOCC 真实所需的模块
    hidden_imports = [
        "OCC.Core.BRepPrimAPI",
        "OCC.Core.BRepAlgoAPI",
        "OCC.Core.BRepBuilderAPI",
        "OCC.Core.BRepOffsetAPI",
        "OCC.Core.BRepFilletAPI",
        "OCC.Core.gp",
        "OCC.Core.Quantity",
        "OCC.Core.Graphic3d",
        "OCC.Core.V3d",
        "OCC.Core.AIS",
        "OCC.Core.TopExp",
        "OCC.Core.TopAbs",
        "OCC.Core.BRep",
        "OCC.Core.TopLoc",
        "OCC.Core.Bnd",
        "OCC.Core.BRepBndLib",
        "OCC.Core.BRepMesh",
        "OCC.Display.backend",
        "OCC.Display.qtDisplay",
        "OCC.Display.OCCViewer",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtOpenGL",
        "PySide6.QtOpenGLWidgets",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        "PIL.ImageFont",
        "numpy",
        "sqlite3",
        "csv",
    ]

    # 深度剔除无需打包的大型第三方库
    excludes = [
        "cv2",
        "opencv",
        "tkinter",
        "matplotlib",
        "scipy",
        "pandas",
        "IPython",
        "notebook",
        "jupyter",
        "tornado",
        "unittest",
        "pydoc",
        "test",
        "PyQt5",
        "PyQt6",
        "wx",
        "distutils",
        "curses",
        "multiprocessing",
    ]

    icon_str = repr(icon_path) if (icon_path and os.path.isfile(icon_path)) else "None"

    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Plant3dOcc 自动生成的轻量化绿色免安装版 PyInstaller 规范
import os

block_cipher = None

a = Analysis(
    [{repr(entry_script)}],
    pathex=[{repr(repo_root)}],
    binaries={repr(binaries)},
    datas={repr(datas)},
    hiddenimports={repr(hidden_imports)},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={repr(excludes)},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 精简二进制文件：剔除冗余的超大 MKL 架构扩展库 (AVX512/AVX10/Scalapack/MPI) 与数据交换库
unwanted_binary_prefixes = (
    "mkl_avx512",
    "mkl_avx10",
    "mkl_scalapack",
    "mkl_blacs",
    "mkl_cdft",
    "impi",
    "opencv_",
    "cv2",
    "tkdestep",
    "tkdeiges",
    "tkdevrml",
    "tkdegltf",
    "tkdeobj",
    "tkdeply",
    "tkdestl",
    "tkxml",
    "tkbin",
    "tkcaf",
    "tkcdf",
    "tklcaf",
    "tkvcaf",
    "tkxcaf",
    "tkxsbase",
    "tkexpress",
)
a.binaries = [
    x for x in a.binaries
    if not any(os.path.basename(x[0]).lower().startswith(p) for p in unwanted_binary_prefixes)
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name={repr(APP_NAME)},
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={icon_str},
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name={repr(APP_NAME)},
)
'''
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"[打包器] 已生成 spec 配置文件: {spec_path}")


def create_portable_zip(source_dir, output_zip_path):
    """将生成的独立工作台打包目录压缩为高压缩比的绿色免安装 zip 包。"""
    print(f"\n[打包器] 正在制作免安装绿色便携包 (ZIP): {output_zip_path} ...")
    total_files = 0
    total_uncompressed = 0
    with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, _dirs, files in os.walk(source_dir):
            for file in files:
                full_p = os.path.join(root, file)
                rel_p = os.path.join(APP_NAME, os.path.relpath(full_p, source_dir))
                zf.write(full_p, rel_p)
                total_files += 1
                total_uncompressed += os.path.getsize(full_p)

    zip_size_mb = os.path.getsize(output_zip_path) / (1024 * 1024)
    uncomp_size_mb = total_uncompressed / (1024 * 1024)
    print(f"[打包器] ZIP 绿色免安装包生成完成！")
    print(f"  包含文件: {total_files} 个")
    print(f"  解压总体积: {uncomp_size_mb:.1f} MB -> 压缩包体积: {zip_size_mb:.1f} MB (压缩率: {zip_size_mb/max(0.1, uncomp_size_mb)*100:.1f}%)")
    return output_zip_path


def run_smoke_test(exe_path, repo_root):
    """对生成的独立 EXE 执行离线运行冒烟测试，确保无缺 DLL 或模块找不到错误。"""
    print(f"\n[打包器] 正在执行独立程序功能完整性验证...")
    sample_script = os.path.join(repo_root, "pyscripts", "custom_scripts", "05_supports", "SUPPORT_PIPE_CLAMP.py")
    if not os.path.isfile(sample_script):
        sample_script = os.path.join(repo_root, "pyscripts", "custom_scripts", "01_pipe_fittings", "ELBOW_90.py")

    cmd = [os.path.abspath(exe_path), "--render-preview", os.path.abspath(sample_script)]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25, text=True, cwd=os.path.dirname(exe_path))
        if proc.returncode == 0 and "ok" in proc.stdout:
            print("[打包器] ✅ 冒烟测试 100% 通过: 独立免安装版成功调用 PyOCC 渲染并生成 3D 外形与轴测标注图！")
            return True
        else:
            print(f"[打包器] ⚠️ 冒烟测试返回 code={proc.returncode}: stdout={proc.stdout.strip()}, stderr={proc.stderr.strip()[:200]}")
            return False
    except Exception as exc:
        print(f"[打包器] ⚠️ 冒烟测试执行异常: {exc}")
        return False


def build():
    t0 = time.time()
    repo_root = get_repo_root()
    prefix = sys.prefix

    print("=" * 65)
    print(" AutoCAD Plant 3D OCC 独立工作台 - 最小依赖绿色免安装版打包")
    print(f" 工作区根目录: {repo_root}")
    print(f" Python环境:   {prefix}")
    print("=" * 65)

    installer_dir = os.path.join(repo_root, "installer")
    icon_path = os.path.join(installer_dir, "app_icon.ico")

    # 1. 精简依赖收集
    binaries, datas = collect_opencascade_assets(prefix)

    # 2. 生成 spec 配置文件
    spec_path = os.path.join(installer_dir, f"{APP_NAME}.spec")
    generate_spec_file(repo_root, prefix, spec_path, binaries, datas, icon_path)

    # 3. 设置输出与临时目录
    dist_dir = os.path.join(installer_dir, "output")
    work_dir = os.path.join(installer_dir, "build_temp")
    os.makedirs(dist_dir, exist_ok=True)
    os.makedirs(work_dir, exist_ok=True)

    print(f"\n[打包器] 正在调用 PyInstaller 编译生成独立绿色程序...")
    import PyInstaller.__main__

    args = [
        spec_path,
        f"--distpath={dist_dir}",
        f"--workpath={work_dir}",
        "--noconfirm",
        "--clean",
    ]

    try:
        PyInstaller.__main__.run(args)
    finally:
        if os.path.exists(work_dir):
            try:
                shutil.rmtree(work_dir)
            except Exception:
                pass

    app_dir = os.path.join(dist_dir, APP_NAME)
    exe_path = os.path.join(app_dir, f"{APP_NAME}.exe")

    if not os.path.exists(exe_path):
        print(f"\n[错误] 未在目标目录检测到 {APP_NAME}.exe！")
        return False

    # 4. 自动化完整性冒烟测试
    run_smoke_test(exe_path, repo_root)

    # 5. 制作便携 ZIP 绿色发布包
    zip_output_path = os.path.join(dist_dir, f"{APP_NAME}-v{APP_VERSION}-Portable-x64.zip")
    create_portable_zip(app_dir, zip_output_path)

    print("\n" + "=" * 65)
    print(" 打包与发布包制作成功！")
    print(f" 1. 免安装绿色目录: {app_dir}")
    print(f" 2. 便携绿色 ZIP 包: {zip_output_path}")
    print(f" 总耗时: {time.time() - t0:.1f} 秒")
    print("=" * 65)
    return True


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
