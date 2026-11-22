#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$IsccPath,
    [string]$PythonExe,
    [switch]$SkipBuild,
    [switch]$OpenOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$issPath = Join-Path $scriptDir 'P3dPyPad.iss'
$outputDir = Join-Path $scriptDir 'output'

function Resolve-Iscc {
    param([string]$ExplicitPath)

    $candidates = @(
        $ExplicitPath,
        $env:INNO_SETUP_ISCC,
        'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        'C:\Program Files\Inno Setup 6\ISCC.exe'
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $command = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw '未找到 Inno Setup 6 的 ISCC.exe。请安装 Inno Setup 6，或用 -IsccPath 显式指定。'
}

$iscc = Resolve-Iscc -ExplicitPath $IsccPath

Write-Host '==================================================' -ForegroundColor Cyan
Write-Host ' [1/3] 打包 AutoCAD Plant 3D 插件独立安装程序' -ForegroundColor Cyan
Write-Host '==================================================' -ForegroundColor Cyan
& (Join-Path $scriptDir 'Publish-PluginExe.ps1') `
    -IsccPath $iscc `
    -SkipBuild:$SkipBuild

Write-Host ''
Write-Host '==================================================' -ForegroundColor Cyan
Write-Host ' [2/3] 打包 PyOCC 独立桌面工作台 (绿色版 + 安装包)' -ForegroundColor Cyan
Write-Host '==================================================' -ForegroundColor Cyan
& (Join-Path $scriptDir 'Publish-OccExe.ps1') `
    -PythonExe $PythonExe `
    -IsccPath $iscc

Write-Host ''
Write-Host '==================================================' -ForegroundColor Cyan
Write-Host ' [3/3] 打包双端全功能二合一安装包 (All-in-One Setup)' -ForegroundColor Cyan
Write-Host '==================================================' -ForegroundColor Cyan
& $iscc '/DPACKAGE_TYPE=allinone' $issPath
if ($LASTEXITCODE -ne 0) {
    throw "二合一安装包打包失败 (exit $LASTEXITCODE)。"
}

$aio = Get-ChildItem -LiteralPath $outputDir -Filter 'P3dPyPad-AllInOne-Setup-*.exe' -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if ($aio) {
    $aioMb = [math]::Round($aio.Length / 1MB, 2)
    Write-Host "[完成] 二合一全功能安装包: $($aio.FullName) ($aioMb MB)" -ForegroundColor Green
}

Write-Host ''
Write-Host '🎉 全部三种类型发布包构建完成！产物列表:' -ForegroundColor Green
Get-ChildItem -LiteralPath $outputDir -File |
    Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length / 1MB, 2)}}, LastWriteTime |
    Format-Table -AutoSize

if ($OpenOutput) {
    Start-Process explorer.exe -ArgumentList "`"$outputDir`""
}
