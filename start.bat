@echo off
chcp 65001 > nul
title Mindustry Mod Creator

echo ========================================
echo    Mindustry Mod Creator v1.7
echo ========================================
echo.

:: Проверяем Python
echo Проверяем Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем Python...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python-installer.exe
)

:: Быстрая проверка pip через pip help
echo Проверяем pip...
pip help >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем pip...
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    del get-pip.py
)

:: Проверяем и устанавливаем библиотеки
echo Проверяем библиотеки...
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем customtkinter...
    pip install customtkinter
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo Устанавливаем pillow...
    pip install pillow
)

if exist __pycache__ rmdir /s /q __pycache__

:: Запускаем приложение
echo.
echo ========================================
echo Запуск Mindustry Mod Creator...
echo ========================================
echo.

python ctk.py
pause