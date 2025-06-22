def cb_solarpanel_create(clear_window, mod_name, os, root, ctk, json, resource_path, mod_folder, messagebox, name_exists_in_content, create_block, open_requirements_editor):
                clear_window()

                ctk.CTkLabel(root, text="Имя панели").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Размер (макс. 10)").pack()
                entry_size = ctk.CTkEntry(root, width=150)
                entry_size.pack()

                ctk.CTkLabel(root, text="Выработка энергии").pack()
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
                        if size > 10 or size < 1:
                            raise ValueError
                        power_production = energy_raw / 60
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