import customtkinter as ctk
import sys
import os
import requests
import importlib.util
from pathlib import Path
from tkinter import messagebox
import threading
import json

# Добавляем пути для импорта
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mindustry_mod_creator', 'Creator'))

from mindustry_mod_creator.Creator.ui.main_window import MainWindow
from mindustry_mod_creator.Creator.utils.resource_utils import resource_path

ctk.set_appearance_mode("Dark")

class Updater:
    def __init__(self):
        self.github_base_url = "https://raw.githubusercontent.com/gbvxgzbwba/mindustry_mod_creator/main"
        self.github_api_url = "https://api.github.com/repos/gbvxgzbwba/mindustry_mod_creator/contents"
        self.local_base_path = Path("mindustry_mod_creator/Creator")
        
    def get_github_file_structure(self, path="Creator"):
        """Получает структуру файлов с GitHub"""
        try:
            url = f"{self.github_api_url}/{path}"
            print(f"Запрос к GitHub API: {url}")  # Для отладки
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            files_structure = {}
            
            for item in response.json():
                if item['type'] == 'file' and item['name'].endswith('.py'):
                    # Сохраняем относительный путь от Creator
                    relative_path = Path(item['path']).relative_to("Creator")
                    files_structure[str(relative_path)] = {
                        'path': item['path'],
                        'download_url': item['download_url']
                    }
                    print(f"Найден файл на GitHub: {relative_path}")  # Для отладки
                elif item['type'] == 'dir':
                    # Рекурсивно получаем файлы из поддиректорий
                    subdir_files = self.get_github_file_structure(item['path'])
                    files_structure.update(subdir_files)
            
            print(f"Всего файлов на GitHub: {len(files_structure)}")  # Для отладки
            return files_structure
            
        except Exception as e:
            print(f"Ошибка при получении структуры файлов с GitHub: {e}")
            return {}
    
    def get_local_file_structure(self):
        """Получает структуру локальных файлов"""
        local_files = {}
        
        if not self.local_base_path.exists():
            print("Локальная папка не существует, будут скачаны все файлы")
            return {}
            
        for root, dirs, files in os.walk(self.local_base_path):
            for file in files:
                if file.endswith('.py'):
                    local_path = Path(root) / file
                    relative_path = local_path.relative_to(self.local_base_path)
                    local_files[str(relative_path)] = local_path
                    print(f"Найден локальный файл: {relative_path}")  # Для отладки
        
        print(f"Всего локальных файлов: {len(local_files)}")  # Для отладки
        return local_files
    
    def get_local_version(self, file_path):
        """Получает версию из локального файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line in content.split('\n'):
                if line.strip().startswith('VERSION='):
                    version_str = line.split('=', 1)[1].strip()
                    version_str = version_str.strip('"\'').strip()
                    return version_str
                    
        except Exception as e:
            print(f"Ошибка при чтении версии из {file_path}: {e}")
            
        return None
    
    def get_remote_version(self, download_url):
        """Получает версию из файла на GitHub"""
        try:
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()
            
            for line in response.text.split('\n'):
                if line.strip().startswith('VERSION='):
                    version_str = line.split('=', 1)[1].strip()
                    version_str = version_str.strip('"\'').strip()
                    return version_str
                    
        except Exception as e:
            print(f"Ошибка при получении версии из GitHub: {e}")
            
        return None
    
    def download_file(self, download_url, relative_path):
        """Скачивает файл с GitHub"""
        try:
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()
            
            local_path = self.local_base_path / relative_path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print(f"Скачан: {relative_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка при скачивании {relative_path}: {e}")
            return False
    
    def compare_versions(self, version1, version2):
        """Сравнивает две версии (формат: X.Y.Z)"""
        try:
            if not version1 and version2:  # Локального файла нет, но есть на GitHub
                return True
            if not version2:  # На GitHub нет версии
                return False
                
            v1_parts = list(map(int, version1.split('.')))
            v2_parts = list(map(int, version2.split('.')))
            
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            return v1_parts < v2_parts
            
        except Exception as e:
            print(f"Ошибка при сравнении версий {version1} и {version2}: {e}")
            return False
    
    def check_for_updates(self):
        """Проверяет наличие обновлений и новых файлов"""
        files_to_update = []
        new_files_to_download = []
        
        print("Получение структуры файлов с GitHub...")
        github_files = self.get_github_file_structure()
        print("Получение структуры локальных файлов...")
        local_files = self.get_local_file_structure()
        
        # Проверяем существующие файлы на обновления
        for relative_path, local_path in local_files.items():
            if relative_path in github_files:
                local_version = self.get_local_version(local_path)
                remote_version = self.get_remote_version(github_files[relative_path]['download_url'])
                
                if self.compare_versions(local_version, remote_version):
                    files_to_update.append({
                        'path': relative_path,
                        'local_version': local_version,
                        'remote_version': remote_version,
                        'download_url': github_files[relative_path]['download_url']
                    })
                    print(f"Найдено обновление для {relative_path}: {local_version} -> {remote_version}")
        
        # Проверяем новые файлы на GitHub
        for relative_path, github_info in github_files.items():
            if relative_path not in local_files:
                remote_version = self.get_remote_version(github_info['download_url'])
                new_files_to_download.append({
                    'path': relative_path,
                    'remote_version': remote_version,
                    'download_url': github_info['download_url'],
                    'is_new': True
                })
                print(f"Найден новый файл: {relative_path} (версия: {remote_version})")
        
        return files_to_update, new_files_to_download
    
    def perform_update(self, files_to_update, new_files_to_download):
        """Выполняет обновление файлов и скачивание новых"""
        all_files = files_to_update + new_files_to_download
        
        if not all_files:
            return True, "Все файлы актуальны! Новых файлов нет."
        
        success_count = 0
        for file_info in all_files:
            if self.download_file(file_info['download_url'], file_info['path']):
                success_count += 1
        
        update_type = []
        if files_to_update:
            update_type.append(f"обновлено {len(files_to_update)} файлов")
        if new_files_to_download:
            update_type.append(f"добавлено {len(new_files_to_download)} новых файлов")
        
        message = f"Успешно {' и '.join(update_type)}. Всего обработано: {success_count}/{len(all_files)}"
        
        if success_count == len(all_files):
            return True, message
        else:
            return False, message + ". Возможны ошибки."

def check_updates_in_background(app_callback):
    """Проверяет обновления в фоновом потоке"""
    def check():
        try:
            updater = Updater()
            files_to_update, new_files_to_download = updater.check_for_updates()
            all_files = files_to_update + new_files_to_download
            
            if all_files:
                # Создаем список файлов для отображения
                update_list = []
                
                for file_info in files_to_update:
                    update_list.append(f"• {file_info['path']} (обновление: {file_info['local_version']} → {file_info['remote_version']})")
                
                for file_info in new_files_to_download:
                    update_list.append(f"• {file_info['path']} (новый файл: {file_info['remote_version']})")
                
                message = (
                    f"Найдены обновления и новые файлы ({len(all_files)}):\n\n"
                    f"{chr(10).join(update_list)}\n\n"
                    f"Хотите обновить сейчас?"
                )
                
                app_callback(message, files_to_update, new_files_to_download)
            else:
                print("Проверка обновлений: все файлы актуальны, новых файлов нет")
                app_callback(None, None, None)  # Нет обновлений
                
        except Exception as e:
            print(f"Ошибка при проверке обновлений: {e}")
            app_callback(f"Ошибка при проверке обновлений: {e}", None, None)
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()

class MainApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.main_window = None
        self.updates_checked = False
        
    def show_update_dialog(self, message, files_to_update, new_files_to_download):
        """Показывает диалог обновления"""
        self.updates_checked = True
        
        if message is None:  # Нет обновлений
            self.start_main_app()
            return
            
        if "Ошибка" in message:  # Ошибка при проверке
            messagebox.showwarning("Ошибка проверки", message, parent=self.root)
            self.start_main_app()
            return
            
        result = messagebox.askyesno(
            "Доступны обновления", 
            message,
            parent=self.root
        )
        
        if result:
            self.perform_update(files_to_update, new_files_to_download)
        else:
            self.start_main_app()
    
    def perform_update(self, files_to_update, new_files_to_download):
        """Выполняет обновление"""
        updater = Updater()
        success, message = updater.perform_update(files_to_update or [], new_files_to_download or [])
        
        if success:
            messagebox.showinfo("Обновление завершено", message, parent=self.root)
        else:
            messagebox.showwarning("Обновление с ошибками", message, parent=self.root)
        
        self.start_main_app()
    
    def start_main_app(self):
        """Запускает основное приложение"""
        try:
            # Убираем загрузочный экран
            for widget in self.root.winfo_children():
                widget.destroy()
            
            self.main_window = MainWindow(self.root)
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить приложение: {e}")
    
    def run(self):
        """Запускает приложение с проверкой обновлений"""
        self.root.title("Mindustry Mod Creator - Проверка обновлений")
        self.root.geometry("500x150")
        
        # Создаем загрузочный экран
        loading_label = ctk.CTkLabel(
            self.root, 
            text="Проверка обновлений...\nЭто может занять несколько секунд", 
            font=("Arial", 14),
            justify="center"
        )
        loading_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        progress_bar = ctk.CTkProgressBar(self.root)
        progress_bar.pack(fill="x", padx=20, pady=10)
        progress_bar.start()
        
        self.root.update()
        
        # Запускаем проверку обновлений в фоне
        check_updates_in_background(self.show_update_dialog)
        
        # Резервный запуск через 10 секунд
        self.root.after(10000, self.force_start_app)
    
    def force_start_app(self):
        """Принудительно запускает приложение если проверка зависла"""
        if not self.updates_checked:
            print("Принудительный запуск приложения...")
            self.start_main_app()

def main():
    app = MainApp()
    app.run()

if __name__ == "__main__":
    main()