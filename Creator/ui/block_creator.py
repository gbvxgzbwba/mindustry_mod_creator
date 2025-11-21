import customtkinter as ctk
import json
import os
import urllib.request
import threading
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from utils.cache_manager import CacheManager
from utils.resource_utils import safe_navigation, name_exists_in_content
from utils.lang_system import LangT
VERSION = "1.2"
class BlockCreator:
    def __init__(self, root, mod_folder, mod_name, main_app):
        self.root = root
        self.mod_folder = mod_folder
        self.mod_name = mod_name
        self.main_app = main_app
        self.cache_manager = CacheManager(mod_name)
        self.icons_dir = os.path.join("mindustry_mod_creator", "icons")
        os.makedirs(self.icons_dir, exist_ok=True)

    def load_all_icons(self, parent_window=None):
                icons_dir = os.path.join("mindustry_mod_creator", "icons")
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
                            "pulverizer": {"layers": [["production/pulverizer.png", 1],["production/pulverizer-top.png", 2],["production/pulverizer-rotator.png", 3]]},

                            "mend-projector": {"layers": [["defense/mend-projector.png", 1]]},
                            "overdrive-projector": {"layers": [["defense/overdrive-projector.png", 1]]}
                        },
                        False
                    )
                ]

                # Создаем папку для иконок, если ее нет
                os.makedirs(icons_dir, exist_ok=True)

                # Проверяем, какие файлы уже существуют
                existing_files = set(os.listdir(icons_dir)) if os.path.exists(icons_dir) else set()

                # Подсчет общего количества иконок (только тех, которых нет)
                total_icons = 0
                download_tasks = []
                merge_tasks = []  # Задачи для объединения слоев

                for base_url, name_icons, is_item in download_configs:
                    if isinstance(name_icons, dict):
                        for name, config in name_icons.items():
                            final_path = os.path.join(icons_dir, f"{name}.png")
                            
                            # Если финальный файл уже существует, пропускаем
                            if f"{name}.png" in existing_files:
                                continue
                            
                            # Для каждого слоя добавляем задачу загрузки
                            temp_files = []
                            for i, (layer_path, layer_num) in enumerate(config["layers"]):
                                temp_filename = f"{name}_temp_layer_{layer_num}.png"
                                temp_path = os.path.join(icons_dir, temp_filename)
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
                                download_tasks.append((base_url + filename, os.path.join(icons_dir, f"{name}.png"), name, 1))

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

    def show_block_creator(self):
        BlockCreator.load_all_icons(self.root)
        """Показать создатель блоков"""
        self.clear_window()
        self.root.configure(fg_color="#3F3D3D")

        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_frame = ctk.CTkFrame(main_frame, width=150, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        back_btn = ctk.CTkButton(right_frame, text=LangT("Назад"), height=60,
                                font=("Arial", 14), command=lambda: self.main_app.show_content_buttons())
        back_btn.pack(fill="x", pady=(0, 10))

        self.setup_blocks_grid(left_frame)
    
    def setup_blocks_grid(self, parent):
        """Настройка сетки блоков"""
        import tkinter as tk
        
        canvas = ctk.CTkCanvas(parent, bg="#2b2b2b", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(parent, orientation="vertical", command=canvas.yview)
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
            (LangT("Стена"), "copper-wall.png", lambda: self.cb_creator_b("wall")),
            (LangT("Конвейер"), "titanium-conveyor.png", lambda: self.cb_creator_b("conveyor")),
            (LangT("Генератор"), "steam-generator.png", lambda: self.cb_creator_b("ConsumeGenerator")),
            (LangT("Солн. панель"), "solar-panel.png", lambda: self.cb_creator_b("SolarGenerator")),
            (LangT("Хранилище"), "container.png", lambda: self.cb_creator_b("StorageBlock")),
            (LangT("Завод"), "silicon-smelter.png", lambda: self.cb_creator_b("GenericCrafter")),
            (LangT("Труба"), "conduit.png", lambda: self.cb_creator_b("conduit")),
            (LangT("Энергоузел"), "power-node.png", lambda: self.cb_creator_b("PowerNode")),
            (LangT("Роутер"), "router.png", lambda: self.cb_creator_b("router")),
            (LangT("Перекрёсток"), "junction.png", lambda: self.cb_creator_b("Junction")),
            (LangT("Разгрушик"), "unloader.png", lambda: self.cb_creator_b("Unloader")),
            (LangT("Роутер жидкости"), "liquid-router.png", lambda: self.cb_creator_b("liquid_router")),
            (LangT("Перекрёсток жидкости"), "liquid-junction.png", lambda: self.cb_creator_b("LiquidJunction")),
            (LangT("Батарейка"), "battery.png", lambda: self.cb_creator_b("Battery")),
            (LangT("Термальный генератор"), "thermal-generator.png", lambda: self.cb_creator_b("ThermalGenerator")),
            (LangT("Жидкостный бак"), "liquid-container.png", lambda: self.cb_creator_b("Liquid_Tank")),
            (LangT("Лучевой узел"), "beam-node.png", lambda: self.cb_creator_b("BeamNode")),
            (LangT("Помпа"), "rotary-pump.png", lambda: self.cb_creator_b("Pump")),
            (LangT("Наземная помпа"), "water-extractor.png", lambda: self.cb_creator_b("SolidPump")),
            ("Регенератор", "mend-projector.png", lambda: self.cb_creator_b("MendProjector")),
            ("Сверхприводный проектор", "overdrive-projector.png", lambda: self.cb_creator_b("OverdriveProjector"))
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

            img = self.load_image(icon_name)
            if img:
                btn.configure(image=img, compound="top")
            
            return btn

        def update_blocks_grid():
            container_width = blocks_container.winfo_width()
            if container_width < 1: return
            
            for widget in blocks_container.winfo_children():
                widget.destroy()
            
            btn_width = 120
            spacing = 10
            columns = max(1, container_width // (btn_width + spacing))
            
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

        update_blocks_grid()
        blocks_container.bind("<Configure>", lambda e: update_blocks_grid())

        def on_resize(event):
            update_blocks_grid()

        blocks_container.bind("<Configure>", on_resize)
    
    def load_image(self, icon_name, size=(64, 64)):
        """Загрузка изображения с обработкой ошибок"""
        try:
            img_path = os.path.join(self.icons_dir, icon_name)
            if os.path.exists(img_path):
                img = Image.open(img_path)
                return ctk.CTkImage(light_image=img, size=size)
            
            if icon_name.endswith(".png"):
                base_name = icon_name[:-4]
                alternatives = [
                    f"item-{base_name}.png",
                    f"liquid-{base_name}.png",
                    f"{base_name}.png"
                ]
                
                for alt in alternatives:
                    alt_path = os.path.join(self.icons_dir, alt)
                    if os.path.exists(alt_path):
                        img = Image.open(alt_path)
                        return ctk.CTkImage(light_image=img, size=size)
        except Exception as e:
            print(f"Ошибка загрузки изображения {icon_name}: {e}")
        return None
    
    def cb_creator_b(self, block_type):
        """Создатель конкретного типа блока"""
        self.clear_window()
        
        widgets = {}
        
        def create_global_fields():
            widgets['name'] = self.create_field(f"{LangT("Имя")} {self.get_block_name(block_type)}", 350)
            widgets['desc'] = self.create_field(LangT("Описание"), 350)
            widgets['health'] = self.create_field(LangT("ХП"), 150)
            widgets['build_time'] = self.create_field(LangT("Время стройки в секундах (макс. 120)"), 150)
        
        def create_local_fields():
            fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
            size_1_2_blocks = ["router"]
            size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                            "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump", "MendProjector", "OverdriveProjector"]
            
            if block_type in fixed_size_1_blocks:
                widgets['size'] = ctk.CTkEntry(self.root, width=150)
                widgets['size'].insert(0, "1")
                widgets['size'].pack_forget()
            elif block_type in size_1_2_blocks:
                widgets['size'] = self.create_field(LangT("Размер (1-2)"), 150)
                widgets['size'].insert(0, "1")
            elif block_type in size_1_15_blocks:
                widgets['size'] = self.create_field(LangT("Размер (1-15)"), 150)
                widgets['size'].insert(0, "1")
            
            if block_type in ["router"]:
                widgets['speed'] = self.create_field(LangT("Скорость (макс. 50)"), 150)

            if block_type in ["conveyor", "Unloader", "Junction"]:
                widgets['speed'] = self.create_field(LangT("Скорость (макс. 50)"), 150)
            
            if block_type in ["router", "Junction", "conveyor","conduit", "liquid_router"]:
                widgets['capacity'] = self.create_field(LangT("Вместимость (макс. 25)"), 150)
            
            if block_type == "PowerNode":
                widgets['range'] = self.create_field(LangT("Радиус (макс. 100)"), 150)
                widgets['connections'] = self.create_field(LangT("Макс. подключения (макс. 500)"), 150)
            
            if block_type in ["SolarGenerator", "ConsumeGenerator", "ThermalGenerator"]:
                max_energy = 1000000 if block_type == "SolarGenerator" else 5000000
                widgets['energy'] = self.create_field(f"{LangT("Выработка энергии (макс.")} {max_energy:,})", 150)
                
            if block_type == "StorageBlock":
                widgets['item_capacity'] = self.create_field(LangT("Вместимость предметов (макс. 100.000)"), 150)
            
            if block_type == "GenericCrafter":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text=LangT("Использует энергию"), 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text=LangT("Потребление энергии"))
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()
                
                widgets['craft_time'] = self.create_field(LangT("Скорость производства (сек/предмет)"), 150)
            
            if block_type == "Battery":
                widgets['power_buffer'] = self.create_field(LangT("Вместимость энергии (макс. 10.000.000)"), 150)
            
            if block_type == "BeamNode":
                widgets['range'] = self.create_field(LangT("Радиус (макс. 50)"), 150)
            
            if block_type in ["Liquid_Tank"]:
                widgets['liquid_capacity'] = self.create_field(LangT("Вместимость жидкости (макс. 10.000.000)"), 150)
                               
            if block_type == "Pump":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text=LangT("Использует энергию"), 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text=LangT("Потребление энергии"))
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()
                
                widgets['pumpAmount'] = self.create_field(LangT("Количество выкачика (1=4 если размер 2 а выкачка 1)(макс. 5000)"), 150)
                widgets['capacity'] = self.create_field(LangT("Хранилище(макс. 15000)"), 150)
        
            if block_type == "SolidPump":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text=LangT("Использует энергию"), 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text=LangT("Потребление энергии"))
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()

                widgets['pumpAmount'] = self.create_field(LangT("Количество выкачика (макс. 1000)"), 150)
                widgets['capacity'] = self.create_field(LangT("Хранилище(макс. 15000)"), 150)
        
            if block_type == "MendProjector":
                widgets['energy_label'] = self.create_field("Потребление энергии (макс 100000)", 150)
                widgets['range'] = self.create_field("Радиус (макс. 30)", 150)
                widgets['healPercent'] = self.create_field("Восстановления % от хп блока (если 25 и у блока 600 хп то лечит 150)(макс. 300)", 150)
                widgets['phaseBoost'] = self.create_field("% усиления лечения (макс. 300)", 150)
                widgets['phaseRangeBoost'] = self.create_field("% усиления радиуса (макс. 150)", 150)
                widgets['useTime'] = self.create_field("Восстановления каждые XXX (макс. 30 - мин 1)", 150)
                widgets['baseColor'] = self.create_field("базовый цвет (RRGGBB)", 150)
                widgets['phaseColor'] = self.create_field("цвет после буста (RRGGBB)", 150)
                widgets['lightRadius'] = self.create_field("Радиус свечения (макс. 30)", 150)

            if block_type == "OverdriveProjector":
                widgets['energy_label'] = self.create_field("Потребление энергии (макс 100000)", 150)
                widgets['range'] = self.create_field("Радиус (макс. 30)", 150)
                widgets['speedBoost'] = self.create_field("Ускорения (макс. 300)", 150)
                widgets['useTime'] = self.create_field("useTime", 150)

        create_global_fields()
        create_local_fields()
        
        def save_block():
            name = widgets['name'].get().strip().replace(" ", "_")
            description = widgets['desc'].get().strip()
            
            if any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in name.lower()):
                messagebox.showerror(LangT("Ошибка"), LangT("Название не может содержать русские символы"))
                return
            
            try:
                health = int(widgets['health'].get())
                build_cost = int(widgets['build_time'].get()) * 60
                
                fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
                size_1_2_blocks = ["router"]
                size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                                "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump", "MendProjector", "OverdriveProjector"]
                
                if block_type in fixed_size_1_blocks:
                    size = 1
                elif block_type in size_1_2_blocks:
                    size = int(widgets['size'].get())
                    if size < 1 or size > 2:
                        raise ValueError(LangT("Размер должен быть 1-2"))
                elif block_type in size_1_15_blocks:
                    size = int(widgets['size'].get())
                    if size < 1 or size > 15:
                        raise ValueError(LangT("Размер должен быть 1-15"))
                else:
                    size = 1
                
                if health < 1: raise ValueError(locals("ХП должно быть > 0"))
                if build_cost < 60: raise ValueError(LangT("Время стройки ≥ 1 сек"))
                
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
                
                if block_type in ["conveyor", "Unloader","Junction","router"]:
                    speed_val = int(widgets['speed'].get())
                    if speed_val < 1 or speed_val > 50:
                        raise ValueError(LangT("Скорость 1-50"))
                    speed = (1 / 60) * speed_val
                    block_data.update({"speed": speed, "displayedSpeed": speed_val})
                
                if block_type in ["router", "Junction","conveyor","conduit","liquid_router"]:
                    capacity = int(widgets['capacity'].get())
                    if capacity < 1 or capacity > 25:
                            raise ValueError(LangT("Вместимость 1-25"))
                    if block_type in ["router", "Junction","conveyor"]:
                        block_data["itemCapacity"] = capacity
                    if block_type in ["conduit","liquid_router"]:
                        block_data["liquidCapacity"] = capacity
                
                if block_type == "PowerNode":
                    range_val = int(widgets['range'].get())
                    connections = int(widgets['connections'].get())
                    
                    if range_val < 1 or range_val > 100: raise ValueError(LangT("Радиус 1-100"))
                    if connections < 2 or connections > 500: raise ValueError(LangT("Подключения 2-500"))
                    
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
                        raise ValueError(LangT("Энергия 1-5.000.000"))
                    block_data.update({
                        "powerProduction": energy_val / 60,
                        "consumes": {"items": [], "liquids": []}
                    })
                
                if block_type == "StorageBlock":
                    capacity = int(widgets['item_capacity'].get())
                    if capacity < 1 or capacity > 100000:
                        raise ValueError(LangT("Вместимость 1-100K"))
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
                        raise ValueError(LangT("Буфер энергии 1-10M"))
                    block_data["consumes"] = {"powerBuffered": buffer_val}
                
                if block_type == "BeamNode":
                    range_val = int(widgets['range'].get())
                    if range_val < 1 or range_val > 50:
                        raise ValueError(LangT("Радиус 1-50"))
                    block_data["range"] = range_val * 8
                                           
                if block_type in ["Liquid_Tank"]:
                    capacity = int(widgets['liquid_capacity'].get())
                    block_data["liquidCapacity"] = capacity
                
                if block_type == "Pump":
                    pumpAmount = int(widgets['pumpAmount'].get())
                    capacity = int(widgets['capacity'].get())
                    amount = pumpAmount / 60
                    if pumpAmount < 1 or pumpAmount > 5000:
                        raise ValueError(LangT("Выкачка не больше 5000"))
                    if capacity < 1 or capacity > 15000:
                        raise ValueError(LangT("Вместимость не больше 15000"))
                    block_data.update({
                        "pumpAmount": amount,
                        "liquidCapacity": capacity
                        })
                
                if block_type == "SolidPump":
                    pumpAmount = int(widgets['pumpAmount'].get())
                    capacity = int(widgets['capacity'].get())
                    amount = pumpAmount / 60
                    if pumpAmount < 1 or pumpAmount > 1000:
                        raise ValueError(LangT("Выкачка не больше 1000"))
                    if capacity < 1 or capacity > 15000:
                        raise ValueError(LangT("Вместимость не больше 15000"))
                    block_data.update({
                        "pumpAmount": amount,
                        "liquidCapacity": capacity
                        })

                if block_type == "MendProjector":
                    energy_label = int(widgets['energy_label'].get())
                    rangeX = int(widgets['range'].get())
                    healPercent = int(widgets['healPercent'].get())
                    phaseBoost = int(widgets['phaseBoost'].get())
                    phaseRangeBoost = int(widgets['phaseRangeBoost'].get())
                    useTime = int(widgets['useTime'].get())
                    baseColor = int(widgets['baseColor'].get())
                    phaseColor = int(widgets['phaseColor'].get())
                    lightRadius = int(widgets['lightRadius'].get())

                    if rangeX < 1 or rangeX > 30:
                        raise ValueError("Радиус не более 30")
                    if healPercent < 1 or healPercent > 300:
                        raise ValueError("Восстановления не более 300")
                    if phaseBoost < 1 or phaseBoost > 300:
                        raise ValueError("Усиления восстановления неболее 300")
                    if phaseRangeBoost < 1 or phaseRangeBoost > 150:
                        raise ValueError("Усиления радиуса не более 150")
                    if useTime < 1 or useTime > 30:
                        raise ValueError("Мин время лечения 1 сек макс 30")
                    if lightRadius < 1 or lightRadius > 30:
                        raise ValueError("Макс радиус свечения 30")
                    if energy_label < 1 or energy_label > 100000:
                        raise ValueError("Макс энергия 100000")
                    
                    block_data.update({
                        "range": rangeX*8,
                        "healPercent": healPercent,
                        "phaseBoost": phaseBoost/2,
                        "useTime": useTime,
                        "phaseColor": phaseColor,
                        "baseColor": baseColor,
                        "phaseRangeBoost": phaseRangeBoost*8,
                        "lightRadius": lightRadius*8,
                        "consumes": {
                            "power": energy_label/60
                        }
                    })

                if block_type == "OverdriveProjector":
                    energy_label = int(widgets['energy_label'].get())
                    rangeX = int(widgets['range'].get())
                    useTime = int(widgets['useTime'].get())
                    speedBoost = int(widgets['speedBoost'].get())
                    block_data.update({
                        "speedBoost": speedBoost,
                        "range": rangeX*8,
                        "useTime": useTime,
                        "consumes": {
                            "power": energy_label/60
                        }
                    })

                category_map = {
                    "wall": "defense", "conveyor": "distribution", "router": "distribution",
                    "PowerNode": "power", "SolarGenerator": "power", "GenericCrafter": "crafting",
                    "conduit": "liquid", "StorageBlock": "distribution", "ConsumeGenerator": "power",
                    "Battery": "power", "ThermalGenerator": "power", "BeamNode": "power",
                    "Junction": "distribution", "Unloader": "distribution", "liquid_router": "liquid",
                    "Liquid_Tank": "liquid", "LiquidJunction": "liquid", "Pump": "liquid",
                    "SolidPump": "production", "MendProjector": "effect", "OverdriveProjector": "effect"
                }
                block_data["category"] = category_map.get(block_type, "misc")
                
            except ValueError as e:
                messagebox.showerror(LangT("Ошибка"), f"{LangT("Некорректные данные:")} {e}")
                return
            
            if not name or not description:
                messagebox.showerror(LangT("Ошибка"), LangT("Заполните имя и описание"))
                return
            
            self.cache_manager.add_to_cache(block_type, name)
            
            if name_exists_in_content(self.mod_folder, name, block_type):
                return
            
            if not self.save_block_json(block_data):
                return
            
            if block_type == "GenericCrafter":
                self.open_GenericCrafter_editor(name, block_data, "items_input")
            elif block_type == "ConsumeGenerator":
                self.open_consumes_editor(name, block_data, "items")
            elif block_type == "SolidPump":
                self.open_solidpump_liquid_edit(name, block_data)
            elif block_type == "MendProjector" or "OverdriveProjector":
                self.open_mender_resource_editor(name, block_data)
            else:
                self.open_requirements_editor(name, block_data)
        
        ctk.CTkButton(self.root, text=LangT("⬅️ Назад"), command=lambda: self.show_block_creator()).pack(pady=20)
        ctk.CTkButton(self.root, text=LangT("💾 Сохранить"), command=save_block).pack(pady=20)
    
    def create_field(self, text, width):
        """Создание поля ввода"""
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(expand=True)
        
        label = ctk.CTkLabel(container, text=text)
        entry = ctk.CTkEntry(container, width=width)
        
        label.grid(row=0, column=0, padx=(0, 10))
        entry.grid(row=0, column=1)
        
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        container.grid_columnconfigure(2, weight=1)
        
        return entry
    
    def get_block_name(self, b_type):
        """Получение читаемого имени типа блока"""
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
    
    def save_block_json(self, block_data):
        """Сохранение JSON файла блока"""
        try:
            blocks_folder = os.path.join(self.mod_folder, "content", "blocks")
            os.makedirs(blocks_folder, exist_ok=True)
            
            block_type = block_data['type']
            block_type_folder = os.path.join(blocks_folder, block_type)
            os.makedirs(block_type_folder, exist_ok=True)
            
            block_file = os.path.join(block_type_folder, f"{block_data['name']}.json")
            with open(block_file, 'w', encoding='utf-8') as f:
                json.dump(block_data, f, indent=4, ensure_ascii=False)
            
            print(f"{LangT("Блок сохранен:")} {block_file}")
            return True
            
        except Exception as e:
            messagebox.showerror(LangT("Ошибка"), f"{LangT("Не удалось сохранить блок:")} {e}")
            return False
    
    def open_requirements_editor(self, block_name, block_data):
        """Редактор требований для блока"""
        #без изменений
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self.main_app)
        content_editor.open_requirements_editor(block_name, block_data)
    
    def open_GenericCrafter_editor(self, block_name, block_data, editor_type="items_input"):
        """Редактор для GenericCrafter"""
        #без изменений
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self.main_app)
        content_editor.open_GenericCrafter_editor(block_name, block_data, editor_type)
    
    def open_consumes_editor(self, block_name, block_data, editor_type="items"):
        """Редактор потребляемых ресурсов"""
        #без изменений
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self.main_app)
        content_editor.open_consumes_editor(block_name, block_data, editor_type)
    
    def open_solidpump_liquid_edit(self, block_name, block_data):
        """Редактор жидкости для SolidPump"""
        #без изменений
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self.main_app)
        content_editor.open_solidpump_liquid_edit(block_name, block_data)
    
    def open_mender_resource_editor(self, block_name, block_data):
        from ui.content_editor import ContentEditor
        content_editor = ContentEditor(self.root, self.mod_folder, self.mod_name, self.main_app)
        content_editor.open_mender_resource_editor(block_name, block_data)

    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()
