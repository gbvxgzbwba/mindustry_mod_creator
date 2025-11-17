import os
import re
import requests
import subprocess
import sys
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Добавляем пути для импорта
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / "mindustry_mod_creator" / "Creator"))

from mindustry_mod_creator.Creator.ui.main_window import MainWindow
from mindustry_mod_creator.Creator.utils.resource_utils import resource_path

ctk.set_appearance_mode("Dark")
from mindustry_mod_creator.Creator.utils.lang_system import LangT
def get_local_version(file_path):
    """Извлекает версию из локального файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'VERSION\s*=\s*"([\d.]+)"', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"{LangT("Ошибка при чтении файла")} {file_path}: {e}")
    return None

def get_github_file_version(relative_path):
    """Получает версию конкретного файла с GitHub"""
    try:
        # Конвертируем путь в формат GitHub (заменяем \ на /)
        github_path = relative_path.replace('\\', '/')
        url = f"https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main/Creator/{github_path}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            match = re.search(r'VERSION\s*=\s*"([\d.]+)"', content)
            if match:
                return match.group(1), content
            else:
                print(f"{LangT("VERSION не найден в файле")} {github_path} {LangT("на GitHub")}")
        else:
            print(f"{LangT("Ошибка HTTP")} {response.status_code} {LangT("для")} {github_path}")
    except Exception as e:
        print(f"{LangT("Ошибка при получении версии файла")} {relative_path} {LangT("с GitHub:")} {e}")
    return None, None

def compare_versions(version1, version2):
    """Сравнивает две версии в формате x.x"""
    if not version1 or not version2:
        return 0
    
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))
    
    # Дополняем до одинаковой длины
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
    return 0

def update_local_file(local_file_path, new_content):
    """Обновляет локальный файл с сохранением оригинального форматирования"""
    try:
        # Создаем директорию если не существует
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        with open(local_file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"{LangT("Ошибка при обновлении файла")} {local_file_path}: {e}")
    return False

def find_py_files_with_version():
    """Находит все .py файлы с определением VERSION в структуре mindustry_mod_creator/Creator/{folders}/{py_files}.py"""
    py_files = []
    base_path = Path(__file__).parent
    
    # Путь к папке mindustry_mod_creator/Creator
    creator_path = base_path / "mindustry_mod_creator" / "Creator"
    
    if not creator_path.exists():
        print(f"{LangT("Папка не найдена:")} {creator_path}")
        return py_files
    
    # Ищем все .py файлы в подпапках Creator
    for py_file in creator_path.rglob("*.py"):
        # Пропускаем файлы в корне Creator, ищем только в подпапках
        if py_file.parent == creator_path:
            continue
            
        version = get_local_version(py_file)
        if version:
            # Получаем относительный путь от Creator
            relative_path = py_file.relative_to(creator_path)
            py_files.append({
                'local_path': py_file,
                'relative_path': str(relative_path),
                'local_version': version
            })
    
    return py_files

def check_and_update_versions():
    """Проверяет версии всех файлов и предлагает обновление"""
    # Находим все локальные файлы с версиями
    local_files = find_py_files_with_version()
    
    if not local_files:
        print(LangT("Не найдены файлы с версиями для проверки"))
        return True
    
    files_to_update = []
    
    # Проверяем каждый файл
    for file_info in local_files:
        github_version, github_content = get_github_file_version(file_info['relative_path'])
        
        if not github_version:
            print(f"{LangT("Не удалось получить версию для")} {file_info['relative_path']} с GitHub")
            continue
        
        comparison = compare_versions(file_info['local_version'], github_version)
        
        if comparison < 0:
            files_to_update.append({
                'local_path': file_info['local_path'],
                'relative_path': file_info['relative_path'],
                'local_version': file_info['local_version'],
                'github_version': github_version,
                'github_content': github_content
            })
    
    # Если есть файлы для обновления, спрашиваем пользователя
    if files_to_update:
        update_info = "\n".join([
            f"- {file['relative_path']}: {file['local_version']} → {file['github_version']}"
            for file in files_to_update
        ])
        
        root = tk.Tk()
        root.withdraw()  # Скрываем основное окно
        
        result = messagebox.askyesno(
            LangT("Обновление доступно"),
            f"{LangT("Найдены обновления для следующих файлов:")}\n\n{update_info}\n\n{LangT("Обновить файлы?")}",
            parent=root
        )
        root.destroy()
        
        if result:
            # Обновляем файлы
            success_count = 0
            for file_info in files_to_update:
                success = update_local_file(file_info['local_path'], file_info['github_content'])
                if success:
                    print(f"{LangT("Успешно обновлен:")} {file_info['relative_path']}")
                    success_count += 1
                else:
                    print(f"{LangT("Ошибка при обновлении:")} {file_info['relative_path']}")
            
            if success_count > 0:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(LangT("Обновление завершено"), f"{LangT("Успешно обновлено")} {success_count} {LangT("файлов!")}")
                root.destroy()
                
                # Перезапускаем приложение после обновления
                print(LangT("Перезапуск приложения..."))
                python = sys.executable
                os.execl(python, python, *sys.argv)
                return False  # Важно: возвращаем False чтобы предотвратить запуск основного приложения
    
    return True

def main():
    # Сначала проверяем обновления
    print(LangT("Проверка обновлений..."))
    should_continue = check_and_update_versions()
    
    if should_continue:
        # Запускаем основное приложение только если не было обновления с перезапуском
        print(LangT("Запуск основного приложения..."))
        app = MainWindow()
        app.run()

if __name__ == "__main__":
    main()