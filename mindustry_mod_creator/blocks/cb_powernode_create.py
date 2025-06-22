def cb_powernode_create(clear_window, root, messagebox, os, mod_name, ctk, resource_path, mod_folder, json, name_exists_in_content, create_block, open_requirements_editor):
                clear_window()

                ctk.CTkLabel(root, text="Имя энерго узла").pack()
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

                ctk.CTkLabel(root, text="Радиус (макс 100)").pack()
                entry_range_1 = ctk.CTkEntry(root, width=150)
                entry_range_1.pack()

                ctk.CTkLabel(root, text="Кол-во Макс подключений (макс 100)").pack()
                entry_connect = ctk.CTkEntry(root, width=150)
                entry_connect.pack()

                ctk.CTkLabel(root, text="Буфер (макс 1.000.000)").pack()
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
                    range_entry = float(entry_range_1.get())
                    maxnodes = int(entry_connect.get())
                    buffer = int(entry_buffer.get())
                    try:
                        health = int(entry_health.get())
                        size = int(entry_size.get())
                        if size > 10 or size < 1:
                            raise ValueError
                        if maxnodes > 100 or maxnodes < 1:
                            raise ValueError
                        if range_entry > 100 or range_entry < 1:
                            raise ValueError
                        if buffer > 1000000 or buffer < 1:
                            raise ValueError
                        range_1 = range_entry * 8
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