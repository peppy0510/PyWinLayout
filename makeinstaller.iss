; -- Example1.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=PyWinLayout
AppVerName=PyWinLayout 0.0.2
DefaultDirName={pf}\PyWinLayout
DefaultGroupName=PyWinLayout
UninstallDisplayIcon={app}\PyWinLayout.exe
Compression=lzma2
SolidCompression=yes
OutputDir="dist"
OutputBaseFilename=PyWinLayout 0.0.2

// SignTool=Standard $f

; SignTool=Standard $f
; SignTool=Standard /d $qmacroboxplayer$q $f 
; SignTool=Standard /d $qStonefield Query Installer$q $f
; SignTool="C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe" /x /y /d $qmacrobox.exe$q $f
; Standard="C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Bin\signtool.exe"
; "C:\Program Files\Inno Setup 5\iscc" "/sStandard=C:\Program Files\Microsoft Visual Studio 8\SDK\v2.0\Bin\signtool.exe sign /f CertPath\mycert.pfx /p MyPassword $p" sfquery.iss
; mycustom=signtool.exe $p
; byparam=$p
; SignTool=mystandard
; SignTool=mycustom /x /y /d $qMy Program$q $f
; SignTool=byparam signtool.exe /x /y /d $qMy Program$q $f

[Files]
; Source: "dist\PyRenamer\MyProg.exe"; DestDir: "{app}"
; Source: "distribute\MyProg.chm"; DestDir: "{app}"
; Source: "distribute\Readme.txt"; DestDir: "{app}"; Flags: isreadme
Source: "dist\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
Name: "{commondesktop}\PyWinLayout"; Filename: "{app}\PyWinLayout.exe"
