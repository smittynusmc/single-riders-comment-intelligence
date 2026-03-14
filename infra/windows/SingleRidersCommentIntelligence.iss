#define AppName "Single Riders Comment Intelligence"
#define AppVersion "0.1.0"

#ifndef BundleRoot
  #error BundleRoot must be provided to the Inno Setup compiler.
#endif

#ifndef OutputRoot
  #define OutputRoot ".\dist\native"
#endif

[Setup]
AppId={{5F1ABEC0-738E-4B0C-9D0C-9F2F0B54C6D0}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={localappdata}\Programs\Single Riders Comment Intelligence
DefaultGroupName={#AppName}
OutputDir={#OutputRoot}
OutputBaseFilename=single-riders-comment-intelligence-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "{#BundleRoot}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Start Single Riders Comment Intelligence"; Filename: "{app}\scripts\start-native.bat"
Name: "{group}\Stop Single Riders Comment Intelligence"; Filename: "{app}\scripts\stop-native.bat"
Name: "{autodesktop}\Single Riders Comment Intelligence"; Filename: "{app}\scripts\start-native.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\scripts\start-native.bat"; Description: "Launch Single Riders Comment Intelligence"; Flags: postinstall nowait skipifsilent
