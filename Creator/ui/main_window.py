import customtkinter as ctk
import os, json
from tkinter import messagebox
from utils.resource_utils import safe_navigation
from ui.mod_editor import ModEditor
VERSION = "1.0"
class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Mindustry Mod Creator")
        self.root.geometry("700x500")
        
        self.mod_name = None
        self.mod_folder = None
        self.setup_theme()
        
    def setup_theme(self):
        """Настройка темы приложения"""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_main_ui(self):
        """Главный интерфейс с списком модов"""
        self.clear_window()
        
        # Разделение на левую и правую части
        left_frame = ctk.CTkFrame(self.root, width=240)
        right_frame = ctk.CTkFrame(self.root)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Левая панель - список модов
        self.setup_mods_list(left_frame)
        
        # Правая панель - кнопка создания
        self.setup_create_section(right_frame)
    
    def setup_mods_list(self, parent):
        """Настройка списка модов"""
        mods_frame = ctk.CTkScrollableFrame(parent)
        mods_frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(mods_frame, text="Ваши моды", font=("Arial", 14)).pack(pady=5)

        # Заполнение списка модами
        mods_dir = os.path.join("mindustry_mod_creator", "mods")
        if os.path.exists(mods_dir):
            for mod_folder in sorted(os.listdir(mods_dir)):
                full_path = os.path.join(mods_dir, mod_folder)
                if os.path.isdir(full_path):
                    btn = ctk.CTkButton(
                        mods_frame, 
                        text=mod_folder,
                        width=200,
                        height=30,
                        command=lambda name=mod_folder: self.on_mod_click(name)
                    )
                    btn.pack(pady=3, padx=5)
    
    def setup_create_section(self, parent):
        """Настройка секции создания"""
        ctk.CTkButton(
            parent,
            text="Создать мод",
            width=200,
            height=50,
            font=("Arial", 14),
            command=self.show_create_ui
        ).pack(expand=True)
    
    def on_mod_click(self, mod_name):
        """Обработчик клика по моду"""
        try:
            self.mod_name = mod_name
            self.show_mod_name_ui_auto(auto_fill=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка открытия: {e}")
    
    def show_create_ui(self):
        """Показать UI создания нового мода"""
        self.mod_name = None
        self.show_mod_name_ui(auto_fill=False)
    
    def show_mod_name_ui_auto(self, auto_fill=False):
        """UI ввода имени мода с автоматическим открытием"""
        self.clear_window()
        self.root.geometry("500x500")
        
        label = ctk.CTkLabel(self.root, text="Название папки")
        self.entry_name = ctk.CTkEntry(self.root, width=200)
        
        if auto_fill and self.mod_name:
            self.entry_name.insert(0, self.mod_name)
        
        label.pack(pady=70)
        self.entry_name.pack(pady=10)
        
        # Автоматически переходим к настройке mod.json через короткую задержку
        self.root.after(100, self.setup_mod_json)

    def show_mod_name_ui(self, auto_fill=False):
        """UI ввода имени мода"""
        self.clear_window()
        self.root.geometry("500x500")
        
        label = ctk.CTkLabel(self.root, text="Название папки")
        self.entry_name = ctk.CTkEntry(self.root, width=200)
        
        if auto_fill and self.mod_name:
            self.entry_name.insert(0, self.mod_name)
        
        button_next = ctk.CTkButton(
            self.root, 
            text="Далее", 
            command=self.setup_mod_json
        )
        
        label.pack(pady=70)
        self.entry_name.pack(pady=10)
        button_next.pack(side=ctk.BOTTOM, pady=50)
    
    def setup_mod_json(self):
        """Настройка mod.json"""
        from ui.mod_editor import ModEditor
        
        self.mod_name = self.entry_name.get().strip()
        if not self.mod_name:
            messagebox.showerror("Ошибка", "Введите название папки!")
            return

        current_dir = os.path.join("mindustry_mod_creator", "mods")
        self.mod_folder = os.path.join(current_dir, self.mod_name)
        os.makedirs(self.mod_folder, exist_ok=True)

        # Проверяем существующий mod.json
        mod_json_path = os.path.join(self.mod_folder, "mod.json")
        
        if os.path.exists(mod_json_path):
            try:
                with open(mod_json_path, "r", encoding="utf-8") as file:
                    mod_data = json.load(file)
                
                # Проверяем, все ли поля заполнены
                required_fields = ["name", "author", "version", "description", "minGameVersion"]
                missing_fields = []
                
                for field in required_fields:
                    value = mod_data.get(field, "").strip() if isinstance(mod_data.get(field), str) else mod_data.get(field)
                    if not value:
                        missing_fields.append(field)
                
                # Если есть незаполненные поля или все поля заполнены - открываем редактор
                if missing_fields:
                    # Есть незаполненные поля - открываем редактор
                    mod_editor = ModEditor(self.root, self.mod_folder, self)
                    mod_editor.open_mod_editor(load_existing=True)
                else:
                    # Все поля заполнены - пропускаем редактор
                    from utils.cache_manager import CacheManager
                    cache_manager = CacheManager(self.mod_name)
                    cache_manager.load_or_create_cache()
                    safe_navigation(self.show_content_buttons)
                    
            except (json.JSONDecodeError, Exception) as e:
                # Если ошибка чтения файла - открываем редактор
                print(f"Ошибка чтения mod.json: {e}")
                mod_editor = ModEditor(self.root, self.mod_folder, self)
                mod_editor.open_mod_editor(load_existing=True)
        else:
            # Файла нет - открываем редактор для создания
            mod_editor = ModEditor(self.root, self.mod_folder, self)
            mod_editor.open_mod_editor(load_existing=False)
    
    # Добавляем эти методы в класс MainWindow:

    def show_content_buttons(self):
        """Показать меню контента"""
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self)
        content_editor.show_content_buttons()

    def show_block_creator(self):
        """Показать создатель блоков"""
        from ui.block_creator import BlockCreator
        block_creator = BlockCreator(self.root, self.mod_folder, self.mod_name, self)
        block_creator.show_block_creator()

    def show_paint_editor(self, item=None):
        """Показать редактор рисования"""
        from ui.paint_editor import PaintEditor
        paint_editor = PaintEditor(self.root, self.mod_folder, self.mod_name, item)

    def run(self):
        """Запуск приложения"""
        self.show_main_ui()
        self.root.mainloop()