@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Setup completed!
echo You can now run start.bat to launch the application
pause 