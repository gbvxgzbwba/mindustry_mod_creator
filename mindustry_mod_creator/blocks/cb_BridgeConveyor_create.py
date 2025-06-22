def cb_BridgeConveyor_create(clear_window, os, root, open_requirements_editor_BridgeConveyor, name_exists_in_content, create_block, ctk, mod_folder, json, messagebox, resource_path, mod_name):
    clear_window()

    root.configure(fg_color="#2b2b2b")

    ctk.CTkLabel(root, text="Имя завода", font=("Arial", 12)).pack()
    entry_name = ctk.CTkEntry(root, width=350)
    entry_name.pack()

    ctk.CTkLabel(root, text="Описание", font=("Arial", 12)).pack()
    entry_desc = ctk.CTkEntry(root, width=350)
    entry_desc.pack()

    ctk.CTkLabel(root, text="ХП", font=("Arial", 12)).pack()
    entry_health = ctk.CTkEntry(root, width=150)
    entry_health.pack()

    ctk.CTkLabel(root, text="Радиус (макс 30)", font=("Arial", 12)).pack()
    entry_range = ctk.CTkEntry(root, width=150)
    entry_range.pack()

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
    label_energy_input = ctk.CTkLabel(root, text="Потребление энергии (вводимое число умножится на 1/60)")
    entry_energy_input = ctk.CTkEntry(root, width=150)
    label_energy_input.pack_forget()
    entry_energy_input.pack_forget()

    with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "r", encoding="utf-8") as f:
        CACHE_FILE = json.load(f)

    ctk.CTkLabel(root, text="Исследования для открытия").pack
    research_parent_entry = ctk.CTkComboBox(
        root, 
        values=CACHE_FILE.get("BridgeConveyor", []),
        state="readonly", 
        width=250
    )

    def save_BridgeConveyor():
        name = entry_name.get().strip().replace(" ", "_")
        description = entry_name.get().strip()
        parent_value = research_parent_entry.get()
        range = entry_range.get()
        try:
            health = int(entry_health.get())
            range = int(entry_range.get())
            if range > 30 or range < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return
        if not name or not description:
            messagebox.showerror("Ошибка", "Все поля должы быть заполнены")
            return
        consumes = {

        }

        if power_enabled.get():
            try:
                enegry_raw = int(entry_energy_input.get())
                power_eat = enegry_raw / 60
                consumes["power"] = power_eat
            except ValueError:
                messagebox.showerror("Ошибка", "Введите число для энерги")
                return
            
        block_data={
            "name": name,
            "description": description,
            "health": health,
            "type": "BridgeConveyor",
            "range": range,
            "size": 1,
            "category": "distribution",
            "consumes": consumes,
            "requirements": [],
            "research": {
                "parent": parent_value,
                "requirenebts": [],
                "objectives": []
            }
        }

        if name not in CACHE_FILE.get("BridgeConveyor", []):
            CACHE_FILE["BridgeConveyor"].append(name)

        with open(resource_path(os.path.join("mindustry_mod_creator", "cache", f"{mod_name}.json")), "w", encoding="utf-8") as f:
            json.dump(CACHE_FILE, f, indent=4, ensure_ascii=False)
        
        if name_exists_in_content(mod_folder, name, "BridgeConveyor"):
            return
        
        open_requirements_editor_BridgeConveyor(name, block_data)
    
    ctk.CTkButton(root, text="💾 Сохранить", command=save_BridgeConveyor).pack(pady=20)
    ctk.CTkButton(root, text="Назад", command=lambda: create_block(mod_name)).pack()