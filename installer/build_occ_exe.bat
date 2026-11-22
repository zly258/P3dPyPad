@echo off
chcp 65001 >nul
title 打包发布 Plant 3D OCC 独立工作台 (EXE)

echo ============================================================
echo   AutoCAD Plant 3D OCC 独立工作台一键打包发布程序
echo ============================================================
echo.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

:: 自动探测当前推荐的 Python 解释器
set PYTHON_EXE=D:\tools\miniconda3\envs\occ\python.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python.exe
)

echo 正在使用 Python: %PYTHON_EXE%
echo 正在执行打包脚本 installer\build_occ_exe.py ...
echo.

"%PYTHON_EXE%" installer\build_occ_exe.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo [成功] 打包完成！正在打开输出发布包目录...
    echo ============================================================
    if exist "installer\output\Plant3dOcc" (
        explorer.exe "installer\output\Plant3dOcc"
    )
) else (
    echo.
    echo ============================================================
    echo [错误] 打包过程中出现错误，请检查上方日志。
    echo ============================================================
)

echo.
pause
