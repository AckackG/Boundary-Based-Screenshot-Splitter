@echo off
chcp 65001 > nul  & rem 设置代码页为 UTF-8，防止中文乱码

echo 正在检查虚拟环境...

rem 定义虚拟环境目录，请根据你的实际情况修改
set VIRTUAL_ENV_DIR=venv

rem 定义入口文件，这里是 main.py
set ENTRY_POINT=main.py

rem 定义输出目录
set OUTPUT_DIR=dist

rem 定义可执行文件名 (可选，如果不设置则默认使用入口文件名)
set EXE_NAME=BoundSplit

rem 定义是否使用窗口模式 (可选，设置为 1 使用窗口模式，设置为 0 使用控制台模式)
set WINDOWED_MODE=1

rem 定义图标文件路径 (可选)
set ICON_FILE=

rem 激活虚拟环境
if exist "%VIRTUAL_ENV_DIR%\Scripts\activate" (
    echo 发现虚拟环境，正在激活...
    call "%VIRTUAL_ENV_DIR%\Scripts\activate"
) else if exist "%VIRTUAL_ENV_DIR%\Scripts\activate.bat" (
    echo 发现虚拟环境，正在激活...
    call "%VIRTUAL_ENV_DIR%\Scripts\activate.bat"
) else (
    echo 未找到虚拟环境，将使用系统 Python 环境。
)

echo 正在执行 PyInstaller...

rem 构建 PyInstaller 命令
set PYINSTALLER_COMMAND=pyinstaller --onefile

rem 设置窗口模式
if "%WINDOWED_MODE%"=="1" (
    set PYINSTALLER_COMMAND=%PYINSTALLER_COMMAND% --windowed
)

rem 设置图标
if defined ICON_FILE (
    set PYINSTALLER_COMMAND=%PYINSTALLER_COMMAND% --icon="%ICON_FILE%"
)

rem 设置可执行文件名
if defined EXE_NAME (
    set PYINSTALLER_COMMAND=%PYINSTALLER_COMMAND% --name "%EXE_NAME%"
)

rem 添加其他 PyInstaller 选项 (如果有需要，例如 --add-data, --add-binary 等)
rem 例如: set PYINSTALLER_COMMAND=%PYINSTALLER_COMMAND% --add-data="src;dest"

rem 指定入口文件
set PYINSTALLER_COMMAND=%PYINSTALLER_COMMAND% "%ENTRY_POINT%"

echo 执行命令: %PYINSTALLER_COMMAND%
%PYINSTALLER_COMMAND%

echo PyInstaller 打包完成。可执行文件位于 %OUTPUT_DIR% 目录。

echo 正在清理临时文件...

rem 清理 build 目录
if exist "build" (
    echo 正在删除 build 目录...
    rmdir /s /q "build"
)

rem 清理 spec 文件
if exist "%ENTRY_POINT%.spec" (
    echo 正在删除 %ENTRY_POINT%.spec 文件...
    del /f /q "%ENTRY_POINT%.spec"
)

echo 临时文件清理完成。

rem 如果激活了虚拟环境，则取消激活
if exist "%VIRTUAL_ENV_DIR%\Scripts\deactivate" (
    call deactivate
) else if exist "%VIRTUAL_ENV_DIR%\Scripts\deactivate.bat" (
    call "%VIRTUAL_ENV_DIR%\Scripts\deactivate.bat"
)

pause