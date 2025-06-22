def open_item_GenericCrafter_editor(block_name, block_data, root, ctk, tk, os, messagebox, mod_folder, clear_window, open_liquid_GenericCrafter_editor):
                clear_window()
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор предметов потребления для '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с прокруткой
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

                # Создаем Listbox с прокруткой
                default_container, default_listbox = create_scrolled_listbox(frame, 20, 10)
                mod_container, mod_listbox = create_scrolled_listbox(frame, 20, 10)
                selected_container, selected_listbox = create_scrolled_listbox(frame, 30, 10)

                default_container.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                mod_container.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                selected_container.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

                # Списки ресурсов
                default_items = [
                    "copper", "lead", "metaglass", "graphite", "sand", "coal",
                    "titanium", "thorium", "scrap", "silicon", "plastanium",
                    "phase-fabric", "surge-alloy", "spore-pod", "blast-compound", "pyratite"
                ]
                for item in default_items:
                    default_listbox.insert(tk.END, item)

                # Загружаем модовые предметы
                mod_items_path = os.path.join(mod_folder, "content", "items")
                if os.path.exists(mod_items_path):
                    for f in os.listdir(mod_items_path):
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
                        amount = int(entry_amount.get())
                        if amount < 1 or amount > 50:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 50!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["consumes"]["items"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]
                    
                    selected_listbox.delete(selected[0])
                    del block_data["consumes"]["items"][selected[0]]
                    
                    # Возвращаем предмет в исходный список
                    if item in default_items:
                        default_listbox.insert(tk.END, item)
                    else:
                        mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(button_frame, text="Добавить слева", width=120,
                            command=lambda: add_from_listbox(default_listbox)).grid(row=0, column=0, padx=5)
                ctk.CTkButton(button_frame, text="Добавить из мода", width=120,
                            command=lambda: add_from_listbox(mod_listbox)).grid(row=0, column=1, padx=5)
                ctk.CTkButton(button_frame, text="Убрать выбранное", width=120,
                            command=remove_selected).grid(row=0, column=2, padx=5)

                def finalize_item():
                    if not block_data["consumes"]["items"]:
                        messagebox.showerror("Ошибка", "Сначала добавьте хотя бы один Предмет!")
                        return
                    messagebox.showinfo("Успех", f"Предмет для {block_name} сохранена!")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                def skip_item():
                    messagebox.showinfo("Информация", f"Вы пропустили добавление предметов для {block_name}.")
                    open_liquid_GenericCrafter_editor(block_name, block_data)

                ctk.CTkButton(root, text="Готово", command=finalize_item, width=200).pack(pady=10)
                ctk.CTkButton(root, text="Пропуск", command=skip_item, width=200).pack(pady=10)