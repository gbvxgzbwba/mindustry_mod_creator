import os
import json
import tkinter as tk
import sys
import urllib.request
import tqdm
import shutil
import json, os

from tkinter import simpledialog
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tqdm import tqdm

requirements_list = []

CACHE_FILE = "cache.json"
def resource_path(relative_path):
    """Получаем путь к файлу при запуске из .exe и из .py"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_or_create_cache(mod_folder):
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
            "steam-generator"
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
        "bridge_conveyor": ["bridge_conveyor"],
        "bridge_conveyor_enegry": ["phase_conveyor"],
        "bridge-conduit": ["bridge-conduit"],
        "bridge-conduit_enegry": ["phase-conduit"]
    }
    path = os.path.join(mod_folder, "cache.json")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_cache, f, indent=4, ensure_ascii=False)
        return default_cache
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_cache, f, indent=4, ensure_ascii=False)
        return default_cache
    
class MindustryModCreator:
    def main():
        def setup_mod_json():
            mod_name = entry_name.get().strip()
            if not mod_name:
                messagebox.showerror("Ошибка", "Введите название папки!")
                return

            current_dir = os.getcwd()
            global mod_folder
            mod_folder = os.path.join(current_dir, mod_name)
            os.makedirs(mod_folder, exist_ok=True)

            # Загрузка или создание cache.json после создания mod_folder
            cache_data = load_or_create_cache(mod_folder)

            mod_json_path = os.path.join(mod_folder, "mod.json")

            if os.path.exists(mod_json_path):
                result = messagebox.askyesno("Файл уже существует", "mod.json уже существует. Перезаписать?")
                if result:
                    open_mod_editor(load_existing=True)
                else:
                    создание_кнопки()
            else:
                open_mod_editor(load_existing=False)

        def clear_window():
            try:
                for widget in root.winfo_children():
                    widget.destroy()
            except tk.TclError:
                print()

        def open_mod_editor(load_existing=False):
            """Открывает окно редактирования mod.json"""
            clear_window()

            # Заголовок окна
            title_label = tk.Label(root, text="Редактирование mod.json", font=("Arial", 16, "bold"))
            title_label.pack(pady=10)

            # Основной фрейм формы
            form_frame = tk.Frame(root)
            form_frame.pack(pady=10)

            # Подписи и поля ввода
            field_names = ["Название мода", "Автор", "Описание"]
            entries = []

            for i, field in enumerate(field_names):
                label = tk.Label(form_frame, text=field, anchor="w")
                entry = tk.Entry(form_frame, bg="#CFDDF3", width=50)
                label.grid(row=i, column=0, sticky="w", padx=10, pady=5)
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries.append(entry)

            # Минимальная версия игры (Combobox)
            label_version = tk.Label(form_frame, text="Минимальная версия игры")
            combo_version = ttk.Combobox(form_frame, values=["146", "149"], state="readonly", width=10)
            combo_version.set("146")

            label_version.grid(row=3, column=0, sticky="w", padx=10, pady=5)
            combo_version.grid(row=3, column=1, padx=10, pady=5, sticky="w")

            # Загрузка существующего mod.json, если нужно
            if load_existing:
                mod_json_path = os.path.join(mod_folder, "mod.json")
                with open(mod_json_path, "r", encoding="utf-8") as file:
                    mod_data = json.load(file)
                entries[0].insert(0, mod_data.get("name", ""))
                entries[1].insert(0, mod_data.get("author", ""))
                entries[2].insert(0, mod_data.get("description", ""))
                combo_version.set(str(mod_data.get("minGameVersion", "146")))

            # Кнопка сохранения
            button_create = tk.Button(root, text="💾 Сохранить mod.json", font=("Arial", 12), bg="#A7D7C5",
                                    command=lambda: create_mod_json(*entries, combo_version))
            button_create.pack(pady=20)

        def create_mod_json(entry_name_1, entry_name_2, entry_name_3, combo_version):
            """Создаёт или обновляет mod.json"""
            name = entry_name_1.get().strip()
            author = entry_name_2.get().strip()
            description = entry_name_3.get().strip()
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
                "version": 0.0,
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
            label = tk.Label(root, text="Что вы хотите добавить?", font=("Arial", 16, "bold"))
            label.pack(pady=(40, 20))

            # Контейнер для кнопок
            button_frame = tk.Frame(root)
            button_frame.pack(pady=10)

            # Универсальные стили
            button_style = {
                "width": 25,
                "height": 2,
                "font": ("Arial", 12),
                "bg": "#D9E8FB",
                "activebackground": "#BDD7EE"
            }

            # Кнопки
            buttons = [
                ("📦 Создать предмет", create_item_window),
                ("💧 Создать жидкость", create_liquid_window),
                ("🧱 Создать блок", create_block)
            ]

            for i, (text, cmd) in enumerate(buttons):
                btn = tk.Button(button_frame, text=text, command=cmd, **button_style)
                btn.grid(row=i, column=0, pady=8)

        def create_item_window():
            """Форма для создания предмета"""
            clear_window()

            tk.Label(root, text="Создание нового предмета", font=("Arial", 16, "bold")).pack(pady=10)

            form_frame = tk.Frame(root)
            form_frame.pack(pady=10)

            # Поля формы: (подпись, ширина Entry)
            fields = [
                ("Название предмета", 50),
                ("Описание", 50),
                ("Воспламеняемость (0-1)", 10),
                ("Взрывоопасность (0-1)", 10),
                ("Радиоактивность (0-1)", 10),
                ("Заряд (0-1)", 10)
            ]

            entries = []

            for i, (label_text, width) in enumerate(fields):
                label = tk.Label(form_frame, text=label_text)
                entry = tk.Entry(form_frame, width=width, bg="#E8F0FE")
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

                content_folder = os.path.join(mod_folder, "content", "items")
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
                sprite_folder = os.path.join(mod_folder, "sprites", "items")
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
            tk.Button(root, text="💾 Сохранить предмет", font=("Arial", 12), bg="#C4F1C5",
                    command=save_item).pack(pady=20)

        def create_liquid_window():
            """Форма для создания жидкости"""
            clear_window()

            tk.Label(root, text="Создание новой жидкости", font=("Arial", 16, "bold")).pack(pady=10)

            form_frame = tk.Frame(root)
            form_frame.pack(pady=10)

            fields = [
                ("Название жидкости", 50),
                ("Описание", 50),
                ("Густота (0-1)", 10),
                ("Температура (0-1)", 10),
                ("Воспламеняемость (0-1)", 10),
                ("Взрывоопасность (0-1)", 10),
                ("Цвет (#rrggbb)", 10)
            ]

            entries = []

            for i, (label_text, width) in enumerate(fields):
                label = tk.Label(form_frame, text=label_text)
                entry = tk.Entry(form_frame, width=width, bg="#E8F0FE")
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

                content_folder = os.path.join(mod_folder, "content", "liquids")
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
            tk.Button(root, text="💾 Сохранить жидкость", font=("Arial", 12), bg="#C4F1C5",
                    command=save_liquid).pack(pady=20)

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

        def create_block():
            root = None  # ← глобально

            clear_window()
            #/////////////////////////////////////////////////////////////////////////////////////
            canvas = tk.Canvas(root)
            scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            scrollable_frame = tk.Frame(canvas)
            window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

            def resize_canvas(event):
                canvas_width = event.width
                canvas.itemconfig(window_id, width=canvas_width)

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", resize_canvas)

            blocks = [
                ("Создать стену", lambda: cb_wall_create()),
                ("Создать солнечную панель", lambda: cb_solarpanel_create()),
                ("Создать генератор", lambda: cb_ConsumesGenerator_create()),
                ("Создать хранилище", lambda: cb_StorageBlock_create()),
                ("Создать завод", lambda: cb_GenericCrafter_create()),
                ("Создать конвейер", lambda: cb_conveyor_create()),
                ("Создать трубу", lambda: cb_conduit_create()),
                ("Создать предметный мост", lambda: cb_bridge_conveyor_create()),
                ("Создать предметный мост (на энергии)", lambda: cb_bridge_conveyor_energy_create()),
                ("Создать жидкостный мост", lambda: cb_bridge_liquid_create()),
                ("Создать жидкостный мост (на энергии)", lambda: cb_bridge_liquid_energy_create()),
                ("Создать руду", lambda: cb_ore_create()),
                ("Назад", lambda: создание_кнопки())
            ]

            for text, command in blocks:
                btn = tk.Button(scrollable_frame, text=text, font=("Arial", 10), width=35, height=2, command=command)
                btn.pack(pady=5)
            #//////////////////////////////////////////////////////////////////////////////////

            #////////////////////////////////////////////////////////////////
            editor = tk.Button(root, text="Редактор JSON", font=0, command=lambda: editor_cb())
            editor.pack(anchor="nw")

            def editor_cb():
                clear_window()

                tk.Button(root, text="⬅️ Назад", font=0, command=create_block).pack(pady=10)
                tk.Label(root, text="Редактирование блоков", font=("Arial", 14)).pack(pady=5)

                blocks_folder = os.path.join(mod_folder, "content", "blocks")

                # Чтение всех подпапок, кроме скрытых или запрещённых
                for folder_name in os.listdir(blocks_folder):
                    folder_path = os.path.join(blocks_folder, folder_name)

                    # 🔒 Пропустить "environment" и любые начинающиеся с точки (скрытые)
                    if not os.path.isdir(folder_path) or folder_name == "environment" or folder_name.startswith("."):
                        continue

                    # Кнопка открытия этой папки
                    btn = tk.Button(root, text=folder_name, font=("Arial", 10), width=30, height=2,
                                    command=lambda p=folder_path: open_block_folder(p))
                    btn.pack(pady=3)

            def open_block_folder(folder_path):
                clear_window()

                tk.Button(root, text="⬅️ Назад", font=0, command=editor_cb).pack(pady=10)

                folder_name = os.path.basename(folder_path)
                tk.Label(root, text=f"Блоки из: {folder_name}", font=("Arial", 12)).pack(pady=5)

                for file in os.listdir(folder_path):
                    if file.endswith(".json"):
                        block_name = os.path.splitext(file)[0]
                        block_type = os.path.basename(folder_path)

                        frame = tk.Frame(root)
                        frame.pack(pady=2)

                        tk.Label(frame, text=block_name, width=40, anchor="w").pack(side="left")

                        # Кнопка редактирования
                        tk.Button(
                            frame,
                            text="Редактировать",
                            command=lambda b=block_name, p=folder_path: edit_block(b, p)
                        ).pack(side="right")

                        # Кнопка для удаления блока
                        def make_delete_callback(bname, fpath):
                            return lambda: delete_block(bname, fpath)

                        tk.Button(
                            frame,
                            text="Удалить",
                            command=make_delete_callback(block_name, folder_path)
                        ).pack(side="right")

            def delete_block(block_name, folder_path):
                block_type = os.path.basename(folder_path)
                json_path = os.path.join(mod_folder, f"content/blocks/{block_type}/{block_name}.json")
                sprite_folder_path = os.path.join(mod_folder, f"sprites/{block_type}/{block_name}")
                block_type_folder = os.path.join(mod_folder, f"content/blocks/{block_type}")
                sprite_type_folder = os.path.join(mod_folder, f"sprites/{block_type}")
                cache_path = resource_path(mod_folder, "cache.json")

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

                    # Удаление пустых родительских папок
                    for path in [block_type_folder, sprite_type_folder]:
                        if os.path.isdir(path) and not os.listdir(path):
                            os.rmdir(path)

                    # Обновить интерфейс
                    parent_folder = os.path.dirname(folder_path)
                    if os.path.exists(folder_path):
                        open_block_folder(folder_path)
                    elif os.path.exists(parent_folder):
                        open_block_folder(parent_folder)
                    else:
                        editor_cb()

                except Exception as e:
                    messagebox.showerror("Ошибка удаления", f"Не удалось удалить: {e}")

            def edit_block(block_name, folder_path):
                path = os.path.join(folder_path, f"{block_name}.json")

                if not os.path.exists(path):
                    messagebox.showerror("Ошибка", f"Файл {block_name}.json не найден.")
                    return

                with open(path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Некорректный JSON.")
                        return

                # Показываем содержимое (или можешь отредактировать его через отдельное окно)
                content = json.dumps(data, indent=2, ensure_ascii=False)
                top = tk.Toplevel(root)
                top.title(f"Редактирование: {block_name}")
                text = tk.Text(top, width=80, height=25)
                text.insert("1.0", content)
                text.pack()

                def save_changes():
                    try:
                        new_data = json.loads(text.get("1.0", tk.END))
                        with open(path, "w", encoding="utf-8") as fw:
                            json.dump(new_data, fw, indent=4, ensure_ascii=False)
                        messagebox.showinfo("Успех", "Файл успешно сохранён!")
                    except json.JSONDecodeError:
                        messagebox.showerror("Ошибка", "Неверный JSON.")

                tk.Button(top, text="Сохранить", command=save_changes).pack(pady=5)
            #////////////////////////////////////////////////////////////
            def open_requirements_editor(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор ресурсов для стройки '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["requirements"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join(mod_folder, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    #texture_auto
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    # texture_auto
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    if 1 <= size <= 10:
                        texture_url = f"https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/block-{size}.png"  # Замените на реальный URL
                        sprite_folder = os.path.join(mod_folder, "sprites", block_type, block_name)
                        texture_name = f"{block_name}.png"
                        texture_path = os.path.join(sprite_folder, texture_name)

                        os.makedirs(sprite_folder, exist_ok=True)

                        if not os.path.exists(texture_path):
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"Текстура {texture_name} успешно загружена в {texture_path}")
                                print("Для изменения текстуры откройте текстуру по пути который сказали и меняйте её, 1 размер = 32x32, каждый следующий +32.")
                            except Exception as e:
                                print(f"Ошибка при загрузке текстуры: {e}")
                        else:
                            print(f"Текстура {texture_name} уже существует, загрузка пропущена.")

                tk.Button(root, text="Готово", command=finalize_block, font=10).pack(pady=20)

            def open_requirements_editor_conveyor(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор ресурсов для стройки '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["requirements"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join(mod_folder, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    #texture_auto
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    if size:
                        texture_names = [
                            "conveyor", "conveyor-0-0", "conveyor-0-1", "conveyor-0-2", "conveyor-0-3",
                            "conveyor-1-0", "conveyor-1-1", "conveyor-1-2", "conveyor-1-3",
                            "conveyor-2-0", "conveyor-2-1", "conveyor-2-2", "conveyor-2-3",
                            "conveyor-3-0", "conveyor-3-1", "conveyor-3-2", "conveyor-3-3",
                            "conveyor-4-0", "conveyor-4-1", "conveyor-4-2", "conveyor-4-3"
                        ]

                        sprite_folder = os.path.join(mod_folder, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)

                        base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/conveyors/"

                        # Определим список отсутствующих текстур
                        missing_textures = []
                        for name in texture_names:
                            new_name = name.replace("conveyor", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                missing_textures.append((name, new_name, texture_path))

                        if len(missing_textures) < len(texture_names):
                            messagebox.showinfo("Пропуск", "Некоторые текстуры уже установлены.")

                        # Скачиваем только те, которых не хватает
                        for name, new_name, texture_path in tqdm(missing_textures, desc="Загрузка текстур", colour="#65EC3B"):
                            texture_url = f"{base_url}{name}.png"
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"✅ Загружено: {new_name}.png в {texture_path}")
                            except Exception as e:
                                print(f"❌ Ошибка при загрузке {new_name}.png: {e}")

                tk.Button(root, text="Готово", command=finalize_block, font=10).pack(pady=20)

            def open_requirements_editor_bridge_conveyor(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор ресурсов для стройки '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["requirements"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join(mod_folder, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    #texture_auto
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    if size:
                        texture_names = [
                            "bridge-conveyor", "bridge-conveyor-bridge", "bridge-conveyor-end", "bridge-conveyor-arrow"
                        ]

                        sprite_folder = os.path.join(mod_folder, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)

                        base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/bridge-conveyors/"

                        missing_textures = []
                        for name in texture_names:
                            new_name = name.replace("bridge-conveyor", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                missing_textures.append((name, new_name, texture_path))

                        if len(missing_textures) < len(texture_names):
                            messagebox.showinfo("Пропуск", "Некоторые текстуры уже установлены.")

                        # Скачиваем только те, которых не хватает
                        for name, new_name, texture_path in tqdm(missing_textures, desc="Загрузка текстур", colour="#65EC3B"):
                            texture_url = f"{base_url}{name}.png"
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"✅ Загружено: {new_name}.png в {texture_path}")
                            except Exception as e:
                                print(f"❌ Ошибка при загрузке {new_name}.png: {e}")
                tk.Button(root, text="Готово", command=finalize_block, font=10).pack(pady=20)

            def open_requirements_editor_conduit(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор ресурсов для стройки '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["requirements"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join(mod_folder, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    #texture_auto
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    if size:
                        texture_names = [
                            "conduit-top-0", "conduit-top-1", "conduit-top-2", "conduit-top-3",
                            "conduit-top-4", "conduit-top-5", "conduit-top-6"
                        ]

                        sprite_folder = os.path.join(mod_folder, "sprites", block_type, block_name)
                        os.makedirs(sprite_folder, exist_ok=True)

                        base_url = "https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/conduit/"

                        missing_textures = []
                        for name in texture_names:
                            new_name = name.replace("conduit", block_name, 1)
                            texture_path = os.path.join(sprite_folder, f"{new_name}.png")
                            if not os.path.exists(texture_path):
                                missing_textures.append((name, new_name, texture_path))

                        if len(missing_textures) < len(texture_names):
                            messagebox.showinfo("Пропуск", "Некоторые текстуры уже установлены.")

                        # Скачиваем только те, которых не хватает
                        for name, new_name, texture_path in tqdm(missing_textures, desc="Загрузка текстур", colour="#65EC3B"):
                            texture_url = f"{base_url}{name}.png"
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"✅ Загружено: {new_name}.png в {texture_path}")
                            except Exception as e:
                                print(f"❌ Ошибка при загрузке {new_name}.png: {e}")

                tk.Button(root, text="Готово", command=finalize_block, font=10).pack(pady=20)

            def open_item_consumes_editor(block_name, block_data):
                """Меню для редактирования потребляемых предметов"""
                clear_window()

                tk.Label(root, text=f"Выбор предметов потребления для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["consumes"]["items"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_item():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_consumes_editor(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_consumes_editor(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_item, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_item, font=10).pack(pady=20)

            def open_liquid_consumes_editor(block_name, block_data):
                """Меню для редактирования потребляемых жидкостей"""
                clear_window()

                tk.Label(root, text=f"Выбор жидкостей потребления для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

                # Списки жидкостей
                default_liquids = [
                    "water", "slag", "oil", "cryofluid"
                ]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                    # Преобразование: (1/60) * ввод
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["consumes"]["liquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")


                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["consumes"]["liquids"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_liquid():
                    if not block_data["consumes"]["liquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_requirements_editor(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_liquid():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Добавте хотябы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_requirements_editor(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_liquid, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_liquid, font=10).pack(pady=20)

            def open_item_GenericCrafter_editor(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор предметов потребления для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["consumes"]["items"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_item():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_item, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_item, font=10).pack(pady=20)

            def open_liquid_GenericCrafter_editor(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор жидкостей потребления для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

                # Списки жидкостей
                default_liquids = [
                    "water", "slag", "oil", "cryofluid"
                ]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                    # Преобразование: (1/60) * ввод
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["consumes"]["liquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")


                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["consumes"]["liquids"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_liquid():
                    if not block_data["consumes"]["liquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_liquid():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Добавте хотябы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_liquid, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_liquid, font=10).pack(pady=20)

            def open_item_GenericCrafter_editor_out(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор предметов выхода для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

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
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["outputItems"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_item():
                    if not block_data["outputItems"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_GenericCrafter_editor_out(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_GenericCrafter_editor_out(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_item, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_item, font=10).pack(pady=20)

            def open_liquid_GenericCrafter_editor_out(block_name, block_data):
                clear_window()

                tk.Label(root, text=f"Выбор жидкости выхода для '{block_name}'", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Списки
                default_listbox = tk.Listbox(frame, width=20, height=10)
                mod_listbox = tk.Listbox(frame, width=20, height=10)
                selected_listbox = tk.Listbox(frame, width=30, height=10)

                default_listbox.grid(row=0, column=0, padx=5)
                mod_listbox.grid(row=0, column=1, padx=5)
                selected_listbox.grid(row=0, column=2, padx=5)

                # Списки жидкостей
                default_liquids = [
                    "water", "slag", "oil", "cryofluid"
                ]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_amount = tk.Entry(root, width=10)
                entry_amount.pack()
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

                    # Преобразование: (1/60) * ввод
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["outputLiquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")


                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                    index = selected[0]
                    selected_listbox.delete(index)
                    del block_data["outputLiquids"][index]

                # Кнопки
                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить слева", command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Добавить из мода", command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                tk.Button(button_frame, text="Убрать выбранное", command=remove_selected).grid(row=0, column=2, padx=5)

                # Кнопка "Готово" для завершения редактирования
                def finalize_liquid():
                    if not block_data["outputLiquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_requirements_editor(block_name, block_data)

                # Кнопка "Пропуск"
                def skip_liquid():
                    if not block_data["outputItems"]:
                        messagebox.showerror("Ошибка", "Добавте хотябы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_requirements_editor(block_name, block_data)

                tk.Button(root, text="Готово", command=finalize_liquid, font=10).pack(pady=20)
                tk.Button(root, text="Пропуск", command=skip_liquid, font=10).pack(pady=20)

            def cb_wall_create():
                clear_window()

                tk.Label(root, text="Имя стены").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Размер (макс. 10)").pack()
                entry_size = tk.Entry(root, width=10)
                entry_size.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("wall", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_wall():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        if size > 10 or size < 1:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    block_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "_comment": {
                            "name": "это имя в игре", 
                            "description": "это описания в игре", 
                            "health": "это количество здоровья", 
                            "size": "это размер, requirements это ресурсы для постройки"
                        },
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

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "wall"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, block_data)
                
                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)

                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_wall).pack(pady=20)

            def cb_solarpanel_create():
                clear_window()
                
                tk.Label(root, text="Имя панели").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Размер (макс. 10)").pack()
                entry_size = tk.Entry(root, width=10)
                entry_size.pack()

                tk.Label(root, text="Выработка энергии (вводимое число умножится на 1/60)").pack()
                entry_energy_input = tk.Entry(root, width=10)
                entry_energy_input.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("SolarGenerator", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_panel():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        energy_raw = float(entry_energy_input.get())
                        if size > 10 or size < 1:
                            raise ValueError
                        power_production = energy_raw / 60
                    except ValueError:
                        messagebox.showerror("Ошибка", "Проверьте числовые значения и убедитесь, что размер не больше 10.")
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
                        "_comment": {
                            "name": "это имя в игре", 
                            "description": "это описания в игре",
                            "health": "это количество здоровья", 
                            "size": "это размер", 
                            "requirements": "это ресурсы для постройки",
                            "powerProduction": "это выроботка энергии (используйте калькулятор ((1:60)*сколько вы хотите) )"
                        },
                        "type": "SolarGenerator",
                        "powerProduction": power_production,
                        "requirements": [],  # добавим позже
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("SolarGenerator", []):
                        CACHE_FILE["SolarGenerator"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "SolarGenerator"):
                        return  # Остановить сохранение

                    # откроем новое окно для добавления ресурсов
                    open_requirements_editor(name, block_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_panel).pack(pady=20)

            def cb_ConsumesGenerator_create():
                clear_window()
                
                tk.Label(root, text="Имя генератора").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Размер (макс. 10)").pack()
                entry_size = tk.Entry(root, width=10)
                entry_size.pack()

                tk.Label(root, text="Выработка энергии (вводимое число умножится на 1/60)").pack()
                entry_energy_input = tk.Entry(root, width=10)
                entry_energy_input.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("ConsumeGenerator", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_ConsumesGenerator():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        energy_raw = float(entry_energy_input.get())
                        if size > 10 or size < 1:
                            raise ValueError
                        power_production = energy_raw / 60
                    except ValueError:
                        messagebox.showerror("Ошибка", "Проверьте числовые значения и убедитесь, что размер не больше 10.")
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
                        "_comment": {
                            "name": "это имя в игре", 
                            "description": "это описания в игре",
                            "health": "это количество здоровья", 
                            "size": "это размер", 
                            "requirements": "это ресурсы для постройки",
                            "powerProduction": "это выроботка энергии (используйте калькулятор ((1:60)*сколько вы хотите) )",
                            "consumes-item": "это ресурсы для генерации тоже самое и liquid но надо делить также как энергию"
                        },
                        "requirements": [],  # добавим позже
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

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "ConsumeGenerator"):
                        return  # Остановить сохранение

                    # откроем новое окно для добавления ресурсов
                    open_item_consumes_editor(name, block_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_ConsumesGenerator).pack(pady=20)

            def cb_StorageBlock_create():
                clear_window()

                tk.Label(root, text="Имя хранилищя").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Размер (макс. 10)").pack()
                entry_size = tk.Entry(root, width=10)
                entry_size.pack()

                tk.Label(root, text="Хранит предметов").pack()
                entry_itemCapacity = tk.Entry(root, width=10)
                entry_itemCapacity.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("StorageBlock", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_StorageBlock():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        itemCapacity = int(entry_itemCapacity.get())
                        if size > 10 or size < 1:
                            raise ValueError
                        if itemCapacity > 100000 or itemCapacity < 1:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10) или (Хранит до 100К)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    StorageBlock_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": size,
                        "category": "distribution",
                        "type": "StorageBlock",
                        "_comment": {
                            "name": "это имя в игре", 
                            "description": "это описания в игре",
                            "health": "это количество здоровья", 
                            "size": "это размер", 
                            "requirements": "это ресурсы для постройки",
                            "itemcapacity": "это сколько может хранить предметов"
                        },
                        "requirements": [],
                        "itemCapacity": itemCapacity,
                        "research": { 
                            "parent": parent_value,
                            "requirements": [],
                            "objectives": []
                        }    
                    }

                    if name not in CACHE_FILE.get("StorageBlock", []):
                        CACHE_FILE["StorageBlock"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "StorageBlock"):
                        return  # Остановить сохранение

                    open_requirements_editor(name, StorageBlock_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_StorageBlock).pack(pady=20)

            def cb_GenericCrafter_create():
                clear_window()

                tk.Label(root, text="Имя завода").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Размер (макс. 10)").pack()
                entry_size = tk.Entry(root, width=10)
                entry_size.pack()

                # Чекбокс включения энергии
                power_enabled = tk.BooleanVar(value=False)

                def toggle_power_entry():
                    if power_enabled.get():
                        label_energy_input.pack()
                        entry_energy_input.pack()
                    else:
                        label_energy_input.pack_forget()
                        entry_energy_input.pack_forget()

                ttk.Checkbutton(root, text="Использует энергию", variable=power_enabled, command=toggle_power_entry).pack(pady=6)

                label_energy_input = tk.Label(root, text="Потребление энергии (вводимое число умножится на 1/60)")
                entry_energy_input = tk.Entry(root, width=10)
                label_energy_input.pack_forget()
                entry_energy_input.pack_forget()

                tk.Label(root, text="Введите скорость производства 1 предмета в 1 секунду").pack()
                entry_time_input = tk.Entry(root, width=10)
                entry_time_input.pack()

                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("GenericCrafter", []),
                    state="readonly",
                    width=30
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
                        if size > 10 or size < 1:
                            raise ValueError
                        time_craft = time_cr / 60
                    except ValueError:
                        messagebox.showerror("Ошибка", "Проверьте числовые значения и размер.")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    # Обработка энергии, если включено
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
                        "_comment": {
                            "name": "это имя в игре", 
                            "description": "это описания в игре",
                            "health": "это количество здоровья", 
                            "size": "это размер", 
                            "requirements": "это ресурсы для постройки",
                            "powerProduction": "это выроботка энергии (используйте калькулятор ((1:60)*сколько вы хотите) )",
                            "consumes-item": "это ресурсы для генерации тоже самое и liquid но надо делить также как энергию",
                            "crafttime":"это скорость производства",
                            "outputitem и liquid": "это выход предметов и жидкости (нельзя больше чем 1 жидкость)"
                        },
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

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)

                    if name_exists_in_content(mod_folder, name, "GenericCrafter"):
                        return

                    open_item_GenericCrafter_editor(name, block_data)

                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_GenericCrafter).pack(pady=20)
                tk.Button(root, text="Назад", font=0, command=создание_кнопки).pack()

            def cb_conveyor_create():
                clear_window()

                tk.Label(root, text="Имя конвеера").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Скорость (предметы в секунду)").pack()
                entry_speed = tk.Entry(root, width=10)
                entry_speed.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("conveyor", []),
                    state="readonly",
                    width=30
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
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
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

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "conveyor"):
                        return  # Остановить сохранение

                    open_requirements_editor_conveyor(name, conveyor_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_conveyor).pack(pady=20)

            def cb_conduit_create():
                clear_window()

                tk.Label(root, text="Имя трубы").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Скорость (жидкость в секунду)").pack()
                entry_speed = tk.Entry(root, width=10)
                entry_speed.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("conduit", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_conduit():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    parent_value = research_parent_entry.get()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        speed = ((1 / 60) * speed1)
                        real_speed = round(speed * 60, 1)
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
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

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "conduit"):
                        return  # Остановить сохранение

                    open_requirements_editor_conduit(name, conduit_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_conduit).pack(pady=20)

            def cb_bridge_conveyor_create():
                clear_window()

                tk.Label(root, text="Имя предметного моста").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Скорость (предметы в секунду)").pack()
                entry_speed = tk.Entry(root, width=10)
                entry_speed.pack()

                tk.Label(root, text="Дальность в блоках").pack()
                entry_range = tk.Entry(root, width=10)
                entry_range.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("bridge_conveyor", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_bridge_conveyor():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        range = int(entry_range.get())
                        speed = ((1 / 60) * speed1)
                        real_speed = round(speed * 60, 1)
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    bridge_conveyor_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "range": range,
                        "speed": speed,
                        "category": "distribution",
                        "type": "BufferedItemBridge",
                        "requirements": [],
                        "research": { 
                            "parent": "",
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("bridge_conveyor", []):
                        CACHE_FILE["bridge_conveyor"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "bridge_conveyor"):
                        return  # Остановить сохранение

                    open_requirements_editor_bridge_conveyor(name, bridge_conveyor_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_bridge_conveyor).pack(pady=20)

            def cb_bridge_conveyor_energy_create():
                clear_window()

                tk.Label(root, text="Имя предметного моста").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Скорость (предметы в секунду)").pack()
                entry_speed = tk.Entry(root, width=10)
                entry_speed.pack()

                tk.Label(root, text="Дальность в блоках").pack()
                entry_range = tk.Entry(root, width=10)
                entry_range.pack()

                tk.Label(root, text="Потребления энергии (вводимое число умножится на 1/60)").pack()
                entry_energy_input = tk.Entry(root, width=10)
                entry_energy_input.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("bridge_conveyor_enegry", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                def save_bridge_conveyor():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    try:
                        health = int(entry_health.get())
                        speed1 = int(entry_speed.get())
                        range = int(entry_range.get())
                        energy_raw = float(entry_energy_input.get())
                        speed = ((1 / 60) * speed1)
                        real_speed = round(speed * 60, 1)
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
                        power_eat = energy_raw / 60
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    bridge_conveyor_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "range": range,
                        "speed": speed,
                        "category": "distribution",
                        "type": "BufferedItemBridge",
                        "requirements": [],
                        "consumes": {
                            "power": power_eat
                        },
                        "research": { 
                            "parent": "",
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("bridge_conveyor_enegry", []):
                        CACHE_FILE["bridge_conveyor_enegry"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "bridge_conveyor_enegry"):
                        return  # Остановить сохранение

                    open_requirements_editor_bridge_conveyor(name, bridge_conveyor_data)

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)
                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_bridge_conveyor).pack(pady=20)

            def cb_bridge_liquid_create():
                clear_window()

                tk.Label(root, text="Имя предметного моста").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Скорость (предметы в секунду)").pack()
                entry_speed = tk.Entry(root, width=10)
                entry_speed.pack()

                tk.Label(root, text="Дальность в блоках").pack()
                entry_range = tk.Entry(root, width=10)
                entry_range.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("bridge_conduit", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)

                def save_bridge_liquid():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    try:
                        health = int(entry_health.get())
                        range = int(entry_range.get())
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    bridge_liquid_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "range": range,
                        "category": "distribution",
                        "type": "LiquidBridge",
                        "requirements": [],
                        "research": { 
                            "parent": "",
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("bridge_conduit", []):
                        CACHE_FILE["bridge_conduit"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "bridge_conduit"):
                        return  # Остановить сохранение

                    open_requirements_editor_bridge_conveyor(name, bridge_liquid_data)

                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_bridge_liquid).pack(pady=20)

            def cb_bridge_liquid_energy_create():
                clear_window()

                tk.Label(root, text="Имя предметного моста").pack()
                entry_name = tk.Entry(root, width=50)
                entry_name.pack()

                tk.Label(root, text="Описание").pack()
                entry_desc = tk.Entry(root, width=50)
                entry_desc.pack()

                tk.Label(root, text="ХП").pack()
                entry_health = tk.Entry(root, width=10)
                entry_health.pack()

                tk.Label(root, text="Дальность в блоках").pack()
                entry_range = tk.Entry(root, width=10)
                entry_range.pack()

                tk.Label(root, text="Потребления энергии (вводимое число умножится на 1/60)").pack()
                entry_energy_input = tk.Entry(root, width=10)
                entry_energy_input.pack()

                # ✅ Чтение cache.json
                with open(resource_path(mod_folder, "cache.json"), "r", encoding="utf-8") as f:
                    CACHE_FILE = json.load(f)

                tk.Label(root, text="Исследования для открытия").pack()
                research_parent_entry = ttk.Combobox(
                    root,
                    values=CACHE_FILE.get("bridge_conduit_enegry", []),
                    state="readonly",
                    width=30
                )
                research_parent_entry.pack()

                tk.Button(root, text="⬅️ Назад", font=0, command=lambda: create_block()).pack(pady=20)

                def save_bridge_liquid():
                    name = entry_name.get().strip().replace(" ", "_")
                    description = entry_desc.get().strip()
                    try:
                        health = int(entry_health.get())
                        range = int(entry_range.get())
                        energy_raw = float(entry_energy_input.get())
                        power_eat = energy_raw / 60
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректные числа (размер до 10)!")
                        return

                    if not name or not description:
                        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
                        return

                    bridge_liquid_data = {
                        "name": name,
                        "description": description,
                        "health": health,
                        "size": 1,
                        "range": range,
                        "category": "distribution",
                        "type": "LiquidBridge",
                        "requirements": [],
                        "consumes": {
                            "power": power_eat
                        },
                        "research": { 
                            "parent": "",
                            "requirements": [],
                            "objectives": []
                        }
                    }

                    if name not in CACHE_FILE.get("bridge_conduit_enegry", []):
                        CACHE_FILE["bridge_conduit_enegry"].append(name)

                    with open(resource_path(mod_folder, "cache.json"), "w", encoding="utf-8") as f:
                        json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)  # ✅

                    if name_exists_in_content(mod_folder, name, "bridge_conduit_enegry"):
                        return  # Остановить сохранение

                    open_requirements_editor_bridge_conveyor(name, bridge_liquid_data)

                tk.Button(root, text="💾 Сохранить", bg="#d0ffd0", command=save_bridge_liquid).pack(pady=20)

            def cb_ore_create():
                clear_window()

                tk.Label(root, text="Редактор Руд", font=("Arial", 14)).pack(pady=10)

                frame = tk.Frame(root)
                frame.pack(pady=10)

                # Левый список: предметы
                items_listbox = tk.Listbox(frame, width=25, height=15)
                items_listbox.grid(row=0, column=0, padx=5)

                # Правый список: руды
                ores_listbox = tk.Listbox(frame, width=40, height=15)
                ores_listbox.grid(row=0, column=2, padx=5)

                # Загрузка всех предметов
                mod_items_path = os.path.join(mod_folder, "content", "items")
                ores_folder = os.path.join(mod_folder, "content", "blocks", "environment")

                # Список для хранения уже добавленных руд
                ores_added = []

                if os.path.exists(ores_folder):
                    for f in os.listdir(ores_folder):
                        if f.endswith(".json"):
                            with open(os.path.join(ores_folder, f), "r", encoding="utf-8") as file:
                                data = json.load(file)
                                if data.get("type") == "OreBlock":
                                    name = os.path.splitext(f)[0]
                                    hardness = data.get("hardness", "?")
                                    ores_added.append(name)
                                    ores_listbox.insert(tk.END, f"{name} — Твёрдость: {hardness}")

                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
                        if f.endswith(".json"):
                            item_name = f.replace(".json", "")
                            # Если для предмета уже есть руда, не добавляем его в список
                            if item_name not in ores_added:
                                items_listbox.insert(tk.END, item_name)

                def show_item_info():
                    selection = items_listbox.curselection()
                    if not selection:
                        messagebox.showerror("Ошибка", "Выберите предмет для просмотра информации.")
                        return

                    name = items_listbox.get(selection[0])
                    path = os.path.join(mod_items_path, f"{name}.json")
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        info = json.dumps(data, indent=2, ensure_ascii=False)
                        messagebox.showinfo(f"Информация о '{name}'", info)
                    else:
                        messagebox.showerror("Ошибка", "Файл предмета не найден.")

                def show_ore_info():
                    selection = ores_listbox.curselection()
                    if not selection:
                        messagebox.showerror("Ошибка", "Выберите руду для просмотра информации.")
                        return

                    name = ores_listbox.get(selection[0]).split(" — ")[0]
                    path = os.path.join(ores_folder, f"{name}.json")
                    if os.path.exists(path):
                        with open(path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        info = json.dumps(data, indent=2, ensure_ascii=False)

                        # Добавляем информацию о предмете, связанном с рудой
                        item_name = data.get("itemDrop")
                        if item_name:
                            item_path = os.path.join(mod_items_path, f"{item_name}.json")
                            if os.path.exists(item_path):
                                with open(item_path, "r", encoding="utf-8") as f:
                                    item_data = json.load(f)
                                item_info = json.dumps(item_data, indent=2, ensure_ascii=False)
                                info += f"\n\nИнформация о предмете:\n{item_info}"

                        messagebox.showinfo(f"Информация о руде '{name}'", info)
                    else:
                        messagebox.showerror("Ошибка", "Файл руды не найден.")

                def add_ore():
                    selection = items_listbox.curselection()
                    if not selection:
                        messagebox.showerror("Ошибка", "Выберите предмет для руды!")
                        return

                    name = items_listbox.get(selection[0])

                    # Ввод твёрдости
                    hardness = simpledialog.askinteger("Твёрдость", "Введите твёрдость руды (1-15):", minvalue=1, maxvalue=15)
                    if hardness is None:
                        return

                    # Создание JSON для руды
                    ore_data = {
                        "type": "OreBlock",
                        "itemDrop": name,
                        "hardness": hardness
                    }

                    # Сохраняем руду
                    os.makedirs(ores_folder, exist_ok=True)
                    ore_path = os.path.join(ores_folder, f"{name}.json")
                    with open(ore_path, "w", encoding="utf-8") as f:
                        json.dump(ore_data, f, indent=4, ensure_ascii=False)

                    ores_listbox.insert(tk.END, f"{name} — Твёрдость: {hardness}")
                    items_listbox.delete(selection[0])

                    # Добавление твёрдости в предмет
                    item_path = os.path.join(mod_items_path, f"{name}.json")
                    if os.path.exists(item_path):
                        with open(item_path, "r", encoding="utf-8") as f:
                            item_data = json.load(f)

                        # Добавляем твёрдость в предмет
                        item_data["hardness"] = hardness

                        # Сохраняем изменения в предмет
                        with open(item_path, "w", encoding="utf-8") as f:
                            json.dump(item_data, f, indent=4, ensure_ascii=False)

                def remove_ore():
                    selection = ores_listbox.curselection()
                    if not selection:
                        messagebox.showerror("Ошибка", "Выберите руду для удаления!")
                        return

                    text = ores_listbox.get(selection[0])
                    name = text.split(" — ")[0]

                    ore_path = os.path.join(ores_folder, f"{name}.json")
                    if os.path.exists(ore_path):
                        os.remove(ore_path)
                        print(f"Файл руды '{name}' удалён.")

                    ores_listbox.delete(selection[0])
                    items_listbox.insert(tk.END, name)

                    # Удаление твёрдости из предмета
                    item_path = os.path.join(mod_items_path, f"{name}.json")
                    if os.path.exists(item_path):
                        with open(item_path, "r", encoding="utf-8") as f:
                            item_data = json.load(f)

                        # Удаляем твёрдость из предмета
                        if "hardness" in item_data:
                            del item_data["hardness"]

                        # Сохраняем изменения в предмет
                        with open(item_path, "w", encoding="utf-8") as f:
                            json.dump(item_data, f, indent=4, ensure_ascii=False)

                button_frame = tk.Frame(root)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="Добавить как руду", command=add_ore).grid(row=0, column=0, padx=5)
                tk.Button(button_frame, text="Удалить руду", command=remove_ore).grid(row=0, column=1, padx=5)

                info_frame = tk.Frame(root)
                info_frame.pack(pady=5)

                tk.Button(info_frame, text="Инфо о предмете (?)", command=show_item_info).grid(row=0, column=0, padx=5)
                tk.Button(info_frame, text="Инфо о руде (?)", command=show_ore_info).grid(row=0, column=1, padx=5)

                tk.Button(root, text="Назад", command=создание_кнопки, font=10).pack(pady=20)

        # Основное окно
        root = tk.Tk()
        root.title("Mindustry Mod Creator")
        root.geometry("500x500")

        label = tk.Label(root, text="Название папки")
        entry_name = tk.Entry(root, bg="#CFDDF3", width=50)
        button_next = tk.Button(root, text="Далее", font=10, command=setup_mod_json)

        label.pack(pady=(70, 0))
        entry_name.pack(pady=(10, 0))
        button_next.pack(side=tk.BOTTOM, pady=50)

        root.mainloop()
        create_block()

if __name__ == "__main__":
    MindustryModCreator.main()
