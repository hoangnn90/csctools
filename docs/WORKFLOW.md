# QT library
## What is QT ?
- a GUI library
- Create UI (button, edit text , etc)

## Why QT ?
- Cross platform

## How to draw UI using QT ?
- Create UI file (.ui) using QtCreator tool
- Use uic.loadUi function (inside library PyQT5) to load UI file


# Flow:
## setupUI()
- Load .ui file
- restore settings restoreSettings()
    - Use QSettings of QT
    - Store information filled before
    - Create QSettings in __init__ func
    - When load UI in setupUI(), restore settings by restoreSettings()
    - When window is closed, save settings by closeEvent()
- setup callback setupCallback()
    - Setup functions associated with events of each component (button - clicked, line edit - textChanged, comboBox - currentIndexChanged)
    - These functions will be called when event occured. E.g button OK clicked, function onConnectBtnClicked() will be called. 
## setupLog()
- Write log to TextEdit te_message

## Create OpenFileDialog window (but not show, show only when search is finished without any error)




