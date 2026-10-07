#define MyAppName "AuraAgenda"
#define MyAppVersion "2.0.3"
#define MyAppPublisher "QuintaDimension Tecnologia"
#define MyAppExeName "AuraAgenda.exe"

[Setup]
AppId={{5F0A42D5-870F-45D3-91F1-9D56DA2F7EAA}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\AuraAgenda
DefaultGroupName=AuraAgenda
OutputDir=output
OutputBaseFilename=AuraAgenda_Setup_2.0.3
SetupIconFile=..\assets\AuraAgenda.ico
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Files]
Source: "..\dist\AuraAgenda.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\AuraAgenda"; Filename: "{app}\AuraAgenda.exe"
Name: "{autodesktop}\AuraAgenda"; Filename: "{app}\AuraAgenda.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Crear acceso directo en el escritorio"; Flags: unchecked

[Run]
Filename: "{app}\AuraAgenda.exe"; Description: "Abrir AuraAgenda"; Flags: nowait postinstall skipifsilent
