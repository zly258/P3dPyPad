; AutoCAD Plant 3D 参数化构件设计与发布工具集 (P3dPyPad) 统一安装配置脚本
; 支持三种发布模式 (通过 ISCC 命令行宏 /DPACKAGE_TYPE=plugin|occ|allinone 切换):
; 1. plugin:   AutoCAD 宿主进程内插件独立安装包 -> P3dPyPad-Plugin-Setup-v1.1.0.exe
; 2. occ:      PyOCC 独立脱机 3D 工作台独立安装包 -> Plant3dOcc-Setup-v1.1.0.exe
; 3. allinone: 双端全功能二合一安装包 -> P3dPyPad-AllInOne-Setup-v1.1.0.exe

#ifndef PACKAGE_TYPE
  #define PACKAGE_TYPE "plugin"
#endif

#define MyAppVersion "1.1.0"
#define MyAppPublisher "zly258 (zhangly1403)"
#define MyAppURL "https://github.com/zly258"
#define ReleaseDir "..\build\bin\Release"
#define SrcDir "..\src\P3dPyPad"
#define CanonicalBundleDir "{commonpf64}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"

#if PACKAGE_TYPE == "plugin"
  #define MyAppName "AutoCAD Plant 3D 参数化构件插件 (P3dPyPad Plugin)"
  #define MyAppId "{{B6E2A1C4-8F0D-4C3A-9E21-7A5D4C2B10E8}"
  #define MyOutputBaseFilename "P3dPyPad-Plugin-Setup-v" + MyAppVersion
  #define MyDefaultDirName CanonicalBundleDir
#elif PACKAGE_TYPE == "occ"
  #define MyAppName "AutoCAD Plant 3D OCC 独立构件设计工作台 (Plant3dOcc)"
  #define MyAppId "{{C7F3B2D5-9E1E-5D4B-AF32-8B6E5D3C21F9}"
  #define MyOutputBaseFilename "Plant3dOcc-Setup-v" + MyAppVersion
  #define MyDefaultDirName "{autopf}\Plant3dOcc"
#elif PACKAGE_TYPE == "allinone"
  #define MyAppName "AutoCAD Plant 3D 参数化构件双端工具箱 (P3dPyPad All-in-One)"
  #define MyAppId "{{D8A4C3E6-AF2F-6E5C-B043-9C7F6E4D32A0}"
  #define MyOutputBaseFilename "P3dPyPad-AllInOne-Setup-v" + MyAppVersion
  #define MyDefaultDirName "{autopf}\P3dPyPad"
#else
  #error "未知 PACKAGE_TYPE: 仅支持 plugin, occ, allinone"
#endif

[Setup]
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={#MyDefaultDirName}
DisableDirPage=yes
DirExistsWarning=no
AppendDefaultDirName=no
#if PACKAGE_TYPE == "plugin"
DisableProgramGroupPage=yes
#else
DisableProgramGroupPage=no
DefaultGroupName={#MyAppName}
#endif
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir=output
OutputBaseFilename={#MyOutputBaseFilename}
SetupIconFile=app_icon.ico
UninstallDisplayIcon={app}\app_icon.ico
UninstallDisplayName={#MyAppName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
CloseApplications=no
AlwaysRestart=no

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

#if PACKAGE_TYPE == "allinone"
[Components]
Name: "plugin"; Description: "AutoCAD Plant 3D 插件 (2019-2026 全版本自适应)"; Types: full compact custom; Flags: fixed
Name: "occ"; Description: "PyOCC 独立构件设计工作台"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"; Components: occ
#endif

#if PACKAGE_TYPE == "occ"
[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"
#endif

[InstallDelete]
#if PACKAGE_TYPE == "plugin"
; 安装前彻底清理旧版目录内容及 ProgramData / AppData 遗留多副本，杜绝版本冲突
Type: filesandordirs; Name: "{app}\Contents"
Type: files; Name: "{app}\PackageContents.xml"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
Type: filesandordirs; Name: "{userappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

#if PACKAGE_TYPE == "allinone"
Type: filesandordirs; Name: "{#CanonicalBundleDir}"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
Type: filesandordirs; Name: "{userappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

[Dirs]
Name: "{app}"; Permissions: users-readexec
#if PACKAGE_TYPE == "allinone"
Name: "{#CanonicalBundleDir}"; Permissions: users-readexec; Components: plugin
#endif

[Files]
#if PACKAGE_TYPE == "plugin"
; 部署到 AutoCAD 2019-2026 全版本默认扫描且受 SECURELOAD 信任的 Program Files 插件目录
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "PackageContents.xml"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ReleaseDir}\2019-2024\P3dPyPad.dll"; DestDir: "{app}\Contents\2019-2024"; Flags: ignoreversion
Source: "{#ReleaseDir}\2019-2024\P3dPyPad.pdb"; DestDir: "{app}\Contents\2019-2024"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#ReleaseDir}\2019-2024\ICSharpCode.AvalonEdit.dll"; DestDir: "{app}\Contents\2019-2024"; Flags: ignoreversion
Source: "{#ReleaseDir}\2019-2024\Resources\*"; DestDir: "{app}\Contents\2019-2024\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.dll"; DestDir: "{app}\Contents\2025-2026"; Flags: ignoreversion
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.pdb"; DestDir: "{app}\Contents\2025-2026"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.deps.json"; DestDir: "{app}\Contents\2025-2026"; Flags: ignoreversion skipifsourcedoesntexist
Source: "{#ReleaseDir}\2025-2026\ICSharpCode.AvalonEdit.dll"; DestDir: "{app}\Contents\2025-2026"; Flags: ignoreversion
Source: "{#ReleaseDir}\2025-2026\Resources\*"; DestDir: "{app}\Contents\2025-2026\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#ReleaseDir}\2025-2026\Resources\*"; DestDir: "{app}\Contents\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

#if PACKAGE_TYPE == "occ"
Source: "output\Plant3dOcc\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
#endif

#if PACKAGE_TYPE == "allinone"
; 部署 CAD 插件到标准 Program Files 插件目录 (覆盖 2019-2026 全版本)
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.ico"; DestDir: "{#CanonicalBundleDir}"; Flags: ignoreversion; Components: plugin
Source: "PackageContents.xml"; DestDir: "{#CanonicalBundleDir}"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\2019-2024\P3dPyPad.dll"; DestDir: "{#CanonicalBundleDir}\Contents\2019-2024"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\2019-2024\P3dPyPad.pdb"; DestDir: "{#CanonicalBundleDir}\Contents\2019-2024"; Flags: ignoreversion skipifsourcedoesntexist; Components: plugin
Source: "{#ReleaseDir}\2019-2024\ICSharpCode.AvalonEdit.dll"; DestDir: "{#CanonicalBundleDir}\Contents\2019-2024"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\2019-2024\Resources\*"; DestDir: "{#CanonicalBundleDir}\Contents\2019-2024\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: plugin
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.dll"; DestDir: "{#CanonicalBundleDir}\Contents\2025-2026"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.pdb"; DestDir: "{#CanonicalBundleDir}\Contents\2025-2026"; Flags: ignoreversion skipifsourcedoesntexist; Components: plugin
Source: "{#ReleaseDir}\2025-2026\P3dPyPad.deps.json"; DestDir: "{#CanonicalBundleDir}\Contents\2025-2026"; Flags: ignoreversion skipifsourcedoesntexist; Components: plugin
Source: "{#ReleaseDir}\2025-2026\ICSharpCode.AvalonEdit.dll"; DestDir: "{#CanonicalBundleDir}\Contents\2025-2026"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\2025-2026\Resources\*"; DestDir: "{#CanonicalBundleDir}\Contents\2025-2026\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: plugin
Source: "{#ReleaseDir}\2025-2026\Resources\*"; DestDir: "{#CanonicalBundleDir}\Contents\Resources"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: plugin

; 部署 PyOCC 独立工作台到主目录的 Plant3dOcc 子目录
Source: "output\Plant3dOcc\*"; DestDir: "{app}\Plant3dOcc"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: occ
Source: "app_icon.ico"; DestDir: "{app}\Plant3dOcc"; Flags: ignoreversion; Components: occ
#endif

[Icons]
#if PACKAGE_TYPE == "occ"
Name: "{commondesktop}\Plant3dOcc"; Filename: "{app}\Plant3dOcc.exe"; Tasks: desktopicon
Name: "{group}\Plant3dOcc"; Filename: "{app}\Plant3dOcc.exe"
Name: "{group}\Uninstall Plant3dOcc"; Filename: "{uninstallexe}"
#endif

#if PACKAGE_TYPE == "allinone"
Name: "{commondesktop}\Plant3dOcc"; Filename: "{app}\Plant3dOcc\Plant3dOcc.exe"; Tasks: desktopicon; Components: occ
Name: "{group}\Plant3dOcc"; Filename: "{app}\Plant3dOcc\Plant3dOcc.exe"; Components: occ
Name: "{group}\Uninstall P3dPyPad"; Filename: "{uninstallexe}"
#endif

[Registry]
#if PACKAGE_TYPE == "plugin" || PACKAGE_TYPE == "allinone"
Root: HKLM; Subkey: "Software\Autodesk\AutoCAD\ApplicationPlugins\P3dPyPad"; ValueType: string; ValueName: "Name"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Autodesk\AutoCAD\ApplicationPlugins\P3dPyPad"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Autodesk\AutoCAD\ApplicationPlugins\P3dPyPad"; ValueType: string; ValueName: "BundlePath"; ValueData: "{#CanonicalBundleDir}"; Flags: uninsdeletekey
#endif

[UninstallDelete]
#if PACKAGE_TYPE == "plugin"
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
Type: filesandordirs; Name: "{userappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

#if PACKAGE_TYPE == "occ"
Type: filesandordirs; Name: "{app}"
#endif

#if PACKAGE_TYPE == "allinone"
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{#CanonicalBundleDir}"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
Type: filesandordirs; Name: "{userappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

[Code]
#if PACKAGE_TYPE == "plugin" || PACKAGE_TYPE == "allinone"
// 清理 AutoCAD 各版本注册表中的旧版 Loaded / Applications 缓存，强制下次启动重新解析最新 Bundle
procedure CleanStaleAutoCadRegistryCache;
var
  Releases, Products, LoadedKeys: TArrayOfString;
  I, J, K: Integer;
  AcadRoot, RelPath, ProdPath, LoadedPath, KeyName: String;
begin
  AcadRoot := 'Software\Autodesk\AutoCAD';
  if not RegGetSubkeyNames(HKCU, AcadRoot, Releases) then Exit;

  for I := 0 to GetArrayLength(Releases) - 1 do
  begin
    RelPath := AcadRoot + '\' + Releases[I];
    if RegGetSubkeyNames(HKCU, RelPath, Products) then
    begin
      for J := 0 to GetArrayLength(Products) - 1 do
      begin
        ProdPath := RelPath + '\' + Products[J];
        RegDeleteKeyIncludingSubkeys(HKCU, ProdPath + '\Applications\P3dPyPad');

        LoadedPath := ProdPath + '\Loaded';
        if RegGetSubkeyNames(HKCU, LoadedPath, LoadedKeys) then
        begin
          for K := 0 to GetArrayLength(LoadedKeys) - 1 do
          begin
            KeyName := Uppercase(LoadedKeys[K]);
            if Pos('P3DPYPAD.BUNDLE', KeyName) > 0 then
              RegDeleteKeyIncludingSubkeys(HKCU, LoadedPath + '\' + LoadedKeys[K]);
          end;
        end;
      end;
    end;
  end;
end;

// 以无 BOM 纯 ASCII 写入 variants.map，避免 UTF-8 BOM 破坏首行映射解析
procedure RegisterShellInMap(const ScriptsDir: String);
var
  MapPath: String;
  Lines: TArrayOfString;
  I, Len: Integer;
  Found: Boolean;
begin
  if not DirExists(ScriptsDir) then Exit;
  MapPath := ScriptsDir + '\variants.map';
  Found := False;
  if FileExists(MapPath) and LoadStringsFromFile(MapPath, Lines) then
  begin
    for I := 0 to GetArrayLength(Lines) - 1 do
    begin
      if Pos('DEV_PROXY=', Trim(Lines[I])) = 1 then
      begin
        Found := True;
        Break;
      end;
    end;
    if not Found then
    begin
      Len := GetArrayLength(Lines);
      SetArrayLength(Lines, Len + 1);
      Lines[Len] := 'DEV_PROXY=DEV_PROXY';
      SaveStringsToFile(MapPath, Lines, False);
    end;
  end
  else if not FileExists(MapPath) then
  begin
    SetArrayLength(Lines, 1);
    Lines[0] := 'DEV_PROXY=DEV_PROXY';
    SaveStringsToFile(MapPath, Lines, False);
  end;
end;

procedure DeployProxyToAllInstalledPlant3D;
var
  Drives, Years: array of String;
  D, Y: Integer;
  CPakCommon, TargetDir, TargetProxy, SourceProxy: String;
begin
  Drives := ['C:\', 'D:\', 'E:\', 'F:\'];
  Years := ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019'];
  SourceProxy := ExpandConstant('{#CanonicalBundleDir}\Contents\Resources\DEV_PROXY.py');
  if not FileExists(SourceProxy) then
    SourceProxy := ExpandConstant('{app}\Contents\Resources\DEV_PROXY.py');

  for D := 0 to GetArrayLength(Drives) - 1 do
  begin
    for Y := 0 to GetArrayLength(Years) - 1 do
    begin
      CPakCommon := Drives[D] + 'AutoCAD Plant 3D ' + Years[Y] + ' Content\CPak Common';
      if DirExists(CPakCommon) then
      begin
        TargetDir := CPakCommon + '\CustomScripts';
        if not DirExists(TargetDir) then
          ForceDirectories(TargetDir);
        if FileExists(SourceProxy) then
        begin
          TargetProxy := TargetDir + '\DEV_PROXY.py';
          FileCopy(SourceProxy, TargetProxy, False);
        end;
        RegisterShellInMap(TargetDir);
      end;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    CleanStaleAutoCadRegistryCache;
  end
  else if CurStep = ssPostInstall then
  begin
    DeployProxyToAllInstalledPlant3D;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    CleanStaleAutoCadRegistryCache;
  end;
end;
#endif
