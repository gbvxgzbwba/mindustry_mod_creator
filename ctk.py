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
from tkinter import messagebox
from copy import deepcopy

sys.dont_write_bytecode = True

theme_test = deepcopy(ctk.ThemeManager.theme)

theme_test["CTkButton"] = {
    "fg_color": "#128f1c", "corner_radius": 15,
    "text_color": "#FFFFFF", "border_width": 5,
    "hover_color": "#005A00", "border_color": "#005A00",
    "text_color_disabled": "#00F7FF"
}
theme_test["CTkEntry"] = {
    "fg_color": "#128f1c", "corner_radius": 15,
    "text_color": "#FFFFFF", "border_width": 5,
    "border_color": "#065500", "placeholder_text_color": "#222222"
}

# Настройка темы CTk
ctk.set_appearance_mode("Dark")  # Режим: "System", "Dark", "Light"
ctk.ThemeManager.theme = theme_test
#ctk.set_default_color_theme("dark-green")  # Темы: "blue", "green", "dark-blue" (((THEME_TEST)))

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
        "SolarGenerator": [
            "solar-panel",
            "solar-panel-large"
        ],
        "ConsumeGenerator": [
            "combustion-generator",
            "steam-generator",
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
        "conveyor": [
            "conveyor",
            "titanium-conveyor"
        ],
        "conduit": [
            "conduit",
            "pulse-conduit"
        ],
        "BridgeConveyor": ["bridge-conveyor", "phase-conveyor"],
        "BridgeConduit": ["bridge-conduit", "phase-conduit"],
        "battery": ["battery", "battery-large"],
        "Drill": ["mechanical-drill", "pneumatic-drill", "laser-drill", "blast-drill"],
        "PowerNode": ["power-node", "power-node-large"],
        "router": ["Router", "Distributor"],
        "Junction": ["Junction"],
        "Unloader": ["Unloader"],
        "liquid_router": ["liquid-router"],
        "Liquid_Junction": ["Liquid-Junction"],
        "LiquidTank": ["liquid-tank"]
    }
    path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")

    cache_file_path = os.path.join("mindustry_mod_creator", "cache")
    os.makedirs(cache_file_path, exist_ok=True)
    
    if not os.path.exists(path):
        with open(path, "w+", encoding="utf-8") as f:
            json.dump(default_cache, f, indent=4, ensure_ascii=False)
        return default_cache
    try:
        with open(path, "r+", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, "w+", encoding="utf-8") as f:
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
            combo_version = ctk.CTkComboBox(form_frame, values=["146", "149"], state="readonly", width=150)
            combo_version.set("146")

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
                combo_version.set(str(mod_data.get("minGameVersion", "146")))

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
            """Окно с кнопками для создания новых объектов"""
            clear_window()

            # Заголовок
            label = ctk.CTkLabel(root, text="Что вы хотите добавить?", font=("Arial", 16, "bold"))
            label.pack(pady=(40, 20))

            # Контейнер для кнопок
            button_frame = ctk.CTkFrame(root)
            button_frame.pack(pady=10)

            # Кнопки
            buttons = [
                ("📦 Создать предмет 📦", create_item_window),
                ("💧 Создать жидкость 💧", create_liquid_window),
                ("🧱 Создать блок 🧱", lambda:create_block(mod_name)),
                ("📁 Создать Zip 🔨", lambda:create_zip()),
                ("📁 Открыть папку мода 📁", lambda:open_mod_folder())
            ]

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
                    zip_path = os.path.join("mindustry_mod_creator", "mods", f"{mod_name}.zip")

                    if not os.path.exists(folder_path):
                        messagebox.showerror("Ошибка", f"Папка мода не существует:\n{folder_path}")
                        return None
                    
                    if not os.listdir(folder_path):
                        messagebox.showerror("Ошибка", f"Папка мода пуста:\n{folder_path}")
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

            for i, (text, cmd) in enumerate(buttons):
                btn = ctk.CTkButton(button_frame, text=text, command=cmd, width=250, height=40,
                                  font=("Arial", 12))
                btn.grid(row=i, column=0, pady=8)

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
                sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", "liquid")
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
                            "copper-wall": "walls/copper-wall.png",
                            #"liquid-tank": "liquid/liquid-tank.png",
                            "liquid-router": "liquid/liquid-router.png",
                            "unloader": "storage/unloader.png",
                            "liquid-junction": "liquid/liquid-junction.png",
                            "router": "distribution/router.png",
                            "junction": "distribution/junction.png",
                            "titanium-conveyor-0-0": "distribution/conveyors/titanium-conveyor-0-0.png",
                            "steam-generator": "power/steam-generator.png",
                            "solar-panel": "power/solar-panel.png",
                            "silicon-smelter": "production/silicon-smelter.png",
                            "conduit-top-0": "liquid/conduits/conduit-top-0.png",
                            "power-node": "power/power-node.png"
                        },
                        False
                    )
                ]

                # Создаем папку для иконок, если ее нет
                os.makedirs(icons_folder, exist_ok=True)

                if parent_window:
                    progress_window = ctk.CTkToplevel(parent_window)
                    progress_window.title("Загрузка иконок")
                    progress_window.geometry("400x150")
                    progress_window.transient(parent_window)
                    progress_window.grab_set()
                    
                    progress_label = ctk.CTkLabel(progress_window, text="Подготовка к загрузке...")
                    progress_label.pack(pady=10)
                    
                    progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)
                    
                    status_label = ctk.CTkLabel(progress_window, text="0/0")
                    status_label.pack(pady=5)
                    
                    progress_window.update()

                total_icons = sum(
                    len(items) if isinstance(items, (list, dict)) else 0 
                    for _, items, _ in download_configs
                )
                downloaded = 0

                def update_progress(current, total, name):
                    if parent_window:
                        progress = (current + 1) / total
                        progress_bar.set(progress)
                        status_label.configure(text=f"{current + 1}/{total} - {name}.png")
                        progress_label.configure(text=f"Загружается: {name}.png")
                        progress_window.update()

                try:
                    for base_url, name_icons, is_item in download_configs:
                        if isinstance(name_icons, dict):
                            for name, path in name_icons.items():
                                url = f"{base_url}{path}"
                                save_path = os.path.join(icons_folder, f"{name}.png")
                                
                                if not os.path.exists(save_path):
                                    try:
                                        urllib.request.urlretrieve(url, save_path)
                                        update_progress(downloaded, total_icons, name)
                                    except Exception as e:
                                        print(f"Ошибка загрузки {name}.png: {e}")
                                        if parent_window:
                                            progress_label.configure(text=f"Ошибка: {name}.png")
                                downloaded += 1
                        else:
                            for name in name_icons:
                                filename = ""
                                if is_item:
                                    # Проверяем, является ли это жидкостью
                                    if name in ["water", "oil", "slag", "cryofluid"]:
                                        filename = f"liquid-{name}.png"
                                    else:
                                        filename = f"item-{name}.png"
                                else:
                                    filename = f"{name}.png"
                                    
                                url = f"{base_url}{filename}"
                                save_path = os.path.join(icons_folder, f"{name}.png")
                                
                                if not os.path.exists(save_path):
                                    try:
                                        urllib.request.urlretrieve(url, save_path)
                                        update_progress(downloaded, total_icons, name)
                                    except Exception as e:
                                        print(f"Ошибка загрузки {name}.png: {e}")
                                        if parent_window:
                                            progress_label.configure(text=f"Ошибка: {name}.png")
                                downloaded += 1

                    if parent_window:
                        progress_label.configure(text="Загрузка завершена!")
                        progress_window.after(2000, progress_window.destroy)
                        
                except Exception as e:
                    if parent_window:
                        progress_label.configure(text=f"Критическая ошибка: {str(e)}")
                        messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
                    else:
                        print(f"Критическая ошибка: {str(e)}")

            load_all_icons(root)

            def load_image(icon_name):
                """Загрузка изображения с обработкой ошибок"""
                try:
                    img_path = os.path.join(icons_dir, icon_name)
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        return ctk.CTkImage(light_image=img, size=(64, 64))
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

            editor_btn = ctk.CTkButton(right_frame, text="Редактор", height=60,
                                    font=("Arial", 14), command=lambda: editor_cb())
            editor_btn.pack(fill="x", pady=(0, 10))

            research_btn = ctk.CTkButton(right_frame, text="Исследования", height=60,
                                    font=("Arial", 14), command=lambda: editor_cb_research())
            research_btn.pack(fill="x")

            def editor_cb_research():
                clear_window()
                
                # Создаем основную рамку для кнопок навигации
                nav_frame = ctk.CTkFrame(root)
                nav_frame.pack(pady=10)
                
                ctk.CTkButton(nav_frame, text="⬅️ Назад", command=lambda:create_block(mod_name)).pack(side="left", padx=5)
                
                # Создаем фрейм для списка блоков (без вкладок)
                blocks_frame = ctk.CTkFrame(root)
                blocks_frame.pack(pady=10, padx=10, fill="both", expand=True)
                
                # Загружаем блоки
                blocks_folder = os.path.join(mod_folder, "content", "blocks")
                if os.path.exists(blocks_folder):
                    for folder_name in os.listdir(blocks_folder):
                        folder_path = os.path.join(blocks_folder, folder_name)
                        
                        if not os.path.isdir(folder_path) or folder_name == "environment" or folder_name.startswith("."):
                            continue
                            
                        # Добавляем кнопку для категории блоков
                        btn = ctk.CTkButton(blocks_frame, text=folder_name, width=250, height=40,
                                        command=lambda p=folder_path: open_block_folder_research(p))
                        btn.pack(pady=3)
            def open_block_folder_research(folder_path):
                clear_window()

                ctk.CTkButton(root, text="⬅️ Назад", command=editor_cb_research).pack(pady=10)

                folder_name = os.path.basename(folder_path)
                ctk.CTkLabel(root, text=f"Блоки из: {folder_name}", font=("Arial", 12)).pack(pady=5)

                for file in os.listdir(folder_path):
                    if file.endswith(".json"):
                        block_name = os.path.splitext(file)[0]
                        block_type = os.path.basename(folder_path)

                        frame = ctk.CTkFrame(root)
                        frame.pack(pady=2, fill="x")

                        ctk.CTkLabel(frame, text=block_name, width=200, anchor="w").pack(side="left")

                        # Только одна кнопка для редактирования требований
                        ctk.CTkButton(frame, text="Редактировать требования", width=150,
                                    command=lambda b=block_name, p=folder_path: edit_requirements(b, p)).pack(side="right", padx=2)
            def edit_requirements(block_name, folder_path):
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
                            text=f"Редактор требований: {block_name}",
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
                        open_block_folder(folder_path)
                    
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
                            command=lambda: open_block_folder_research(folder_path)).pack(side="left", padx=20)

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
                ("Стена", "copper-wall.png", lambda: cb_wall_create()),
                ("Конвейер", "titanium-conveyor-0-0.png", lambda: cb_conveyor_create()),
                ("Генератор", "steam-generator.png", lambda: cb_ConsumesGenerator_create()),
                ("Солн. панель", "solar-panel.png", lambda: cb_solarpanel_create()),
                ("Хранилище", "storage.png", lambda: cb_StorageBlock_create()),
                ("Завод", "silicon-smelter.png", lambda: cb_GenericCrafter_create()),
                ("Труба", "conduit-top-0.png", lambda: cb_conduit_create()),
                ("Энергоузел", "power-node.png", lambda: cb_powernode_create()),
                ("Роутер", "router.png", lambda: cb_router_create()),
                ("Перекрёсток", "junction.png", lambda: cb_Junction_create()),
                ("Разгрушик", "unloader.png", lambda: cb_unloader_create()),
                ("Роутер жидкости", "liquid-router.png", lambda: cb_liquid_router_create()),
                ("Перекрёсток жидкости", "liquid-junction.png", lambda: cb_liquid_Junction_create())
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

            def editor_cb():
                clear_window()
                
                # Создаем основную рамку для кнопок навигации
                nav_frame = ctk.CTkFrame(root)
                nav_frame.pack(pady=10)
                
                ctk.CTkButton(nav_frame, text="⬅️ Назад", command=lambda:create_block(mod_name)).pack(side="left", padx=5)
                
                # Создаем вкладки для разных типов контента
                tabs = ctk.CTkTabview(root)
                tabs.pack(pady=10, padx=10, fill="both", expand=True)
                
                # Добавляем вкладки
                tabs.add("Блоки")
                tabs.add("Предметы")
                tabs.add("Жидкости")
                
                # Вкладка для блоков
                blocks_folder = os.path.join(mod_folder, "content", "blocks")
                if os.path.exists(blocks_folder):
                    for folder_name in os.listdir(blocks_folder):
                        folder_path = os.path.join(blocks_folder, folder_name)
                        
                        if not os.path.isdir(folder_path) or folder_name == "environment" or folder_name.startswith("."):
                            continue
                            
                        # Добавляем кнопку для категории блоков
                        btn = ctk.CTkButton(tabs.tab("Блоки"), text=folder_name, width=250, height=40,
                                        command=lambda p=folder_path: open_block_folder(p))
                        btn.pack(pady=3)
                
                # Вкладка для предметов
                items_folder = os.path.join(mod_folder, "content", "items")
                if os.path.exists(items_folder):
                    for file in os.listdir(items_folder):
                        if file.endswith(".json"):
                            item_name = os.path.splitext(file)[0]
                            
                            frame = ctk.CTkFrame(tabs.tab("Предметы"))
                            frame.pack(pady=2, fill="x")
                            
                            ctk.CTkLabel(frame, text=item_name, width=200, anchor="w").pack(side="left")
                            
                            # Кнопки для предмета
                            ctk.CTkButton(frame, text="Редактировать", width=100,
                                        command=lambda n=item_name: edit_item(n)).pack(side="right", padx=2)
                            ctk.CTkButton(frame, text="Удалить", width=100,
                                        command=lambda n=item_name: delete_item(n)).pack(side="right", padx=2)
                
                # Вкладка для жидкостей
                liquids_folder = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(liquids_folder):
                    for file in os.listdir(liquids_folder):
                        if file.endswith(".json"):
                            liquid_name = os.path.splitext(file)[0]
                            
                            frame = ctk.CTkFrame(tabs.tab("Жидкости"))
                            frame.pack(pady=2, fill="x")
                            
                            ctk.CTkLabel(frame, text=liquid_name, width=200, anchor="w").pack(side="left")
                            
                            # Кнопки для жидкости
                            ctk.CTkButton(frame, text="Редактировать", width=100,
                                        command=lambda n=liquid_name: edit_liquid(n)).pack(side="right", padx=2)
                            ctk.CTkButton(frame, text="Удалить", width=100,
                                        command=lambda n=liquid_name: delete_liquid(n)).pack(side="right", padx=2)
            def open_block_folder(folder_path):
                clear_window()

                ctk.CTkButton(root, text="⬅️ Назад", command=editor_cb).pack(pady=10)

                folder_name = os.path.basename(folder_path)
                ctk.CTkLabel(root, text=f"Блоки из: {folder_name}", font=("Arial", 12)).pack(pady=5)

                for file in os.listdir(folder_path):
                    if file.endswith(".json"):
                        block_name = os.path.splitext(file)[0]
                        block_type = os.path.basename(folder_path)

                        frame = ctk.CTkFrame(root)
                        frame.pack(pady=2, fill="x")

                        ctk.CTkLabel(frame, text=block_name, width=200, anchor="w").pack(side="left")

                        # Кнопка редактирования
                        ctk.CTkButton(frame, text="Редактировать", width=100,
                                    command=lambda b=block_name, p=folder_path: edit_block(b, p)).pack(side="right", padx=2)

                        # Кнопка для удаления блока
                        ctk.CTkButton(frame, text="Удалить", width=100,
                                    command=lambda b=block_name, p=folder_path: delete_block(b, p)).pack(side="right", padx=2)
            def delete_block(block_name, folder_path):
                block_type = os.path.basename(folder_path)
                json_path = os.path.join(folder_path, f"{block_name}.json")
                sprite_folder_path = os.path.join(mod_folder, "sprites", block_type, block_name)
                cache_path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")

                try:
                    # Удалить JSON-файл
                    if os.path.exists(json_path):
                        os.remove(json_path)

                    # Удалить папку с текстурами, если она есть
                    if os.path.isdir(sprite_folder_path):
                        shutil.rmtree(sprite_folder_path)

                    # Удаление из cache.json
                    if os.path.exists(cache_path):
                        with open(cache_path, "r", encoding="utf-8") as f:
                            cache = json.load(f)

                        if block_type in cache and block_name in cache[block_type]:
                            cache[block_type].remove(block_name)
                            with open(cache_path, "w", encoding="utf-8") as f:
                                json.dump(cache, f, indent=4, ensure_ascii=False)

                    # Обновить интерфейс
                    open_block_folder(folder_path)

                except Exception as e:
                    messagebox.showerror("Ошибка удаления", f"Не удалось удалить: {e}")
            def edit_block(block_name, folder_path):
                path = os.path.join(folder_path, f"{block_name}.json")
                edit_json_file(path, f"Редактирование блока: {block_name}")
            def edit_item(item_name):
                path = os.path.join(mod_folder, "content", "items", f"{item_name}.json")
                edit_json_file(path, f"Редактирование предмета: {item_name}")
            def edit_liquid(liquid_name):
                path = os.path.join(mod_folder, "content", "liquids", f"{liquid_name}.json")
                edit_json_file(path, f"Редактирование жидкости: {liquid_name}")
            def delete_item(item_name):
                json_path = os.path.join(mod_folder, "content", "items", f"{item_name}.json")
                sprite_path = os.path.join(mod_folder, "sprites", "items", f"{item_name}.png")
                
                try:
                    if os.path.exists(json_path):
                        os.remove(json_path)
                    if os.path.exists(sprite_path):
                        os.remove(sprite_path)
                    messagebox.showinfo("Успех", f"Предмет {item_name} удален!")
                    editor_cb()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить предмет: {e}")
            def delete_liquid(liquid_name):
                json_path = os.path.join(mod_folder, "content", "liquids", f"{liquid_name}.json")
                
                try:
                    if os.path.exists(json_path):
                        os.remove(json_path)
                    messagebox.showinfo("Успех", f"Жидкость {liquid_name} удалена!")
                    editor_cb()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить жидкость: {e}")
            def edit_json_file(file_path, title):
                if not os.path.exists(file_path):
                    messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
                    return

                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Некорректный JSON.")
                        return

                top = ctk.CTkToplevel(root)
                top.title(title)
                top.geometry("800x600")
                
                text_frame = ctk.CTkFrame(top)
                text_frame.pack(pady=10, padx=10, fill="both", expand=True)
                
                text = ctk.CTkTextbox(text_frame, font=("Consolas", 12))
                text.pack(fill="both", expand=True, padx=5, pady=5)
                text.insert("1.0", json.dumps(data, indent=4, ensure_ascii=False))
                
                button_frame = ctk.CTkFrame(top)
                button_frame.pack(pady=10)
                
                def save_changes():
                    try:
                        new_data = json.loads(text.get("1.0", tk.END))
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(new_data, f, indent=4, ensure_ascii=False)
                        messagebox.showinfo("Успех", "Файл успешно сохранён!")
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
                
                ctk.CTkButton(button_frame, text="Сохранить", command=save_changes).pack(side="left", padx=5)
                ctk.CTkButton(button_frame, text="Отмена", command=top.destroy).pack(side="left", padx=5)

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
                        
                        size = block_data.get("size", 1)
                        texture_url = f"https://github.com/gbvxgzbwba/texture123/raw/main/block-{size}.png"
                        texture_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type)
                        os.makedirs(texture_folder, exist_ok=True)
                        texture_path = os.path.join(texture_folder, f"{block_name}.png")
                        
                        if not os.path.exists(texture_path):
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"Текстура автоматически загружена: {texture_url}")
                            except Exception as e:
                                print(f"Ошибка загрузки текстуры: {e}")
                        
                        block_path = os.path.join(content_folder, f"{block_name}.json")
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
                            hover_color="#701c1c", border_color="#701c1c",
                            command=создание_кнопки).pack(side="left", padx=20)

            def open_requirements_editor_conveyor(block_name, block_data):
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
                            text=f"Редактор ресурсов конвейера: {block_name}, {block_type}, максимум 70.000",
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
                        texture_names = [
                            "conveyor", "conveyor-0-0", "conveyor-0-1", "conveyor-0-2", "conveyor-0-3",
                            "conveyor-1-0", "conveyor-1-1", "conveyor-1-2", "conveyor-1-3",
                            "conveyor-2-0", "conveyor-2-1", "conveyor-2-2", "conveyor-2-3",
                            "conveyor-3-0", "conveyor-3-1", "conveyor-3-2", "conveyor-3-3",
                            "conveyor-4-0", "conveyor-4-1", "conveyor-4-2", "conveyor-4-3"
                        ]
                        
                        sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)
                        
                        base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/conveyors/"
                        total_files = len(texture_names)
                        downloaded = 0
                        
                        def update_progress():
                            nonlocal downloaded
                            progress = (downloaded) / total_files
                            progress_bar.set(progress)
                            status_label.configure(text=f"{downloaded}/{total_files}")
                            progress_window.update()
                        
                        def download_textures():
                            nonlocal downloaded
                            try:
                                for name in texture_names:
                                    new_name = name.replace("conveyor", block_name, 1)
                                    texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                                    
                                    if not os.path.exists(texture_path):
                                        texture_url = f"{base_url}{name}.png"
                                        try:
                                            urllib.request.urlretrieve(texture_url, texture_path)
                                            progress_label.configure(text=f"Загружено: {new_name}.png")
                                        except Exception as e:
                                            progress_label.configure(text=f"Ошибка: {new_name}.png")
                                    
                                    downloaded += 1
                                    progress_window.after(100, update_progress)
                                
                                # После завершения загрузки
                                progress_window.after(100, lambda: finish_saving())
                            
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
                                
                                messagebox.showinfo("Успех", f"Конвейер '{block_name}' успешно сохранён!")
                                создание_кнопки()
                            
                            except Exception as e:
                                error_occurred(str(e))
                        
                        def error_occurred(error_msg):
                            progress_window.destroy()
                            for child in btn_frame.winfo_children():
                                child.configure(state="normal")
                            messagebox.showerror("Ошибка", f"Не удалось сохранить конвейер: {error_msg}")
                        
                        # Запускаем загрузку в отдельном потоке
                        threading.Thread(target=download_textures, daemon=True).start()
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось начать сохранение: {str(e)}")
                
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

            def open_requirements_editor_conduit(block_name, block_data):
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
                            text=f"Редактор ресурсов кондуита: {block_name}, максимум 70.000",
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
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса!")
                        return
                    
                    block_data["requirements"] = requirements
                    
                    try:
                        block_type = block_data.get("type")
                        content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                        os.makedirs(content_folder, exist_ok=True)
                        
                        # Загрузка текстур кондуита
                        texture_names = [
                            "conduit-top-0", "conduit-top-1", "conduit-top-2", "conduit-top-3",
                            "conduit-top-4", "conduit-top-5", "conduit-top-6"
                        ]

                        sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)

                        base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/conduit/"
                        
                        # Создаем окно прогресса
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
                        
                        total_files = len(texture_names)
                        downloaded = 0
                        
                        def update_progress():
                            nonlocal downloaded
                            progress = (downloaded) / total_files
                            progress_bar.set(progress)
                            status_label.configure(text=f"{downloaded}/{total_files}")
                            progress_window.update()
                        
                        def download_textures():
                            nonlocal downloaded
                            try:
                                for name in texture_names:
                                    new_name = name.replace("conduit", block_name, 1)
                                    texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                                    
                                    if not os.path.exists(texture_path):
                                        texture_url = f"{base_url}{name}.png"
                                        try:
                                            urllib.request.urlretrieve(texture_url, texture_path)
                                            progress_label.configure(text=f"Загружено: {new_name}.png")
                                        except Exception as e:
                                            progress_label.configure(text=f"Ошибка: {new_name}.png")
                                    
                                    downloaded += 1
                                    progress_window.after(100, update_progress)
                                
                                # После завершения загрузки
                                progress_window.after(100, lambda: finish_saving())
                            
                            except Exception as e:
                                progress_window.after(100, lambda: error_occurred(str(e)))
                        
                        def finish_saving():
                            try:
                                block_path = os.path.join(content_folder, f"{block_name}.json")
                                with open(block_path, "w", encoding="utf-8") as f:
                                    json.dump(block_data, f, indent=4, ensure_ascii=False)
                                
                                progress_window.destroy()
                                messagebox.showinfo("Успех", f"Кондуит '{block_name}' успешно сохранён!")
                                создание_кнопки()
                            
                            except Exception as e:
                                error_occurred(str(e))
                        
                        def error_occurred(error_msg):
                            progress_window.destroy()
                            messagebox.showerror("Ошибка", f"Не удалось сохранить кондуит: {error_msg}")
                        
                        # Запускаем загрузку в отдельном потоке
                        threading.Thread(target=download_textures, daemon=True).start()
                    
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Не удалось начать сохранение: {str(e)}")
                
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
                
                def skip_liquids():
                    # Проверяем, есть ли хотя бы что-то в потребляемых предметах
                    if not block_data["consumes"].get("items"):
                        messagebox.showerror("Ошибка", "Если пропустиил предмет добавте жидкость")
                        return
                
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

#/////////////////////////////////////////////////////////////////////////////////
            def cb_wall_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя стены").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)").pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                # ✅ Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("wall", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_wall():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        if size > 15 or size < 1:
                            raise ValueError
                        if health > 1000000 or health < 1:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "category": "defense",
                        "type": "wall",
                        "requirements": [],
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("wall", []):
                        CACHE_FILE["wall"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:

                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "wall"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, block_data)
                
                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_wall).pack(pady=20)

            def cb_conveyor_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя конвейера").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (предметы в секунду) (макс. 50)").pack()
                entry_speed = ctk.CTkEntry(root, width=150)
                entry_speed.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("conveyor", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_conveyor():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = (1 / 60) * speed1
                        real_speed = round(speed * 60, 1)
                        if health > 500000 or health < 1:
                             raise ValueError
                        if speed1 > 50 or speed1 < 1:
                             raise ValueError
                        print(f"game= {real_speed} | code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    conveyor_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "speed": speed,
                        "displaySpeed": speed,
                        "category": "distribution",
                        "type": "conveyor",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("conveyor", []):
                        CACHE_FILE["conveyor"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "conveyor"):
                        return  # Остановить сохранение

                    open_requirements_editor_conveyor(name, conveyor_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_conveyor).pack(pady=20)

            def cb_GenericCrafter_create():
                clear_window()
                
                # Устанавливаем серый фон
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text="Имя завода", font=("Arial", 12)).pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание", font=("Arial", 12)).pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)", font=("Arial", 12)).pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)", font=("Arial", 12)).pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                # Чекбокс включения энергии
                power_enabled = ctk.BooleanVar(value=False)

                def toggle_power_entry():
                    if power_enabled.get():
                        label_energy_input.pack()
                        entry_energy_input.pack()
                    else:
                        label_energy_input.pack_forget()
                        entry_energy_input.pack_forget()

                ctk.CTkCheckBox(root, text="Использует энергию", variable=power_enabled, command=toggle_power_entry).pack(pady=6)

                label_energy_input = ctk.CTkLabel(root, text="Потребление энергии")
                entry_energy_input = ctk.CTkEntry(root, width=150)
                label_energy_input.pack_forget()
                entry_energy_input.pack_forget()

                ctk.CTkLabel(root, text="Введите скорость производства 1 предмета в 1 секунду").pack()
                entry_time_input = ctk.CTkEntry(root, width=150)
                entry_time_input.pack()

                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("GenericCrafter", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_GenericCrafter():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()

                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        time_cr = int(entry_time_input.get())
                        time_craft = time_cr * 60
                        if health > 1000000 or health < 1:
                             raise ValueError
                        if size > 15 or size < 1:
                             raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Проверьте числовые значения и размер.")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    consumes = {
                        "items": [],
                        "liquids": []
                    }

                    if power_enabled.get():
                        try:
                            energy_raw = int(entry_energy_input.get())
                            power_eat = energy_raw / 60
                            consumes["power"] = power_eat
                        except ValueError:
                            messagebox.showerror("Ошибка", "Введите целое число для энергии.")
                            return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "craftTime": time_craft,
                        "itemCapacity": 50,
                        "LiduidCapacity": 50,
                        "updateEffect": "smeltsmoke",
                        "category": "crafting",
                        "type": "GenericCrafter",
                        "requirements": [],
                        "consumes": consumes,
                        "outputItems": [],
                        "outputLiquids": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("GenericCrafter", []):
                        CACHE_FILE["GenericCrafter"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "GenericCrafter"):
                        return

                    open_item_GenericCrafter_editor(name, block_data)

                ctk.CTkButton(root, text="💾 Сохранить", command=save_GenericCrafter).pack(pady=20)
                ctk.CTkButton(root, text="Назад", command=lambda: create_block(mod_name)).pack()

            def cb_solarpanel_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя панели").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)").pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                ctk.CTkLabel(root, text="Выработка энергии (макс. 1.000.000)").pack()
                entry_energy_input = ctk.CTkEntry(root, width=150)
                entry_energy_input.pack()

                # ✅ Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("SolarGenerator", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_SolarGenerator():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        energy_raw = float(entry_energy_input.get())
                        power_production = energy_raw / 60
                        if health > 1000000 or health < 1:
                            raise ValueError
                        if size > 15 or size < 1:
                            raise ValueError
                        if energy_raw > 1000000 or energy_raw < 1:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "category": "power",
                        "powerProduction": power_production,
                        "type": "SolarGenerator",
                        "requirements": [],
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("SolarGenerator", []):
                        CACHE_FILE["SolarGenerator"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:

                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "SolarGenerator"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, block_data)
                
                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)

                ctk.CTkButton(root, text="💾 Сохранить", command=save_SolarGenerator).pack(pady=20)

            def cb_StorageBlock_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя хранилищя").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)").pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                ctk.CTkLabel(root, text="Кол-во. хранения (макс. 100.000)").pack()
                entry_item_cp = ctk.CTkEntry(root, width=150)
                entry_item_cp.pack()

                # ✅ Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("StorageBlock", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_StorageBlock():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        itemCapacity = int(entry_item_cp.get())
                        if size > 15 or size < 1:
                            raise ValueError
                        if itemCapacity > 100000 or itemCapacity < 1:
                            raise ValueError
                        if health > 1000000 or health < 1:
                             raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "category": "distribution",
                        "itemCapacity": itemCapacity,
                        "type": "StorageBlock",
                        "requirements": [],
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("StorageBlock", []):
                        CACHE_FILE["StorageBlock"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:

                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "StorageBlock"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, block_data)
                
                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)

                ctk.CTkButton(root, text="💾 Сохранить", command=save_StorageBlock).pack(pady=20)

            def cb_conduit_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя трубы").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (жидкость в секунду) (макс. 50)").pack()
                entry_speed = ctk.CTkEntry(root, width=150)
                entry_speed.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("conduit", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_conduit():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = (1 / 60) * speed1
                        real_speed = round(speed * 60, 1)
                        if health > 500000 or health < 1:
                             raise ValueError
                        if speed1 > 50 or speed1 < 1:
                             raise ValueError
                        print(f"game= {real_speed} | code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    conduit_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "displaySpeed": speed,
                        "speed": speed,
                        "category": "liquid",
                        "type": "conduit",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("conduit", []):
                        CACHE_FILE["conduit"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "conduit"):
                        return  # Остановить сохранение

                    open_requirements_editor_conduit(name, conduit_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_conduit).pack(pady=20)

            def cb_ConsumesGenerator_create():
                clear_window()
                
                # Устанавливаем серый фон
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text="Имя генератора", font=("Arial", 12)).pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание", font=("Arial", 12)).pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)", font=("Arial", 12)).pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)", font=("Arial", 12)).pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                ctk.CTkLabel(root, text="Выработка энергии (макс. 5.000.000)", font=("Arial", 12)).pack()
                entry_energy_input = ctk.CTkEntry(root, width=150)
                entry_energy_input.pack()

                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("ConsumeGenerator", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_ConsumeGenerator():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        energy_raw = float(entry_energy_input.get())
                        power_production = energy_raw / 60
                        if health > 1000000 or health < 1:
                             raise ValueError
                        if size > 15 or size < 1:
                             raise ValueError
                        if energy_raw > 5000000 or energy_raw < 1:
                             raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Проверьте числовые значения и размер.")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "itemCapacity": 50,
                        "LiduidCapacity": 50,
                        "category": "power",
                        "type": "ConsumeGenerator",
                        "powerProduction": power_production,
                        "requirements": [],
                        "consumes": {
                            "items": [],
                            "liquids": []
                        },
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("ConsumeGenerator", []):
                        CACHE_FILE["ConsumeGenerator"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "ConsumeGenerator"):
                        return

                    open_item_consumes_editor(name, block_data)

                ctk.CTkButton(root, text="💾 Сохранить", command=save_ConsumeGenerator).pack(pady=20)
                ctk.CTkButton(root, text="Назад", command=lambda: create_block(mod_name)).pack()

            def cb_powernode_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя энерго узла").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 1.000.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 15)").pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                ctk.CTkLabel(root, text="Радиус (макс. 100)").pack()
                entry_range_1 = ctk.CTkEntry(root, width=150)
                entry_range_1.pack()

                ctk.CTkLabel(root, text="Кол-во Макс подключений (макс. 500)(мин. 2)").pack()
                entry_connect = ctk.CTkEntry(root, width=150)
                entry_connect.pack()

                ctk.CTkLabel(root, text="Буфер (макс. 5.000.000)").pack()
                entry_buffer = ctk.CTkEntry(root, width=150)
                entry_buffer.pack()

                # ✅ Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("PowerNode", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_PowerNode():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    range_entry = int(entry_range_1.get())
                    maxnodes = int(entry_connect.get())
                    buffer = int(entry_buffer.get())
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        range_1 = range_entry * 8
                        if health > 1000000 or health < 1:
                             raise ValueError
                        if size > 15 or size < 1:
                             raise ValueError
                        if range_entry > 100 or range_entry < 1:
                             raise ValueError
                        if maxnodes > 500 or maxnodes < 2:
                             raise ValueError
                        if buffer > 5000000 or buffer < 1:
                             raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "category": "power",
                        "type": "PowerNode",
                        "requirements": [],
                        "powerBuffer": buffer,
                        "maxNodes": maxnodes,
                        "range": range_1,
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("PowerNode", []):
                        CACHE_FILE["PowerNode"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:

                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "PowerNode"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, block_data)
                
                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)

                ctk.CTkButton(root, text="💾 Сохранить", command=save_PowerNode).pack(pady=20)

            def cb_router_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя Роутера").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (предметы в секунду) (макс. 50)").pack()
                entry_speed = ctk.CTkEntry(root, width=150)
                entry_speed.pack()

                ctk.CTkLabel(root, text="Вместимоть (макс. 25)").pack()
                entry_itemCapacity = ctk.CTkEntry(root, width=150)
                entry_itemCapacity.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("router", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_router():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    itemCapacity = int(entry_itemCapacity.get())
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = (1 / 60) * speed1
                        real_speed = round(speed * 60, 1)
                        if health > 500000 or health < 1:
                             raise ValueError
                        if speed1 > 50 or speed1 < 1:
                             raise ValueError
                        if itemCapacity > 25 or itemCapacity < 1:
                            raise ValueError
                        print(f"game= {real_speed} | code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    router_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "itemCapacity": itemCapacity,
                        "speed": speed,
                        "category": "distribution",
                        "type": "Router",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("router", []):
                        CACHE_FILE["router"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "Router"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, router_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_router).pack(pady=20)

            def cb_Junction_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя перекрёстка").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (предметы в секунду) (макс. 50)").pack()
                entry_speed = ctk.CTkEntry(root, width=150)
                entry_speed.pack()

                ctk.CTkLabel(root, text="Вместимоть (макс. 25)").pack()
                entry_itemCapacity = ctk.CTkEntry(root, width=150)
                entry_itemCapacity.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("Junction", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_Junction():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    itemCapacity = int(entry_itemCapacity.get())
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = (1 / 60) * speed1
                        real_speed = round(speed * 60, 1)
                        if health > 500000 or health < 1:
                             raise ValueError
                        if speed1 > 50 or speed1 < 1:
                             raise ValueError
                        if itemCapacity > 25 or itemCapacity < 1:
                            raise ValueError
                        print(f"game= {real_speed} | code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    Junction_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "capacity": itemCapacity,
                        "speed": speed,
                        "category": "distribution",
                        "type": "Junction",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("Junction", []):
                        CACHE_FILE["Junction"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "Junction"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, Junction_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_Junction).pack(pady=20)

            def cb_unloader_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя Разгрузчика").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (предметы в секунду) (макс. 50)").pack()
                entry_speed = ctk.CTkEntry(root, width=150)
                entry_speed.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("Unloader", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_Unloader():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = (1 / 60) * speed1
                        real_speed = round(speed * 60, 1)
                        if health > 500000 or health < 1:
                             raise ValueError
                        if speed1 > 50 or speed1 < 1:
                             raise ValueError
                        print(f"game= {real_speed} | code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    Unloader_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "speed": speed,
                        "category": "distribution",
                        "type": "Unloader",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("Unloader", []):
                        CACHE_FILE["Unloader"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "Unloader"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, Unloader_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_Unloader).pack(pady=20)
     
            def cb_liquid_router_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя Роутера").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Вместимоть (макс. 25)").pack()
                entry_itemCapacity = ctk.CTkEntry(root, width=150)
                entry_itemCapacity.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("liquid_router", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_router():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    itemCapacity = int(entry_itemCapacity.get())
                    try:
                        health = int(entry_health.get())
                        if health > 500000 or health < 1:
                             raise ValueError
                        if itemCapacity > 25 or itemCapacity < 1:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    router_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "liquidCapacity": itemCapacity,
                        "category": "liquid",
                        "type": "LiquidRouter",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("liquid_router", []):
                        CACHE_FILE["liquid_router"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "LiquidRouter"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, router_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_router).pack(pady=20)

            def cb_liquid_Junction_create():
                clear_window()

                ctk.CTkLabel(root, text="Имя перекрёстка").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП (макс. 500.000)").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                # Чтение cache.json
                with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                ctk.CTkLabel(root, text="Исследования для открытия").pack()
                research_parent_entry = ctk.CTkComboBox(
                    root,
                    values=CACHE_FILE.get("Liquid_Junction", []),
                    state="readonly",
                    width=250
                )
                research_parent_entry.pack()

                def save_Junction():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        if health > 500000 or health < 1:
                             raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    Junction_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "category": "liquid",
                        "type": "LiquidJunction",
                        "requirements": [],
                        "research": {
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("Liquid_Junction", []):
                        CACHE_FILE["Liquid_Junction"].append(name)

                    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "LiquidJunction"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, Junction_data)

                ctk.CTkButton(root, text="⬅️ Назад", command=lambda: create_block(mod_name)).pack(pady=20)
                ctk.CTkButton(root, text="💾 Сохранить", command=save_Junction).pack(pady=20)

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

        def on_mod_click(mod_name):
            """Функция, вызываемая при нажатии на мод"""
            # Уничтожаем текущие виджеты
            for widget in root.winfo_children():
                widget.destroy()
            
            # Создаем UI как в show_create_ui, но с автоматическим заполнением
            root.geometry("500x500")
            label = ctk.CTkLabel(root, text="Название папки")
            global entry_name
            entry_name = ctk.CTkEntry(root, width=200)
            entry_name.insert(0, mod_name)  # Автоматически заполняем имя мода
            
            label.pack(pady=70)
            entry_name.pack(pady=10)
            
            # Автоматически вызываем setup_mod_json без кнопки "Далее"
            setup_mod_json()

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

            label = ctk.CTkLabel(root, text="Название папки")
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
