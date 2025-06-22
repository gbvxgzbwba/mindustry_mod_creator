@echo off
chcp 65001 > nul
title Mindustry Mod Creator

:: Проверяем, установлен ли Python
echo Проверяем установку Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python не найден, начинаем установку...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
    echo Установка Python 3.13.3... Пожалуйста, подождите...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python-installer.exe
    echo Установка Python завершена
)

:: Обновляем pip
echo Обновляем pip...
python -m pip install --upgrade pip >nul 2>&1

:: Устанавливаем необходимые библиотеки
echo Устанавливаем необходимые библиотеки...
pip install customtkinter >nul 2>&1

:: Запускаем приложение
echo Запуск Mindustry Mod Creator...
python ctk.py

pause