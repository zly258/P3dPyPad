#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$PythonExe,
    [string]$IsccPath,
    [switch]$SkipZip,
    [switch]$OpenOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $scriptDir
$builder = Join-Path $scriptDir 'build_occ_exe.py'
$outputDir = Join-Path $scriptDir 'output'

function Resolve-Python {
    param([string]$ExplicitPath)

    $candidates = @(
        $ExplicitPath,
        $env:P3D_PYTHON_EXE,
        'D:\tools\miniconda3\envs\occ\python.exe'
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $command = Get-Command 'python.exe' -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw '未找到 Python 解释器。请用 -PythonExe 显式指定已安装 PySide6 + OCC 的 python.exe。'
}

$python = Resolve-Python -ExplicitPath $PythonExe
$previousIoEncoding = $env:PYTHONIOENCODING
$previousUtf8Mode = $env:PYTHONUTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
Push-Location $repoRoot
try {
    Write-Host "[1/1] 使用 Python 打包 PyOCC 独立 EXE: $python"
    & $python $builder
    if ($LASTEXITCODE -ne 0) {
        throw "PyOCC 打包失败 (exit $LASTEXITCODE)。"
    }

    $zip = Get-ChildItem -LiteralPath $outputDir -Filter 'Plant3dOcc-*-Portable-*.zip' -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    $appDir = Join-Path $outputDir 'Plant3dOcc'

    if (-not $zip -and -not (Test-Path -LiteralPath $appDir)) {
        throw "打包完成但未在 $outputDir 找到 Plant3dOcc 产物。"
    }

    Write-Host ''
    if (Test-Path -LiteralPath $appDir) {
        Write-Host "[完成] PyOCC 绿色目录: $appDir"
    }
    if ($zip) {
        $sizeMb = [math]::Round($zip.Length / 1MB, 2)
        Write-Host "[完成] PyOCC 便携 ZIP: $($zip.FullName) ($sizeMb MB)"
    }

    # 若具备 Inno Setup 则顺便生成独立安装包
    $candidates = @($IsccPath, $env:INNO_SETUP_ISCC, 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe', 'C:\Program Files\Inno Setup 6\ISCC.exe')
    $iscc = $candidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
    if ($iscc) {
        $issPath = Join-Path $scriptDir 'P3dPyPad.iss'
        Write-Host "[打包器] 使用 Inno Setup 编译 PyOCC 独立桌面安装程序..."
        & $iscc '/DPACKAGE_TYPE=occ' $issPath
        $installer = Get-ChildItem -LiteralPath $outputDir -Filter 'Plant3dOcc-Setup-*.exe' -File |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($installer) {
            $instMb = [math]::Round($installer.Length / 1MB, 2)
            Write-Host "[完成] PyOCC 安装包: $($installer.FullName) ($instMb MB)"
        }
    }

    if ($OpenOutput) {
        $target = if ($zip) { $zip.FullName } else { $appDir }
        if ($zip) {
            Start-Process explorer.exe -ArgumentList "/select,`"$target`""
        }
        else {
            Start-Process explorer.exe -ArgumentList "`"$target`""
        }
    }
}
finally {
    Pop-Location
    $env:PYTHONIOENCODING = $previousIoEncoding
    $env:PYTHONUTF8 = $previousUtf8Mode
}
