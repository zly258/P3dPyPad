@echo off
chcp 65001 >nul
title AutoCAD Plant 3D 参数化构件工具集 全流程一键发布构建
color 0b

echo ======================================================================
echo   AutoCAD Plant 3D 参数化构件设计与发布工具集 (P3dPyPad)
echo   全套发布构建: C# 插件 + Inno Setup 全机安装包 + PyOCC 绿色免安装版
echo ======================================================================
echo.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

:: 1. 编译 C# 解决方案 (Release)
echo [1/3] 正在编译 C# 插件工程 (P3dPyPad.sln / Release) ...
dotnet build P3dPyPad.sln -c Release
if %ERRORLEVEL% NEQ 0 (
    echo [错误] C# 工程编译失败，停止后续打包。
    pause
    exit /b %ERRORLEVEL%
)
echo [成功] C# 程序集编译完成！
echo.

:: 2. 调用 Inno Setup 编译全机所有用户安装包
echo [2/3] 正在使用 Inno Setup 编译安装包 ...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"

if exist %ISCC% (
    echo   [2.1] 正在生成 AutoCAD 独立插件安装包 (P3dPyPad-Plugin-Setup) ...
    %ISCC% /DPACKAGE_TYPE=plugin "installer\P3dPyPad.iss"
    if %ERRORLEVEL% EQU 0 (
        echo   [成功] AutoCAD 独立插件安装包生成完成！
    ) else (
        echo   [警告] 插件安装包编译出现警告或错误。
    )

    if exist "installer\output\Plant3dOcc" (
        echo   [2.2] 正在生成双端二合一全功能安装包 (P3dPyPad-AllInOne-Setup) ...
        %ISCC% /DPACKAGE_TYPE=allinone "installer\P3dPyPad.iss"
        if %ERRORLEVEL% EQU 0 (
            echo   [成功] 双端全功能安装包生成完成！
        ) else (
            echo   [警告] 全功能安装包编译出现警告或错误。
        )
    )
) else (
    echo [提示] 未在默认路径找到 Inno Setup 6 (ISCC.exe)，跳过 ISS 编译。
)
echo.

:: 3. 打包生成 PyOCC 独立便携免安装绿色版 (Plant3dOcc ZIP)
echo [3/3] 正在打包 PyOCC 独立桌面工作台绿色便携版 ...
set PYTHON_EXE=D:\tools\miniconda3\envs\occ\python.exe
if not exist "%PYTHON_EXE%" set PYTHON_EXE=python.exe

"%PYTHON_EXE%" installer\build_occ_exe.py
if %ERRORLEVEL% EQU 0 (
    echo [成功] PyOCC 独立便携绿色免安装版打包完成！
) else (
    echo [警告] PyOCC 打包过程中出现问题。
)

echo.
echo ======================================================================
echo   全部发布产物制作完成！输出目录: installer\output
echo ======================================================================
if exist "installer\output" explorer.exe "installer\output"
pause
