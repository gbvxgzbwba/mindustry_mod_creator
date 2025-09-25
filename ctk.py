import customtkinter as ctk
import urllib.request
import shutil
import json, os, sys
import zipfile
import tkinter as tk
import threading
import platform
import subprocess

from PIL import Image, ImageTk
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import messagebox, filedialog
from copy import deepcopy
from tkinter import colorchooser, messagebox

sys.dont_write_bytecode = True

theme = deepcopy(ctk.ThemeManager.theme)

theme["CTkButton"] = {
    "fg_color": "#128f1c", "corner_radius": 15,
    "text_color": "#FFFFFF", "border_width": 5,
    "hover_color": "#005A00", "border_color": "#005A00",
    "text_color_disabled": "#00F7FF"
}
theme["CTkEntry"] = {
    "fg_color": "#128f1c", "corner_radius": 15,
    "text_color": "#FFFFFF", "border_width": 5,
    "border_color": "#065500", "placeholder_text_color": "#222222"
}

# Настройка темы CTk
ctk.set_appearance_mode("Dark")  # Режим: "System", "Dark", "Light"
ctk.ThemeManager.theme = theme

requirements_list = []

CACHE_FILE = "cache.json"
def resource_path(relative_path):
    """Получаем путь к файлу при запуске из .exe и из .py"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_or_create_cache(mod_name):
    default_cache = {
        "_comment": "Не удаляйте этот фаил он нужен для работы исследования",
        "wall": [
            "copper-wall",
            "copper-wall-large",
            "titanium-wall",
            "titanium-wall-large",
            "plastanium-wall",
            "plastanium-wall-large",
            "thorium-wall",
            "thorium-wall-large",
            "surge-wall",
            "surge-wall-large",
            "phase-wall",
            "phase-wall-large"
        ],
        "ThermalGenerator": [
            "thermal-generator"
        ],
        "SolarGenerator": [
            "solar-panel",
            "solar-panel-large"
        ],
        "ConsumeGenerator": [
            "combustion-generator",
            "steam-generator",
            "rtg-generator",
            "differential-generator"
        ],
        "StorageBlock": [
            "container",
            "vault"
        ],
        "GenericCrafter": [
            "graphite-press",
            "pyratite-mixer",
            "blast-mixer",
            "silicon-smelter",
            "spore-press",
            "coal-centrifuge",
            "multi-press",
            "silicon-crucible",
            "plastanium-compressor",
            "phase-weaver",
            "kiln",
            "pulverizer",
            "melter",
            "surge-smelter",
            "separator",
            "cryofluid-mixer",
            "disassembler"
        ],
        "beam-node":[
            "beam-node"
        ],
        "conveyor": [
            "conveyor",
            "titanium-conveyor"
        ],
        "conduit": [
            "conduit",
            "pulse-conduit"
        ],
        "Pump": ["impulse-pump", "rotary-pump", "mechanical-pump"],
        "SolidPump": ["water-extractor"],
        "PowerNode": ["power-node", "power-node-large"],
        "router": ["Router", "Distributor"],
        "Junction": ["Junction"],
        "Unloader": ["Unloader"],
        "liquid_router": ["liquid-router"],
        "Liquid_Junction": ["Liquid-Junction"],
        "Liquid_Tank": ["liquid-container", "liquid-tank"],
        "Battery": ["Battery-large", "Battery"]
    }

    path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")
    cache_file_path = os.path.join("mindustry_mod_creator", "cache")
    os.makedirs(cache_file_path, exist_ok=True)
    
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_cache, f, indent=4, ensure_ascii=False)
        return default_cache
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            cache_data = json.load(f)
        
        # Проверяем и добавляем отсутствующие параметры - ДОБАВЬТЕ ЭТОТ БЛОК
        updated = False
        for key, default_value in default_cache.items():
            if key not in cache_data:
                cache_data[key] = default_value
                updated = True
            elif not isinstance(cache_data[key], list):
                cache_data[key] = default_value
                updated = True
        
        if updated:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=4, ensure_ascii=False)
        
        return cache_data
        
    except json.JSONDecodeError:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_cache, f, indent=4, ensure_ascii=False)
        return default_cache
    
class MindustryModCreator:
    mod_folder = None
    mod_name = None
    def main():
        def setup_mod_json():
            global mod_name
            mod_name = entry_name.get().strip()
            if not mod_name:
                messagebox.showerror("Ошибка", "Введите название папки!")
                return

            current_dir = os.path.join("mindustry_mod_creator", "mods")
            global mod_folder
            mod_folder = os.path.join(current_dir, mod_name)
            os.makedirs(mod_folder, exist_ok=True)

            cache_data = load_or_create_cache(mod_name)
            mod_json_path = os.path.join(mod_folder, "mod.json")

            if os.path.exists(mod_json_path):
                result = messagebox.askyesno("Файл уже существует", "mod.json уже существует. Перезаписать?")
                if result:
                    open_mod_editor(mod_folder, load_existing=True)
                else:
                    создание_кнопки()
            else:
                open_mod_editor(mod_folder, load_existing=False)

        def setup_mod_json_auto():
            global mod_name
            mod_name = entry_name.get().strip()
            if not mod_name:
                messagebox.showerror("Ошибка", "Введите название папки!")
                return

            current_dir = os.path.join("mindustry_mod_creator", "mods")
            global mod_folder
            mod_folder = os.path.join(current_dir, mod_name)
            os.makedirs(mod_folder, exist_ok=True)

            cache_data = load_or_create_cache(mod_name)
            mod_json_path = os.path.join(mod_folder, "mod.json")

            if os.path.exists(mod_json_path):
                    создание_кнопки()
            else:
                open_mod_editor(mod_folder, load_existing=False)

        def clear_window():
            for widget in root.winfo_children():
                widget.destroy()

        def open_mod_editor(mod_folder, load_existing=False):
            """Открывает окно редактирования mod.json"""
            clear_window()

            # Заголовок окна
            title_label = ctk.CTkLabel(root, text="Редактирование mod.json", font=("Arial", 16, "bold"))
            title_label.pack(pady=10)

            # Основной фрейм формы
            form_frame = ctk.CTkFrame(root)
            form_frame.pack(pady=10)

            # Подписи и поля ввода
            field_names = ["Название мода", "Автор", "Версия мода", "Описание"]
            entries = []

            for i, field in enumerate(field_names):
                label = ctk.CTkLabel(form_frame, text=field, anchor="w")
                entry = ctk.CTkEntry(form_frame, width=350)
                label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries.append(entry)

            # Минимальная версия игры (Combobox)
            label_version = ctk.CTkLabel(form_frame, text="Минимальная версия игры")
            combo_version = ctk.CTkComboBox(form_frame, values=["149", "150", "151"], state="readonly", width=150)
            combo_version.set("151")

            label_version.grid(row=4, column=0, sticky="w", padx=10, pady=5)
            combo_version.grid(row=4, column=1, padx=10, pady=5, sticky="w")

            # Загрузка существующего mod.json, если нужно
            if load_existing:
                mod_json_path = os.path.join(mod_folder, "mod.json")
                with open(mod_json_path, "r", encoding="utf-8") as file:
                    mod_data = json.load(file)
                entries[0].insert(0, mod_data.get("name", ""))
                entries[1].insert(0, mod_data.get("author", ""))
                entries[2].insert(0, mod_data.get("version", ""))
                entries[3].insert(0, mod_data.get("description", ""))
                combo_version.set(str(mod_data.get("minGameVersion", "149")))

            # Кнопка сохранения
            button_create = ctk.CTkButton(root, text="💾 Сохранить mod.json", font=("Arial", 12),
                                    command=lambda: create_mod_json(mod_folder, *entries, combo_version))
            button_create.pack(pady=20)

        def create_mod_json(mod_folder, entry_name_1, entry_name_2, entry_name_3, entry_name_4, combo_version):
            """Создаёт или обновляет mod.json"""
            name = entry_name_1.get().strip()
            author = entry_name_2.get().strip()
            version_mod = entry_name_3.get().strip()
            description = entry_name_4.get().strip()
            version_str = combo_version.get()
            try:
                version = float(version_str)
                # Если число целое — делаем int, иначе оставляем float
                version = int(version) if version.is_integer() else version
            except ValueError:
                messagebox.showerror("Ошибка", "Выберите корректную версию игры!")
                return


            if not name or not author or not description:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                return

            mod_json_path = os.path.join(mod_folder, "mod.json")

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

            создание_кнопки()

        def создание_кнопки():
            """Главное меню с просмотром контента"""

            def delete_item(item, content_type):
                """Удаление элемента с очисткой всех связанных данных"""
                # Определяем тип (для blocks - item["type"], для остальных - content_type)
                sprite_type = item["type"] if content_type == "blocks" else content_type
                item_name = item["name"]
                
                # Основные пути для проверки
                texture_folder = os.path.join(mod_folder, "sprites", sprite_type, item_name)  # sprites/type/name/
                single_texture = os.path.join(mod_folder, "sprites", sprite_type, f"{item_name}.png")  # sprites/type/name.png
                cache_path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")  # cache/modname.json

                # Формируем сообщение о том, что будет удалено
                confirm_msg = f"Вы уверены, что хотите удалить {content_type[:-1]} '{item_name}'?\n\n"
                confirm_msg += f"• Файл данных: {item['full_path']}\n"
                
                # Добавляем информацию о текстурах
                if os.path.exists(texture_folder):
                    confirm_msg += f"• Будет удалена ВСЯ папка с текстурами: {texture_folder}\n"
                elif os.path.exists(single_texture):
                    confirm_msg += f"• Будет удален файл текстуры: {single_texture}\n"
                else:
                    confirm_msg += "• Текстуры не найдены\n"

                # Запрашиваем подтверждение
                if not messagebox.askyesno("Подтверждение удаления", confirm_msg):
                    return

                try:
                    # 1. Удаляем основной файл данных
                    if os.path.exists(item["full_path"]):
                        os.remove(item["full_path"])

                    # 2. Удаляем текстуры (приоритет - удаление папки)
                    if os.path.exists(texture_folder):
                        shutil.rmtree(texture_folder)
                    elif os.path.exists(single_texture):
                        os.remove(single_texture)

                    # 3. Чистим кэш
                    item_removed = False  # Инициализируем переменную перед использованием
                    if os.path.exists(cache_path):
                        with open(cache_path, "r", encoding="utf-8") as f:
                            cache = json.load(f)
                        
                        # Ищем элемент во всех категориях кэша
                        for category in list(cache.keys()):  # Используем list() для безопасной итерации
                            if category == "_comment":
                                continue  # Пропускаем комментарий
                            
                            if isinstance(cache[category], list) and item_name in cache[category]:
                                cache[category].remove(item_name)
                                item_removed = True
                                
                                # Если категория стала пустой - удаляем её
                                if not cache[category]:
                                    del cache[category]
                                
                                break  # Прекращаем поиск после первого нахождения
                        
                        # Сохраняем изменения в кэше, если элемент был найден и удалён
                        if item_removed:
                            with open(cache_path, "w", encoding="utf-8") as f:
                                json.dump(cache, f, indent=4, ensure_ascii=False)

                    # Формируем сообщение о результате
                    result_msg = f"{content_type[:-1]} '{item_name}' успешно удален\n"
                    result_msg += "• Все связанные текстуры удалены\n" if os.path.exists(texture_folder) or os.path.exists(single_texture) else ""
                    
                    messagebox.showinfo("Успех", result_msg)
                    # Обновляем интерфейс
                    создание_кнопки()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")

            def edit_item_json(json_path):
                """Редактирование JSON файла"""
                if not os.path.exists(json_path):
                    messagebox.showerror("Ошибка", f"Файл не найден: {json_path}")
                    return
                
                with open(json_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Некорректный JSON файл")
                        return
                
                # Создаем окно редактора
                editor = ctk.CTkToplevel(root)
                editor.title(f"Редактор {os.path.basename(json_path)}")
                editor.geometry("800x600")

                editor.after(500, lambda: editor.focus_force())
                
                text_frame = ctk.CTkFrame(editor)
                text_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                text = ctk.CTkTextbox(text_frame, font=("Consolas", 12))
                text.pack(fill="both", expand=True)
                text.insert("1.0", json.dumps(data, indent=4, ensure_ascii=False))
                
                button_frame = ctk.CTkFrame(editor)
                button_frame.pack(pady=10)
                
                def save_changes():
                    try:
                        new_data = json.loads(text.get("1.0", tk.END))
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(new_data, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo("Успех", "Изменения сохранены")
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
                
                ctk.CTkButton(button_frame, text="Сохранить", command=save_changes).pack(side="left", padx=5)
                ctk.CTkButton(button_frame, text="Отмена", command=editor.destroy).pack(side="left", padx=5)

            def open_mod_folder():
                mods_folder = os.path.join("mindustry_mod_creator", "mods", f"{mod_name}")
                try:
                    if not os.path.exists(mods_folder):
                        messagebox.showerror("Ошибка", f"Папка с модами не существует:\n{mods_folder}")
                        return
                    
                    if platform.system() == "Windows":
                        os.startfile(mods_folder)
                    elif platform.system() == "Darwin":
                        subprocess.run(["open", mods_folder])
                    else:  # Linux
                        subprocess.run(["xdg-open", mods_folder])
                        
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")

            def create_zip():
                try:
                    folder_path = os.path.join("mindustry_mod_creator", "mods", mod_name)
                    zip_path = os.path.join(f"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Mindustry\\saves\\mods\\{mod_name}.zip")
                    #appdata = os.getenv('AppData')
                    #zip_path = os.path.join(f"{appdata}", "Mindustry/mods/", f"{mod_name}.zip")

                    if not os.path.exists(folder_path):
                        messagebox.showerror("Ошибка", f"Папка мода не существует:\n{folder_path}")
                        return None
                    
                    if not os.listdir(folder_path):
                        messagebox.showerror("Ошибка", f"Папка мода пуста:\n{folder_path}")
                        return None

                    # Удаляем старый ZIP-архив, если он существует
                    if os.path.exists(zip_path):
                        try:
                            os.remove(zip_path)
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Не удалось удалить старый архив:\n{str(e)}")
                            return None

                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(folder_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                                zipf.write(file_path, arcname)
                    
                    messagebox.showinfo("Успех", f"ZIP-архив мода создан:\n{zip_path}")
                    return zip_path
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось создать архив:\n{str(e)}")
                    return None

            def edit_requirements_from_context():
                """Редактор требований для блока, выбранного в главном меню"""
                if not hasattr(root, 'current_block_item'):
                    messagebox.showerror("Ошибка", "Блок не выбран")
                    return
                
                item = root.current_block_item
                block_name = item["name"]
                folder_path = os.path.dirname(item["full_path"])
                
                # Загружаем данные блока
                block_path = os.path.join(folder_path, f"{block_name}.json")
                if not os.path.exists(block_path):
                    messagebox.showerror("Ошибка", f"Файл блока не найден: {block_path}")
                    return
                
                with open(block_path, "r", encoding="utf-8") as f:
                    try:
                        block_data = json.load(f)
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Некорректный JSON файл блока.")
                        return
                
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join(mod_folder, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор требований: {block_name}, лимит 25000",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_item_icon(item_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{item_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки предметов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", 
                    "coal", "titanium", "thorium", "scrap", "silicon",
                    "plastanium", "phase-fabric", "surge-alloy", "spore-pod", 
                    "blast-compound", "pyratite"
                ]
                
                mod_items = []
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    mod_items = [f.replace(".json", "") for f in os.listdir(mod_items_path) if f.endswith(".json")]

                default_item_entries = {}
                mod_item_entries = {}

                def create_item_card(parent, item, is_mod_item=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_item_icon(item)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=item.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    int_value = tk.IntVar(value=0)
                    str_value = tk.StringVar(value="0")
                    max_value = 25000

                    if "research" in block_data and "requirements" in block_data["research"]:
                        for req in block_data["research"]["requirements"]:
                            if req["item"] == item:
                                str_value.set(str(req["amount"]))
                                break

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            int_value.set(int(val) if val else 0)
                        except:
                            int_value.set(0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        if not new_val.isdigit():
                            return False
                        if len(new_val) > 5:
                            return False
                        if int(new_val) > max_value:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = int(current) if current else 0
                            except ValueError:
                                current_num = 0
                            new_value = max(0, min(max_value, current_num + change))
                            str_value.set(str(new_value))
                        except Exception as e:
                            str_value.set("0")

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center",
                        command=lambda: update_value(-1)
                    )
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#BE6F24",
                        border_color="#613e11",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center",
                        command=lambda: update_value(1)
                    )
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_item:
                        mod_item_entries[item] = int_value
                    else:
                        default_item_entries[item] = int_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_item = item in mod_items
                        card = create_item_card(items_frame, item, is_mod_item)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем скроллируемый контейнер для всех предметов
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewheel(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                canvas.bind_all("<MouseWheel>", on_mousewheel)
                
                # Объединяем все предметы в один список
                all_items = default_items + mod_items
                update_grid(canvas, items_frame, all_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    requirements = []
                    
                    for item, var in default_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            requirements.append({"item": item, "amount": amount})
                    
                    for item, var in mod_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            requirements.append({"item": item, "amount": amount})
                    
                    if not requirements:
                        messagebox.showwarning("Ошибка", "Вы не добавили ни одного ресурса!")
                        return
                    
                    if "research" not in block_data:
                        block_data["research"] = {}
                    
                    block_data["research"]["requirements"] = requirements
                    
                    try:
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Требования для блока '{block_name}' успешно сохранены!")
                        создание_кнопки()
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить требования: {str(e)}")
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Отмена", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", 
                            border_color="#701c1c",
                            command=создание_кнопки).pack(side="left", padx=20)

            def edit_requirements_from_parent():
                """Редактор требований для блока, выбранного в главном меню"""
                if not hasattr(root, 'current_block_item'):
                    messagebox.showerror("Ошибка", "Блок не выбран")
                    return
                
                item = root.current_block_item
                block_name = item["name"]
                folder_path = os.path.dirname(item["full_path"])
                
                # Загружаем данные блока
                block_path = os.path.join(folder_path, f"{block_name}.json")
                if not os.path.exists(block_path):
                    messagebox.showerror("Ошибка", f"Файл блока не найден: {block_path}")
                    return
                
                with open(block_path, "r", encoding="utf-8") as f:
                    try:
                        block_data = json.load(f)
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Некорректный JSON файл блока.")
                        return
                
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join(mod_folder, "sprites", block_type, block_name, f"{block_name}.png")
                    if not os.path.exists(texture_path):
                        texture_path = os.path.join(mod_folder, "sprites", block_type, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Выберите родительский блок для: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                # Загрузка списка блоков из кэша
                mod_name = os.path.basename(mod_folder)
                cache_path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")
                blocks_list = []
                
                if os.path.exists(cache_path):
                    with open(cache_path, "r", encoding="utf-8") as f:
                        try:
                            cache_data = json.load(f)
                            # Получаем список блоков в формате {"type": "block_type", "name": "block_name"}
                            for block_type, blocks in cache_data.items():
                                if block_type == "_comment":
                                    continue
                                if isinstance(blocks, list):
                                    for block_name_in_cache in blocks:
                                        if block_name_in_cache:  # Пропускаем пустые имена
                                            blocks_list.append({
                                                "type": block_type,
                                                "name": block_name_in_cache
                                            })
                        except json.JSONDecodeError as e:
                            messagebox.showerror("Ошибка", f"Некорректный JSON файл кэша: {e}")
                            return
                
                # Фрейм для списка блоков с grid layout
                blocks_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                blocks_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Прокручиваемый canvas
                canvas = tk.Canvas(blocks_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(blocks_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                
                inner_frame = ctk.CTkFrame(canvas, fg_color="transparent")
                canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")
                
                # Функция для безопасной прокрутки
                def on_mousewheel(event):
                    try:
                        if canvas.winfo_exists():  # Проверяем, существует ли canvas
                            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    except:
                        pass  # Игнорируем ошибки, если canvas был уничтожен
                
                # Привязываем колесо мыши к canvas
                canvas.bind("<MouseWheel>", on_mousewheel)
                inner_frame.bind("<MouseWheel>", lambda e: canvas.event_generate("<MouseWheel>", delta=e.delta))
                
                def on_canvas_configure(event):
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    # Обновляем ширину внутреннего фрейма
                    canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                
                canvas.bind("<Configure>", on_canvas_configure)
                
                def load_block_icon(block_info):
                    if not isinstance(block_info, dict):
                        print("Ошибка: block_info должен быть словарем")
                        return None
                        
                    block_name = block_info.get("name")
                    if not block_name:
                        print("Ошибка: В block_info отсутствует 'name'")
                        return None
                    
                    block_types = {
                        "LiquidRouter",
                        "conveyor",
                        "wall",
                        "GenericCrafter",
                        "SolarGenerator",
                        "StorageBlock",
                        "conduit",
                        "ConsumeGenerator",
                        "PowerNode",
                        "Router",
                        "Junction",
                        "Unloader",
                        "LiquidJunction",
                        "Battery",
                        "ThermalGenerator"
                    }
                    block_types = {t for t in block_types if t is not None}

                    search_paths = []
                    for block_type in block_types:
                        search_paths.extend([
                            os.path.join(mod_folder, "sprites", block_type, block_name, f"{block_name}.png"),
                            os.path.join(mod_folder, "sprites", block_type, f"{block_name}.png")
                        ])
                    
                    search_paths.extend([
                        os.path.join("mindustry_mod_creator", "icons", f"{block_name}.png")
                    ])
                    
                    for path in search_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except Exception as e:
                                print(f"Ошибка загрузки изображения {path}: {e}")
                                continue
                    try:
                        print(f"Текстура для блока {block_name} не найдена. Создана заглушка")
                        empty_img = Image.new('RGBA', (50, 50), (100, 100, 100, 255))
                        return ctk.CTkImage(light_image=empty_img, size=(50, 50))
                    except Exception as e:
                        print(f"Ошибка создания заглушки: {e}")
                        return None
                
                def create_block_card(parent, block_info):
                    block_type = block_info["type"]
                    block_name_in_cache = block_info["name"]
                    
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            width=200,
                                            height=220)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Верхняя часть с иконкой и информацией
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="both", expand=True)
                    
                    icon = load_block_icon(block_info)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack(pady=5)
                    
                    ctk.CTkLabel(top_frame, 
                                text=block_name_in_cache,
                                font=("Arial", 14, "bold"),
                                anchor="center").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=f"Тип: {block_type}",
                                font=("Arial", 11),
                                anchor="center").pack()
                    
                    # Кнопка выбора
                    def on_select():
                        # Добавляем выбранный блок как parent
                        if "research" not in block_data:
                            block_data["research"] = {"parent": block_name_in_cache}
                        else:
                            block_data["research"]["parent"] = block_name_in_cache
                        
                        # Сохраняем изменения
                        try:
                            with open(block_path, "w", encoding="utf-8") as f:
                                json.dump(block_data, f, indent=4, ensure_ascii=False)
                            messagebox.showinfo("Успех", f"Родительский блок '{block_name_in_cache}' установлен")
                            edit_requirements_from_context()
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
                    
                    ctk.CTkButton(content_frame, 
                                text="Выбрать", 
                                command=on_select).pack(pady=5)
                    
                    return card_frame
                
                # Создаем карточки в grid layout
                columns = 4  # Количество колонок по умолчанию
                row = 0
                col = 0
                
                for i, block_info in enumerate(blocks_list):
                    if i % columns == 0 and i != 0:
                        row += 1
                        col = 0
                    
                    card = create_block_card(inner_frame, block_info)
                    card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    inner_frame.grid_columnconfigure(col, weight=1)
                    col += 1
                
                # Кнопка отмены
                buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                buttons_frame.pack(fill="x", pady=(10, 0))
                
                ctk.CTkButton(buttons_frame, 
                            text="Отмена", 
                            command=lambda:создание_кнопки(),
                            fg_color="#e62525",
                            hover_color="#701c1c").pack(side="right", padx=10)
                
                # Обновляем прокрутку после создания всех элементов
                inner_frame.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Функция для адаптивного изменения количества колонок
                def update_columns(event=None):
                    nonlocal columns
                    canvas_width = canvas.winfo_width()
                    if canvas_width > 1:
                        new_columns = max(1, canvas_width // 210)  # 200 (ширина карточки) + 10 (отступы)
                        if new_columns != columns:
                            columns = new_columns
                            rearrange_cards()
                
                def rearrange_cards():
                    # Удаляем все текущие карточки
                    for widget in inner_frame.winfo_children():
                        widget.destroy()
                    
                    # Создаем карточки заново с новым количеством колонок
                    row = 0
                    col = 0
                    for i, block_info in enumerate(blocks_list):
                        if i % columns == 0 and i != 0:
                            row += 1
                            col = 0
                        
                        card = create_block_card(inner_frame, block_info)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                        inner_frame.grid_columnconfigure(col, weight=1)
                        col += 1
                    
                    inner_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                
                # Привязываем обработчик изменения размера
                canvas.bind("<Configure>", lambda e: (on_canvas_configure(e), update_columns(e)))
                update_columns()

            def paint(item=None):
                """Редактор пиксельной графики 32x32 с шаблонами"""
                ctk.set_default_color_theme("blue")  # Или "green", "dark-blue" — встроенные темы
                # Глобальные переменные
                global current_color, grid_size, cell_size, canvas_size, current_tool, history, history_index, is_drawing, save_path
                
                # Настройки редактора
                current_color = "#000000"
                grid_size = 32
                cell_size = 20
                canvas_size = grid_size * cell_size
                current_tool = "pencil"
                history = []
                history_index = -1
                is_drawing = False

                if item is not None:
                    if "full_path" in item:
                        if "items" in item["full_path"]:
                            content_type = "items"
                        elif "liquids" in item["full_path"]:
                            content_type = "liquids"
                
                templates_dir = os.path.join("mindustry_mod_creator", "icons", "paint", content_type)
                os.makedirs(templates_dir, exist_ok=True)
                
                if item is None:
                    save_dir = os.path.join("mindustry_mod_creator", "icons", "paint")
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, "new_image.png")
                    item_name = "new_image"
                else:
                    item_name = item.get("name", "unnamed")
                    content_type = item.get("type", "items")
                    
                    possible_paths = [
                        os.path.join(mod_folder, "sprites", content_type, item_name, f"{item_name}.png"),
                        os.path.join(mod_folder, "sprites", content_type, f"{item_name}.png"),
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join(mod_folder, "sprites", "liquids", f"{item_name}.png"),
                        os.path.join(os.path.dirname(item.get("full_path", "")), f"{item_name}.png")
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            save_path = path
                            break
                    else:
                        save_dir = os.path.dirname(item.get("full_path", mod_folder))
                        os.makedirs(save_dir, exist_ok=True)
                        save_path = os.path.join(save_dir, f"{item_name}.png")

                # --- Функции истории ---
                def save_state():
                    global history, history_index
                    
                    if history_index < len(history) - 1:
                        history = history[:history_index + 1]
                    
                    state = []
                    for x in range(grid_size):
                        row = []
                        for y in range(grid_size):
                            items = canvas.find_withtag(f"pixel_{x}_{y}")
                            color = None
                            if items:
                                color = canvas.itemcget(items[0], "fill")
                            row.append(color)
                        state.append(row)
                    
                    history.append(state)
                    history_index = len(history) - 1

                def undo():
                    global history_index
                    if history_index > 0:
                        history_index -= 1
                        restore_state()

                def redo():
                    global history_index
                    if history_index < len(history) - 1:
                        history_index += 1
                        restore_state()

                def restore_state():
                    state = history[history_index]
                    canvas.delete("all")
                    draw_grid()
                    
                    for x in range(grid_size):
                        for y in range(grid_size):
                            if state[x][y] is not None:
                                canvas.create_rectangle(
                                    x * cell_size, y * cell_size,
                                    (x + 1) * cell_size, (y + 1) * cell_size,
                                    fill=state[x][y], outline="", tags=f"pixel_{x}_{y}"
                                )

                # --- Основные функции рисования ---
                def start_drawing(event):
                    global is_drawing
                    is_drawing = True
                    draw_pixel(event)
                    save_state()

                def draw_pixel(event):
                    if not is_drawing:
                        return
                        
                    x = event.x // cell_size
                    y = event.y // cell_size
                    if 0 <= x < grid_size and 0 <= y < grid_size:
                        canvas.delete(f"pixel_{x}_{y}")
                        if current_tool == "eraser":
                            return
                        elif current_tool in ["pencil", "fill"]:
                            canvas.create_rectangle(
                                x * cell_size, y * cell_size,
                                (x + 1) * cell_size, (y + 1) * cell_size,
                                fill=current_color, outline="", tags=f"pixel_{x}_{y}"
                            )

                def stop_drawing(event):
                    global is_drawing
                    is_drawing = False
                    save_state()

                def flood_fill(x, y, target_color, replacement_color):
                    if target_color == replacement_color:
                        return
                    if x < 0 or x >= grid_size or y < 0 or y >= grid_size:
                        return
                    
                    items = canvas.find_withtag(f"pixel_{x}_{y}")
                    current_pixel_color = None
                    if items:
                        current_pixel_color = canvas.itemcget(items[0], "fill")
                    
                    if current_pixel_color != target_color:
                        return
                    
                    canvas.delete(f"pixel_{x}_{y}")
                    canvas.create_rectangle(
                        x * cell_size, y * cell_size,
                        (x + 1) * cell_size, (y + 1) * cell_size,
                        fill=replacement_color, outline="", tags=f"pixel_{x}_{y}"
                    )
                    
                    flood_fill(x+1, y, target_color, replacement_color)
                    flood_fill(x-1, y, target_color, replacement_color)
                    flood_fill(x, y+1, target_color, replacement_color)
                    flood_fill(x, y-1, target_color, replacement_color)

                def handle_click(event):
                    x = event.x // cell_size
                    y = event.y // cell_size
                    if 0 <= x < grid_size and 0 <= y < grid_size:
                        if current_tool == "fill":
                            save_state()
                            items = canvas.find_withtag(f"pixel_{x}_{y}")
                            target_color = None
                            if items:
                                target_color = canvas.itemcget(items[0], "fill")
                            flood_fill(x, y, target_color, current_color)
                            save_state()
                        else:
                            start_drawing(event)

                def change_color():
                    global current_color
                    color = colorchooser.askcolor(title="Выберите цвет", initialcolor=current_color)
                    if color[1]:
                        current_color = color[1]
                        color_button.configure(fg_color=current_color)
                        set_tool("pencil")

                def clear_canvas():
                    canvas.delete("all")
                    draw_grid()
                    save_state()

                def draw_grid():
                    # Темно-серый фон
                    canvas.configure(bg="#e0e0e0")
                    for i in range(grid_size + 1):
                        # Вертикальные линии (толщина 2 пикселя)
                        canvas.create_line(
                            i * cell_size, 0, 
                            i * cell_size, canvas_size, 
                            fill="#d0d0d0", width=2  # ← Добавлен параметр width
                        )
                        # Горизонтальные линии (толщина 2 пикселя)
                        canvas.create_line(
                            0, i * cell_size, 
                            canvas_size, i * cell_size, 
                            fill="#d0d0d0", width=2  # ← Добавлен параметр width
                        )

                def save_image():
                    img = Image.new("RGBA", (grid_size, grid_size), (0, 0, 0, 0))
                    pixels = img.load()
                    
                    for x in range(grid_size):
                        for y in range(grid_size):
                            items = canvas.find_withtag(f"pixel_{x}_{y}")
                            if items:
                                color = canvas.itemcget(items[0], "fill")
                                if color:
                                    try:
                                        r, g, b = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                                        pixels[x, y] = (r, g, b, 255)
                                    except:
                                        pixels[x, y] = (0, 0, 0, 255)
                    
                    img.save(save_path)
                    messagebox.showinfo("Сохранено", f"Изображение сохранено в:\n{save_path}")

                def set_tool(tool):
                    global current_tool
                    current_tool = tool
                    
                    pencil_button.configure(fg_color="#2b2b2b")
                    eraser_button.configure(fg_color="#2b2b2b")
                    fill_button.configure(fg_color="#2b2b2b")
                    
                    if tool == "pencil":
                        pencil_button.configure(fg_color="#1f6aa5")
                    elif tool == "eraser":
                        eraser_button.configure(fg_color="#1f6aa5")
                    elif tool == "fill":
                        fill_button.configure(fg_color="#1f6aa5")

                def load_template_image(path):
                    try:
                        img = Image.open(path)
                        
                        if img.size != (32, 32):
                            img = img.resize((32, 32), Image.NEAREST)
                        
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        
                        pixels = img.load()
                        
                        clear_canvas()
                        
                        for x in range(32):
                            for y in range(32):
                                pixel = pixels[x, y]
                                if len(pixel) == 4:
                                    r, g, b, a = pixel
                                    if a > 0:
                                        color = f"#{r:02x}{g:02x}{b:02x}"
                                        canvas.create_rectangle(
                                            x * cell_size, y * cell_size,
                                            (x + 1) * cell_size, (y + 1) * cell_size,
                                            fill=color, outline="", tags=f"pixel_{x}_{y}"
                                        )
                        save_state()
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось загрузить шаблон: {e}")

                def show_templates():
                    templates = []
                    if os.path.exists(templates_dir):
                        for file in os.listdir(templates_dir):
                            if file.endswith(".png"):
                                templates.append({
                                    "name": file[:-4],
                                    "path": os.path.join(templates_dir, file)
                                })
                    
                    if not templates:
                        messagebox.showinfo("Шаблоны", f"В папке шаблонов ({content_type}) нет изображений")
                        return
                    
                    template_window = ctk.CTkToplevel(paint_window)
                    template_window.title("Выберите шаблон")
                    template_window.geometry("600x400")
                    
                    scroll_frame = ctk.CTkScrollableFrame(template_window)
                    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    for template in templates:
                        try:
                            img = Image.open(template["path"])
                            img = img.resize((64, 64), Image.NEAREST)
                            ctk_img = ctk.CTkImage(light_image=img, size=(64, 64))
                            
                            frame = ctk.CTkFrame(scroll_frame)
                            frame.pack(fill="x", pady=5)
                            
                            ctk.CTkLabel(frame, image=ctk_img, text="").pack(side="left", padx=10)
                            ctk.CTkLabel(frame, text=template["name"], font=("Arial", 14)).pack(side="left", padx=10)
                            
                            def load_template(path=template["path"]):
                                load_template_image(path)
                                template_window.destroy()
                            
                            ctk.CTkButton(frame, text="Загрузить", command=load_template).pack(side="right", padx=10)
                        except Exception as e:
                            print(f"Ошибка загрузки шаблона {template['name']}: {e}")

                # --- Создание интерфейса ---
                paint_window = ctk.CTkToplevel(root)
                paint_window.title(f"32x32 Pixel Editor - {item_name}")
                paint_window.resizable(False, False)

                canvas = ctk.CTkCanvas(paint_window, bg="#e0e0e0", width=canvas_size, height=canvas_size, highlightthickness=0)
                canvas.pack()

                tool_frame = ctk.CTkFrame(paint_window, fg_color="transparent")
                tool_frame.pack(fill="x", pady=(10, 0))

                ctk.CTkButton(
                    tool_frame,
                    text="< Отмена",
                    command=undo,
                    width=80,
                    fg_color="#555555",
                    hover_color="#444444"
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    tool_frame,
                    text="Повтор >",
                    command=redo,
                    width=80,
                    fg_color="#555555",
                    hover_color="#444444"
                ).pack(side="left", padx=2)

                pencil_button = ctk.CTkButton(
                    tool_frame, 
                    text="Карандаш",
                    command=lambda: set_tool("pencil"),
                    width=80,
                    fg_color="#1f6aa5"
                )
                pencil_button.pack(side="left", padx=5)

                eraser_button = ctk.CTkButton(
                    tool_frame,
                    text="Ластик",
                    command=lambda: set_tool("eraser"),
                    width=80
                )
                eraser_button.pack(side="left", padx=5)

                fill_button = ctk.CTkButton(
                    tool_frame,
                    text="Заливка",
                    command=lambda: set_tool("fill"),
                    width=80
                )
                fill_button.pack(side="left", padx=5)

                color_button = ctk.CTkButton(
                    tool_frame, 
                    text="Цвет", 
                    command=change_color,
                    fg_color=current_color,
                    hover_color=current_color,
                    width=80
                )
                color_button.pack(side="left", padx=5)

                ctk.CTkButton(
                    tool_frame,
                    text="Очистить",
                    command=clear_canvas,
                    width=80
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    tool_frame,
                    text="Шаблоны",
                    command=show_templates,
                    width=80,
                    fg_color="#4CAF50",
                    hover_color="#388E3C"
                ).pack(side="left", padx=5)

                ctk.CTkButton(
                    tool_frame,
                    text="Сохранить",
                    command=save_image,
                    width=80
                ).pack(side="left", padx=5)

                canvas.bind("<B1-Motion>", draw_pixel)
                canvas.bind("<Button-1>", handle_click)
                canvas.bind("<ButtonRelease-1>", stop_drawing)

                draw_grid()

                ctk.ThemeManager.theme = theme
                
                if os.path.exists(save_path):
                    try:
                        img = Image.open(save_path)
                        if img.size != (grid_size, grid_size):
                            img = img.resize((grid_size, grid_size), Image.NEAREST)
                        
                        if img.mode != "RGBA":
                            img = img.convert("RGBA")
                        
                        pixels = img.load()
                        for x in range(grid_size):
                            for y in range(grid_size):
                                r, g, b, a = pixels[x, y]
                                if a > 0:
                                    color = f"#{r:02x}{g:02x}{b:02x}"
                                    canvas.create_rectangle(
                                        x * cell_size, y * cell_size,
                                        (x + 1) * cell_size, (y + 1) * cell_size,
                                        fill=color, outline="", tags=f"pixel_{x}_{y}"
                                    )
                        save_state()
                    except Exception as e:
                        print(f"Ошибка загрузки изображения: {e}")
                        save_state()
                else:
                    save_state()

            def shem_import():
                appdata_path = os.getenv('APPDATA')
                if not appdata_path:
                    messagebox.showerror("Ошибка", "Не удалось найти папку AppData")
                    return
                
                # Формируем путь к папке схем Mindustry
                mindustry_schematics = os.path.join(appdata_path, 'Mindustry', 'schematics')
                
                file_path = filedialog.askopenfilename(
                    title="Выберите схему",
                    filetypes=(("Схемы", "*.msch"), ("Все файлы", "*.*")),
                    initialdir=mindustry_schematics
                )
                if not file_path:
                    return
                
                dest_dir = os.path.join(mod_folder, "schematics")
                
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    counter = 1
                    while True:
                        new_filename = f"{counter}.msch"
                        des_path = os.path.join(dest_dir, new_filename)
                        if not os.path.exists(des_path):
                            break
                        counter += 1
                        if counter > 100:
                            messagebox.showerror("Ошибка", "Достигнут лимит файлов (100)")
                            return

                    shutil.copy2(file_path, des_path)

                    messagebox.showinfo("Успех", f"Схема добавлена как {new_filename}")
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"{str(e)}")

            global mod_folder
            mod_folder = os.path.join("mindustry_mod_creator", "mods", f"{mod_name}")
            
            clear_window()
            root.configure(fg_color="#2b2b2b")

            # Основной контейнер
            main_frame = ctk.CTkFrame(root, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Левая панель с кнопками действий
            left_panel = ctk.CTkFrame(main_frame, width=200, fg_color="#3a3a3a", corner_radius=8)
            left_panel.pack(side="left", fill="y", padx=(0, 10))
            left_panel.pack_propagate(False)

            # Кнопки в левой панели
            action_buttons = [
                ("🧱 Создать блок", lambda: create_block(mod_name)),
                ("📦 Создать предмет", create_item_window),
                ("💧 Создать жидкость", create_liquid_window)
            ]

            action_buttons_2 = [
                ("📁 Создать ZIP", create_zip),
                ("📂 Открыть папку", open_mod_folder)
            ]

            for text, cmd in action_buttons:
                btn = ctk.CTkButton(
                    left_panel,
                    hover_color="#800000", border_color="#800000",
                    text=text,
                    width=180,
                    height=40,
                    font=("Arial", 14),
                    anchor="w",
                    command=cmd
                )
                btn.pack(pady=5, padx=10, fill="x")

            for text, cmd in action_buttons_2:
                btn = ctk.CTkButton(
                    left_panel,
                    hover_color="#001380", border_color="#001380",
                    text=text,
                    width=180,
                    height=40,
                    font=("Arial", 14),
                    anchor="w",
                    command=cmd
                )
                btn.pack(pady=5, padx=10, fill="x")

            # Основная область с контентом
            content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            content_frame.pack(side="right", fill="both", expand=True)

            # Вкладки для разных типов контента
            tabs = ctk.CTkTabview(content_frame)
            tabs.pack(fill="both", expand=True)
            
            # Создаем вкладки
            tabs.add("Блоки")
            tabs.add("Предметы") 
            tabs.add("Жидкости")

            # Функция для загрузки и отображения контента
            def load_content(tab_name, content_type):
                tab = tabs.tab(tab_name)
                
                # Основной контейнер без отступов
                main_frame = ctk.CTkFrame(tab, fg_color="#2b2b2b")
                main_frame.pack(fill="both", expand=True, padx=0, pady=0)

                # Настройка скроллинга
                canvas = tk.Canvas(main_frame, bg="#2b2b2b", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(main_frame, command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)

                # Контейнер для карточек
                content_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b")
                canvas.create_window((0, 0), window=content_frame, anchor="nw")

                # Получение списка элементов (как в оригинале)
                items = []
                content_path = os.path.join(mod_folder, "content", content_type)
                
                if not os.path.exists(content_path):
                    ctk.CTkLabel(content_frame, text=f"Папка {content_type} не найдена").pack(pady=20)
                    return

                if content_type == "blocks":
                    for block_type in os.listdir(content_path):
                        type_path = os.path.join(content_path, block_type)
                        if os.path.isdir(type_path):
                            for file in os.listdir(type_path):
                                if file.endswith(".json"):
                                    items.append({
                                        "name": os.path.splitext(file)[0],
                                        "type": block_type,
                                        "full_path": os.path.join(type_path, file)
                                    })
                else:
                    for file in os.listdir(content_path):
                        if file.endswith(".json"):
                            items.append({
                                "name": os.path.splitext(file)[0],
                                "full_path": os.path.join(content_path, file)
                            })

                if not items:
                    ctk.CTkLabel(content_frame, text=f"Нет {content_type} в моде").pack(pady=20)
                    return

                # Параметры карточек
                CARD_WIDTH = 170
                CARD_HEIGHT = 170
                MARGIN = 15  # Отступ между карточками
                
                # Функция создания карточки (оптимизированная)
                def create_card(parent, item):
                    card = ctk.CTkFrame(
                        parent,
                        width=CARD_WIDTH,
                        height=CARD_HEIGHT,
                        fg_color="#3a3a3a",
                        corner_radius=8,
                        border_width=1,
                        border_color="#4a4a4a"
                    )
                    card.pack_propagate(False)
                    
                    # Загрузка иконки
                    try:
                        # Функция для поиска файла изображения по возможным путям
                        def find_image_path(possible_paths):
                            for path in possible_paths:
                                if os.path.exists(path):
                                    return path
                            return None

                        # Функция создания CTkImage из пути
                        def create_ctk_image(img_path, size=(80, 80)):
                            if img_path and os.path.exists(img_path):
                                try:
                                    return ctk.CTkImage(Image.open(img_path), size=size)
                                except Exception as e:
                                    print(f"Ошибка загрузки изображения {img_path}: {e}")
                            return None

                        # Функция генерации возможных путей для слоя
                        def generate_layer_paths(mod_folder, item, content_type, layer_filename):
                            sprite_type = item.get("type", content_type)
                            base_paths = []
                            
                            # Особые случаи для conduit и conveyor
                            if item.get("type") == "conduit":
                                base_paths = [
                                    os.path.join(mod_folder, "sprites", "conduit", item["name"], layer_filename),
                                    os.path.join(mod_folder, "sprites", "conduit", layer_filename)
                                ]
                            elif item.get("type") == "conveyor":
                                base_paths = [
                                    os.path.join(mod_folder, "sprites", "conveyor", item["name"], layer_filename),
                                    os.path.join(mod_folder, "sprites", "conveyor", layer_filename)
                                ]
                            else:
                                # Общие пути для других типов
                                base_paths = [
                                    os.path.join(mod_folder, "sprites", sprite_type, item["name"], layer_filename),
                                    os.path.join(mod_folder, "sprites", sprite_type, layer_filename),
                                    os.path.join(mod_folder, "sprites", "items", item["name"], layer_filename),
                                    os.path.join(mod_folder, "sprites", "items", layer_filename),
                                    os.path.join(mod_folder, "sprites", "liquids", item["name"], layer_filename),
                                    os.path.join(mod_folder, "sprites", "liquids", layer_filename)
                                ]
                            
                            # Добавляем общий путь в sprites
                            base_paths.append(os.path.join(mod_folder, "sprites", layer_filename))
                            return base_paths

                        # Основная логика загрузки изображения
                        layers = item.get("layers", [
                            ["{name}.png", 1],
                            ["{name}-rotator.png", 2],
                            ["{name}-top.png", 3]
                        ])

                        img = None

                        # Если есть слои для композиции
                        if layers:
                            # Сортируем слои по номеру (чем больше цифра, тем выше слой)
                            sorted_layers = sorted(layers, key=lambda x: x[1])
                            temp_image = None
                            
                            for layer_template, layer_number in sorted_layers:
                                # Заменяем {name} на фактическое имя предмета
                                layer_filename = layer_template.replace("{name}", item["name"])
                                
                                # Генерируем возможные пути для слоя
                                possible_paths = generate_layer_paths(mod_folder, item, content_type, layer_filename)
                                layer_img_path = find_image_path(possible_paths)
                                
                                if not layer_img_path:
                                    continue
                                    
                                try:
                                    layer_img = Image.open(layer_img_path).convert("RGBA")
                                    
                                    # Если временное изображение еще не создано, инициализируем его
                                    if temp_image is None:
                                        temp_image = Image.new("RGBA", layer_img.size, (0, 0, 0, 0))
                                    
                                    # Накладываем текущий слой на временное изображение
                                    temp_image = Image.alpha_composite(temp_image, layer_img)
                                    
                                except Exception as e:
                                    print(f"Ошибка обработки слоя {layer_filename}: {e}")
                                    continue
                            
                            # Создаем финальное изображение если слои были успешно обработаны
                            if temp_image is not None:
                                img = ctk.CTkImage(temp_image, size=(80, 80))
                        
                        # Если слоев нет или композиция не удалась, используем обычную логику
                        if img is None:
                            sprite_type = item.get("type", content_type)
                            base_filename = f"{item['name']}.png"
                            
                            # Генерируем возможные пути для основного изображения
                            possible_paths = generate_layer_paths(mod_folder, item, content_type, base_filename)
                            img_path = find_image_path(possible_paths)
                            
                            if img_path:
                                img = create_ctk_image(img_path)

                    except Exception as e:
                        print(f"Критическая ошибка загрузки изображения для {item.get('name', 'unknown')}: {e}")
                        img = None
                    
                    ctk.CTkLabel(card, image=img, text="X" if not img else "", 
                                font=("Arial", 40) if not img else None).pack(pady=(10, 5))
                    
                    if "type" in item:
                        ctk.CTkLabel(card, text=item["type"], font=("Arial", 12, "bold")).pack(pady=(0, 5))
                    
                    ctk.CTkLabel(card, text=item["name"], font=("Arial", 12, "bold"),
                                wraplength=CARD_WIDTH-20).pack(pady=(0, 15))
                    
                    # Контекстное меню
                    menu = tk.Menu(root, tearoff=0)
                    menu.add_command(label="Удалить", command=lambda: delete_item(item, content_type))
                    menu.add_command(label="Редактировать JSON", command=lambda: edit_item_json(item["full_path"]))
                    
                    if content_type in ["items", "liquids"]:
                        menu.add_command(label="Редактор фото", command=lambda item=item: paint(item))
                    elif content_type == "blocks":
                        menu.add_command(label="Редактировать исследования", 
                                        command=lambda: [setattr(root, 'current_block_item', item), edit_requirements_from_parent()])
                    
                    def show_menu(e):
                        try: menu.tk_popup(e.x_root, e.y_root)
                        finally: menu.grab_release()
                    
                    card.bind("<Button-3>", show_menu)
                    card.bind("<Double-Button-1>", lambda e: edit_item_json(item["full_path"]))
                    
                    return card

                # Интеллектуальное размещение карточек
                def place_cards():
                    canvas.update_idletasks()
                    width = canvas.winfo_width()
                    
                    # Рассчитываем доступное пространство
                    cards_per_row = max(1, width // (CARD_WIDTH + MARGIN))
                    remaining_space = width - (cards_per_row * (CARD_WIDTH + MARGIN))
                    
                    # Очищаем предыдущее размещение
                    for widget in content_frame.winfo_children():
                        widget.destroy()
                    
                    current_row = None
                    for i, item in enumerate(items):
                        if i % cards_per_row == 0:
                            current_row = ctk.CTkFrame(content_frame, fg_color="transparent")
                            current_row.pack(fill="x", pady=0)
                        
                        card = create_card(current_row, item)
                        card.pack(side="left", padx=MARGIN//2)
                        
                        # Равномерное распределение оставшегося пространства
                        if i % cards_per_row == cards_per_row - 1 and remaining_space > 0:
                            extra = ctk.CTkFrame(current_row, width=remaining_space, fg_color="transparent")
                            extra.pack(side="left")

                    content_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))

                # Первоначальное размещение и обработка ресайза
                place_cards()
                canvas.bind("<Configure>", lambda e: place_cards())

            # Загружаем контент для каждой вкладки
            load_content("Блоки", "blocks")
            load_content("Предметы", "items") 
            load_content("Жидкости", "liquids")

        def create_item_window():
            """Форма для создания предмета"""
            clear_window()

            ctk.CTkLabel(root, text="Создание нового предмета", font=("Arial", 16, "bold")).pack(pady=10)

            form_frame = ctk.CTkFrame(root)
            form_frame.pack(pady=10)

            fields = [
                ("Название предмета", 150),
                ("Описание", 150),
                ("Воспламеняемость (0-1)", 150),
                ("Взрывоопасность (0-1)", 150),
                ("Радиоактивность (0-1)", 150),
                ("Заряд (0-1)", 150),
                ("Цвет (#rrggbb)", 150)
            ]

            entries = []

            for i, (label_text, width) in enumerate(fields):
                label = ctk.CTkLabel(form_frame, text=label_text)
                entry = ctk.CTkEntry(form_frame, width=width)
                label.grid(row=i, column=0, sticky="w", pady=5, padx=10)
                entry.grid(row=i, column=1, pady=5, padx=10)
                entries.append(entry)

            # Функция сохранения внутри
            def save_item():
                name = entries[0].get().strip().replace(" ", "_")
                desc = entries[1].get().strip()
                try:
                    flammability = float(entries[2].get())
                    explosiveness = float(entries[3].get())
                    radioactivity = float(entries[4].get())
                    charge = float(entries[5].get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Числовые значения должны быть от 0 до 1!")
                    return
                
                color = entries[6].get().strip()

                if not name or not desc:
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                    return

                content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "items")
                os.makedirs(content_folder, exist_ok=True)

                item_data = {
                    "name": name,
                    "description": desc,
                    "flammability": flammability,
                    "explosiveness": explosiveness,
                    "radioactivity": radioactivity,
                    "charge": charge,
                    "color": color
                }

                item_file_path = os.path.join(content_folder, f"{name}.json")
                with open(item_file_path, "w", encoding="utf-8") as file:
                    json.dump(item_data, file, indent=4, ensure_ascii=False)

                # Загрузка текстуры
                texture_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/ore/ore.png"  # можно сделать переменной позже
                sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", "items")
                texture_path = os.path.join(sprite_folder, f"{name}.png")
                os.makedirs(sprite_folder, exist_ok=True)

                if not os.path.exists(texture_path):
                    try:
                        urllib.request.urlretrieve(texture_url, texture_path)
                        print(f"Текстура {name}.png загружена.")
                    except Exception as e:
                        print(f"Ошибка при загрузке текстуры: {e}")
                else:
                    print("Текстура уже существует.")

                messagebox.showinfo("Успех", f"Предмет '{name}' сохранён!")
                создание_кнопки()

            # Кнопка сохранения
            ctk.CTkButton(root, text="💾 Сохранить предмет", font=("Arial", 12),
                    command=save_item).pack(pady=20)
            ctk.CTkButton(root, text="Назад", font=("Arial", 12),
                    command=lambda:создание_кнопки()).pack(pady=20)
            
        def create_liquid_window():            
            clear_window()

            ctk.CTkLabel(root, text="Создание новой жидкости", font=("Arial", 16, "bold")).pack(pady=10)

            form_frame = ctk.CTkFrame(root)
            form_frame.pack(pady=10)

            fields = [
                ("Название жидкости", 150),
                ("Описание", 150),
                ("Густота (0-1)", 150),
                ("Температура (0-1)", 150),
                ("Воспламеняемость (0-1)", 150),
                ("Взрывоопасность (0-1)", 150),
                ("Цвет (#rrggbb)", 150)
            ]

            entries = []

            for i, (label_text, width) in enumerate(fields):
                label = ctk.CTkLabel(form_frame, text=label_text)
                entry = ctk.CTkEntry(form_frame, width=width)
                label.grid(row=i, column=0, sticky="w", pady=5, padx=10)
                entry.grid(row=i, column=1, pady=5, padx=10)
                entries.append(entry)

            def save_liquid():
                name = entries[0].get().strip().replace(" ", "_")
                desc = entries[1].get().strip()

                try:
                    viscosity = float(entries[2].get())
                    temperature = float(entries[3].get())
                    flammability = float(entries[4].get())
                    explosiveness = float(entries[5].get())
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректное числовое значение!")
                    return

                color = entries[6].get().strip()

                if not name or not desc or not color:
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                    return

                content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "liquids")
                os.makedirs(content_folder, exist_ok=True)

                liquid_data = {
                    "name": name,
                    "description": desc,
                    "viscosity": viscosity,
                    "temperature": temperature,
                    "flammability": flammability,
                    "explosiveness": explosiveness,
                    "color": color
                }

                liquid_file_path = os.path.join(content_folder, f"{name}.json")
                with open(liquid_file_path, "w", encoding="utf-8") as file:
                    json.dump(liquid_data, file, indent=4, ensure_ascii=False)
                
                # Загрузка текстуры
                texture_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/items/liquid-water.png"  # можно сделать переменной позже
                sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", "liquids")
                texture_path = os.path.join(sprite_folder, f"{name}.png")
                os.makedirs(sprite_folder, exist_ok=True)

                if not os.path.exists(texture_path):
                    try:
                        urllib.request.urlretrieve(texture_url, texture_path)
                        print(f"Текстура {name}.png загружена.")
                    except Exception as e:
                        print(f"Ошибка при загрузке текстуры: {e}")
                else:
                    print("Текстура уже существует.")

                messagebox.showinfo("Успех", f"Жидкость '{name}' сохранена!")
                создание_кнопки()

            # Кнопка сохранения
            ctk.CTkButton(root, text="💾 Сохранить жидкость", font=("Arial", 12),
                    command=save_liquid).pack(pady=20)
            ctk.CTkButton(root, text="Назад", font=("Arial", 12),
                    command=lambda:создание_кнопки()).pack(pady=20)

        def name_exists_in_content(mod_folder, name, new_type):
            content_path = os.path.join(mod_folder, "content", "blocks")

            if not os.path.exists(content_path):
                return False  # Ничего нет — ничего не проверяем

            for block_type in os.listdir(content_path):
                type_folder = os.path.join(content_path, block_type)
                if not os.path.isdir(type_folder):
                    continue

                for file_name in os.listdir(type_folder):
                    base_name, ext = os.path.splitext(file_name)
                    if base_name == name:
                        if block_type == new_type:
                            result = messagebox.askquestion(
                                "Предупреждение",
                                f"Блок с именем '{name}' уже существует в типе '{new_type}'.\nВы хотите продолжить и обновить блок?",
                                icon='warning'
                            )
                            if result == "no":
                                return True  # Прекращаем
                            else:
                                return False  # Продолжаем
                        else:
                            messagebox.showerror(
                                "Ошибка",
                                f"Имя '{name}' уже используется в типе '{block_type}', а вы создаёте '{new_type}'."
                            )
                            return True
            return False

        def create_block(mod_name):
            global mod_folder
            mod_folder = os.path.join("mindustry_mod_creator", "mods", f"{mod_name}")
            icons_dir = os.path.join("mindustry_mod_creator", "icons") 
            os.makedirs(icons_dir, exist_ok=True)
            icons_folder = os.path.join("mindustry_mod_creator", "icons")

            def load_all_icons(parent_window=None):
                # Конфигурация загрузки
                download_configs = [
                    (
                        "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/items/",
                        ["copper", "lead", "metaglass", "graphite", "sand", "coal",
                        "titanium", "thorium", "scrap", "silicon", "plastanium",
                        "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite",
                        "water", "oil", "slag", "cryofluid"],
                        True
                    ),
                    (
                        "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/",
                        {
                            "copper-wall": {"layers": [["walls/copper-wall.png", 1]]},
                            "copper-wall-large": {"layers": [["walls/copper-wall-large.png", 1]]},
                            "titanium-wall": {"layers": [["walls/titanium-wall.png", 1]]},
                            "titanium-wall-large": {"layers": [["walls/titanium-wall-large.png", 1]]},
                            "plastanium-wall": {"layers": [["walls/plastanium-wall.png", 1]]},
                            "plastanium-wall-large": {"layers": [["walls/plastanium-wall-large.png", 1]]},
                            "thorium-wall": {"layers": [["walls/thorium-wall.png", 1]]},
                            "thorium-wall-large": {"layers": [["walls/thorium-wall-large.png", 1]]},
                            "surge-wall": {"layers": [["walls/surge-wall.png", 1]]},
                            "surge-wall-large": {"layers": [["walls/surge-wall-large.png", 1]]},
                            "phase-wall": {"layers": [["walls/phase-wall.png", 1]]},
                            "phase-wall-large": {"layers": [["walls/phase-wall-large.png", 1]]},

                            "liquid-router": {"layers": [ ["liquid/liquid-router.png", 2],["liquid/liquid-router-bottom.png", 1]]},
                            "bridge-conduit": {"layers": [["liquid/bridge-conduit.png", 1]]},
                            "phase-conduit": {"layers": [["liquid/phase-conduit.png", 1]]},
                            "conduit": {"layers": [["liquid/conduits/conduit-top-0.png", 2],["liquid/conduits/conduit-bottom.png", 1]]},
                            "pulse-conduit": {"layers": [["liquid/conduits/pulse-conduit-top-0.png", 2],["liquid/conduits/conduit-bottom.png", 1]]},
                            "liquid-junction": {"layers": [["liquid/liquid-junction.png", 1]]},
                            "liquid-container": {"layers": [["liquid/liquid-container.png", 2],["liquid/liquid-container-bottom.png", 1]]},
                            "liquid-tank": {"layers": [["liquid/liquid-tank.png", 2],["liquid/liquid-tank-bottom.png", 1]]},
                            "mechanical-pump": {"layers": [["liquid/mechanical-pump.png", 1]]},
                            "rotary-pump": {"layers": [["liquid/rotary-pump.png", 1]]},
                            "impulse-pump": {"layers": [["liquid/impulse-pump.png", 1]]},
                            "water-extractor": {"layers": [["drills/water-extractor.png", 1],["drills/water-extractor-rotator.png", 2],["drills/water-extractor-top.png", 3]]},

                            "container": {"layers": [["storage/container.png", 1],["storage/container-team.png", 2]]},
                            "vault": {"layers": [["storage/vault.png", 1],["storage/vault-team.png", 2]]},
                            "unloader": {"layers": [["storage/unloader.png", 1]]},

                            "thermal-generator": {"layers": [["power/thermal-generator.png", 1]]},
                            "battery": {"layers": [["power/battery.png", 1]]},
                            "battery-large": {"layers": [["power/battery-large.png", 1]]},
                            "steam-generator": {"layers": [["power/steam-generator.png", 1]]},
                            "rtg-generator": {"layers": [["power/rtg-generator.png", 1]]},
                            "solar-panel": {"layers": [["power/solar-panel.png", 1]]},
                            "solar-panel-large": {"layers": [["power/solar-panel-large.png", 1]]},
                            "power-node": {"layers": [["power/power-node.png", 1]]},
                            "power-node-large": {"layers": [["power/power-node-large.png", 1]]},
                            "beam-node": {"layers": [["power/beam-node.png", 1]]},
                            "combustion-generator": {"layers": [["power/combustion-generator.png", 1]]},
                            "differential-generator": {"layers": [["power/differential-generator.png", 1]]},

                            "router": {"layers": [["distribution/router.png", 1]]},
                            "bridge-conveyor": {"layers": [["distribution/bridge-conveyor.png", 1]]},
                            "phase-conveyor": {"layers": [["distribution/phase-conveyor.png", 1]]},
                            "distributor": {"layers": [["distribution/distributor.png", 1]]},
                            "junction": {"layers": [["distribution/junction.png", 1]]},
                            "titanium-conveyor": {"layers": [["distribution/conveyors/titanium-conveyor-0-0.png", 1]]},
                            "conveyor": {"layers": [["distribution/conveyors/conveyor-0-0.png", 1]]},

                            "silicon-smelter": {"layers": [["production/silicon-smelter.png", 1]]},
                            "graphite-press": {"layers": [["production/graphite-press.png", 1]]},
                            "pyratite-mixer": {"layers": [["production/pyratite-mixer.png", 1]]},
                            "blast-mixer": {"layers": [["production/blast-mixer.png", 1]]},
                            "kiln": {"layers": [["production/kiln.png", 1]]},
                            "spore-press": {"layers": [["production/spore-press.png", 2],["production/spore-press-bottom.png", 1],["production/spore-press-piston-icon.png", 3]]},
                            "coal-centrifuge": {"layers": [["production/coal-centrifuge.png", 1]]},
                            "multi-press": {"layers": [["production/multi-press.png", 1]]},
                            "silicon-crucible": {"layers": [["production/silicon-crucible.png", 1]]},
                            "plastanium-compressor": {"layers": [["production/plastanium-compressor.png", 1]]},
                            "phase-weaver": {"layers": [["production/phase-weaver.png", 2],["production/phase-weaver-bottom.png", 1],["production/phase-weaver-weave.png", 3]]},
                            "melter": {"layers": [["production/melter.png", 1]]},
                            "surge-smelter": {"layers": [["production/surge-smelter.png", 1]]},
                            "separator": {"layers": [["production/separator.png", 2],["production/separator-bottom.png", 1],["production/separator-spinner.png", 3]]},
                            "cryofluid-mixer": {"layers": [["production/cryofluid-mixer.png", 1]]},
                            "disassembler": {"layers": [["production/disassembler.png", 2],["production/disassembler-bottom.png", 1],["production/disassembler-spinner.png", 3]]},
                            "pulverizer": {"layers": [["production/pulverizer.png", 1],["production/pulverizer-top.png", 2],["production/pulverizer-rotator.png", 3]]}
                        },
                        False
                    )
                ]

                # Создаем папку для иконок, если ее нет
                os.makedirs(icons_folder, exist_ok=True)

                # Проверяем, какие файлы уже существуют
                existing_files = set(os.listdir(icons_folder)) if os.path.exists(icons_folder) else set()

                # Подсчет общего количества иконок (только тех, которых нет)
                total_icons = 0
                download_tasks = []
                merge_tasks = []  # Задачи для объединения слоев

                for base_url, name_icons, is_item in download_configs:
                    if isinstance(name_icons, dict):
                        for name, config in name_icons.items():
                            final_path = os.path.join(icons_folder, f"{name}.png")
                            
                            # Если финальный файл уже существует, пропускаем
                            if f"{name}.png" in existing_files:
                                continue
                            
                            # Для каждого слоя добавляем задачу загрузки
                            temp_files = []
                            for i, (layer_path, layer_num) in enumerate(config["layers"]):
                                temp_filename = f"{name}_temp_layer_{layer_num}.png"
                                temp_path = os.path.join(icons_folder, temp_filename)
                                total_icons += 1
                                download_tasks.append((base_url + layer_path, temp_path, name, layer_num))
                                temp_files.append((temp_path, layer_num))
                            
                            # Добавляем задачу объединения
                            merge_tasks.append((name, temp_files, final_path))
                                
                    else:
                        for name in name_icons:
                            if f"{name}.png" not in existing_files:
                                filename = f"liquid-{name}.png" if name in ["water", "oil", "slag", "cryofluid"] else f"item-{name}.png" if is_item else f"{name}.png"
                                total_icons += 1
                                download_tasks.append((base_url + filename, os.path.join(icons_folder, f"{name}.png"), name, 1))

                if total_icons == 0:
                    return True

                # Инициализация окна прогресса
                if parent_window:
                    progress_window = ctk.CTkToplevel(parent_window)
                    progress_window.title("Загрузка иконок")
                    progress_window.geometry("400x150")
                    progress_window.transient(parent_window)
                    progress_window.grab_set()
                    
                    progress_label = ctk.CTkLabel(progress_window, text=f"Загрузка {total_icons} иконок...")
                    progress_label.pack(pady=10)
                    
                    progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)
                    
                    status_label = ctk.CTkLabel(progress_window, text="0/0")
                    status_label.pack(pady=5)
                    
                    progress_window.update()

                downloaded = 0
                errors = []

                def update_progress(current, total, name, layer_num, stage="download"):
                    if parent_window:
                        progress = (current + 1) / total
                        progress_bar.set(progress)
                        if stage == "download":
                            status_label.configure(text=f"{current + 1}/{total} - {name} (слой {layer_num})")
                            progress_label.configure(text=f"Загружается: {name} - слой {layer_num}")
                        else:
                            status_label.configure(text=f"{current + 1}/{total} - {name} (объединение)")
                            progress_label.configure(text=f"Объединяется: {name}")
                        progress_window.update()

                def download_file(url, save_path, name, layer_num):
                    try:
                        urllib.request.urlretrieve(url, save_path)
                        return True, (name, layer_num)
                    except Exception as e:
                        return False, (name, layer_num, str(e))

                def merge_layers(name, temp_files, final_path):
                    try:
                        from PIL import Image
                        
                        # Сортируем слои по номеру (1 - низ, 2 - верх, 3 - самый верх)
                        temp_files.sort(key=lambda x: x[1])
                        
                        # Загружаем первый слой как основу
                        base_image = Image.open(temp_files[0][0]).convert("RGBA")
                        
                        # Накладываем остальные слои поверх
                        for temp_path, layer_num in temp_files[1:]:
                            layer_image = Image.open(temp_path).convert("RGBA")
                            base_image = Image.alpha_composite(base_image, layer_image)
                        
                        # Сохраняем объединенное изображение
                        base_image.save(final_path, "PNG")
                        
                        # Удаляем временные файлы
                        for temp_path, _ in temp_files:
                            os.remove(temp_path)
                            
                        return True, name
                    except Exception as e:
                        return False, (name, str(e))

                try:
                    # Загружаем все слои
                    with ThreadPoolExecutor(max_workers=4) as executor:
                        futures = {executor.submit(download_file, url, path, name, layer): (url, path, name, layer) for url, path, name, layer in download_tasks}
                        
                        for future in as_completed(futures):
                            url, path, name, layer = futures[future]
                            success, result = future.result()
                            
                            if success:
                                downloaded += 1
                                if parent_window:
                                    update_progress(downloaded, total_icons, name, layer, "download")
                            else:
                                name, layer, error = result
                                errors.append((name, layer, error))
                                downloaded += 1
                                if parent_window:
                                    progress_label.configure(text=f"Ошибка: {name} (слой {layer})")

                    # Объединяем слои
                    if merge_tasks:
                        total_merge = len(merge_tasks)
                        for i, (name, temp_files, final_path) in enumerate(merge_tasks):
                            if parent_window:
                                update_progress(i, total_merge, name, 0, "merge")
                            
                            success, result = merge_layers(name, temp_files, final_path)
                            if not success:
                                errors.append((name, "merge", result[1]))

                    # Вывод ошибок, если они есть
                    if errors:
                        error_msg = "\n".join(f"{name} ({'слой ' + str(layer) if isinstance(layer, int) else layer}): {error}" for name, layer, error in errors)
                        if parent_window:
                            messagebox.showwarning("Ошибки загрузки", f"Не удалось загрузить некоторые иконки:\n{error_msg}")
                        else:
                            print(f"Ошибки загрузки:\n{error_msg}")

                    if parent_window:
                        progress_label.configure(text="Загрузка завершена!")
                        progress_window.after(2000, progress_window.destroy)
                        
                    return True
                    
                except Exception as e:
                    error_msg = f"Критическая ошибка: {str(e)}"
                    if parent_window:
                        progress_label.configure(text=error_msg)
                        messagebox.showerror("Ошибка", error_msg)
                    else:
                        print(error_msg)
                    return False
            load_all_icons(root)
            def load_image(icon_name, size=(64, 64)):
                """Загрузка изображения с обработкой ошибок"""
                try:
                    img_path = os.path.join(icons_dir, icon_name)
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        return ctk.CTkImage(light_image=img, size=size)
                    
                    # Попробуем найти альтернативное имя (для обратной совместимости)
                    if icon_name.endswith(".png"):
                        base_name = icon_name[:-4]
                        alternatives = [
                            f"item-{base_name}.png",
                            f"liquid-{base_name}.png",
                            f"{base_name}.png"
                        ]
                        
                        for alt in alternatives:
                            alt_path = os.path.join(icons_dir, alt)
                            if os.path.exists(alt_path):
                                img = Image.open(alt_path)
                                return ctk.CTkImage(light_image=img, size=size)
                except Exception as e:
                    print(f"Ошибка загрузки изображения {icon_name}: {e}")
                return None

            clear_window()
            root.configure(fg_color="#3F3D3D")

            main_frame = ctk.CTkFrame(root, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)

            left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

            right_frame = ctk.CTkFrame(main_frame, width=150, fg_color="transparent")
            right_frame.pack(side="right", fill="y")

            back_btn = ctk.CTkButton(right_frame, text="Назад", height=60,
                                    font=("Arial", 14), command=lambda: создание_кнопки())
            back_btn.pack(fill="x", pady=(0, 10))

            #///////
            canvas = ctk.CTkCanvas(left_frame, bg="#2b2b2b", highlightthickness=0)
            scrollbar = ctk.CTkScrollbar(left_frame, orientation="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            scrollable_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b")
            window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            def resize_canvas(event):
                canvas_width = event.width
                canvas.itemconfig(window_id, width=canvas_width)

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", resize_canvas)

            blocks = [
                ("Стена", "copper-wall.png", lambda: cb_creator_b("wall")),
                ("Конвейер", "titanium-conveyor.png", lambda: cb_creator_b("conveyor")),
                ("Генератор", "steam-generator.png", lambda: cb_creator_b("ConsumeGenerator")),
                ("Солн. панель", "solar-panel.png", lambda: cb_creator_b("SolarGenerator")),
                ("Хранилище", "container.png", lambda: cb_creator_b("StorageBlock")),
                ("Завод", "silicon-smelter.png", lambda: cb_creator_b("GenericCrafter")),
                ("Труба", "conduit.png", lambda: cb_creator_b("conduit")),
                ("Энергоузел", "power-node.png", lambda: cb_creator_b("PowerNode")),
                ("Роутер", "router.png", lambda: cb_creator_b("router")),
                ("Перекрёсток", "junction.png", lambda: cb_creator_b("Junction")),
                ("Разгрушик", "unloader.png", lambda: cb_creator_b("Unloader")),
                ("Роутер жидкости", "liquid-router.png", lambda: cb_creator_b("liquid_router")),
                ("Перекрёсток жидкости", "liquid-junction.png", lambda: cb_creator_b("LiquidJunction")),
                ("Батарейка", "battery.png", lambda: cb_creator_b("Battery")),
                ("Термальный генератор", "thermal-generator.png", lambda: cb_creator_b("ThermalGenerator")),
                ("Жидкостный бак", "liquid-container.png", lambda: cb_creator_b("Liquid_Tank")),
                ("Лучевой узел", "beam-node.png", lambda: cb_creator_b("BeamNode")),
                ("Помпа", "rotary-pump.png", lambda: cb_creator_b("Pump")),
                ("Наземная помпа", "water-extractor.png", lambda: cb_creator_b("SolidPump"))
            ]

            blocks_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            blocks_container.pack(fill="both", expand=True, pady=10)

            def create_block_button(parent, text, icon_name, command):
                btn = ctk.CTkButton(
                    parent,
                    text=text,
                    width=120,
                    height=120,
                    font=("Arial", 12),
                    fg_color="#4753FF",
                    border_color="#1a0fbe",
                    hover_color="#1a0fbe",
                    corner_radius=0,
                    command=command
                )

                img = load_image(icon_name)
                if img:
                    btn.configure(image=img, compound="top")
                
                return btn

            def update_blocks_grid():
                container_width = blocks_container.winfo_width()
                if container_width < 1: return
                
                # Удаляем старые кнопки
                for widget in blocks_container.winfo_children():
                    widget.destroy()
                
                # Рассчитываем колонки
                btn_width = 120
                spacing = 10
                columns = max(1, container_width // (btn_width + spacing))
                
                # Создаем ряды
                for i in range(0, len(blocks), columns):
                    row_frame = ctk.CTkFrame(blocks_container, fg_color="transparent")
                    row_frame.pack(fill="x", pady=5)
                    
                    for block in blocks[i:i+columns]:
                        btn = create_block_button(
                            row_frame,
                            text=block[0],
                            icon_name=block[1],
                            command=block[2]
                        )
                        btn.pack(side="left", padx=5, expand=True)

            # Инициализация
            update_blocks_grid()
            blocks_container.bind("<Configure>", lambda e: update_blocks_grid())

            def on_resize(event):
                update_blocks_grid()

            blocks_container.bind("<Configure>", on_resize)

            def open_requirements_editor(block_name, block_data):
                clear_window()
                
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор ресурсов: {block_name}, {block_type}, максимум 70.000",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_item_icon(item_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{item_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки предметов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", 
                    "coal", "titanium", "thorium", "scrap", "silicon",
                    "plastanium", "phase-fabric", "surge-alloy", "spore-pod", 
                    "blast-compound", "pyratite"
                ]
                
                mod_items = []
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    mod_items = [f.replace(".json", "") for f in os.listdir(mod_items_path) if f.endswith(".json")]

                default_item_entries = {}
                mod_item_entries = {}

                def create_item_card(parent, item, is_mod_item=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_item_icon(item)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=item.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    int_value = tk.IntVar(value=0)
                    str_value = tk.StringVar(value="0")
                    max_value = 70000

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            int_value.set(int(val) if val else 0)
                        except:
                            int_value.set(0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        if not new_val.isdigit():
                            return False
                        if len(new_val) > 5:
                            return False
                        if int(new_val) > max_value:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    # Настройка grid layout
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = int(current) if current else 0
                            except ValueError:
                                current_num = 0
                            new_value = max(0, min(max_value, current_num + change))
                            str_value.set(str(new_value))
                        except Exception as e:
                            str_value.set("0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#BE6F24",
                        border_color="#613e11",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_item:
                        mod_item_entries[item] = int_value
                    else:
                        default_item_entries[item] = int_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_item = item in mod_items
                        card = create_item_card(items_frame, item, is_mod_item)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех предметов
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все предметы в один список
                all_items = default_items + mod_items
                update_grid(canvas, items_frame, all_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)
                
                def save_requirements():
                    requirements = []
                    
                    for item, var in default_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            requirements.append({"item": item, "amount": amount})
                    
                    for item, var in mod_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            requirements.append({"item": item, "amount": amount})
                    
                    if not requirements:
                        messagebox.showwarning("Ошибка", "Вы не добавили ни одного ресурса!")
                        return
                    
                    block_data["requirements"] = requirements
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        # Создаем окно прогресса и блокируем кнопки
                        progress_window = ctk.CTkToplevel(root)
                        progress_window.title("Загрузка текстур")
                        progress_window.geometry("400x150")
                        progress_window.transient(root)
                        progress_window.grab_set()
                        progress_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Блокируем закрытие
                        
                        progress_label = ctk.CTkLabel(progress_window, text="Подготовка к загрузке...")
                        progress_label.pack(pady=10)
                        
                        progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                        progress_bar.pack(pady=10)
                        progress_bar.set(0)
                        
                        status_label = ctk.CTkLabel(progress_window, text="0/0")
                        status_label.pack(pady=5)
                        
                        # Блокируем кнопки в основном окне
                        for child in btn_frame.winfo_children():
                            child.configure(state="disabled")

                        # Список текстур для загрузки
                        texture_names = []
                        base_url = ""

                        if block_type == "wall":
                            texture_names = ["copper-wall.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/walls/"

                        elif block_type == "Battery":
                            texture_names = ["battery.png", "battery-top.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "conveyor":
                            texture_names = [
                                "conveyor-0-0.png", "conveyor-0-1.png", "conveyor-0-2.png", "conveyor-0-3.png",
                                "conveyor-1-0.png", "conveyor-1-1.png", "conveyor-1-2.png", "conveyor-1-3.png",
                                "conveyor-2-0.png", "conveyor-2-1.png", "conveyor-2-2.png", "conveyor-2-3.png",
                                "conveyor-3-0.png", "conveyor-3-1.png", "conveyor-3-2.png", "conveyor-3-3.png",
                                "conveyor-4-0.png", "conveyor-4-1.png", "conveyor-4-2.png", "conveyor-4-3.png"
                            ]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/distribution/conveyors/"
                        elif block_type == "GenericCrafter":
                            texture_names = ["silicon-smelter.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/production/"
                        elif block_type == "SolarGenerator":
                            texture_names = ["solar-panel.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "StorageBlock":
                            texture_names = ["container.png","container-team.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/storage/"
                        elif block_type == "conduit":
                            texture_names = ["conduit-top-0.png", "conduit-top-1.png", "conduit-top-2.png", "conduit-top-3.png",
                                "conduit-top-4.png", "conduit-bottom-0.png", "conduit-bottom-1.png", "conduit-bottom-2.png",
                                "conduit-bottom-3.png", "conduit-bottom-4.png", "conduit-bottom.png"
                            ]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/liquid/conduits/"
                        elif block_type == "ConsumeGenerator":
                            texture_names = [
                                "rtg-generator.png"
                            ]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "PowerNode":
                            texture_names = ["power-node.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "Router":
                            texture_names = ["router.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/distribution/"
                        elif block_type == "Junction":
                            texture_names = ["junction.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/distribution/"
                        elif block_type == "Unloader":
                            texture_names = ["unloader.png", "unloader-center.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/storage/"
                        elif block_type == "LiquidRouter":
                            texture_names = ["liquid-router.png", "liquid-router-bottom.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/liquid/"
                        elif block_type == "LiquidJunction":
                            texture_names = ["liquid-junction.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/liquid/"
                        elif block_type == "ThermalGenerator":
                            texture_names = ["thermal-generator.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "BeamNode":
                            texture_names = ["beam-node.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/power/"
                        elif block_type == "Pump":
                            texture_names = ["rotary-pump.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/liquid/"
                        elif block_type == "SolidPump":
                            texture_names = ["water-extractor.png","water-extractor-rotator.png","water-extractor-top.png"]
                            base_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/blocks/drills/"
                        else:
                            raise ValueError(f"Неизвестный тип блока: {block_type}")

                        if len(texture_names) == 1:
                            sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type)
                        else:
                            sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)
                        
                        total_files = len(texture_names)
                        downloaded = 0
                        
                        def update_progress():
                            nonlocal downloaded
                            progress = downloaded / total_files
                            progress_bar.set(progress)
                            status_label.configure(text=f"{downloaded}/{total_files}")
                            progress_window.update()
                        
                        def resize_image(image_path, size_multiplier):
                            """Изменяет размер изображения согласно множителю (1=32px, 2=64px, ...)"""
                            from PIL import Image
                            try:
                                original_size = 32  # Базовый размер текстур Mindustry
                                new_size = original_size * size_multiplier
                                
                                img = Image.open(image_path)
                                if img.size != (new_size, new_size):
                                    img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
                                    img.save(image_path)
                            except Exception as e:
                                print(f"Ошибка при изменении размера {image_path}: {e}")
                        
                        def download_textures():
                            nonlocal downloaded
                            try:
                                size_multiplier = int(block_data.get("size", 1))
                                size_multiplier = max(1, min(15, size_multiplier))  # Ограничиваем диапазон 1-15
                                
                                for texture in texture_names:
                                    try:
                                        # Формируем новое имя файла
                                        if block_type == "battery":
                                            new_name = texture.replace("battery", block_name)
                                        elif block_type == "wall":
                                            new_name = texture.replace("copper-wall", block_name)
                                        elif block_type == "conveyor":
                                            new_name = texture.replace("conveyor", block_name)
                                        elif block_type == "GenericCrafter":
                                            new_name = texture.replace("silicon-smelter", block_name)
                                        elif block_type == "SolarGenerator":
                                            new_name = texture.replace("solar-panel", block_name)
                                        elif block_type == "StorageBlock":
                                            new_name = texture.replace("container", block_name)
                                        elif block_type == "conduit":
                                            new_name = texture.replace("conduit", block_name)
                                        elif block_type == "ConsumeGenerator":
                                            new_name = texture.replace("rtg-generator", block_name)
                                        elif block_type == "PowerNode":
                                            new_name = texture.replace("power-node", block_name)
                                        elif block_type == "Router":
                                            new_name = texture.replace("router", block_name)
                                        elif block_type == "Junction":
                                            new_name = texture.replace("junction", block_name)
                                        elif block_type == "Unloader":
                                            new_name = texture.replace("unloader", block_name)
                                        elif block_type == "LiquidRouter":
                                            new_name = texture.replace("liquid-router", block_name)
                                        elif block_type == "LiquidJunction":
                                            new_name = texture.replace("liquid-junction", block_name)
                                        elif block_type == "ThermalGenerator":
                                            new_name = texture.replace("thermal-generator", block_name)
                                        elif block_type == "BeamNode":
                                            new_name = texture.replace("beam-node", block_name)
                                        elif block_type == "Pump":
                                            new_name = texture.replace("rotary-pump", block_name)
                                        elif block_type == "SolidPump":
                                            new_name = texture.replace("water-extractor", block_name)
                                        else:
                                            new_name = f"{block_name}{texture[texture.find('-'):]}" if '-' in texture else f"{block_name}.png"
                                        
                                        texture_path = os.path.join(sprite_folder, new_name)
                                        
                                        if not os.path.exists(texture_path):
                                            texture_url = f"{base_url}{texture}"
                                            urllib.request.urlretrieve(texture_url, texture_path)
                                            resize_image(texture_path, size_multiplier)
                                            progress_label.configure(text=f"Загружено: {new_name}")
                                        
                                        downloaded += 1
                                        progress_window.after(100, update_progress)
                                    
                                    except Exception as e:
                                        progress_label.configure(text=f"Ошибка загрузки: {texture}")
                                        print(f"Ошибка при загрузке {texture}: {str(e)}")
                                        downloaded += 1  # Все равно увеличиваем счетчик
                                
                                progress_window.after(100, finish_saving)
                            
                            except Exception as e:
                                progress_window.after(100, lambda: error_occurred(str(e)))
                        
                        def finish_saving():
                            try:
                                block_path = os.path.join(content_folder, f"{block_name}.json")
                                with open(block_path, "w", encoding="utf-8") as f:
                                    json.dump(block_data, f, indent=4, ensure_ascii=False)
                                
                                progress_window.destroy()
                                for child in btn_frame.winfo_children():
                                    child.configure(state="normal")
                                
                                messagebox.showinfo("Успех", f"Блок '{block_name}' успешно сохранён!")
                                создание_кнопки()
                            
                            except Exception as e:
                                error_occurred(str(e))
                        
                        def error_occurred(error_msg):
                            progress_window.destroy()
                            for child in btn_frame.winfo_children():
                                child.configure(state="normal")
                            messagebox.showerror("Ошибка", f"Не удалось сохранить блок: {error_msg}")
                        
                        # Запускаем загрузку в отдельном потоке
                        threading.Thread(target=download_textures, daemon=True).start()

                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось начать сохранение: {str(e)}")
                        # Восстанавливаем состояние кнопок на случай ошибки
                        for child in btn_frame.winfo_children():
                            child.configure(state="normal")
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Отмена", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=создание_кнопки).pack(side="left", padx=20)

            def open_item_GenericCrafter_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор потребляемых предметов: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_item_icon(item_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{item_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки предметов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", 
                    "coal", "titanium", "thorium", "scrap", "silicon",
                    "plastanium", "phase-fabric", "surge-alloy", "spore-pod", 
                    "blast-compound", "pyratite"
                ]
                
                mod_items = []
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    mod_items = [f.replace(".json", "") for f in os.listdir(mod_items_path) if f.endswith(".json")]

                default_item_entries = {}
                mod_item_entries = {}

                def create_item_card(parent, item, is_mod_item=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_item_icon(item)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=item.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    int_value = tk.IntVar(value=0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            int_value.set(int(val) if val else 0)
                        except:
                            int_value.set(0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        if not new_val.isdigit():
                            return False
                        if len(new_val) > 2:
                            return False
                        if int(new_val) > max_value:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    # Настройка grid layout
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = int(current) if current else 0
                            except ValueError:
                                current_num = 0
                            new_value = max(0, min(max_value, current_num + change))
                            str_value.set(str(new_value))
                        except Exception as e:
                            str_value.set("0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#BE6F24",
                        border_color="#613e11",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_item:
                        mod_item_entries[item] = int_value
                    else:
                        default_item_entries[item] = int_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_item = item in mod_items
                        card = create_item_card(items_frame, item, is_mod_item)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех предметов
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все предметы в один список
                all_items = default_items + mod_items
                update_grid(canvas, items_frame, all_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    consumes_items = []
                    
                    for item, var in default_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            consumes_items.append({"item": item, "amount": amount})
                    
                    for item, var in mod_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            consumes_items.append({"item": item, "amount": amount})
                    
                    if not consumes_items:
                        messagebox.showwarning("Ошибка", "Вы не добавили ни одного предмета!")
                        return
                    
                    block_data["consumes"]["items"] = consumes_items
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Потребляемые предметы для блока '{block_name}' успешно сохранены!")
                        open_liquid_GenericCrafter_editor(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить предметы: {str(e)}")
                
                def skip_items():
                    open_liquid_GenericCrafter_editor(block_name, block_data)
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_items).pack(side="left", padx=20)

            def open_liquid_GenericCrafter_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор потребляемых жидкостей: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_liquid_icon(liquid_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{liquid_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                
                mod_liquids = []
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    mod_liquids = [f.replace(".json", "") for f in os.listdir(mod_liquids_path) if f.endswith(".json")]

                default_liquid_entries = {}
                mod_liquid_entries = {}

                def create_liquid_card(parent, liquid, is_mod_liquid=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_liquid_icon(liquid)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=liquid.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    float_value = tk.DoubleVar(value=0.0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50.0

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            float_value.set(float(val) if val else 0.0)
                        except:
                            float_value.set(0.0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        try:
                            val = float(new_val)
                            if val < 0 or val > max_value:
                                return False
                        except ValueError:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = float(current) if current else 0.0
                            except ValueError:
                                current_num = 0.0
                            new_value = max(0.0, min(max_value, current_num + change))
                            str_value.set(f"{new_value:.1f}")
                        except Exception as e:
                            str_value.set("0.0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-0.1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#3a7ebf",
                        border_color="#1f4b7a",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(0.1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("1.0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_liquid:
                        mod_liquid_entries[liquid] = float_value
                    else:
                        default_liquid_entries[liquid] = float_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_liquid = item in mod_liquids
                        card = create_liquid_card(items_frame, item, is_mod_liquid)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех жидкостей
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все жидкости в один список
                all_liquids = default_liquids + mod_liquids
                update_grid(canvas, items_frame, all_liquids)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_liquids))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    consumes_liquids = []
                    
                    for liquid, var in default_liquid_entries.items():
                        amount = var.get()
                        if amount > 0:
                            calculated_amount = round((1 / 60) * amount, 25)
                            consumes_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    for liquid, var in mod_liquid_entries.items():
                        amount = var.get()
                        if amount > 0:
                            calculated_amount = round((1 / 60) * amount, 25)
                            consumes_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    if not consumes_liquids and not block_data["consumes"].get("items"):
                        messagebox.showwarning("Ошибка", "Вы не добавили ни жидкостей, ни предметов!")
                        return
                    
                    block_data["consumes"]["liquids"] = consumes_liquids
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Потребляемые жидкости для блока '{block_name}' успешно сохранены!")
                        open_item_GenericCrafter_editor_out(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить жидкости: {str(e)}")
                
                def skip_liquids():
                    if not block_data["consumes"].get("items"):
                        messagebox.showerror("Ошибка", "Вы не добавили предмет, нельзя пропустить жидкость")
                    if block_data["consumes"].get("items"):
                        open_item_GenericCrafter_editor_out(block_name, block_data)
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_liquids).pack(side="left", padx=20)

            def open_item_GenericCrafter_editor_out(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор выходных предметов: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_item_icon(item_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{item_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки предметов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", 
                    "coal", "titanium", "thorium", "scrap", "silicon",
                    "plastanium", "phase-fabric", "surge-alloy", "spore-pod", 
                    "blast-compound", "pyratite"
                ]
                
                mod_items = []
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    mod_items = [f.replace(".json", "") for f in os.listdir(mod_items_path) if f.endswith(".json")]

                default_item_entries = {}
                mod_item_entries = {}

                def create_item_card(parent, item, is_mod_item=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_item_icon(item)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=item.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    int_value = tk.IntVar(value=0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            int_value.set(int(val) if val else 0)
                        except:
                            int_value.set(0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        if not new_val.isdigit():
                            return False
                        if len(new_val) > 2:
                            return False
                        if int(new_val) > max_value:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    # Настройка grid layout
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = int(current) if current else 0
                            except ValueError:
                                current_num = 0
                            new_value = max(0, min(max_value, current_num + change))
                            str_value.set(str(new_value))
                        except Exception as e:
                            str_value.set("0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#2e8b57",
                        border_color="#1a5232",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_item:
                        mod_item_entries[item] = int_value
                    else:
                        default_item_entries[item] = int_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_item = item in mod_items
                        card = create_item_card(items_frame, item, is_mod_item)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех предметов
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все предметы в один список
                all_items = default_items + mod_items
                update_grid(canvas, items_frame, all_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    output_items = []
                    
                    for item, var in default_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            output_items.append({"item": item, "amount": amount})
                    
                    for item, var in mod_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            output_items.append({"item": item, "amount": amount})
                    
                    if not output_items and not block_data.get("outputLiquids"):
                        messagebox.showwarning("Ошибка", "Вы не добавили ни предметов, ни жидкостей!")
                        return
                    
                    block_data["outputItems"] = output_items
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Выходные предметы для блока '{block_name}' успешно сохранены!")
                        open_liquid_GenericCrafter_editor_out(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить предметы: {str(e)}")
                
                def skip_items():
                    open_liquid_GenericCrafter_editor_out(block_name, block_data)
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_items).pack(side="left", padx=20)

            def open_liquid_GenericCrafter_editor_out(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор выходных жидкостей: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_liquid_icon(liquid_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{liquid_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                
                mod_liquids = []
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    mod_liquids = [f.replace(".json", "") for f in os.listdir(mod_liquids_path) if f.endswith(".json")]

                default_liquid_entries = {}
                mod_liquid_entries = {}

                def create_liquid_card(parent, liquid, is_mod_liquid=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_liquid_icon(liquid)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=liquid.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    float_value = tk.DoubleVar(value=0.0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50.0

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            float_value.set(float(val) if val else 0.0)
                        except:
                            float_value.set(0.0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        try:
                            val = float(new_val)
                            if val < 0 or val > max_value:
                                return False
                        except ValueError:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = float(current) if current else 0.0
                            except ValueError:
                                current_num = 0.0
                            new_value = max(0.0, min(max_value, current_num + change))
                            str_value.set(f"{new_value:.1f}")
                        except Exception as e:
                            str_value.set("0.0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-0.1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#3a7ebf",
                        border_color="#1f4b7a",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(0.1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("1.0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_liquid:
                        mod_liquid_entries[liquid] = float_value
                    else:
                        default_liquid_entries[liquid] = float_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_liquid = item in mod_liquids
                        card = create_liquid_card(items_frame, item, is_mod_liquid)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех жидкостей
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все жидкости в один список
                all_liquids = default_liquids + mod_liquids
                update_grid(canvas, items_frame, all_liquids)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_liquids))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    output_liquids = []
                    
                    for liquid, var in default_liquid_entries.items():
                        amount = var.get()
                        if amount > 0:
                            calculated_amount = round((1 / 60) * amount, 25)
                            output_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    for liquid, var in mod_liquid_entries.items():
                        amount = var.get()
                        if amount > 0:
                            calculated_amount = round((1 / 60) * amount, 25)
                            output_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    if not output_liquids and not block_data.get("outputItems"):
                        messagebox.showwarning("Ошибка", "Вы не добавили ни жидкостей, ни предметов!")
                        return
                    
                    block_data["outputLiquids"] = output_liquids
                    clean_empty_consumes(block_data)
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Выходные жидкости для блока '{block_name}' успешно сохранены!")
                        open_requirements_editor(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить жидкости: {str(e)}")
                
                def skip_liquids():
                    if not block_data.get("outputItems"):
                        messagebox.showerror("Ошибка", "Вы не добавили предмет, нельзя пропустить жидкость")
                    if block_data.get("outputItems"):
                        clean_empty_consumes(block_data)
                        open_requirements_editor(block_name, block_data)

                def clean_empty_consumes(block_data):
                    """
                    Проверяет и удаляет пустые массивы в структуре consumes и outputLiquids/outputItems
                    """
                    # Проверяем и очищаем consumes
                    if "consumes" in block_data:
                        consumes = block_data["consumes"]
                        
                        # Если consumes пустой объект, удаляем его
                        if consumes == {}:
                            del block_data["consumes"]
                        else:
                            # Удаляем пустые массивы внутри consumes
                            if "items" in consumes and isinstance(consumes["items"], list) and len(consumes["items"]) == 0:
                                del consumes["items"]
                            
                            if "liquids" in consumes and isinstance(consumes["liquids"], list) and len(consumes["liquids"]) == 0:
                                del consumes["liquids"]
                            
                            # Если после очистки consumes стал пустым, удаляем его полностью
                            if consumes == {}:
                                del block_data["consumes"]
                    
                    # Проверяем и очищаем outputLiquids
                    if "outputLiquids" in block_data and isinstance(block_data["outputLiquids"], list) and len(block_data["outputLiquids"]) == 0:
                        del block_data["outputLiquids"]
                    
                    # Проверяем и очищаем outputItems
                    if "outputItems" in block_data and isinstance(block_data["outputItems"], list) and len(block_data["outputItems"]) == 0:
                        del block_data["outputItems"]

                    if "liquidCapacity" in block_data and isinstance(block_data["liquidCapacity"], list) and len(block_data["liquidCapacity"]) == 0:
                        del block_data["liquidCapacity"]
                    
                    if "itemCapacity" in block_data and isinstance(block_data["itemCapacity"], list) and len(block_data["itemCapacity"]) == 0:
                        del block_data["itemCapacity"]
                    
                    return block_data
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_liquids).pack(side="left", padx=20)

            def open_item_consumes_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор потребляемых предметов: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_item_icon(item_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "items", f"{item_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{item_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки предметов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", 
                    "coal", "titanium", "thorium", "scrap", "silicon",
                    "plastanium", "phase-fabric", "surge-alloy", "spore-pod", 
                    "blast-compound", "pyratite"
                ]
                
                mod_items = []
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    mod_items = [f.replace(".json", "") for f in os.listdir(mod_items_path) if f.endswith(".json")]

                default_item_entries = {}
                mod_item_entries = {}

                def create_item_card(parent, item, is_mod_item=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_item_icon(item)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=item.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    int_value = tk.IntVar(value=0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            int_value.set(int(val) if val else 0)
                        except:
                            int_value.set(0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        if not new_val.isdigit():
                            return False
                        if len(new_val) > 2:
                            return False
                        if int(new_val) > max_value:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    # Настройка grid layout
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = int(current) if current else 0
                            except ValueError:
                                current_num = 0
                            new_value = max(0, min(max_value, current_num + change))
                            str_value.set(str(new_value))
                        except Exception as e:
                            str_value.set("0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#BE6F24",
                        border_color="#613e11",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_item:
                        mod_item_entries[item] = int_value
                    else:
                        default_item_entries[item] = int_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_item = item in mod_items
                        card = create_item_card(items_frame, item, is_mod_item)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех предметов
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все предметы в один список
                all_items = default_items + mod_items
                update_grid(canvas, items_frame, all_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    consumes_items = []
                    
                    for item, var in default_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            consumes_items.append({"item": item, "amount": amount})
                    
                    for item, var in mod_item_entries.items():
                        amount = var.get()
                        if amount > 0:
                            consumes_items.append({"item": item, "amount": amount})
                    
                    if not consumes_items and not block_data["consumes"].get("liquids"):
                        messagebox.showerror("Ошибка", "Должно быть хотя бы что-то одно: предметы ИЛИ жидкости!")
                        return
                    
                    block_data["consumes"]["items"] = consumes_items
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Потребляемые предметы для блока '{block_name}' успешно сохранены!")
                        open_liquid_consumes_editor(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить предметы: {str(e)}")
                
                def skip_items():
                    open_liquid_consumes_editor(block_name, block_data)
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_items).pack(side="left", padx=20)

            def open_liquid_consumes_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Редактор потребляемых жидкостей: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_liquid_icon(liquid_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{liquid_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                
                mod_liquids = []
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    mod_liquids = [f.replace(".json", "") for f in os.listdir(mod_liquids_path) if f.endswith(".json")]

                default_liquid_entries = {}
                mod_liquid_entries = {}

                def create_liquid_card(parent, liquid, is_mod_liquid=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_liquid_icon(liquid)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=liquid.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    float_value = tk.DoubleVar(value=0.0)
                    str_value = tk.StringVar(value="0")
                    max_value = 50.0

                    def sync_values(*args):
                        try:
                            val = str_value.get()
                            float_value.set(float(val) if val else 0.0)
                        except:
                            float_value.set(0.0)
                    
                    str_value.trace_add("write", sync_values)
                    
                    def validate_input(new_val):
                        if new_val == "":
                            return True
                        try:
                            val = float(new_val)
                            if val < 0 or val > max_value:
                                return False
                        except ValueError:
                            return False
                        return True
                    
                    validation = parent.register(validate_input)
                    
                    controls_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
                    controls_frame.pack(fill="x", pady=5)
                    
                    controls_frame.grid_columnconfigure(0, weight=0, minsize=35)
                    controls_frame.grid_columnconfigure(1, weight=1, minsize=70)
                    controls_frame.grid_columnconfigure(2, weight=0, minsize=35)
                    
                    def update_value(change):
                        try:
                            current = str_value.get()
                            try:
                                current_num = float(current) if current else 0.0
                            except ValueError:
                                current_num = 0.0
                            new_value = max(0.0, min(max_value, current_num + change))
                            str_value.set(f"{new_value:.1f}")
                        except Exception as e:
                            str_value.set("0.0")

                    def start_increment(change):
                        global is_pressed
                        is_pressed = True
                        update_value(change)
                        root.after(100, lambda: repeat_increment(change))

                    def stop_increment():
                        global is_pressed
                        is_pressed = False

                    def repeat_increment(change):
                        if is_pressed:
                            update_value(change)
                            root.after(100, lambda: repeat_increment(change))

                    minus_btn = ctk.CTkButton(
                        controls_frame,
                        text="-",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        fg_color="#e62525",
                        hover_color="#701c1c",
                        border_color="#701c1c",
                        corner_radius=6,
                        anchor="center"
                    )
                    minus_btn.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
                    minus_btn.bind("<ButtonPress-1>", lambda e: start_increment(-0.1))
                    minus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())

                    entry = ctk.CTkEntry(
                        controls_frame,
                        width=70,
                        height=35,
                        font=("Arial", 14),
                        textvariable=str_value,
                        fg_color="#3a7ebf",
                        border_color="#1f4b7a",
                        justify="center",
                        validate="key",
                        validatecommand=(validation, "%P")
                    )
                    entry.grid(row=0, column=1, padx=5, sticky="ew")

                    plus_btn = ctk.CTkButton(
                        controls_frame,
                        text="+",
                        width=35,
                        height=35,
                        font=("Arial", 16),
                        corner_radius=6,
                        anchor="center"
                    )
                    plus_btn.grid(row=0, column=2, padx=(5, 0), sticky="nsew")
                    plus_btn.bind("<ButtonPress-1>", lambda e: start_increment(0.1))
                    plus_btn.bind("<ButtonRelease-1>", lambda e: stop_increment())
                    
                    def handle_focus_out(event):
                        if str_value.get() == "":
                            str_value.set("1.0")
                    
                    entry.bind("<FocusOut>", handle_focus_out)
                    
                    if is_mod_liquid:
                        mod_liquid_entries[liquid] = float_value
                    else:
                        default_liquid_entries[liquid] = float_value
                    
                    return card_frame
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_liquid = item in mod_liquids
                        card = create_liquid_card(items_frame, item, is_mod_liquid)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех жидкостей
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewhell(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)),"units")
                canvas.bind_all("<MouseWheel>", on_mousewhell)
                canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
                canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
                
                # Объединяем все жидкости в один список
                all_liquids = default_liquids + mod_liquids
                update_grid(canvas, items_frame, all_liquids)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_liquids))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                footer_frame = ctk.CTkFrame(main_frame, height=70, fg_color="#3a3a3a", corner_radius=8)
                footer_frame.pack(fill="x", pady=(15, 0))
                
                btn_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
                btn_frame.pack(expand=True, pady=15)

                def save_requirements():
                    consumes_liquids = []
                    
                    for liquid, var in default_liquid_entries.items():
                        amount = var.get()
                        if amount > 0:
                            calculated_amount = round((1 / 60) * amount, 25)
                            consumes_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    for liquid, var in mod_liquid_entries.items():
                        amount = var.get()
                        if amount > 0: 
                            calculated_amount = round((1 / 60) * amount, 25)
                            consumes_liquids.append({
                                "liquid": liquid,
                                "amount": calculated_amount
                            })
                    
                    # Проверяем, что есть хотя бы что-то одно (предметы или жидкости)
                    if not block_data["consumes"].get("items") and not consumes_liquids:
                        messagebox.showerror("Ошибка", "Должно быть хотя бы что-то одно: предметы ИЛИ жидкости!")
                        return
                    
                    block_data["consumes"]["liquids"] = consumes_liquids
                    clean_empty_consumes(block_data)
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Потребляемые жидкости для блока '{block_name}' успешно сохранены!")
                        open_requirements_editor(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить жидкости: {str(e)}")

                def clean_empty_consumes(block_data):
                    """
                    Проверяет и удаляет пустые массивы в структуре consumes и outputLiquids/outputItems
                    """
                    # Проверяем и очищаем consumes
                    if "consumes" in block_data:
                        consumes = block_data["consumes"]
                        
                        # Если consumes пустой объект, удаляем его
                        if consumes == {}:
                            del block_data["consumes"]
                        else:
                            # Удаляем пустые массивы внутри consumes
                            if "items" in consumes and isinstance(consumes["items"], list) and len(consumes["items"]) == 0:
                                del consumes["items"]
                            
                            if "liquids" in consumes and isinstance(consumes["liquids"], list) and len(consumes["liquids"]) == 0:
                                del consumes["liquids"]
                            
                            # Если после очистки consumes стал пустым, удаляем его полностью
                            if consumes == {}:
                                del block_data["consumes"]

                    if "liquidCapacity" in block_data and isinstance(block_data["liquidCapacity"], list) and len(block_data["liquidCapacity"]) == 0:
                        del block_data["liquidCapacity"]
                    
                    if "itemCapacity" in block_data and isinstance(block_data["itemCapacity"], list) and len(block_data["itemCapacity"]) == 0:
                        del block_data["itemCapacity"]
                    
                    return block_data

                def skip_liquids():
                    # Проверяем, есть ли хотя бы что-то в потребляемых предметах
                    if not block_data["consumes"].get("items"):
                        messagebox.showerror("Ошибка", "Если пропустиил предмет добавте жидкость")
                        return
                    if block_data["consumes"].get("items"):
                        clean_empty_consumes(block_data)
                        open_requirements_editor(block_name, block_data)
                
                ctk.CTkButton(btn_frame, 
                            text="Сохранить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            command=save_requirements).pack(side="left", padx=20)
                
                ctk.CTkButton(btn_frame, 
                            text="Пропустить", 
                            width=140, 
                            height=45,
                            font=("Arial", 14),
                            fg_color="#e62525", 
                            hover_color="#701c1c", border_color="#701c1c",
                            command=skip_liquids).pack(side="left", padx=20)

            def open_solidpump_liquid_edit(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                main_frame = ctk.CTkFrame(root, fg_color="transparent")
                main_frame.pack(padx=10, pady=10, fill="both", expand=True)
                
                header_frame = ctk.CTkFrame(main_frame, height=90, fg_color="#3a3a3a", corner_radius=8)
                header_frame.pack(fill="x", pady=(0, 15))
                
                try:
                    block_type = block_data.get("type")
                    texture_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name, f"{block_name}.png")
                    if os.path.exists(texture_path):
                        img = Image.open(texture_path)
                        img = img.resize((70, 70), Image.LANCZOS)
                        ctk_img = ctk.CTkImage(light_image=img, size=(70, 70))
                        img_label = ctk.CTkLabel(header_frame, image=ctk_img, text="")
                        img_label.pack(side="left", padx=20)
                except Exception as e:
                    print(f"Ошибка загрузки изображения: {e}")
                
                ctk.CTkLabel(header_frame, 
                            text=f"Выбор жидкости для насоса: {block_name}",
                            font=("Arial", 18, "bold")).pack(side="left", padx=10)
                
                content_frame = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", corner_radius=8)
                content_frame.pack(fill="both", expand=True)
                
                def load_liquid_icon(liquid_name):
                    icon_paths = [
                        os.path.join(mod_folder, "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "sprites", "liquids", f"{liquid_name}.png"),
                        os.path.join("mindustry_mod_creator", "icons", f"{liquid_name}.png")
                    ]
                    for path in icon_paths:
                        if os.path.exists(path):
                            try:
                                img = Image.open(path)
                                img = img.resize((50, 50), Image.LANCZOS)
                                return ctk.CTkImage(light_image=img, size=(50, 50))
                            except:
                                continue
                    return None
                
                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                
                mod_liquids = []
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    mod_liquids = [f.replace(".json", "") for f in os.listdir(mod_liquids_path) if f.endswith(".json")]

                def create_liquid_card(parent, liquid, is_mod_liquid=False):
                    card_frame = ctk.CTkFrame(parent, 
                                            fg_color="#4a4a4a", 
                                            corner_radius=8,
                                            height=180)
                    card_frame.pack_propagate(False)
                    
                    content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                    content_frame.pack(fill="both", expand=True, padx=10, pady=10)
                    
                    top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    top_frame.pack(fill="x", pady=(0, 10))
                    
                    icon = load_liquid_icon(liquid)
                    if icon:
                        ctk.CTkLabel(top_frame, image=icon, text="").pack()
                    
                    ctk.CTkLabel(top_frame, 
                                text=liquid.capitalize(), 
                                font=("Arial", 14),
                                anchor="center").pack()
                    
                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                    bottom_frame.pack(fill="x", pady=(10, 0))

                    select_btn = ctk.CTkButton(
                        bottom_frame,
                        text="Выбрать",
                        width=120,
                        height=35,
                        font=("Arial", 14),
                        command=lambda: select_liquid(liquid)
                    )
                    select_btn.pack(pady=10)
                    
                    return card_frame
                
                def select_liquid(liquid):
                    # Добавляем {"result": liquid} в JSON блока
                    block_data["result"] = liquid
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
                        with open(block_path, "w", encoding="utf-8") as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        messagebox.showinfo("Успех", f"Жидкость '{liquid}' добавлена в блок '{block_name}'!")
                        # Сразу открываем редактор требований после выбора
                        open_requirements_editor(block_name, block_data)
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить жидкость: {str(e)}")
                
                def calculate_columns(container_width):
                    min_card_width = 180
                    spacing = 10
                    max_columns = max(1, container_width // (min_card_width + spacing))
                    if max_columns * (min_card_width + spacing) - spacing <= container_width:
                        return max_columns, min_card_width
                    return 1, -1
                
                def update_grid(canvas, items_frame, items):
                    container_width = canvas.winfo_width()
                    if container_width < 1:
                        return
                    
                    columns, card_width = calculate_columns(container_width)
                    
                    for widget in items_frame.grid_slaves():
                        widget.grid_forget()
                    
                    for i, item in enumerate(items):
                        row = i // columns
                        col = i % columns
                        is_mod_liquid = item in mod_liquids
                        card = create_liquid_card(items_frame, item, is_mod_liquid)
                        if card_width == -1:
                            card.configure(width=container_width - 20)
                        else:
                            card.configure(width=card_width)
                        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                    
                    items_frame.update_idletasks()
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    
                    if items_frame.winfo_height() <= canvas.winfo_height():
                        canvas.yview_moveto(0)
                        scrollbar.pack_forget()
                    else:
                        scrollbar.pack(side="right", fill="y")
                
                # Создаем один скроллируемый контейнер для всех жидкостей
                canvas = tk.Canvas(content_frame, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(content_frame, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")

                def on_mousewheel(event):
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
                # Добавляем обработку прокрутки для Linux
                def on_button_4(event):
                    canvas.yview_scroll(-1, "units")
                
                def on_button_5(event):
                    canvas.yview_scroll(1, "units")
                
                # Привязываем события прокрутки
                canvas.bind_all("<MouseWheel>", on_mousewheel)
                canvas.bind_all("<Button-4>", on_button_4)
                canvas.bind_all("<Button-5>", on_button_5)
                
                # Объединяем все жидкости в один список
                all_liquids = default_liquids + mod_liquids
                
                # Сразу вызываем обновление сетки после создания
                canvas.after(100, lambda: update_grid(canvas, items_frame, all_liquids))
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, all_liquids))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            #/////////////////////////////////////////////////////////////////////////////////
            def cb_creator_b(block_type):
                clear_window()
                
                # Словарь для хранения всех виджетов
                widgets = {}
                
                # Глобальные поля (общие для всех блоков)
                def create_global_fields():
                    widgets['name'] = create_field(f"Имя {get_block_name(block_type)}", 350)
                    widgets['desc'] = create_field("Описание", 350)
                    widgets['health'] = create_field("ХП", 150)
                    widgets['build_time'] = create_field("Время стройки в секундах (макс. 120)", 150)
                
                # Локальные поля (специфичные для каждого типа)
                def create_local_fields():
                    # Блоки с фиксированным размером 1 (без ввода)
                    fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
                    
                    # Блоки с размером 1-2 (только router)
                    size_1_2_blocks = ["router"]
                    
                    # Блоки с размером 1-15 (все остальные)
                    size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                                    "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump"]
                    
                    if block_type in fixed_size_1_blocks:
                        # Фиксированный размер 1 - скрытое поле
                        widgets['size'] = ctk.CTkEntry(root, width=150)
                        widgets['size'].insert(0, "1")
                        widgets['size'].pack_forget()  # Скрываем, но значение есть
                        
                    elif block_type in size_1_2_blocks:
                        # Размер 1-2
                        widgets['size'] = create_field("Размер (1-2)", 150)
                        widgets['size'].insert(0, "1")
                        
                    elif block_type in size_1_15_blocks:
                        # Размер 1-15
                        widgets['size'] = create_field("Размер (1-15)", 150)
                        widgets['size'].insert(0, "1")
                    
                    # Специфичные поля для каждого типа
                    if block_type in ["router"]:
                        widgets['speed'] = create_field("Скорость (макс. 50)", 150)

                    if block_type in ["conveyor", "Unloader", "Junction"]:
                        widgets['speed'] = create_field("Скорость (макс. 50)", 150)
                    
                    if block_type in ["router", "Junction", "conveyor","conduit", "liquid_router"]:
                        widgets['capacity'] = create_field("Вместимость (макс. 25)", 150)
                    
                    if block_type == "PowerNode":
                        widgets['range'] = create_field("Радиус (макс. 100)", 150)
                        widgets['connections'] = create_field("Макс. подключения (макс. 500)", 150)
                    
                    if block_type in ["SolarGenerator", "ConsumeGenerator", "ThermalGenerator"]:
                        max_energy = 1000000 if block_type == "SolarGenerator" else 5000000
                        widgets['energy'] = create_field(f"Выработка энергии (макс. {max_energy:,})", 150)
                        
                    if block_type == "StorageBlock":
                        widgets['item_capacity'] = create_field("Вместимость предметов (макс. 100.000)", 150)
                    
                    if block_type == "GenericCrafter":
                        # Чекбокс энергии
                        widgets['power_enabled'] = ctk.BooleanVar(value=False)
                        
                        def toggle_power():
                            if widgets['power_enabled'].get():
                                widgets['energy_label'].pack()
                                widgets['energy_consumption'].pack()
                            else:
                                widgets['energy_label'].pack_forget()
                                widgets['energy_consumption'].pack_forget()
                        
                        ctk.CTkCheckBox(root, text="Использует энергию", 
                                    variable=widgets['power_enabled'], 
                                    command=toggle_power).pack(pady=6)
                        
                        widgets['energy_label'] = ctk.CTkLabel(root, text="Потребление энергии")
                        widgets['energy_consumption'] = ctk.CTkEntry(root, width=150)
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                        
                        widgets['craft_time'] = create_field("Скорость производства (сек/предмет)", 150)
                    
                    if block_type == "Battery":
                        widgets['power_buffer'] = create_field("Вместимость энергии (макс. 10.000.000)", 150)
                    
                    if block_type == "BeamNode":
                        widgets['range'] = create_field("Радиус (макс. 50)", 150)
                    
                    if block_type in ["Liquid_Tank"]:
                        widgets['liquid_capacity'] = create_field("Вместимость жидкости (макс. 10.000.000)", 150)
                                       
                    if block_type == "Pump":
                        # Чекбокс энергии
                        widgets['power_enabled'] = ctk.BooleanVar(value=False)
                        
                        def toggle_power():
                            if widgets['power_enabled'].get():
                                widgets['energy_label'].pack()
                                widgets['energy_consumption'].pack()
                            else:
                                widgets['energy_label'].pack_forget()
                                widgets['energy_consumption'].pack_forget()
                        
                        ctk.CTkCheckBox(root, text="Использует энергию", 
                                    variable=widgets['power_enabled'], 
                                    command=toggle_power).pack(pady=6)
                        
                        widgets['energy_label'] = ctk.CTkLabel(root, text="Потребление энергии")
                        widgets['energy_consumption'] = ctk.CTkEntry(root, width=150)
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                        
                        widgets['pumpAmount'] = create_field("Количество выкачика (1=4 если размер 2 а выкачка 1)(макс. 5000)", 150)
                        widgets['capacity'] = create_field("Хранилище(макс. 15000)", 150)
                
                    if block_type == "SolidPump":
                        # Чекбокс энергии
                        widgets['power_enabled'] = ctk.BooleanVar(value=False)
                        
                        def toggle_power():
                            if widgets['power_enabled'].get():
                                widgets['energy_label'].pack()
                                widgets['energy_consumption'].pack()
                            else:
                                widgets['energy_label'].pack_forget()
                                widgets['energy_consumption'].pack_forget()
                        
                        ctk.CTkCheckBox(root, text="Использует энергию", 
                                    variable=widgets['power_enabled'], 
                                    command=toggle_power).pack(pady=6)
                        
                        widgets['energy_label'] = ctk.CTkLabel(root, text="Потребление энергии")
                        widgets['energy_consumption'] = ctk.CTkEntry(root, width=150)
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()

                        widgets['pumpAmount'] = create_field("Количество выкачика (макс. 1000)", 150)
                        widgets['capacity'] = create_field("Хранилище(макс. 15000)", 150)
                        
                # Вспомогательная функция для создания полей
                def create_field(text, width):
                    frame = ctk.CTkFrame(root, fg_color="transparent")
                    frame.pack(fill="x", pady=5)
                    
                    # Создаем контейнер для центрирования
                    container = ctk.CTkFrame(frame, fg_color="transparent")
                    container.pack(expand=True)
                    
                    label = ctk.CTkLabel(container, text=text)
                    entry = ctk.CTkEntry(container, width=width)
                    
                    label.grid(row=0, column=0, padx=(0, 10))
                    entry.grid(row=0, column=1)
                    
                    # Центрируем контейнер
                    container.grid_columnconfigure(0, weight=1)
                    container.grid_columnconfigure(1, weight=0)
                    container.grid_columnconfigure(2, weight=1)
                    
                    return entry
                
                # Функция для получения читаемого имени
                def get_block_name(b_type):
                    names = {
                        "wall": "стены", "conveyor": "конвейера", "router": "роутера",
                        "PowerNode": "энерго узла", "SolarGenerator": "солнечной панели",
                        "GenericCrafter": "завода", "conduit": "трубы", 
                        "StorageBlock": "хранилища", "ConsumeGenerator": "генератора",
                        "Battery": "батареи", "ThermalGenerator": "теплового генератора",
                        "BeamNode": "лучевого узла", "Junction": "перекрёстка",
                        "Unloader": "разгрузчика", "liquid_router": "жидкостного роутера",
                        "Liquid_Tank": "бака жидкости", "LiquidJunction": "жидкостного перекрёстка",
                        "Pump": "Помпы", "SolidPump": "наземной помпы"
                    }
                    return names.get(b_type, "блока")
                
                # Функция для сохранения JSON файла блока
                def save_block_json(block_data):
                    try:
                        # Создаем папку для блоков, если ее нет
                        blocks_folder = os.path.join(mod_folder, "content", "blocks")
                        os.makedirs(blocks_folder, exist_ok=True)
                        
                        # Получаем тип блока и создаем для него папку
                        block_type = block_data['type']
                        block_type_folder = os.path.join(blocks_folder, block_type)
                        os.makedirs(block_type_folder, exist_ok=True)
                        
                        # Сохраняем JSON файл
                        block_file = os.path.join(block_type_folder, f"{block_data['name']}.json")
                        with open(block_file, 'w', encoding='utf-8') as f:
                            json.dump(block_data, f, indent=4, ensure_ascii=False)
                        
                        print(f"Блок сохранен: {block_file}")
                        return True
                        
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить блок: {e}")
                        return False
                
                # Создаем поля
                create_global_fields()
                create_local_fields()
                
                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)
                
                def save_block():
                    # Получаем значения из глобальных полей
                    name = widgets['name'].get().strip().replace(" ", "_")
                    description = widgets['desc'].get().strip()
                    
                    # Проверка на русские символы
                    if any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in name.lower()):
                        messagebox.showerror("Ошибка", "Название не может содержать русские символы")
                        return
                    
                    try:
                        # Базовые значения
                        health = int(widgets['health'].get())
                        build_cost = int(widgets['build_time'].get()) * 60
                        
                        # Определяем размер в зависимости от типа блока
                        fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
                        size_1_2_blocks = ["router"]
                        size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                                        "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump"]
                        
                        if block_type in fixed_size_1_blocks:
                            size = 1  # Фиксированный размер 1
                        elif block_type in size_1_2_blocks:
                            size = int(widgets['size'].get())
                            if size < 1 or size > 2:
                                raise ValueError("Размер должен быть 1-2")
                        elif block_type in size_1_15_blocks:
                            size = int(widgets['size'].get())
                            if size < 1 or size > 15:
                                raise ValueError("Размер должен быть 1-15")
                        else:
                            size = 1  # По умолчанию
                        
                        # Базовые проверки
                        if health < 1: raise ValueError("ХП должно быть > 0")
                        if build_cost < 60: raise ValueError("Время стройки ≥ 1 сек")
                        
                        # Создаем базовую структуру блока
                        block_data = {
                            "name": name,
                            "description": description,
                            "health": health,
                            "size": size,
                            "buildTime": build_cost,
                            "type": block_type,
                            "requirements": [],
                            "research": {"parent": "", "requirements": [], "objectives": []}
                        }
                        
                        # Добавляем специфичные поля
                        if block_type in ["router"]:
                            speed_val = int(widgets['speed'].get())
                            if speed_val < 1 or speed_val > 50:
                                raise ValueError("Скорость 1-50")
                            speed = (1 / 60) * speed_val
                            block_data.update({"speed": speed, "displaySpeed": speed})

                        if block_type in ["conveyor", "Unloader","Junction"]:
                            speed_val = int(widgets['speed'].get())
                            if speed_val < 1 or speed_val > 50:
                                raise ValueError("Скорость 1-50")
                            speed = (1 / 60) * speed_val
                        
                        if block_type in ["router", "Junction","conveyor","conduit","liquid_router"]:
                            capacity = int(widgets['capacity'].get())
                            if capacity < 1 or capacity > 25:
                                    raise ValueError("Вместимость 1-25")
                            if block_type in ["router", "Junction","conveyor"]:
                                block_data["itemCapacity"] = capacity
                            if block_type in ["conduit","liquid_router"]:
                                block_data["liquidCapacity"] = capacity
                        
                        if block_type == "PowerNode":
                            range_val = int(widgets['range'].get())
                            connections = int(widgets['connections'].get())
                            
                            if range_val < 1 or range_val > 100: raise ValueError("Радиус 1-100")
                            if connections < 2 or connections > 500: raise ValueError("Подключения 2-500")
                            
                            block_data.update({
                                "range": range_val * 8,
                                "maxNodes": connections
                            })
                        
                        if block_type in ["SolarGenerator", "ThermalGenerator"]:
                            energy_val = float(widgets['energy'].get())
                            max_energy = 1000000 if block_type == "SolarGenerator" else 5000000
                            if energy_val < 1 or energy_val > max_energy:
                                raise ValueError(f"Энергия 1-{max_energy}")
                            block_data["powerProduction"] = energy_val / 60

                        if block_type == "ConsumeGenerator":
                            energy_val = float(widgets['energy'].get())
                            if energy_val < 1 or energy_val > 5000000:
                                raise ValueError("Энергия 1-5.000.000")
                            block_data.update({
                                "powerProduction": energy_val / 60,
                                "consumes": {"items": [], "liquids": []}
                            })
                        
                        if block_type == "StorageBlock":
                            capacity = int(widgets['item_capacity'].get())
                            if capacity < 1 or capacity > 100000:
                                raise ValueError("Вместимость 1-100K")
                            block_data["itemCapacity"] = capacity
                        
                        if block_type == "GenericCrafter":
                            craft_time = int(widgets['craft_time'].get())
                            block_data.update({
                                "craftTime": craft_time * 60,
                                "itemCapacity": 50,
                                "liquidCapacity": 50,
                                "consumes": {"items": [], "liquids": []},
                                "outputItems": [],
                                "outputLiquids": [],
                                "drawer": {
                                    "type": "DrawMulti",
                                    "drawers": [
                                        {
                                            "type": "DrawRegion"
                                        },
                                        {
                                            "type": "DrawFlame",
                                            "flameColor": "FFDD1D",
                                            "flameRadius": 3,
                                            "flameRadiusScl": 4.0,
                                            "flameRadiusMag": 1.5
                                        }
                                    ]
                                }
                            })
                            
                            if widgets['power_enabled'].get():
                                energy_cons = int(widgets['energy_consumption'].get())
                                block_data["consumes"]["power"] = energy_cons / 60
                        
                        if block_type == "Battery":
                            buffer_val = int(widgets['power_buffer'].get())
                            if buffer_val < 1 or buffer_val > 10000000:
                                raise ValueError("Буфер энергии 1-10M")
                            block_data["consumes"] = {"powerBuffered": buffer_val}
                        
                        if block_type == "BeamNode":
                            range_val = int(widgets['range'].get())
                            if range_val < 1 or range_val > 50:
                                raise ValueError("Радиус 1-50")
                            block_data["range"] = range_val * 8
                                               
                        if block_type in ["Liquid_Tank"]:
                            capacity = int(widgets['liquid_capacity'].get())
                            block_data["liquidCapacity"] = capacity
                        
                        if block_type == "Pump":
                            pumpAmount = int(widgets['pumpAmount'].get())
                            capacity = int(widgets['capacity'].get())
                            amount = pumpAmount / 60
                            if pumpAmount < 1 or pumpAmount > 5000:
                                raise ValueError("Выкачка не больше 5000")
                            if capacity < 1 or capacity > 15000:
                                raise ValueError("Вместимость не больше 15000")
                            block_data.update({
                                "pumpAmount": amount,
                                "liquidCapacity": capacity
                                })
                        
                        if block_type == "SolidPump":
                            pumpAmount = int(widgets['pumpAmount'].get())
                            capacity = int(widgets['capacity'].get())
                            amount = pumpAmount / 60
                            if pumpAmount < 1 or pumpAmount > 1000:
                                raise ValueError("Выкачка не больше 1000")
                            if capacity < 1 or capacity > 15000:
                                raise ValueError("Вместимость не больше 15000")
                            block_data.update({
                                "pumpAmount": amount,
                                "liquidCapacity": capacity
                                })
                        
                        # Устанавливаем категорию
                        category_map = {
                            "wall": "defense", "conveyor": "distribution", "router": "distribution",
                            "PowerNode": "power", "SolarGenerator": "power", "GenericCrafter": "crafting",
                            "conduit": "liquid", "StorageBlock": "distribution", "ConsumeGenerator": "power",
                            "Battery": "power", "ThermalGenerator": "power", "BeamNode": "power",
                            "Junction": "distribution", "Unloader": "distribution", "liquid_router": "liquid",
                            "Liquid_Tank": "liquid", "LiquidJunction": "liquid", "Pump": "liquid",
                            "SolidPump": "production"
                        }
                        block_data["category"] = category_map.get(block_type, "misc")
                        
                    except ValueError as e:
                        messagebox.showerror("Ошибка", f"Некорректные данные: {e}")
                        return
                    
                    if not name or not description:
                        messagebox.showerror("Ошибка", "Заполните имя и описание")
                        return
                    
                    # Сохраняем в кэш
                    if block_type not in CACHE_FILE:
                        CACHE_FILE[block_type] = []
                    if name not in CACHE_FILE[block_type]:
                        CACHE_FILE[block_type].append(name)
                    
                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)
                    
                    # Проверка существования имени
                    if name_exists_in_content(mod_folder, name, block_type):
                        return
                    
                    # Сохраняем JSON файл блока
                    if not save_block_json(block_data):
                        return
                    
                    # Открываем соответствующий редактор
                    if block_type == "GenericCrafter":
                        open_item_GenericCrafter_editor(name, block_data)
                    elif block_type == "ConsumeGenerator":
                        open_item_consumes_editor(name, block_data)
                    elif block_type == "SolidPump":
                        open_solidpump_liquid_edit(name, block_data)
                    else:
                        open_requirements_editor(name, block_data)
                
                # Кнопки
                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_block).pack(pady=20)

        # Создание главного окна 
        root = ctk.CTk()
        root.title("Mindustry Mod Creator")
        root.geometry("700x500")

        # Разделение на левую (30%) и правую (70%) части
        left_frame = ctk.CTkFrame(root, width=240)
        right_frame = ctk.CTkFrame(root)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Левая панель (30%) - список модов
        mods_frame = ctk.CTkScrollableFrame(left_frame)
        mods_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Заголовок списка модов
        ctk.CTkLabel(mods_frame, text="Ваши моды", font=("Arial", 14)).pack(pady=5)

        def load_all_icons_paint(parent_window=None):
            # Конфигурация загрузки items с указанием полных путей
            download_configs = [
                (
                    "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/",
                    {
                        "copper": "items/item-copper.png",
                        "beryllium": "items/item-beryllium.png",
                        "carbide": "items/item-carbide.png",
                        "fissile-matter": "items/item-fissile-matter.png",
                        "oxide": "items/item-oxide.png",
                        "tungsten": "items/item-tungsten.png",
                        "dormant-cyst": "items/item-dormant-cyst.png",
                        "lead": "items/item-lead.png",
                        "metaglass": "items/item-metaglass.png",
                        "graphite": "items/item-graphite.png",
                        "sand": "items/item-sand.png",
                        "coal": "items/item-coal.png",
                        "titanium": "items/item-titanium.png",
                        "thorium": "items/item-thorium.png",
                        "scrap": "items/item-scrap.png",
                        "silicon": "items/item-silicon.png",
                        "plastanium": "items/item-plastanium.png",
                        "phase-fabric": "items/item-phase-fabric.png",
                        "surge-alloy": "items/item-surge-alloy.png",
                        "spore-pod": "items/item-spore-pod.png",
                        "pyratite": "items/item-pyratite.png",
                    },
                    os.path.join("mindustry_mod_creator", "icons", "paint", "items"),
                    False
                ),
                (
                    "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/",
                    {
                        "arkycite": "items/liquid-arkycite.png",
                        "water": "items/liquid-water.png",
                        "slag": "items/liquid-slag.png",
                        "oil": "items/liquid-oil.png",
                        "neoplasm": "items/liquid-neoplasm.png",
                        "cyanogen": "items/liquid-cyanogen.png",
                        "cryofluid": "items/liquid-cryofluid.png"
                    },
                    os.path.join("mindustry_mod_creator", "icons", "paint", "liquids"),
                    False
                )
            ]

            # Создаем папки для иконок, если их нет
            for config in download_configs:
                os.makedirs(config[2], exist_ok=True)

            # Подсчет общего количества иконок (только тех, которых нет)
            total_icons = 0
            download_tasks = []

            for base_url, name_icons, icons_folder, is_item in download_configs:
                existing_files = set(os.listdir(icons_folder)) if os.path.exists(icons_folder) else set()
                if isinstance(name_icons, dict):
                    for name, path in name_icons.items():
                        if f"{name}.png" not in existing_files:
                            total_icons += 1
                            download_tasks.append((base_url + path, os.path.join(icons_folder, f"{name}.png"), name))

            if total_icons == 0:
                return True

            # Инициализация окна прогресса
            if parent_window:
                progress_window = ctk.CTkToplevel(parent_window)
                progress_window.title("Загрузка иконок")
                progress_window.geometry("400x150")
                progress_window.transient(parent_window)
                progress_window.grab_set()
                
                progress_label = ctk.CTkLabel(progress_window, text=f"Загрузка {total_icons} иконок...")
                progress_label.pack(pady=10)
                
                progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                progress_bar.pack(pady=10)
                progress_bar.set(0)
                
                status_label = ctk.CTkLabel(progress_window, text="0/0")
                status_label.pack(pady=5)
                
                progress_window.update()

            downloaded = 0
            errors = []

            def update_progress(current, total, name):
                if parent_window:
                    progress = (current + 1) / total
                    progress_bar.set(progress)
                    status_label.configure(text=f"{current + 1}/{total} - {name}.png")
                    progress_label.configure(text=f"Загружается: {name}.png")
                    progress_window.update()

            def download_file(url, save_path, name):
                try:
                    urllib.request.urlretrieve(url, save_path)
                    return True, name
                except Exception as e:
                    return False, (name, str(e))

            try:
                # Используем ThreadPoolExecutor для параллельной загрузки (4 потока)
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {executor.submit(download_file, url, path, name): (url, path, name) for url, path, name in download_tasks}
                    
                    for future in as_completed(futures):
                        url, path, name = futures[future]
                        success, result = future.result()
                        
                        if success:
                            downloaded += 1
                            if parent_window:
                                update_progress(downloaded, total_icons, name)
                        else:
                            errors.append(result)
                            downloaded += 1
                            if parent_window:
                                progress_label.configure(text=f"Ошибка: {name}.png")

                # Вывод ошибок, если они есть
                if errors:
                    error_msg = "\n".join(f"{name}: {error}" for name, error in errors)
                    if parent_window:
                        messagebox.showwarning("Ошибки загрузки", f"Не удалось загрузить некоторые иконки:\n{error_msg}")
                    else:
                        print(f"Ошибки загрузки:\n{error_msg}")

                if parent_window:
                    progress_label.configure(text="Загрузка завершена!")
                    progress_window.after(2000, progress_window.destroy)
                    
                return True
                
            except Exception as e:
                error_msg = f"Критическая ошибка: {str(e)}"
                if parent_window:
                    progress_label.configure(text=error_msg)
                    messagebox.showerror("Ошибка", error_msg)
                else:
                    print(error_msg)
                return False
        load_all_icons_paint(root)

        def on_mod_click(mod_name):
            """Функция, вызываемая при нажатии на мод"""
            # Уничтожаем текущие виджеты
            for widget in root.winfo_children():
                widget.destroy()
            
            # Создаем UI как в show_create_ui, но с автоматическим заполнением
            root.geometry("500x500")
            label = ctk.CTkLabel(root, text="Названия папка")
            global entry_name
            entry_name = ctk.CTkEntry(root, width=200)
            entry_name.insert(0, mod_name)  # Автоматически заполняем имя мода
            
            label.pack(pady=70)
            entry_name.pack(pady=10)
            
            # Автоматически вызываем setup_mod_json без кнопки "Далее"
            setup_mod_json_auto()

        # Заполнение списка модами из папки
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
                        command=lambda name=mod_folder: on_mod_click(name)
                    )
                    btn.pack(pady=3, padx=5)

        def show_create_ui():
            """Показывает UI для создания нового мода"""
            global entry_name
            root.geometry("500x500")
            for widget in root.winfo_children():
                widget.destroy()

            label = ctk.CTkLabel(root, text="Названия папка")
            entry_name = ctk.CTkEntry(root, width=200)
            button_next = ctk.CTkButton(root, text="Далее", command=setup_mod_json)
            
            label.pack(pady=70)
            entry_name.pack(pady=10)
            button_next.pack(side=ctk.BOTTOM, pady=50)

        # Правая панель (70%) - кнопка создания
        ctk.CTkButton(
            right_frame,
            text="Создать мод",
            width=200,
            height=50,
            font=("Arial", 14),
            command=show_create_ui
        ).pack(expand=True)

        root.mainloop()

if __name__ == "__main__":
    MindustryModCreator.main()
