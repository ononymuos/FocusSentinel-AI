; FocusSentinel AI - Inno Setup Script
; Author: Usama Baig (https://github.com/ononymuos/FocusSentinel-AI)

#define MyAppName "FocusSentinel AI"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Usama Baig"
#define MyAppURL "https://github.com/ononymuos/FocusSentinel-AI"
#define MyAppExeName "FocusSentinel.exe"

[Setup]
AppId={{A8F4321E-68B9-4C82-9B7C-901F1564EF90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=C:\Users\hecke\FocusSentinel-AI\dist_installer
OutputBaseFilename=FocusSentinel_Setup_v1.1.0
SetupIconFile=C:\Users\hecke\FocusSentinel-AI\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\hecke\FocusSentinel-AI\dist\FocusSentinel\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
