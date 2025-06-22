import customtkinter as ctk
import urllib.request
import shutil
import json, os, sys
import tkinter as tk
import threading

from tkinter import messagebox
from customtkinter import ThemeManager
from copy import deepcopy

theme_test = deepcopy(ctk.ThemeManager.theme)

theme_test["CTkButton"] = {
    "fg_color": "#128f1c", "corner_radius": 15,
    "text_color": "#FFFFFF", "border_width": 5,
    "hover_color": "#005A00", "border_color": "#005A00",
    "text_color_disabled": "#00F7FF"
}
theme_test["CTk"] = {
    "fg_color": "#303030"
}
theme_test["CTkLabel"] = {
    "text_color": "#FFFFFF", "fg_color": "#202320",
    "corner_radius": 10
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
        "BridgeConveyor": ["bridge-conveyor", "phase-conveyor"],
        "BridgeConduit": ["bridge-conduit", "phase-conduit"],
        "battery": ["battery", "battery-large"],
        "Drill": ["mechanical-drill", "pneumatic-drill", "laser-drill", "blast-drill"],
        "PowerNode": ["power-node", "power-node-large"]
    }
    path = os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")
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
            from mindustry_mod_creator.item import item_creator
            item_creator.create_item_window(clear_window, создание_кнопки, ctk, root, messagebox, os, mod_folder, json)
            
        def create_liquid_window():
            from mindustry_mod_creator.liquid import liquid_creator
            liquid_creator.create_liquid_window(clear_window, создание_кнопки, ctk, root, messagebox, os, mod_folder, json)

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
                
                ctk.CTkButton(nav_frame, text="⬅️ Назад", command=create_block).pack(side="left", padx=5)
                
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
                cache_path = os.path.join(mod_folder, "cache.json")

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
                from mindustry_mod_creator.blocks.creator import open_requirements_editor
                open_requirements_editor.open_requirements_editor(block_name, block_data, ctk, clear_window, root, tk, mod_folder, os, messagebox, создание_кнопки, json, urllib)

            def open_requirements_editor_conveyor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_requirements_editor_conveyor
                open_requirements_editor_conveyor.open_requirements_editor_conveyor(block_name, block_data, os, root, ctk, tk, clear_window, mod_folder, json, messagebox, создание_кнопки, threading, urllib)

            def open_item_GenericCrafter_editor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_item_GenericCrafter_editor
                open_item_GenericCrafter_editor.open_item_GenericCrafter_editor(block_name, block_data, root, ctk, tk, os, messagebox, mod_folder, clear_window, open_liquid_GenericCrafter_editor)

            def open_liquid_GenericCrafter_editor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_liquid_GenericCrafter_editor
                open_liquid_GenericCrafter_editor.open_liquid_GenericCrafter_editor(block_name, block_data, clear_window, os, mod_folder, tk, ctk, messagebox, root, open_item_GenericCrafter_editor_out)

            def open_item_GenericCrafter_editor_out(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_item_GenericCrafter_editor_out
                open_item_GenericCrafter_editor_out.open_item_GenericCrafter_editor_out(block_name, block_data, root, clear_window, os, tk, ctk, messagebox, mod_folder, open_liquid_GenericCrafter_editor_out)

            def open_liquid_GenericCrafter_editor_out(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_liquid_GenericCrafter_editor_out
                open_liquid_GenericCrafter_editor_out.open_liquid_GenericCrafter_editor_out(block_name, block_data, open_requirements_editor, root, os, mod_folder, tk, ctk, clear_window, messagebox)

            def open_requirements_editor_conduit(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_requirements_editor_conduit
                open_requirements_editor_conduit.open_requirements_editor_conduit(block_name, block_data, os, mod_folder, clear_window, ctk, root, tk, messagebox, json, urllib, threading, создание_кнопки)

            def open_item_consumes_editor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_item_consumes_editor
                open_item_consumes_editor.open_item_consumes_editor(block_name, block_data, clear_window, ctk, tk, root, messagebox,  os, mod_folder, open_liquid_consumes_editor)

            def open_liquid_consumes_editor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_liquid_consumes_editor
                open_liquid_consumes_editor.open_liquid_consumes_editor(block_name, block_data, clear_window, os, mod_folder, tk, ctk, root, messagebox, open_requirements_editor)

            def open_requirements_editor_BridgeConveyor(block_name, block_data):
                from mindustry_mod_creator.blocks.creator import open_requirements_editor_BridgeConveyor
                open_requirements_editor_BridgeConveyor.open_requirements_editor_BridgeConveyor(block_name, block_data, os, root, ctk, tk, clear_window, mod_folder, json, messagebox, создание_кнопки, threading, urllib)
#/////////////////////////////////////////////////////////////////////////////////
            def cb_wall_create():
                from mindustry_mod_creator.blocks import cb_wall_create
                cb_wall_create.cb_wall_create(clear_window, root, ctk, mod_name, resource_path, mod_folder, json, os, messagebox, name_exists_in_content, open_requirements_editor, create_block)
 
            def cb_conveyor_create():
                from mindustry_mod_creator.blocks import cb_conveyor_create
                cb_conveyor_create.cb_conveyor_create(clear_window, os, root, ctk, json, mod_name, resource_path, mod_folder, messagebox, open_requirements_editor_conveyor, name_exists_in_content, create_block)
 
            def cb_GenericCrafter_create():
                from mindustry_mod_creator.blocks import cb_GenericCrafter_create
                cb_GenericCrafter_create.cb_GenericCrafter_create(clear_window, os, mod_name,  root, ctk, json, mod_folder, messagebox, resource_path, name_exists_in_content, open_item_GenericCrafter_editor, create_block)
 
            def cb_solarpanel_create():
                from mindustry_mod_creator.blocks import cb_solarpanel_create
                cb_solarpanel_create.cb_solarpanel_create(clear_window, mod_name, os, root, ctk, json, resource_path, mod_folder, messagebox, name_exists_in_content, create_block, open_requirements_editor)
 
            def cb_StorageBlock_create():
                from mindustry_mod_creator.blocks import cb_StorageBlock_create
                cb_StorageBlock_create.cb_StorageBlock_create(clear_window, ctk, mod_name, root, mod_folder, json, resource_path, messagebox, os, create_block, name_exists_in_content, open_requirements_editor)
 
            def cb_conduit_create():
                from mindustry_mod_creator.blocks import cb_conduit_create
                cb_conduit_create.cb_conduit_create(clear_window, os, json, mod_name, name_exists_in_content, root, ctk, mod_folder, resource_path, messagebox, open_requirements_editor_conduit, create_block)
 
            def cb_ConsumesGenerator_create():
                from mindustry_mod_creator.blocks import cb_ConsumesGenerator_create
                cb_ConsumesGenerator_create.cb_ConsumesGenerator_create(clear_window, create_block, mod_name, os, ctk, mod_folder, json, resource_path, messagebox, root, name_exists_in_content, open_item_consumes_editor)
 
            def cb_powernode_create():
                from mindustry_mod_creator.blocks import cb_powernode_create
                cb_powernode_create.cb_powernode_create(clear_window, root, messagebox, os, mod_name, ctk, resource_path, mod_folder, json, name_exists_in_content, create_block, open_requirements_editor)
 
            def cb_BridgeConveyor_create():
                from mindustry_mod_creator.blocks import cb_BridgeConveyor_create
                cb_BridgeConveyor_create.cb_BridgeConveyor_create(clear_window, os, root, open_requirements_editor_BridgeConveyor, name_exists_in_content, create_block, ctk, mod_folder, json, messagebox, resource_path, mod_name)
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
