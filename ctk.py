import customtkinter as ctk
import urllib.request
import shutil
import json, os, sys
import tkinter as tk
import threading
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
        "PowerNode": ["power-node", "power-node-large"]
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
                ("📦 Создать предмет", create_item_window),
                ("💧 Создать жидкость", create_liquid_window),
                ("🧱 Создать блок", lambda:create_block(mod_name))
            ]

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

            # Поля формы: (подпись, ширина Entry)
            fields = [
                ("Название предмета", 350),
                ("Описание", 350),
                ("Воспламеняемость (0-1)", 150),
                ("Взрывоопасность (0-1)", 150),
                ("Радиоактивность (0-1)", 150),
                ("Заряд (0-1)", 150)
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
                import urllib.request  # Если не импортировано выше

                name = entries[0].get().strip().replace(" ", "_")
                desc = entries[1].get().strip()
                try:
                    values = [float(e.get()) for e in entries[2:]]
                except ValueError:
                    messagebox.showerror("Ошибка", "Числовые значения должны быть от 0 до 1!")
                    return

                if not name or not desc:
                    messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                    return

                content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "items")
                os.makedirs(content_folder, exist_ok=True)

                item_data = {
                    "name": name,
                    "description": desc,
                    "flammability": values[0],
                    "explosiveness": values[1],
                    "radioactivity": values[2],
                    "charge": values[3]
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
                ("Название жидкости", 350),
                ("Описание", 350),
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

            icons = os.path.join("mindustry_mod_creator", "icons")
            os.makedirs(icons, exist_ok=True)

            clear_window()
            # Устанавливаем серый фон
            root.configure(fg_color="#3F3D3D")

            # Создаем основную структуру (2 колонки)
            main_frame = ctk.CTkFrame(root, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # Левая часть (все блоки) - 80% ширины
            left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

            # Правая часть (управление) - 20% ширины
            right_frame = ctk.CTkFrame(main_frame, width=150, fg_color="transparent")
            right_frame.pack(side="right", fill="y")

            # Добавляем кнопки управления в правую часть
            back_btn = ctk.CTkButton(right_frame, text="Назад", height=60, 
                                    font=("Arial", 14), command=lambda: создание_кнопки())
            back_btn.pack(fill="x", pady=(0, 10))

            editor_btn = ctk.CTkButton(right_frame, text="Редактор", height=60, 
                                    font=("Arial", 14), command=lambda: editor_cb())
            editor_btn.pack(fill="x")

            # Создаем область с прокруткой для блоков
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
            def _on_mousewheel(event):
                try:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except tk.TclError:
                    pass

            canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
            canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
            canvas.bind("<Configure>", resize_canvas)

            blocks = [
                ("Стена", lambda: cb_wall_create()),
                ("Конвейер", lambda: cb_conveyor_create()),
                ("Генератор", lambda: cb_ConsumesGenerator_create()),
                ("Солн. панель", lambda: cb_solarpanel_create()),
                ("Хранилище", lambda: cb_StorageBlock_create()),
                ("Завод", lambda: cb_GenericCrafter_create()),
                ("Труба", lambda: cb_conduit_create()),
                ("Предм. мост", lambda: cb_BridgeConveyor_create()),
                ("Жидк. мост", lambda: cb_bridge_liquid_create()),
                ("Энергоузел", lambda: cb_powernode_create())
            ]

            # Создаем контейнер для всех блоков
            blocks_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            blocks_container.pack(fill="both", expand=True, pady=10)

            # Добавляем все блоки по 3 в ряд (без разделения на части)
            for i in range(0, len(blocks), 3):
                row_frame = ctk.CTkFrame(blocks_container, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)
                
                for block in blocks[i:i+3]:
                    btn = ctk.CTkButton(
                        row_frame, 
                        text=block[0], 
                        height=65,
                        font=("Arial", 13),
                        command=block[1]
                    )
                    btn.pack(side="left", padx=5, expand=True, fill="x")

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
                name_icons = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                icons_folder = os.path.join("mindustry_mod_creator", "icons")
                icons_url = "https://raw.githubusercontent.com/Anuken/Mindustry/master/core/assets-raw/sprites/items/"
                
                def load_icons():
                    os.makedirs(icons_folder, exist_ok=True)
                    for name in name_icons:
                        url_icon_folder = f"{icons_url}item-{name}.png"
                        save_icon = os.path.join(icons_folder, f"{name}.png")
                        if not os.path.exists(save_icon):
                            try:
                                print(f"Скачиваю: {name}.png...")
                                urllib.request.urlretrieve(url_icon_folder, save_icon)
                                print(f"Успешно: {name}.png")
                            except Exception as e:
                                print(f"Ошибка загрузки {name}.png: {e}")
                
                load_icons()
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
                        card = create_item_card(items_frame, item)
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
                
                tabview = ctk.CTkTabview(content_frame, fg_color="#3a3a3a")
                tabview.pack(fill="both", expand=True, padx=10, pady=10)
                
                tab_default = tabview.add("Стандартные")
                
                canvas = tk.Canvas(tab_default, bg="#3a3a3a", highlightthickness=0)
                scrollbar = ctk.CTkScrollbar(tab_default, orientation="vertical", command=canvas.yview)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                scrollbar.pack(side="right", fill="y")
                canvas.pack(side="left", fill="both", expand=True)
                
                items_frame = ctk.CTkFrame(canvas, fg_color="#3a3a3a")
                canvas.create_window((0, 0), window=items_frame, anchor="nw")
                
                update_grid(canvas, items_frame, default_items)
                
                canvas.bind("<Configure>", lambda e: update_grid(canvas, items_frame, default_items))
                items_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                
                if mod_items:
                    tab_mod = tabview.add("Модовые")
                    
                    mod_canvas = tk.Canvas(tab_mod, bg="#3a3a3a", highlightthickness=0)
                    mod_scrollbar = ctk.CTkScrollbar(tab_mod, orientation="vertical", command=mod_canvas.yview)
                    mod_canvas.configure(yscrollcommand=mod_scrollbar.set)
                    
                    mod_scrollbar.pack(side="right", fill="y")
                    mod_canvas.pack(side="left", fill="both", expand=True)
                    
                    mod_items_frame = ctk.CTkFrame(mod_canvas, fg_color="#3a3a3a")
                    mod_canvas.create_window((0, 0), window=mod_items_frame, anchor="nw")
                    
                    update_grid(mod_canvas, mod_items_frame, mod_items)
                    
                    mod_canvas.bind("<Configure>", lambda e: update_grid(mod_canvas, mod_items_frame, mod_items))
                    mod_items_frame.bind("<Configure>", lambda e: mod_canvas.configure(scrollregion=mod_canvas.bbox("all")))
                
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
                
                # Устанавливаем серый фон для всего окна
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор ресурсов для стройки '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",  # Цвет фона полосы прокрутки
                        bg="#6a6a6a",           # Цвет ползунка
                        activebackground="#7a7a7a"  # Цвет при наведении
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 5000:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 5000!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["requirements"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    
                    # Удаляем предмет из исходного списка
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]  # Извлекаем имя предмета
                    
                    # Удаляем из правого списка
                    selected_listbox.delete(selected[0])
                    del block_data["requirements"][selected[0]]
                    
                    # Возвращаем предмет в соответствующий список
                    if item in [default_listbox.get(i) for i in range(default_listbox.size())]:
                        # Если предмет есть в default списке, не добавляем снова
                        pass
                    elif item in [mod_listbox.get(i) for i in range(mod_listbox.size())]:
                        # Если предмет есть в mod списке, не добавляем снова
                        pass
                    else:
                        # Проверяем, откуда был взят предмет
                        if item in default_items:
                            default_listbox.insert(tk.END, item)
                        else:
                            mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(
                    button_frame, 
                    text="Добавить слева", 
                    command=lambda: add_from_listbox(default_listbox),
                    width=120
                ).grid(row=0, column=0, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Добавить из мода", 
                    command=lambda: add_from_listbox(mod_listbox),
                    width=120
                ).grid(row=0, column=1, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Убрать выбранное", 
                    command=remove_selected,
                    width=120
                ).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    
                    # Создаем окно прогресса
                    progress_window = ctk.CTkToplevel(root)
                    progress_window.title("Загрузка текстур")
                    progress_window.geometry("400x150")
                    progress_window.transient(root)
                    progress_window.grab_set()
                    
                    progress_label = ctk.CTkLabel(progress_window, text="Загрузка текстур...")
                    progress_label.pack(pady=10)
                    
                    progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)
                    
                    status_label = ctk.CTkLabel(progress_window, text="0/0")
                    status_label.pack(pady=5)
                    
                    # Загрузка текстур конвейера
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
                        progress = (downloaded + 1) / total_files
                        progress_bar.set(progress)
                        status_label.configure(text=f"{downloaded + 1}/{total_files}")
                        progress_window.update()
                    
                    # Функция для загрузки в отдельном потоке
                    def download_textures():
                        nonlocal downloaded
                        for name in texture_names:
                            new_name = name.replace("conveyor", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                texture_url = f"{base_url}{name}.png"
                                try:
                                    urllib.request.urlretrieve(texture_url, texture_path)
                                    downloaded += 1
                                    progress_label.configure(text=f"Загружено: {new_name}.png")
                                except Exception as e:
                                    progress_label.configure(text=f"Ошибка при загрузке {new_name}.png")
                                finally:
                                    update_progress()
                            else:
                                downloaded += 1
                                update_progress()
                        
                        progress_window.after(1000, progress_window.destroy)
                    
                    threading.Thread(target=download_textures, daemon=True).start()

                ctk.CTkButton(
                    root, 
                    text="Готово", 
                    command=finalize_block, 
                    font=("Arial", 12),
                    width=200,
                    height=40
                ).pack(pady=20)

            def open_item_GenericCrafter_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор предметов потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с прокруткой
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 50!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["consumes"]["items"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["items"][selected[0]]
                    
                    # Возвращаем предмет в исходный список
                    if item in default_items:
                        default_listbox.insert(tk.END, item)
                    else:
                        mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_item():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_item, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_item, width=200).pack(pady=10)

            def open_liquid_GenericCrafter_editor_out(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                ctk.CTkLabel(root, text=f"Выбор жидкости выхода для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    if len(block_data["outputLiquids"]) >= 1:
                        messagebox.showerror("Ошибка", "Максимум 1 выходных жидкостей!")
                        return
                    try:
                        user_input = float(entry_amount.get())
                        if user_input < 1 or user_input > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество (от 1 до 50)!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите жидкость!")
                        return

                    liquid = listbox.get(selected[0])
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["outputLiquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    liquid = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["outputLiquids"][selected[0]]
                    
                    # Возвращаем жидкость в исходный список
                    if liquid in default_liquids:
                        default_listbox.insert(tk.END, liquid)
                    else:
                        mod_listbox.insert(tk.END, liquid)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_liquid():
                    if not block_data["outputLiquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_requirements_editor(block_name, block_data)

                def skip_liquid():
                    if not block_data["outputItems"]:
                        messagebox.showerror("Ошибка", "Добавьте хотя бы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_requirements_editor(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_liquid, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_liquid, width=200).pack(pady=10)

            def open_item_GenericCrafter_editor_out(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                ctk.CTkLabel(root, text=f"Выбор предметов выхода для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    if len(block_data["outputItems"]) >= 5:
                        messagebox.showerror("Ошибка", "Максимум 5 выходных предметов!")
                        return
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 50!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["outputItems"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["outputItems"][selected[0]]
                    
                    # Возвращаем предмет в исходный список
                    if item in default_items:
                        default_listbox.insert(tk.END, item)
                    else:
                        mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_item():
                    if not block_data["outputItems"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_GenericCrafter_editor_out(block_name, block_data)

                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_GenericCrafter_editor_out(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_item, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_item, width=200).pack(pady=10)

            def open_liquid_GenericCrafter_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                ctk.CTkLabel(root, text=f"Выбор жидкостей потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        user_input = float(entry_amount.get())
                        if user_input < 1 or user_input > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество (от 1 до 50)!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите жидкость!")
                        return

                    liquid = listbox.get(selected[0])
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["consumes"]["liquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    liquid = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["liquids"][selected[0]]
                    
                    # Возвращаем жидкость в исходный список
                    if liquid in default_liquids:
                        default_listbox.insert(tk.END, liquid)
                    else:
                        mod_listbox.insert(tk.END, liquid)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_liquid():
                    if not block_data["consumes"]["liquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                def skip_liquid():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Добавьте хотя бы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_liquid, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_liquid, width=200).pack(pady=10)

            def open_requirements_editor_conduit(block_name, block_data):
                clear_window()
                
                # Устанавливаем серый фон для всего окна
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор ресурсов для стройки '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",  # Цвет фона полосы прокрутки
                        bg="#6a6a6a",           # Цвет ползунка
                        activebackground="#7a7a7a"  # Цвет при наведении
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 5000:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 5000!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["requirements"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    
                    # Удаляем предмет из исходного списка
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]  # Извлекаем имя предмета
                    
                    # Удаляем из правого списка
                    selected_listbox.delete(selected[0])
                    del block_data["requirements"][selected[0]]
                    
                    # Возвращаем предмет в соответствующий список
                    if item in [default_listbox.get(i) for i in range(default_listbox.size())]:
                        # Если предмет есть в default списке, не добавляем снова
                        pass
                    elif item in [mod_listbox.get(i) for i in range(mod_listbox.size())]:
                        # Если предмет есть в mod списке, не добавляем снова
                        pass
                    else:
                        # Проверяем, откуда был взят предмет
                        if item in default_items:
                            default_listbox.insert(tk.END, item)
                        else:
                            mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(
                    button_frame, 
                    text="Добавить слева", 
                    command=lambda: add_from_listbox(default_listbox),
                    width=120
                ).grid(row=0, column=0, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Добавить из мода", 
                    command=lambda: add_from_listbox(mod_listbox),
                    width=120
                ).grid(row=0, column=1, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Убрать выбранное", 
                    command=remove_selected,
                    width=120
                ).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    
                    # Создаем окно прогресса
                    progress_window = ctk.CTkToplevel(root)
                    progress_window.title("Загрузка текстур")
                    progress_window.geometry("400x150")
                    progress_window.transient(root)
                    progress_window.grab_set()
                    
                    progress_label = ctk.CTkLabel(progress_window, text="Загрузка текстур...")
                    progress_label.pack(pady=10)
                    
                    progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)
                    
                    status_label = ctk.CTkLabel(progress_window, text="0/0")
                    status_label.pack(pady=5)
                    
                    # Загрузка текстур конвейера
                    texture_names = [
                        "conduit-top-0", "conduit-top-1", "conduit-top-2", "conduit-top-3",
                        "conduit-top-4", "conduit-top-5", "conduit-top-6"
                    ]

                    sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name)
                    os.makedirs(sprite_folder, exist_ok=True)

                    base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/conduit/"
                    
                    total_files = len(texture_names)
                    downloaded = 0
                    
                    def update_progress():
                        progress = (downloaded + 1) / total_files
                        progress_bar.set(progress)
                        status_label.configure(text=f"{downloaded + 1}/{total_files}")
                        progress_window.update()
                    
                    # Функция для загрузки в отдельном потоке
                    def download_textures():
                        nonlocal downloaded
                        for name in texture_names:
                            new_name = name.replace("conduit", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                texture_url = f"{base_url}{name}.png"
                                try:
                                    urllib.request.urlretrieve(texture_url, texture_path)
                                    downloaded += 1
                                    progress_label.configure(text=f"Загружено: {new_name}.png")
                                except Exception as e:
                                    progress_label.configure(text=f"Ошибка при загрузке {new_name}.png")
                                finally:
                                    update_progress()
                            else:
                                downloaded += 1
                                update_progress()
                        
                        progress_window.after(1000, progress_window.destroy)
                    
                    threading.Thread(target=download_textures, daemon=True).start()

                ctk.CTkButton(
                    root, 
                    text="Готово", 
                    command=finalize_block, 
                    font=("Arial", 12),
                    width=200,
                    height=40
                ).pack(pady=20)

            def open_item_consumes_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор предметов потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с прокруткой
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 50!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["consumes"]["items"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["items"][selected[0]]
                    
                    # Возвращаем предмет в исходный список
                    if item in default_items:
                        default_listbox.insert(tk.END, item)
                    else:
                        mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_item():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_consumes_editor(block_name, block_data)

                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_consumes_editor(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_item, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_item, width=200).pack(pady=10)

            def open_liquid_consumes_editor(block_name, block_data):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                ctk.CTkLabel(root, text=f"Выбор жидкостей потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        user_input = float(entry_amount.get())
                        if user_input < 1 or user_input > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество (от 1 до 50)!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите жидкость!")
                        return

                    liquid = listbox.get(selected[0])
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["consumes"]["liquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    liquid = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["liquids"][selected[0]]
                    
                    # Возвращаем жидкость в исходный список
                    if liquid in default_liquids:
                        default_listbox.insert(tk.END, liquid)
                    else:
                        mod_listbox.insert(tk.END, liquid)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_liquid():
                    if not block_data["consumes"]["liquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_requirements_editor(block_name, block_data)

                def skip_liquid():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Добавьте хотя бы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_requirements_editor(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_liquid, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_liquid, width=200).pack(pady=10)

            def open_requirements_editor_BridgeConveyor(block_name, block_data):
                clear_window()
                
                # Устанавливаем серый фон для всего окна
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор ресурсов для стройки '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",  # Цвет фона полосы прокрутки
                        bg="#6a6a6a",           # Цвет ползунка
                        activebackground="#7a7a7a"  # Цвет при наведении
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 5000:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 5000!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["requirements"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    
                    # Удаляем предмет из исходного списка
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]  # Извлекаем имя предмета
                    
                    # Удаляем из правого списка
                    selected_listbox.delete(selected[0])
                    del block_data["requirements"][selected[0]]
                    
                    # Возвращаем предмет в соответствующий список
                    if item in [default_listbox.get(i) for i in range(default_listbox.size())]:
                        # Если предмет есть в default списке, не добавляем снова
                        pass
                    elif item in [mod_listbox.get(i) for i in range(mod_listbox.size())]:
                        # Если предмет есть в mod списке, не добавляем снова
                        pass
                    else:
                        # Проверяем, откуда был взят предмет
                        if item in default_items:
                            default_listbox.insert(tk.END, item)
                        else:
                            mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(
                    button_frame, 
                    text="Добавить слева", 
                    command=lambda: add_from_listbox(default_listbox),
                    width=120
                ).grid(row=0, column=0, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Добавить из мода", 
                    command=lambda: add_from_listbox(mod_listbox),
                    width=120
                ).grid(row=0, column=1, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Убрать выбранное", 
                    command=remove_selected,
                    width=120
                ).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    
                    # Создаем окно прогресса
                    progress_window = ctk.CTkToplevel(root)
                    progress_window.title("Загрузка текстур")
                    progress_window.geometry("400x150")
                    progress_window.transient(root)
                    progress_window.grab_set()
                    
                    progress_label = ctk.CTkLabel(progress_window, text="Загрузка текстур...")
                    progress_label.pack(pady=10)
                    
                    progress_bar = ctk.CTkProgressBar(progress_window, width=300)
                    progress_bar.pack(pady=10)
                    progress_bar.set(0)
                    
                    status_label = ctk.CTkLabel(progress_window, text="0/0")
                    status_label.pack(pady=5)
                    
                    # Загрузка текстур конвейера
                    texture_names = [
                        "bridge-conveyor", "bridge-conveyor-arrow", 
                        "bridge-conveyor-bridge", "bridge-conveyor-end"
                    ]

                    sprite_folder = os.path.join("mindustry_mod_creator", "mods", mod_name, "sprites", block_type, block_name)
                    os.makedirs(sprite_folder, exist_ok=True)

                    base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/bridge-conveyors/"
                    
                    total_files = len(texture_names)
                    downloaded = 0
                    
                    def update_progress():
                        progress = (downloaded + 1) / total_files
                        progress_bar.set(progress)
                        status_label.configure(text=f"{downloaded + 1}/{total_files}")
                        progress_window.update()
                    
                    # Функция для загрузки в отдельном потоке
                    def download_textures():
                        nonlocal downloaded
                        for name in texture_names:
                            new_name = name.replace("bridge-conveyor", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                texture_url = f"{base_url}{name}.png"
                                try:
                                    urllib.request.urlretrieve(texture_url, texture_path)
                                    downloaded += 1
                                    progress_label.configure(text=f"Загружено: {new_name}.png")
                                except Exception as e:
                                    progress_label.configure(text=f"Ошибка при загрузке {new_name}.png")
                                finally:
                                    update_progress()
                            else:
                                downloaded += 1
                                update_progress()
                        
                        progress_window.after(1000, progress_window.destroy)
                    
                    threading.Thread(target=download_textures, daemon=True).start()

                ctk.CTkButton(
                    root, 
                    text="Готово", 
                    command=finalize_block, 
                    font=("Arial", 12),
                    width=200,
                    height=40
                ).pack(pady=20)

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
                        print(f"game= {real_speed}+ (10+- | 50+- | 100+-) || code= {speed}")
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
                        time_craft = time_cr / 60
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
                        power_production = int(energy_raw / 60)
                        if health > 1000000 or health < 1:
                            raise ValueError
                        if size > 15 or size < 1:
                            raise ValueError
                        if power_production > 1000000 or power_production < 1:
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
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
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
                        if power_production > 5000000 or power_production < 1:
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
