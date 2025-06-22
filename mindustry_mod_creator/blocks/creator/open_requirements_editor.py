def open_requirements_editor(block_name, block_data, ctk, clear_window, root, tk, mod_folder, os, messagebox, создание_кнопки, json, urllib):
                clear_window()
                
                # Устанавливаем серый фон для всего окна
                root.configure(fg_color="#2b2b2b")
                
                ctk.CTkLabel(root, text=f"Выбор ресурсов для стройки '{block_name}'", 
                            font=("Arial", 14)).pack(pady=10)

                frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                frame.pack(pady=10)

                # Функция для создания Listbox с полосой прокрутки
                def create_scrolled_listbox(parent, width, height):
                    container = ctk.CTkFrame(parent)
                    scrollbar = tk.Scrollbar(
                        container,
                        troughcolor="#4a4a4a",  # Цвет фона полосы прокрутки
                        bg="#6a6a6a",           # Цвет ползунка
                        activebackground="#7a7a7a"  # Цвет при наведении
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
                        if amount < 1 or amount > 5000:
                            raise ValueError
                    except ValueError:
                        messagebox.showerror("Ошибка", "Введите корректное количество от 1 до 5000!")
                        return

                    selected = listbox.curselection()
                    if not selected:
                        messagebox.showerror("Ошибка", "Выберите ресурс!")
                        return

                    item = listbox.get(selected[0])
                    block_data["requirements"].append({"item": item, "amount": amount})
                    selected_listbox.insert(tk.END, f"{item} x{amount}")
                    
                    # Удаляем предмет из исходного списка
                    listbox.delete(selected[0])

                def remove_selected():
                    selected = selected_listbox.curselection()
                    if not selected:
                        return
                        
                    item_with_amount = selected_listbox.get(selected[0])
                    item = item_with_amount.split(" x")[0]  # Извлекаем имя предмета
                    
                    # Удаляем из правого списка
                    selected_listbox.delete(selected[0])
                    del block_data["requirements"][selected[0]]
                    
                    # Возвращаем предмет в соответствующий список
                    if item in [default_listbox.get(i) for i in range(default_listbox.size())]:
                        # Если предмет есть в default списке, не добавляем снова
                        pass
                    elif item in [mod_listbox.get(i) for i in range(mod_listbox.size())]:
                        # Если предмет есть в mod списке, не добавляем снова
                        pass
                    else:
                        # Проверяем, откуда был взят предмет
                        if item in default_items:
                            default_listbox.insert(tk.END, item)
                        else:
                            mod_listbox.insert(tk.END, item)

                # Кнопки
                button_frame = ctk.CTkFrame(root, fg_color="#3a3a3a")
                button_frame.pack(pady=10)

                ctk.CTkButton(
                    button_frame, 
                    text="Добавить слева", 
                    command=lambda: add_from_listbox(default_listbox),
                    width=120
                ).grid(row=0, column=0, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Добавить из мода", 
                    command=lambda: add_from_listbox(mod_listbox),
                    width=120
                ).grid(row=0, column=1, padx=5)
                
                ctk.CTkButton(
                    button_frame, 
                    text="Убрать выбранное", 
                    command=remove_selected,
                    width=120
                ).grid(row=0, column=2, padx=5)

                def finalize_block():
                    if not block_data.get("requirements"):
                        messagebox.showerror("Ошибка", "Вы не добавили ни одного ресурса в требования!")
                        return

                    block_type = block_data.get("type")
                    content_folder = os.path.join(mod_folder, "content", "blocks", block_type)
                    os.makedirs(content_folder, exist_ok=True)

                    block_path = os.path.join(content_folder, f"{block_name}.json")
                    with open(block_path, "w", encoding="utf-8") as f:
                        json.dump(block_data, f, indent=4, ensure_ascii=False)

                    messagebox.showinfo("Успех", f"Блок '{block_name}' сохранён с ресурсами!")
                    создание_кнопки()
                    
                    # Загрузка текстур
                    block_type = block_data.get("type")
                    size = block_data.get("size")

                    if 1 <= size <= 10:
                        texture_url = f"https://raw.githubusercontent.com/gbvxgzbwba/texture123/main/block-{size}.png"
                        sprite_folder = os.path.join(mod_folder, "sprites", block_type, block_name)
                        texture_name = f"{block_name}.png"
                        texture_path = os.path.join(sprite_folder, texture_name)

                        os.makedirs(sprite_folder, exist_ok=True)

                        if not os.path.exists(texture_path):
                            try:
                                urllib.request.urlretrieve(texture_url, texture_path)
                                print(f"Текстура {texture_name} успешно загружена в {texture_path}")
                            except Exception as e:
                                print(f"Ошибка при загрузке текстуры: {e}")
                        else:
                            print(f"Текстура {texture_name} уже существует, загрузка пропущена.")

                ctk.CTkButton(
                    root, 
                    text="Готово", 
                    command=finalize_block, 
                    font=("Arial", 12),
                    width=200,
                    height=40
                ).pack(pady=20)