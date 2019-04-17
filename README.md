## Features

* Easily change layout with hotkey.
* Works as a taskbar tray icon.
* Support multi-monitor desktop environment.
* Built-in preset automatically adapts to pivot screen horizontal and vertical.
* You can enable and disable "Run on Windows startup" from the tray icon menu.
* Aligns minimum or maximum size limited applications such as music player exactly to the edge of screen.

## How to install

* Just download and install the latest release file.
* Alternatively, if you like to build your own, download or clone a repository then execute makebuild.py. Python 3.x, Python packages in the requirements.pip file, and Inno Setup is required.


## How to use

* Once you execute, then tray icon will shows up.
* Below table shows built-in preset.

| `NumLock is Turned On` |                    |                         |
|:----------------------:|:------------------:|:-----------------------:|
| `Win+Num7(TopLeft)`    | `Win+Num8(Top)`    | `Win+Num9(TopRight)`    |
| `Win+Num4(Left)`       | `Win+Num5(Middle)` | `Win+Num6(Right)`       |
| `Win+Num1(BottomLeft)` | `Win+Num2(Bottom)` | `Win+Num3(BottomRight)` |

* Each hotkey is switched differently depending on the aspect ratio of the screen.
* To control windows such as Task Manager, you must run in administrator mode.

## Supported platforms

* Microsoft Windows 10
* Other versions of Windows have not been tested yet.

## TODO

* Mac OSX support.
* Preset editor, and JSON support.
* Preset handler for very small size screen.
* Bypass UAC confirmation when execute as administrator mode.
