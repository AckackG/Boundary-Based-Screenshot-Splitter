@echo off
:: 激活虚拟环境
call .\venv\Scripts\activate.bat

:: 启动程序
python image_cropper.py

:: 暂停，以便查看任何错误信息
pause 