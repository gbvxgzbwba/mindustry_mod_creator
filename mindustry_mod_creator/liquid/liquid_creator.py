def create_liquid_window(clear_window, создание_кнопки, ctk, root, messagebox, os, mod_folder, json):            
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
            ctk.CTkButton(root, text="💾 Сохранить жидкость", font=("Arial", 12),
                    command=save_liquid).pack(pady=20)
            ctk.CTkButton(root, text="Назад", font=("Arial", 12),
                    command=lambda:создание_кнопки()).pack(pady=20)