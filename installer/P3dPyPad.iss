; AutoCAD Plant 3D 参数化构件设计与发布工具集 (P3dPyPad) 统一安装配置脚本
; 支持三种发布模式 (通过 ISCC 命令行宏 /DPACKAGE_TYPE=plugin|occ|allinone 切换):
; 1. plugin:   AutoCAD 宿主进程内插件独立安装包 (约 1.85 MB) -> P3dPyPad-Plugin-Setup-v1.0.0.exe
; 2. occ:      PyOCC 独立脱机 3D 工作台独立安装包 -> Plant3dOcc-Setup-v1.0.0.exe
; 3. allinone: 双端全功能二合一安装包 -> P3dPyPad-AllInOne-Setup-v1.0.0.exe

#ifndef PACKAGE_TYPE
  #define PACKAGE_TYPE "plugin"
#endif

#define MyAppVersion "1.0.0"
#define MyAppPublisher "zly258 (zhangly1403)"
#define MyAppURL "https://github.com/zly258"
#define ReleaseDir "..\build\bin\Release"
#define SrcDir "..\src\P3dPyPad"

#if PACKAGE_TYPE == "plugin"
  #define MyAppName "AutoCAD Plant 3D 参数化构件插件 (P3dPyPad Plugin)"
  #define MyAppId "{{B6E2A1C4-8F0D-4C3A-9E21-7A5D4C2B10E8}"
  #define MyOutputBaseFilename "P3dPyPad-Plugin-Setup-v" + MyAppVersion
  #define MyDefaultDirName "{commonpf}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
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
Name: "plugin"; Description: "AutoCAD Plant 3D 插件 (2019-2026)"; Types: full compact custom; Flags: fixed
Name: "occ"; Description: "PyOCC 独立构件设计工作台"; Types: full custom

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"; Components: occ
#endif

#if PACKAGE_TYPE == "occ"
[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加快捷方式:"
#endif

[Dirs]
Name: "{app}"; Permissions: authusers-full users-readexec
#if PACKAGE_TYPE == "plugin" || PACKAGE_TYPE == "allinone"
Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Permissions: authusers-full users-readexec
#endif

[Files]
#if PACKAGE_TYPE == "plugin"
; 1. 部署到标准系统级 Program Files 插件目录 (All Users 根目录)
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "PackageContents.xml"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ReleaseDir}\P3dPyPad.dll"; DestDir: "{app}\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\ICSharpCode.AvalonEdit.dll"; DestDir: "{app}\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\Resources\DEV_PROXY.py"; DestDir: "{app}\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\Resources\hot_reload.lsp"; DestDir: "{app}\Contents"; Flags: ignoreversion

; 2. 同步部署到 ProgramData 插件目录 (实现多环境与全用户双保险静默加载)
Source: "app_icon.ico"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Flags: ignoreversion
Source: "PackageContents.xml"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Flags: ignoreversion
Source: "{#ReleaseDir}\P3dPyPad.dll"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\ICSharpCode.AvalonEdit.dll"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\Resources\DEV_PROXY.py"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion
Source: "{#ReleaseDir}\Resources\hot_reload.lsp"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion

; 3. 部署单件热更新代理外壳到 CPak Common\CustomScripts
Source: "{#SrcDir}\Resources\DEV_PROXY.py"; DestDir: "{code:CustomScriptsDir}"; Flags: ignoreversion; Check: CustomScriptsExists
#endif

#if PACKAGE_TYPE == "occ"
Source: "output\Plant3dOcc\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion
#endif

#if PACKAGE_TYPE == "allinone"
; 部署 CAD 插件 (受组件选项控制)
Source: "app_icon.ico"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Flags: ignoreversion; Components: plugin
Source: "PackageContents.xml"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\P3dPyPad.dll"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\ICSharpCode.AvalonEdit.dll"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\Resources\DEV_PROXY.py"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion; Components: plugin
Source: "{#ReleaseDir}\Resources\hot_reload.lsp"; DestDir: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle\Contents"; Flags: ignoreversion; Components: plugin
Source: "{#SrcDir}\Resources\DEV_PROXY.py"; DestDir: "{code:CustomScriptsDir}"; Flags: ignoreversion; Check: CustomScriptsExists; Components: plugin

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
Root: HKLM; Subkey: "Software\Autodesk\AutoCAD\ApplicationPlugins\P3dPyPad"; ValueType: string; ValueName: "BundlePath"; ValueData: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"; Flags: uninsdeletekey
#endif

[UninstallDelete]
#if PACKAGE_TYPE == "plugin"
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

#if PACKAGE_TYPE == "occ"
Type: filesandordirs; Name: "{app}"
#endif

#if PACKAGE_TYPE == "allinone"
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\Autodesk\ApplicationPlugins\P3dPyPad.bundle"
#endif

[Code]
#if PACKAGE_TYPE == "plugin" || PACKAGE_TYPE == "allinone"
function CustomScriptsDir(Param: String): String;
var
  Years: array of String;
  I: Integer;
  Candidate: String;
begin
  Years := ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019'];
  for I := 0 to GetArrayLength(Years) - 1 do
  begin
    Candidate := 'C:\AutoCAD Plant 3D ' + Years[I] + ' Content\CPak Common\CustomScripts';
    if DirExists(Candidate) then
    begin
      Result := Candidate;
      Exit;
    end;
  end;
  Result := 'C:\AutoCAD Plant 3D 2019 Content\CPak Common\CustomScripts';
end;

function CustomScriptsExists: Boolean;
begin
  Result := DirExists(CustomScriptsDir(''));
end;

procedure RegisterShellInMap(const ScriptsDir: String);
var
  MapPath, Line: String;
  Lines: TStringList;
  I: Integer;
  Found: Boolean;
begin
  if not DirExists(ScriptsDir) then Exit;
  MapPath := ScriptsDir + '\variants.map';
  Line := 'DEV_PROXY=DEV_PROXY';
  Lines := TStringList.Create;
  try
    if FileExists(MapPath) then
      Lines.LoadFromFile(MapPath);
    Found := False;
    for I := 0 to Lines.Count - 1 do
    begin
      if Pos('DEV_PROXY=', Lines[I]) = 1 then
        Found := True;
    end;
    if not Found then
    begin
      Lines.Add(Line);
      Lines.SaveToFile(MapPath);
    end;
  finally
    Lines.Free;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  Years: array of String;
  I: Integer;
  TargetDir: String;
begin
  if CurStep <> ssPostInstall then Exit;
  
  Years := ['2026', '2025', '2024', '2023', '2022', '2021', '2020', '2019'];
  for I := 0 to GetArrayLength(Years) - 1 do
  begin
    TargetDir := 'C:\AutoCAD Plant 3D ' + Years[I] + ' Content\CPak Common\CustomScripts';
    if DirExists(TargetDir) then
    begin
      RegisterShellInMap(TargetDir);
    end;
  end;
end;
#endif
