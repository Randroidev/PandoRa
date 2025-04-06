import tkinter as tk
from tkinter import ttk, colorchooser
from PIL import Image, ImageTk

class SettingsWindow:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent, config_manager, on_apply_settings_callback, theme="dark"):
        if self._initialized:
            self.bring_to_front()
            return

        self.parent = parent
        self.config_manager = config_manager
        self.on_apply_settings_callback = on_apply_settings_callback
        self.theme = theme
        self._initialized = True
        self.restart_required = tk.BooleanVar(value=False)  # Переменная для галочки "Need Restart"
        self.bg_color = "#2d2d2d"
        self.fg_color = "#ffffff"
        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Application Settings")
        self.window.geometry("600x500")
        self.window.minsize(600, 400)

        # Получаем цвета из конфигурации в зависимости от темы
        self.bg_color = self.config_manager.config["Theme"][f"{self.theme}_bg_color"]
        self.fg_color = self.config_manager.config["Theme"][f"{self.theme}_fg_color"]
        # Устанавливаю цвет окна
        self.window.configure(bg=self.bg_color)

        try:
            icon = Image.open("images/gear.png")
            icon = ImageTk.PhotoImage(icon)
            self.window.tk.call('wm', 'iconphoto', self.window._w, icon)
        except:
            pass

        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_force()
        self.window.protocol("WM_DELETE_WINDOW", self._close)

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background="#3d3d3d" if self.theme == "dark" else "#e0e0e0",
                        foreground=self.fg_color)
        style.configure("TFrame", background=self.bg_color)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        self.vars = {}
        self.original_values = {}  # Для отслеживания изменений
        self.create_tabs()

        button_frame = tk.Frame(self.window, bg=self.bg_color)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Save", command=self._apply,
                  bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults,
                  bg="#FF5722", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self._close,
                  bg="#757575", fg="white").pack(side=tk.LEFT, padx=5)

        # Добавляем галочку "Need Restart Application"
        #self.restart_check = ttk.Checkbutton(button_frame, text="Need Restart Application",
        #                                     variable=self.restart_required, state="disabled")
        #self.restart_check.pack(side=tk.LEFT, padx=5)

    def get_paired_option(self, option, section_options):
        if "color" in option:
            base = option.replace("color", "")
            alpha_candidate = f"{base}alpha"
            if alpha_candidate in section_options:
                return alpha_candidate

            parts = option.split('_')
            if (len(parts) >= 3 and
                    parts[0] == "color" and
                    parts[-1].isdigit()):
                alpha_candidate = f"alpha_{'_'.join(parts[1:])}"
                if alpha_candidate in section_options:
                    return alpha_candidate
        return None

    def create_tabs(self):
        padding = 20
        # Получаем списки из объекта app
        disabled_list = getattr(self.config_manager, "disabled", [])
        restart_list = getattr(self.config_manager, "need_restart", [])

        for section in self.config_manager.config.sections():
            # Пропускаем секции NeedRestart и Disabled
            if section in ["NeedRestart", "Disabled"]:
                continue

            if not self.config_manager.config[section]:
                continue

            # Добавляем звёздочку к имени вкладки, если она в restart_list
            tab_title = section
            if section in restart_list:
                tab_title += " [*]"

            frame = ttk.Frame(self.notebook)
            if section in disabled_list:
                tab_title += " (disabled)"
                self.notebook.add(frame, state="disabled", text=tab_title)
            else:
                self.notebook.add(frame, text=tab_title)

            canvas = tk.Canvas(frame, bg=self.bg_color)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

            def configure_canvas(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            scrollable_frame.bind("<Configure>", configure_canvas)

            def _on_mousewheel(event):
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            canvas.pack(side="left", fill="both", expand=True, padx=padding)
            scrollbar.pack(side="right", fill="y")

            row = 0
            processed_options = set()
            section_options = list(self.config_manager.config[section].keys())

            for option in section_options:
                if option in processed_options:
                    continue

                # Добавляем звёздочку и жирный шрифт для параметров из restart_list
                label_text = option.replace('_', ' ').title()
                font_style = "normal"
                if option in restart_list:
                    label_text += " [*]"
                    font_style = "bold"

                # Курсив для отключённых параметров
                if option in disabled_list:
                    label_text += " (disabled)"
                    font_style = "italic"

                label = tk.Label(scrollable_frame, text=label_text, bg=self.bg_color, fg=self.fg_color,
                                 font=("TkDefaultFont", 9, font_style))
                label.grid(row=row, column=0, padx=(0, 10), pady=5, sticky="e")

                value = self.config_manager.config[section][option]
                alpha_option = self.get_paired_option(option, section_options)
                # Отключение на уровне секции или параметра
                is_disabled = section in disabled_list or option in disabled_list

                if option == "theme":
                    var = tk.StringVar(value=value)
                    widget = ttk.Combobox(scrollable_frame, textvariable=var,
                                          values=["light", "dark"], state="readonly" if not is_disabled else "disabled")
                    self.vars[f"{section}.{option}"] = var

                elif value.lower() in ["true", "false"]:
                    var = tk.BooleanVar(value=self.config_manager.getboolean(section, option))
                    widget = ttk.Checkbutton(scrollable_frame, variable=var,
                                             state="normal" if not is_disabled else "disabled")
                    self.vars[f"{section}.{option}"] = var

                elif "color" in option:
                    var = tk.StringVar(value=value)
                    widget = tk.Frame(scrollable_frame, bg=self.bg_color)

                    color_button = tk.Button(widget, width=3, bg=value,
                                             command=lambda s=section, o=option: self.choose_color(s, o),
                                             cursor="hand2", state="normal" if not is_disabled else "disabled")
                    color_button.pack(side=tk.LEFT, padx=(0, 5))
                    self.vars[f"{section}.{option}"] = var

                    if alpha_option:
                        alpha_var = tk.DoubleVar(value=self.config_manager.getfloat(section, alpha_option))
                        alpha_scale = ttk.Scale(widget, from_=0, to=1, variable=alpha_var, length=100,
                                                state="normal" if not is_disabled else "disabled")
                        alpha_scale.pack(side=tk.LEFT)
                        self.vars[f"{section}.{alpha_option}"] = alpha_var
                        processed_options.add(alpha_option)

                elif value.replace(".", "").isdigit():
                    if "." in value:
                        var = tk.DoubleVar(value=self.config_manager.getfloat(section, option))
                    else:
                        var = tk.IntVar(value=self.config_manager.getint(section, option))
                    widget = ttk.Entry(scrollable_frame, textvariable=var,
                                       state="normal" if not is_disabled else "disabled")
                    self.vars[f"{section}.{option}"] = var

                else:
                    var = tk.StringVar(value=value)
                    widget = ttk.Entry(scrollable_frame, textvariable=var,
                                       state="normal" if not is_disabled else "disabled")
                    self.vars[f"{section}.{option}"] = var

                # Сохраняем исходное значение для проверки изменений
                #self.original_values[f"{section}.{option}"] = var.get()

                # Отслеживание изменений для параметров из restart_list
                #if option in restart_list or section in restart_list:
                #    var.trace_add("write", lambda *args, key=f"{section}.{option}": self.check_restart(key))

                widget.grid(row=row, column=1, pady=5, sticky="w")
                row += 1

            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    #def check_restart(self, key):
    #    """Проверка изменений для параметров из app.need_restart_application"""
    #    current_value = self.vars[key].get()
    #    original_value = self.original_values[key]
    #    if current_value != original_value:
    #        self.restart_required.set(True)

    def choose_color(self, section, option):
        initial_color = self.vars[f"{section}.{option}"].get()
        color = colorchooser.askcolor(
            title=f"Choose {option}",
            initialcolor=initial_color,
            parent=self.window
        )
        if color[1]:
            self.vars[f"{section}.{option}"].set(color[1])
            self.update_color_preview(section, option, color[1])

    def update_color_preview(self, section, option, color):
        for i, tab in enumerate(self.notebook.tabs()):
            if self.notebook.tab(i, "text") == section or self.notebook.tab(i, "text") == section + " [*]":
                tab_widget = self.notebook.nametowidget(tab)
                canvas = tab_widget.winfo_children()[0]
                scrollable_frame = canvas.winfo_children()[0]
                for row in scrollable_frame.grid_slaves():
                    if row.grid_info()["column"] == 0:
                        label = row
                        if label.winfo_class() == "Label" and (label.cget("text") == option.replace('_', ' ').title() + " [*]" or label.cget("text") == option.replace('_', ' ').title()):
                            frame = scrollable_frame.grid_slaves(row=label.grid_info()["row"], column=1)[0]
                            color_button = frame.winfo_children()[0]
                            color_button.configure(bg=color)
                            break
                break

    def _apply(self):
        for key, var in self.vars.items():
            section, option = key.split(".")
            self.config_manager.set(section, option, var.get())
        self.config_manager.save_settings()
        if self.on_apply_settings_callback:
            self.on_apply_settings_callback()
        self._close()

    def reset_to_defaults(self):
        self.config_manager.reset_to_defaults()
        self._close()
        SettingsWindow(self.parent, self.config_manager, self.on_apply_settings_callback, self.theme)

    def bring_to_front(self):
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()

    def _close(self):
        type(self)._instance = None
        self._initialized = False
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    config = ConfigManager()
    editor = SettingsWindow(root, config, None, theme="dark")
    editor.window.grab_set()

    root.mainloop()