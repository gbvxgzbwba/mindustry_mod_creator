def cb_GenericCrafter_create(clear_window, os, mod_name, root, ctk, json, mod_folder, messagebox, resource_path, name_exists_in_content, open_item_GenericCrafter_editor, create_block):
                clear_window()
                
                # Устанавливаем серый фон
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

                ctk.CTkLabel(root, text="Размер (макс. 10)", font=("Arial", 12)).pack()
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

                label_energy_input = ctk.CTkLabel(root, text="Потребление энергии (вводимое число умножится на 1/60)")
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
                        if size > 10 or size < 1:
                            raise ValueError
                        time_craft = time_cr / 60
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
