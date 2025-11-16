import customtkinter as ctk
import json
import os
from tkinter import messagebox
from utils.cache_manager import CacheManager
from utils.resource_utils import safe_navigation
VERSION = "1.0"
class ModEditor:
    def __init__(self, root, mod_folder, main_app):
        self.root = root
        self.mod_folder = mod_folder
        self.main_app = main_app
        self.cache_manager = CacheManager(os.path.basename(mod_folder))
    
    def open_mod_editor(self, load_existing=False):
        """Открывает окно редактирования mod.json"""
        self.clear_window()

        # Заголовок окна
        title_label = ctk.CTkLabel(self.root, text="Редактирование mod.json", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Основной фрейм формы
        form_frame = ctk.CTkFrame(self.root)
        form_frame.pack(pady=10)

        # Поля ввода
        field_names = ["Название мода", "Автор", "Версия мода", "Описание"]
        self.entries = []

        for i, field in enumerate(field_names):
            label = ctk.CTkLabel(form_frame, text=field, anchor="w")
            entry = ctk.CTkEntry(form_frame, width=350)
            label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

        # Минимальная версия игры
        label_version = ctk.CTkLabel(form_frame, text="Минимальная версия игры")
        self.combo_version = ctk.CTkComboBox(form_frame, values=["149", "150", "151"], state="readonly", width=150)
        self.combo_version.set("151")

        label_version.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.combo_version.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Загрузка существующего mod.json
        if load_existing:
            self.load_existing_mod_json()

        # Кнопка сохранения
        button_create = ctk.CTkButton(
            self.root, 
            text="💾 Сохранить mod.json", 
            font=("Arial", 12),
            command=self.create_mod_json
        )
        button_create.pack(pady=20)
    
    def load_existing_mod_json(self):
        """Загрузка существующего mod.json"""
        mod_json_path = os.path.join(self.mod_folder, "mod.json")
        if os.path.exists(mod_json_path):
            with open(mod_json_path, "r", encoding="utf-8") as file:
                mod_data = json.load(file)
            self.entries[0].insert(0, mod_data.get("name", ""))
            self.entries[1].insert(0, mod_data.get("author", ""))
            self.entries[2].insert(0, mod_data.get("version", ""))
            self.entries[3].insert(0, mod_data.get("description", ""))
            self.combo_version.set(str(mod_data.get("minGameVersion", "149")))
    
    def create_mod_json(self):
        """Создаёт или обновляет mod.json"""
        name = self.entries[0].get().strip()
        author = self.entries[1].get().strip()
        version_mod = self.entries[2].get().strip()
        description = self.entries[3].get().strip()
        version_str = self.combo_version.get()
        
        try:
            version = float(version_str)
            version = int(version) if version.is_integer() else version
        except ValueError:
            messagebox.showerror("Ошибка", "Выберите корректную версию игры!")
            return

        if not name or not author or not description:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        mod_json_path = os.path.join(self.mod_folder, "mod.json")

        mod_data = {
            "name": name,
            "author": author,
            "version": version_mod,
            "description": description,
            "minGameVersion": version
        }

        with open(mod_json_path, "w", encoding="utf-8") as file:
            json.dump(mod_data, file, indent=4, ensure_ascii=False)

        messagebox.showinfo("Успех", f"Файл {mod_json_path} сохранён!")
        
        # Загружаем кэш и переходим к главному меню
        self.cache_manager.load_or_create_cache()
        safe_navigation(self.main_app.show_content_buttons)
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()