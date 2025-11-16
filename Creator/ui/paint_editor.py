import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser, messagebox
from PIL import Image
import os
import gc
VERSION = "1.0"
class PaintEditor:
    def __init__(self, root, mod_folder, mod_name, item=None):
        self.root = root
        self.mod_folder = mod_folder
        self.mod_name = mod_name
        self.item = item
        
        # Настройки редактора
        self.current_color = "#000000"
        self.grid_size = 32
        self.cell_size = 20
        self.canvas_size = self.grid_size * self.cell_size
        self.current_tool = "pencil"
        self.history = []
        self.history_index = -1
        self.is_drawing = False
        self.save_path = None
        
        self.setup_editor()
    
    def setup_editor(self):
        """Настройка редактора пиксельной графики"""
        ctk.set_default_color_theme("blue")
        
        if self.item is not None:
            if "full_path" in self.item:
                if "items" in self.item["full_path"]:
                    content_type = "items"
                elif "liquids" in self.item["full_path"]:
                    content_type = "liquids"
        else:
            content_type = "items"
        
        self.templates_dir = os.path.join("mindustry_mod_creator", "icons", "paint", content_type)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        if self.item is None:
            save_dir = os.path.join("mindustry_mod_creator", "icons", "paint")
            os.makedirs(save_dir, exist_ok=True)
            self.save_path = os.path.join(save_dir, "new_image.png")
            item_name = "new_image"
        else:
            item_name = self.item.get("name", "unnamed")
            content_type = self.item.get("type", "items")
            
            possible_paths = [
                os.path.join(self.mod_folder, "sprites", content_type, item_name, f"{item_name}.png"),
                os.path.join(self.mod_folder, "sprites", content_type, f"{item_name}.png"),
                os.path.join(self.mod_folder, "sprites", "items", f"{item_name}.png"),
                os.path.join(self.mod_folder, "sprites", "liquids", f"{item_name}.png"),
                os.path.join(os.path.dirname(self.item.get("full_path", "")), f"{item_name}.png")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.save_path = path
                    break
            else:
                save_dir = os.path.dirname(self.item.get("full_path", self.mod_folder))
                os.makedirs(save_dir, exist_ok=True)
                self.save_path = os.path.join(save_dir, f"{item_name}.png")

        self.create_interface(item_name)
    
    def create_interface(self, item_name):
        """Создание интерфейса редактора"""
        self.paint_window = ctk.CTkToplevel(self.root)
        self.paint_window.title(f"32x32 Pixel Editor - {item_name}")
        self.paint_window.resizable(False, False)
        self.paint_window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.canvas = ctk.CTkCanvas(self.paint_window, bg="#e0e0e0", width=self.canvas_size, height=self.canvas_size, highlightthickness=0)
        self.canvas.pack()

        tool_frame = ctk.CTkFrame(self.paint_window, fg_color="transparent")
        tool_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(
            tool_frame,
            text="< Отмена",
            command=self.undo,
            width=80,
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            tool_frame,
            text="Повтор >",
            command=self.redo,
            width=80,
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=2)

        self.pencil_button = ctk.CTkButton(
            tool_frame, 
            text="Карандаш",
            command=lambda: self.set_tool("pencil"),
            width=80,
            fg_color="#1f6aa5"
        )
        self.pencil_button.pack(side="left", padx=5)

        self.eraser_button = ctk.CTkButton(
            tool_frame,
            text="Ластик",
            command=lambda: self.set_tool("eraser"),
            width=80
        )
        self.eraser_button.pack(side="left", padx=5)

        self.fill_button = ctk.CTkButton(
            tool_frame,
            text="Заливка",
            command=lambda: self.set_tool("fill"),
            width=80
        )
        self.fill_button.pack(side="left", padx=5)

        self.color_button = ctk.CTkButton(
            tool_frame, 
            text="Цвет", 
            command=self.change_color,
            fg_color=self.current_color,
            hover_color=self.current_color,
            width=80
        )
        self.color_button.pack(side="left", padx=5)

        ctk.CTkButton(
            tool_frame,
            text="Очистить",
            command=self.clear_canvas,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            tool_frame,
            text="Шаблоны",
            command=self.show_templates,
            width=80,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            tool_frame,
            text="Сохранить",
            command=self.save_image,
            width=80
        ).pack(side="left", padx=5)

        self.canvas.bind("<B1-Motion>", self.draw_pixel)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)

        self.draw_grid()

        if os.path.exists(self.save_path):
            try:
                self.load_existing_image()
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
                self.save_state()
        else:
            self.save_state()
    
    def on_closing(self):
        """Очистка ресурсов при закрытии окна"""
        try:
            if hasattr(self, 'img') and self.img and hasattr(self.img, 'close'):
                self.img.close()
        except:
            pass
        
        if hasattr(self, 'canvas'):
            self.canvas.delete("all")
            self.canvas = None
            
        if hasattr(self, 'paint_window'):
            self.paint_window.destroy()
        
        gc.collect()
    
    # --- Функции истории ---
    def save_state(self):
        """Сохранение состояния в историю"""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        state = []
        for x in range(self.grid_size):
            row = []
            for y in range(self.grid_size):
                items = self.canvas.find_withtag(f"pixel_{x}_{y}")
                color = None
                if items:
                    color = self.canvas.itemcget(items[0], "fill")
                row.append(color)
            state.append(row)
        
        self.history.append(state)
        self.history_index = len(self.history) - 1

    def undo(self):
        """Отмена действия"""
        if self.history_index > 0:
            self.history_index -= 1
            self.restore_state()

    def redo(self):
        """Повтор действия"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore_state()

    def restore_state(self):
        """Восстановление состояния из истории"""
        state = self.history[self.history_index]
        self.canvas.delete("all")
        self.draw_grid()
        
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if state[x][y] is not None:
                    self.canvas.create_rectangle(
                        x * self.cell_size, y * self.cell_size,
                        (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                        fill=state[x][y], outline="", tags=f"pixel_{x}_{y}"
                    )

    # --- Основные функции рисования ---
    def start_drawing(self, event):
        """Начало рисования"""
        self.is_drawing = True
        self.draw_pixel(event)
        self.save_state()

    def draw_pixel(self, event):
        """Рисование пикселя"""
        if not self.is_drawing:
            return
            
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.canvas.delete(f"pixel_{x}_{y}")
            if self.current_tool == "eraser":
                return
            elif self.current_tool in ["pencil", "fill"]:
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=self.current_color, outline="", tags=f"pixel_{x}_{y}"
                )

    def stop_drawing(self, event):
        """Остановка рисования"""
        self.is_drawing = False
        self.save_state()

    def flood_fill(self, x, y, target_color, replacement_color):
        """Заливка области"""
        if target_color == replacement_color:
            return
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return
        
        items = self.canvas.find_withtag(f"pixel_{x}_{y}")
        current_pixel_color = None
        if items:
            current_pixel_color = self.canvas.itemcget(items[0], "fill")
        
        if current_pixel_color != target_color:
            return
        
        self.canvas.delete(f"pixel_{x}_{y}")
        self.canvas.create_rectangle(
            x * self.cell_size, y * self.cell_size,
            (x + 1) * self.cell_size, (y + 1) * self.cell_size,
            fill=replacement_color, outline="", tags=f"pixel_{x}_{y}"
        )
        
        self.flood_fill(x+1, y, target_color, replacement_color)
        self.flood_fill(x-1, y, target_color, replacement_color)
        self.flood_fill(x, y+1, target_color, replacement_color)
        self.flood_fill(x, y-1, target_color, replacement_color)

    def handle_click(self, event):
        """Обработчик клика"""
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            if self.current_tool == "fill":
                self.save_state()
                items = self.canvas.find_withtag(f"pixel_{x}_{y}")
                target_color = None
                if items:
                    target_color = self.canvas.itemcget(items[0], "fill")
                self.flood_fill(x, y, target_color, self.current_color)
                self.save_state()
            else:
                self.start_drawing(event)

    def change_color(self):
        """Смена цвета"""
        color = colorchooser.askcolor(title="Выберите цвет", initialcolor=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.color_button.configure(fg_color=self.current_color)
            self.set_tool("pencil")

    def clear_canvas(self):
        """Очистка холста"""
        self.canvas.delete("all")
        self.draw_grid()
        self.save_state()

    def draw_grid(self):
        """Отрисовка сетки"""
        self.canvas.configure(bg="#e0e0e0")
        for i in range(self.grid_size + 1):
            self.canvas.create_line(
                i * self.cell_size, 0, 
                i * self.cell_size, self.canvas_size, 
                fill="#d0d0d0", width=2
            )
            self.canvas.create_line(
                0, i * self.cell_size, 
                self.canvas_size, i * self.cell_size, 
                fill="#d0d0d0", width=2
            )

    def save_image(self):
        """Сохранение изображения"""
        try:
            self.img = Image.new("RGBA", (self.grid_size, self.grid_size), (0, 0, 0, 0))
            pixels = self.img.load()
            
            for x in range(self.grid_size):
                for y in range(self.grid_size):
                    items = self.canvas.find_withtag(f"pixel_{x}_{y}")
                    if items:
                        color = self.canvas.itemcget(items[0], "fill")
                        if color:
                            try:
                                r, g, b = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                                pixels[x, y] = (r, g, b, 255)
                            except:
                                pixels[x, y] = (0, 0, 0, 255)
            
            self.img.save(self.save_path)
            messagebox.showinfo("Сохранено", f"Изображение сохранено в:\n{self.save_path}")
        finally:
            if hasattr(self, 'img'):
                self.img.close()

    def set_tool(self, tool):
        """Установка инструмента"""
        self.current_tool = tool
        
        self.pencil_button.configure(fg_color="#2b2b2b")
        self.eraser_button.configure(fg_color="#2b2b2b")
        self.fill_button.configure(fg_color="#2b2b2b")
        
        if tool == "pencil":
            self.pencil_button.configure(fg_color="#1f6aa5")
        elif tool == "eraser":
            self.eraser_button.configure(fg_color="#1f6aa5")
        elif tool == "fill":
            self.fill_button.configure(fg_color="#1f6aa5")

    def load_template_image(self, path):
        """Загрузка шаблонного изображения"""
        try:
            img = Image.open(path)
            
            if img.size != (32, 32):
                img = img.resize((32, 32), Image.NEAREST)
            
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            pixels = img.load()
            
            self.clear_canvas()
            
            for x in range(32):
                for y in range(32):
                    pixel = pixels[x, y]
                    if len(pixel) == 4:
                        r, g, b, a = pixel
                        if a > 0:
                            color = f"#{r:02x}{g:02x}{b:02x}"
                            self.canvas.create_rectangle(
                                x * self.cell_size, y * self.cell_size,
                                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                                fill=color, outline="", tags=f"pixel_{x}_{y}"
                            )
            img.close()
            self.save_state()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить шаблон: {e}")

    def show_templates(self):
        """Показать шаблоны"""
        templates = []
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith(".png"):
                    templates.append({
                        "name": file[:-4],
                        "path": os.path.join(self.templates_dir, file)
                    })
        
        if not templates:
            messagebox.showinfo("Шаблоны", f"В папке шаблонов нет изображений")
            return
        
        template_window = ctk.CTkToplevel(self.paint_window)
        template_window.title("Выберите шаблон")
        template_window.geometry("600x400")
        
        scroll_frame = ctk.CTkScrollableFrame(template_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for template in templates:
            try:
                img = Image.open(template["path"])
                img = img.resize((64, 64), Image.NEAREST)
                ctk_img = ctk.CTkImage(light_image=img, size=(64, 64))
                
                frame = ctk.CTkFrame(scroll_frame)
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(frame, image=ctk_img, text="").pack(side="left", padx=10)
                ctk.CTkLabel(frame, text=template["name"], font=("Arial", 14)).pack(side="left", padx=10)
                
                def load_template(path=template["path"]):
                    self.load_template_image(path)
                    template_window.destroy()
                
                ctk.CTkButton(frame, text="Загрузить", command=load_template).pack(side="right", padx=10)
            except Exception as e:
                print(f"Ошибка загрузки шаблона {template['name']}: {e}")

    def load_existing_image(self):
        """Загрузка существующего изображения"""
        img = Image.open(self.save_path)
        if img.size != (self.grid_size, self.grid_size):
            img = img.resize((self.grid_size, self.grid_size), Image.NEAREST)
        
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        
        pixels = img.load()
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.canvas.create_rectangle(
                        x * self.cell_size, y * self.cell_size,
                        (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                        fill=color, outline="", tags=f"pixel_{x}_{y}"
                    )
        self.save_state()