[Setup]
AppName=PyWinLayout
AppVerName=PyWinLayout 0.1.0
DefaultDirName={pf}\PyWinLayout
DefaultGroupName=PyWinLayout
AppPublisher=Taehong Kim
UninstallDisplayIcon={app}\PyWinLayout.exe
Compression=lzma2/max
SolidCompression=yes
OutputDir="dist"
OutputBaseFilename=PyWinLayout-0.1.0-Setup

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
Name: "{commondesktop}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
