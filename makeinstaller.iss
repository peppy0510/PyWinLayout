; http://www.jrsoftware.org/ishelp/index.php

[Setup]
AppName="PyWinLayout"
AppVerName="PyWinLayout 0.1.1"
DefaultDirName="{pf}\PyWinLayout"
DefaultGroupName="PyWinLayout"
AppVersion="0.1.1"
AppCopyright="Taehong Kim"
AppPublisher="Taehong Kim"
UninstallDisplayIcon="{app}\PyWinLayout.exe"
Compression=lzma2/max
SolidCompression=yes
OutputDir="dist"
OutputBaseFilename="PyWinLayout-0.1.1-Setup"
; VersionInfoVersion="0.1.1"
VersionInfoProductVersion="0.1.1"
VersionInfoCompany="Taehong Kim"
VersionInfoCopyright="Taehong Kim"
ArchitecturesInstallIn64BitMode="x64"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
Name: "{commondesktop}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
