@echo off
echo 正在创建虚拟环境...
python -m venv venv

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 设置完成！
echo 您现在可以运行 start.bat 来启动应用程序
pause 