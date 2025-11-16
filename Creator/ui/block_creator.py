import customtkinter as ctk
import json
import os
import urllib.request
import threading
from tkinter import messagebox
from PIL import Image
from utils.cache_manager import CacheManager
from utils.resource_utils import safe_navigation, name_exists_in_content
VERSION = "1.0"
class BlockCreator:
    def __init__(self, root, mod_folder, mod_name, main_app):
        self.root = root
        self.mod_folder = mod_folder
        self.mod_name = mod_name
        self.main_app = main_app
        self.cache_manager = CacheManager(mod_name)
        self.icons_dir = os.path.join("mindustry_mod_creator", "icons")
        os.makedirs(self.icons_dir, exist_ok=True)
    
    def show_block_creator(self):
        """Показать создатель блоков"""
        self.clear_window()
        self.root.configure(fg_color="#3F3D3D")

        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right_frame = ctk.CTkFrame(main_frame, width=150, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        back_btn = ctk.CTkButton(right_frame, text="Назад", height=60,
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
            ("Стена", "copper-wall.png", lambda: self.cb_creator_b("wall")),
            ("Конвейер", "titanium-conveyor.png", lambda: self.cb_creator_b("conveyor")),
            ("Генератор", "steam-generator.png", lambda: self.cb_creator_b("ConsumeGenerator")),
            ("Солн. панель", "solar-panel.png", lambda: self.cb_creator_b("SolarGenerator")),
            ("Хранилище", "container.png", lambda: self.cb_creator_b("StorageBlock")),
            ("Завод", "silicon-smelter.png", lambda: self.cb_creator_b("GenericCrafter")),
            ("Труба", "conduit.png", lambda: self.cb_creator_b("conduit")),
            ("Энергоузел", "power-node.png", lambda: self.cb_creator_b("PowerNode")),
            ("Роутер", "router.png", lambda: self.cb_creator_b("router")),
            ("Перекрёсток", "junction.png", lambda: self.cb_creator_b("Junction")),
            ("Разгрушик", "unloader.png", lambda: self.cb_creator_b("Unloader")),
            ("Роутер жидкости", "liquid-router.png", lambda: self.cb_creator_b("liquid_router")),
            ("Перекрёсток жидкости", "liquid-junction.png", lambda: self.cb_creator_b("LiquidJunction")),
            ("Батарейка", "battery.png", lambda: self.cb_creator_b("Battery")),
            ("Термальный генератор", "thermal-generator.png", lambda: self.cb_creator_b("ThermalGenerator")),
            ("Жидкостный бак", "liquid-container.png", lambda: self.cb_creator_b("Liquid_Tank")),
            ("Лучевой узел", "beam-node.png", lambda: self.cb_creator_b("BeamNode")),
            ("Помпа", "rotary-pump.png", lambda: self.cb_creator_b("Pump")),
            ("Наземная помпа", "water-extractor.png", lambda: self.cb_creator_b("SolidPump"))
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
            widgets['name'] = self.create_field(f"Имя {self.get_block_name(block_type)}", 350)
            widgets['desc'] = self.create_field("Описание", 350)
            widgets['health'] = self.create_field("ХП", 150)
            widgets['build_time'] = self.create_field("Время стройки в секундах (макс. 120)", 150)
        
        def create_local_fields():
            fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
            size_1_2_blocks = ["router"]
            size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                            "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump"]
            
            if block_type in fixed_size_1_blocks:
                widgets['size'] = ctk.CTkEntry(self.root, width=150)
                widgets['size'].insert(0, "1")
                widgets['size'].pack_forget()
            elif block_type in size_1_2_blocks:
                widgets['size'] = self.create_field("Размер (1-2)", 150)
                widgets['size'].insert(0, "1")
            elif block_type in size_1_15_blocks:
                widgets['size'] = self.create_field("Размер (1-15)", 150)
                widgets['size'].insert(0, "1")
            
            if block_type in ["router"]:
                widgets['speed'] = self.create_field("Скорость (макс. 50)", 150)

            if block_type in ["conveyor", "Unloader", "Junction"]:
                widgets['speed'] = self.create_field("Скорость (макс. 50)", 150)
            
            if block_type in ["router", "Junction", "conveyor","conduit", "liquid_router"]:
                widgets['capacity'] = self.create_field("Вместимость (макс. 25)", 150)
            
            if block_type == "PowerNode":
                widgets['range'] = self.create_field("Радиус (макс. 100)", 150)
                widgets['connections'] = self.create_field("Макс. подключения (макс. 500)", 150)
            
            if block_type in ["SolarGenerator", "ConsumeGenerator", "ThermalGenerator"]:
                max_energy = 1000000 if block_type == "SolarGenerator" else 5000000
                widgets['energy'] = self.create_field(f"Выработка энергии (макс. {max_energy:,})", 150)
                
            if block_type == "StorageBlock":
                widgets['item_capacity'] = self.create_field("Вместимость предметов (макс. 100.000)", 150)
            
            if block_type == "GenericCrafter":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text="Использует энергию", 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text="Потребление энергии")
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()
                
                widgets['craft_time'] = self.create_field("Скорость производства (сек/предмет)", 150)
            
            if block_type == "Battery":
                widgets['power_buffer'] = self.create_field("Вместимость энергии (макс. 10.000.000)", 150)
            
            if block_type == "BeamNode":
                widgets['range'] = self.create_field("Радиус (макс. 50)", 150)
            
            if block_type in ["Liquid_Tank"]:
                widgets['liquid_capacity'] = self.create_field("Вместимость жидкости (макс. 10.000.000)", 150)
                               
            if block_type == "Pump":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text="Использует энергию", 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text="Потребление энергии")
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()
                
                widgets['pumpAmount'] = self.create_field("Количество выкачика (1=4 если размер 2 а выкачка 1)(макс. 5000)", 150)
                widgets['capacity'] = self.create_field("Хранилище(макс. 15000)", 150)
        
            if block_type == "SolidPump":
                widgets['power_enabled'] = ctk.BooleanVar(value=False)
                
                def toggle_power():
                    if widgets['power_enabled'].get():
                        widgets['energy_label'].pack()
                        widgets['energy_consumption'].pack()
                    else:
                        widgets['energy_label'].pack_forget()
                        widgets['energy_consumption'].pack_forget()
                
                ctk.CTkCheckBox(self.root, text="Использует энергию", 
                            variable=widgets['power_enabled'], 
                            command=toggle_power).pack(pady=6)
                
                widgets['energy_label'] = ctk.CTkLabel(self.root, text="Потребление энергии")
                widgets['energy_consumption'] = ctk.CTkEntry(self.root, width=150)
                widgets['energy_label'].pack_forget()
                widgets['energy_consumption'].pack_forget()

                widgets['pumpAmount'] = self.create_field("Количество выкачика (макс. 1000)", 150)
                widgets['capacity'] = self.create_field("Хранилище(макс. 15000)", 150)
        
        create_global_fields()
        create_local_fields()
        
        def save_block():
            name = widgets['name'].get().strip().replace(" ", "_")
            description = widgets['desc'].get().strip()
            
            if any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in name.lower()):
                messagebox.showerror("Ошибка", "Название не может содержать русские символы")
                return
            
            try:
                health = int(widgets['health'].get())
                build_cost = int(widgets['build_time'].get()) * 60
                
                fixed_size_1_blocks = ["conveyor", "conduit", "Junction", "Unloader", "liquid_router", "LiquidJunction", "BeamNode"]
                size_1_2_blocks = ["router"]
                size_1_15_blocks = ["PowerNode", "wall", "SolarGenerator", "GenericCrafter", "StorageBlock", 
                                "ConsumeGenerator", "Battery", "ThermalGenerator", "Liquid_Tank", "Pump", "SolidPump"]
                
                if block_type in fixed_size_1_blocks:
                    size = 1
                elif block_type in size_1_2_blocks:
                    size = int(widgets['size'].get())
                    if size < 1 or size > 2:
                        raise ValueError("Размер должен быть 1-2")
                elif block_type in size_1_15_blocks:
                    size = int(widgets['size'].get())
                    if size < 1 or size > 15:
                        raise ValueError("Размер должен быть 1-15")
                else:
                    size = 1
                
                if health < 1: raise ValueError("ХП должно быть > 0")
                if build_cost < 60: raise ValueError("Время стройки ≥ 1 сек")
                
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
                        raise ValueError("Скорость 1-50")
                    speed = (1 / 60) * speed_val
                    block_data.update({"speed": speed, "displayedSpeed": speed_val})
                
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
            else:
                self.open_requirements_editor(name, block_data)
        
        ctk.CTkButton(self.root, text="⬅️ Назад", command=lambda: self.show_block_creator()).pack(pady=20)
        ctk.CTkButton(self.root, text="💾 Сохранить", command=save_block).pack(pady=20)
    
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
            
            print(f"Блок сохранен: {block_file}")
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить блок: {e}")
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
    
    def clear_window(self):
        """Очистка окна"""
        for widget in self.root.winfo_children():
            widget.destroy()