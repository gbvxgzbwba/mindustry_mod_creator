def cb_conveyor_create(clear_window, os, root, ctk, json, mod_name, resource_path, mod_folder, messagebox, open_requirements_editor_conveyor, name_exists_in_content, create_block):
                clear_window()

                ctk.CTkLabel(root, text="Имя конвейера").pack()
                entry_name = ctk.CTkEntry(root, width=350)
                entry_name.pack()

                ctk.CTkLabel(root, text="Описание").pack()
                entry_desc = ctk.CTkEntry(root, width=350)
                entry_desc.pack()

                ctk.CTkLabel(root, text="ХП").pack()
                entry_health = ctk.CTkEntry(root, width=150)
                entry_health.pack()

                ctk.CTkLabel(root, text="Скорость (предметы в секунду)").pack()
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
                        print(f"game= {real_speed}+ (10+- || 20+-) || code= {speed}")
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