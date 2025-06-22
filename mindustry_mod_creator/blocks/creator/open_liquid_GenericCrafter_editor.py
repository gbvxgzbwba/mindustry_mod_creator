def open_liquid_GenericCrafter_editor(block_name, block_data, clear_window, os, mod_folder, tk, ctk, messagebox, root, open_item_GenericCrafter_editor_out):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",
                        bg="#6a6a6a",
                        activebackground="#7a7a7a"
                    )
                    listbox = tk.Listbox(
                        container, 
                        width=width, 
                        height=height,
                        yscrollcommand=scrollbar.set,
                        bg="#4a4a4a",
                        fg="white",
                        selectbackground="#5a5a5a",
                        selectforeground="white",
                        font=("Arial", 10),
                        relief="flat",
                        highlightthickness=0
                    )
                    scrollbar.config(command=listbox.yview)
                    
                    scrollbar.pack(side="right", fill="y")
                    listbox.pack(side="left", fill="both", expand=True)
                    
                    return container, listbox

                ctk.CTkLabel(root, text=f"Выбор жидкостей потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки жидкостей
                default_liquids = ["water", "slag", "oil", "cryofluid"]
                for liquid in default_liquids:
                    default_listbox.insert(tk.END, liquid)

                # Загружаем модовые жидкости
                mod_liquids_path = os.path.join(mod_folder, "content", "liquids")
                if os.path.exists(mod_liquids_path):
                    for f in os.listdir(mod_liquids_path):
                        if f.endswith(".json"):
                            mod_listbox.insert(tk.END, f.replace(".json", ""))

                # Поле для количества
                entry_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                entry_frame.pack(pady=5)
                
                ctk.CTkLabel(entry_frame, text="Количество:").pack(side="left", padx=5)
                entry_amount = ctk.CTkEntry(entry_frame, width=100)
                entry_amount.pack(side="left", padx=5)
                entry_amount.insert(0, "1")

                def add_from_listbox(listbox):
                    try:
                        user_input = float(entry_amount.get())
                        if user_input < 1 or user_input > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество (от 1 до 50)!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите жидкость!")
                        return

                    liquid = listbox.get(selected[0])
                    calculated_amount = round((1 / 60) * user_input, 25)

                    block_data["consumes"]["liquids"].append({
                        "liquid": liquid,
                        "amount": calculated_amount
                    })

                    selected_listbox.insert(tk.END, f"{liquid} x{user_input} (→ {calculated_amount})")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    liquid = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["liquids"][selected[0]]
                    
                    # Возвращаем жидкость в исходный список
                    if liquid in default_liquids:
                        default_listbox.insert(tk.END, liquid)
                    else:
                        mod_listbox.insert(tk.END, liquid)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_liquid():
                    if not block_data["consumes"]["liquids"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы одну жидкость!")
                        return
                    messagebox.showinfo("Успех", f"Жидкость для {block_name} сохранена!")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                def skip_liquid():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Добавьте хотя бы 1 жидкость если пропустили предмет!")
                        return
                    messagebox.showinfo("Информация", f"Вы пропустили добавление жидкостей для {block_name}.")
                    open_item_GenericCrafter_editor_out(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_liquid, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_liquid, width=200).pack(pady=10)