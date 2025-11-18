@echo off
chcp 65001 > nul
title Mindustry Mod Creator

:: Создаем ESC символ
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

echo %ESC%[92m========================================%ESC%[0m
echo %ESC%[96m   Mindustry Mod Creator v1.7%ESC%[0m
echo %ESC%[92m========================================%ESC%[0m
echo.

:: Проверяем Python
echo %ESC%[93mПроверяем Python...%ESC%[0m
python --version >nul 2>&1
if errorlevel 1 (
    echo %ESC%[91mPython не найден!%ESC%[0m
    echo %ESC%[93mУстанавливаем Python...%ESC%[0m
    curl -o python-installer.exe https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=0
    del python-installer.exe
    echo %ESC%[92mPython успешно установлен!%ESC%[0m
)

:: Быстрая проверка pip через pip help
echo %ESC%[93mПроверяем pip...%ESC%[0m
pip help >nul 2>&1
if errorlevel 1 (
    echo %ESC%[91mPip не найден!%ESC%[0m
    echo %ESC%[93mУстанавливаем pip...%ESC%[0m
    curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py
    python get-pip.py
    del get-pip.py
    echo %ESC%[92mPip успешно установлен!%ESC%[0m
)

:: Проверяем и устанавливаем библиотеки
echo %ESC%[93mПроверяем библиотеки...%ESC%[0m

python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo %ESC%[93mУстанавливаем customtkinter...%ESC%[0m
    pip install customtkinter
    echo %ESC%[92mcustomtkinter установлен!%ESC%[0m
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo %ESC%[93mУстанавливаем requests...%ESC%[0m
    pip install requests
    echo %ESC%[93mrequests установлен!%ESC%[0m
)

python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo %ESC%[93mУстанавливаем pillow...%ESC%[0m
    pip install pillow
    echo %ESC%[92mPillow установлен!%ESC%[0m
)

if exist __pycache__ (
    echo %ESC%[93mОчищаем кэш...%ESC%[0m
    rmdir /s /q __pycache__
    echo %ESC%[92mКэш очищен!%ESC%[0m
)

:: Запускаем приложение
echo.
echo %ESC%[92m========================================%ESC%[0m
echo %ESC%[96mЗапуск Mindustry Mod Creator...%ESC%[0m
echo %ESC%[92m========================================%ESC%[0m
echo.

cd /d "%~dp0"

:: Создаем необходимые папки
if not exist "mindustry_mod_creator/Creator/core" mkdir "mindustry_mod_creator/Creator/core"
if not exist "mindustry_mod_creator/Creator/data" mkdir "mindustry_mod_creator/Creator/data"
if not exist "mindustry_mod_creator/Creator/ui" mkdir "mindustry_mod_creator/Creator/ui"
if not exist "mindustry_mod_creator/Creator/utils" mkdir "mindustry_mod_creator/Creator/utils"
if not exist "mindustry_mod_creator/Creator/utils" mkdir "mindustry_mod_creator/Creator/langs"

:: Скачиваем файлы
if not exist "mindustry_mod_creator\Creator\core\block_types.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/core/block_types.py" -o "mindustry_mod_creator\Creator\core\block_types.py"
if not exist "mindustry_mod_creator\Creator\core\mod_manager.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/core/mod_manager.py" -o "mindustry_mod_creator\Creator\core\mod_manager.py"
if not exist "mindustry_mod_creator\Creator\data\default_cache.json" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/data/default_cache.json" -o "mindustry_mod_creator\Creator\data\default_cache.json"
if not exist "mindustry_mod_creator\Creator\ui\block_creator.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/ui/block_creator.py" -o "mindustry_mod_creator\Creator\ui\block_creator.py"
if not exist "mindustry_mod_creator\Creator\ui\content_editor.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/ui/content_editor.py" -o "mindustry_mod_creator\Creator\ui\content_editor.py"
if not exist "mindustry_mod_creator\Creator\ui\main_window.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/ui/main_window.py" -o "mindustry_mod_creator\Creator\ui\main_window.py"
if not exist "mindustry_mod_creator\Creator\ui\mod_editor.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/ui/mod_editor.py" -o "mindustry_mod_creator\Creator\ui\mod_editor.py"
if not exist "mindustry_mod_creator\Creator\ui\paint_editor.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/ui/paint_editor.py" -o "mindustry_mod_creator\Creator\ui\paint_editor.py"
if not exist "mindustry_mod_creator\Creator\utils\cache_manager.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/utils/cache_manager.py" -o "mindustry_mod_creator\Creator\utils\cache_manager.py"
if not exist "mindustry_mod_creator\Creator\utils\file_utils.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/utils/file_utils.py" -o "mindustry_mod_creator\Creator\utils\file_utils.py"
if not exist "mindustry_mod_creator\Creator\utils\resource_utils.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/utils/resource_utils.py" -o "mindustry_mod_creator\Creator\utils\resource_utils.py"
if not exist "mindustry_mod_creator\Creator\langs\ru.json" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/langs/ru.json" -o "mindustry_mod_creator\Creator\langs\ru.json"
if not exist "mindustry_mod_creator\Creator\langs\en.json" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/langs/en.json" -o "mindustry_mod_creator\Creator\langs\en.json"
if not exist "mindustry_mod_creator\Creator\utils\lang_system.py" curl -L "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/utils/lang_system.py" -o "mindustry_mod_creator\Creator\utils\lang_system.py"

python main.py