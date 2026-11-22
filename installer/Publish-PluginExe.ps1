#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$IsccPath,
    [switch]$SkipBuild,
    [switch]$OpenOutput
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$repoRoot = Split-Path -Parent $scriptDir
$issPath = Join-Path $scriptDir 'P3dPyPad.iss'
$releaseDir = Join-Path $repoRoot 'build\bin\Release'
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

Push-Location $repoRoot
try {
    if (-not $SkipBuild) {
        Write-Host '[1/2] 编译 C# 插件 (Release, 跳过本机 Bundle 部署)...'
        dotnet build 'P3dPyPad.sln' -c Release -p:SkipBundleDeploy=true
        if ($LASTEXITCODE -ne 0) {
            throw "C# 编译失败 (exit $LASTEXITCODE)。"
        }
    }

    $pluginDll = Join-Path $releaseDir 'P3dPyPad.dll'
    if (-not (Test-Path -LiteralPath $pluginDll)) {
        throw "未找到 Release 产物: $pluginDll。请先构建或去掉 -SkipBuild。"
    }

    $iscc = Resolve-Iscc -ExplicitPath $IsccPath
    Write-Host "[2/2] 使用 Inno Setup 打包插件独立安装程序: $iscc"
    & $iscc '/DPACKAGE_TYPE=plugin' $issPath
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup 打包失败 (exit $LASTEXITCODE)。"
    }

    $installer = Get-ChildItem -LiteralPath $outputDir -Filter 'P3dPyPad-Plugin-Setup-*.exe' -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $installer) {
        throw "打包成功但未在 $outputDir 找到 P3dPyPad-Plugin-Setup-*.exe。"
    }

    # 同步生成通用别名 P3dPyPad-Setup-v1.0.0.exe
    $aliasPath = Join-Path $outputDir 'P3dPyPad-Setup-v1.0.0.exe'
    Copy-Item -LiteralPath $installer.FullName -Destination $aliasPath -Force

    $sizeMb = [math]::Round($installer.Length / 1MB, 2)
    Write-Host ''
    Write-Host "[完成] 插件安装包: $($installer.FullName) ($sizeMb MB)"

    if ($OpenOutput) {
        Start-Process explorer.exe -ArgumentList "/select,`"$($installer.FullName)`""
    }
}
finally {
    Pop-Location
}
