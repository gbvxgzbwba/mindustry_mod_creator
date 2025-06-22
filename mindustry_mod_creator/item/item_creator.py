def create_item_window(clear_window, создание_кнопки, ctk, root, messagebox, os, mod_folder, json):
            """Форма для создания предмета"""
            clear_window()

            ctk.CTkLabel(root, text="Создание нового предмета", font=("Arial", 16, "bold")).pack(pady=10)

            form_frame = ctk.CTkFrame(root)
            form_frame.pack(pady=10)

            # Поля формы: (подпись, ширина Entry)
            fields = [
                ("Название предмета", 350),
                ("Описание", 350),
                ("Воспламеняемость (0-1)", 150),
                ("Взрывоопасность (0-1)", 150),
                ("Радиоактивность (0-1)", 150),
                ("Заряд (0-1)", 150)
            ]

            entries = []

            for i, (label_text, width) in enumerate(fields):
                label = ctk.CTkLabel(form_frame, text=label_text)
                entry = ctk.CTkEntry(form_frame, width=width)
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
            ctk.CTkButton(root, text="💾 Сохранить предмет", font=("Arial", 12),
                    command=save_item).pack(pady=20)
            ctk.CTkButton(root, text="Назад", font=("Arial", 12),
                    command=lambda:создание_кнопки()).pack(pady=20)