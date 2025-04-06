import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
from PIL import Image, ImageTk
from config_manager import ConfigManager
from file_handler import DataLoader
from custom_toolbar import CustomToolbar
from plot_manager import PlotManager
from time_manager import TimeManager
from flag_manager import FlagManager
from settings_window import SettingsWindow
from column_selector import ColumnSelector
from theme_manager import ThemeManager


class DataVisualizationApp:
    def __init__(self, root, file_path=None, demo_mode=None, demo_args=None):
        self.root = root
        self.plt = plt
        self.file_path = file_path
        self.demo_mode = demo_mode
        self.demo_args = demo_args
        self.data_loader = DataLoader(file_path=file_path,
                                      root=self.root,
                                      demo_mode=demo_mode,
                                      demo_args=demo_args)
        self.ax_percent = None
        self.legend_warning_occurred = False

        # Инициализация переменных для хранения выбора столбцов
        self.numeric_vars = {}
        self.percent_vars = {}
        self.bool_vars = {}
        self.flags_vars = {}

        # Загрузка всей конфигурации
        self.config = ConfigManager()
        self.config.load_app_config(self)

        # Инициализация менеджеров
        self.theme_manager = ThemeManager(self)
        self.plot_manager = PlotManager(self)
        self.time_manager = TimeManager(self)
        self.flag_manager = FlagManager(self)

        self.setup_ui()

    def setup_ui(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_icons()
        self.window_size()
        self.create_figure()
        self.create_toolbar()   # need canvas from figure
        self.theme_manager.apply_window_theme()
        self.theme_manager.apply_toolbar_theme()
        self.plot_manager.plot_data()

    def create_figure(self):
        self.fig = self.plt.figure(figsize=(10, 8),
                                   facecolor=self.light_bg_color if self.theme == "light"
                                   else self.dark_bg_color)

        screen_height = self.root.winfo_screenheight()
        num_flags = len(self.data_loader.flag_columns)
        total_flag_height = self.flag_height_px * num_flags
        main_height_px = screen_height - total_flag_height
        total_flag_height_frac = total_flag_height / screen_height
        self.main_height_frac = main_height_px / screen_height

        # Основной график размещаем сразу под флагами
        rect = [
            self.rectangle_left,
            self.rectangle_bottom + self.rectangle_top,
            (1.0 - self.rectangle_right),
            self.main_height_frac - self.rectangle_bottom - self.rectangle_top
        ]
        self.ax_main = self.fig.add_axes(rect)
        self.ax_main.set_facecolor(self.light_bg_color if self.theme == "light"
                                   else self.dark_bg_color)

        # Создаем процентную ось с помощью twinx()
        self.ax_percent = self.ax_main.twinx()
        self.ax_percent.set_ylim(0, 100)  # Начальный диапазон для процентов

        # Создаем оси для флагов, синхронизированные по X с основной осью
        self.flag_axes = []
        for i, col in enumerate(self.data_loader.flag_columns):
            rect = [
                self.rectangle_left,
                self.main_height_frac + (num_flags - i - 1) * self.flag_height_px / screen_height + self.rectangle_top,
                (1.0 - self.rectangle_right),
                self.flag_height_px / screen_height
            ]
            ax = self.fig.add_axes(rect, sharex=self.ax_main)
            ax.set_facecolor(self.light_bg_color if self.theme == "light"
                             else self.dark_bg_color)
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            display_name = col.replace("F-", "") if col.startswith("F-") else col
            ax.set_ylabel(display_name, rotation=0, ha="right", va="center",
                          fontsize=self.font_size, fontweight="bold" if self.legend_bold else "normal")
            ax.set_autoscale_on(False)
            ax.set_navigate(False)
            ax.set_xticks([])
            ax.set_xlabel("")
            self.flag_axes.append(ax)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def create_toolbar(self):
        self.toolbar = CustomToolbar(self.canvas, self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.BOTH, anchor=tk.CENTER)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.toolbar.zoom()
        self.toolbar.pan()

        self.button_frame = ttk.Frame(self.toolbar)
        self.button_frame.pack(side=tk.LEFT, padx=10)

        first_timestamp = self.data_loader.timestamps.iloc[0]
        year = first_timestamp.year
        time_str = first_timestamp.strftime('%H:%M')

        self.frame_bar = self.button_frame
        self.background_button = tk.Button(
            self.frame_bar, text="G",
            command=self.toggle_background, bg="#4CAF50", fg="white"
        )
        self.background_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.background_button, "Toggle background color on flag plots")

        self.vertical_lines_button = tk.Button(
            self.frame_bar, text="T",
            command=self.toggle_vertical_lines, bg="#4C50CA", fg="white"
        )
        self.vertical_lines_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.vertical_lines_button, "Toggle vertical lines on plots")

        self.time_format_button = tk.Button(
            self.frame_bar, text=str(year) if self.show_time_only.get() else time_str,
            command=self.time_manager.toggle_time_format, bg="#FF5722", fg="white"
        )
        self.time_format_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.time_format_button, "Toggle time format (Date/Time)")

        self.create_column_selector_button()
        self.create_application_settings_button()

        self.theme_button = ttk.Button(
            self.frame_bar, image=self.light_icon if self.theme == "light" else self.dark_icon,
            command=self.theme_manager.toggle_theme
        )
        self.theme_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.theme_button, "Toggle theme (Light/Dark)")

    def create_tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        tooltip.withdraw()

        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() - 10
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def save_view_limits(self):
        """Сохраняет текущие пределы осей перед перерисовкой."""
        self.main_xlim = self.ax_main.get_xlim()
        self.main_ylim = self.ax_main.get_ylim()
        self.percent_ylim = self.ax_percent.get_ylim()
        self.flag_ylims = [ax.get_ylim() for ax in self.flag_axes]

    def restore_view_limits(self):
        """Восстанавливает сохранённые пределы осей после перерисовки."""
        self.ax_main.set_xlim(self.main_xlim)
        self.ax_main.set_ylim(self.main_ylim)
        self.ax_percent.set_ylim(self.percent_ylim)
        for ax, ylim in zip(self.flag_axes, self.flag_ylims):
            ax.set_ylim(ylim)
        self.canvas.draw()

    def toggle_background(self):
        """Переключает фон флагов и перерисовывает график с сохранением масштаба."""
        self.save_view_limits()  # Сохраняем текущий масштаб
        self.show_flag_background.set(not self.show_flag_background.get())
        self.plot_manager.plot_data()
        self.restore_view_limits()  # Восстанавливаем масштаб

    def toggle_vertical_lines(self):
        """Переключает вертикальные линии и перерисовывает график с сохранением масштаба."""
        self.save_view_limits()  # Сохраняем текущий масштаб
        self.show_vertical_lines.set(not self.show_vertical_lines.get())
        self.plot_manager.plot_data()
        self.restore_view_limits()  # Восстанавливаем масштаб

    def save_settings(self):
        self.config.save_app_config(self)

    def on_close(self):
        try:
            self.save_settings()
            if hasattr(self.data_loader, 'cleanup'):
                self.data_loader.cleanup()
        except Exception as e:
            print(f"Error when closing the application: {e}")
        finally:
            self.root.quit()
            self.root.destroy()

    def create_column_selector_button(self):
        self.column_button = ttk.Button(
            self.frame_bar,
            image=self.check_icon,
            command=self.show_column_selector
        )
        self.column_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.column_button, "Column Selector")

    def show_column_selector(self):
        if not hasattr(self, '_column_selector'):
            self._column_selector = ColumnSelector(
                self.root,
                self.config,
                self.data_loader,
                self.on_apply_callback,
                self.theme
            )
        else:
            if hasattr(self._column_selector, 'window'):
                if self._column_selector.window.winfo_exists():
                    self._column_selector.bring_to_front()
                else:
                    self._column_selector = ColumnSelector(
                        self.root,
                        self.config,
                        self.data_loader,
                        self.on_apply_callback,
                        self.theme
                    )

    def on_apply_callback(self, selection):
        self.selected_columns = {
            'flags': selection['flags'],
            'numerics': selection['numerics'],
            'percents': selection.get('percents', []),
            'bools': selection['bools']
        }
        #self.save_view_limits()  # Сохраняем текущий масштаб
        self.plot_manager.plot_data()
        #self.restore_view_limits()  # Восстанавливаем масштаб

    def create_application_settings_button(self):
        self.settings_button = ttk.Button(
            self.frame_bar,
            image=self.gear_icon,
            command=self.show_application_settings
        )
        self.settings_button.pack(side=tk.LEFT, padx=5)
        self.create_tooltip(self.settings_button, "Application Settings")

    def show_application_settings(self):
        self.save_settings()
        if not hasattr(self, '_settings_window'):
            self._settings_window = SettingsWindow(
                self.root,
                self.config,
                self.on_apply_settings_callback,
                self.theme
            )
        else:
            if hasattr(self._settings_window, 'window'):
                if self._settings_window.window.winfo_exists():
                    self._settings_window.bring_to_front()
                else:
                    self._settings_window = SettingsWindow(
                        self.root,
                        self.config,
                        self.on_apply_settings_callback,
                        self.theme
                    )

    def on_apply_settings_callback(self):
        self.config.load_app_config(self)
        self.theme_manager.apply_window_theme()
        self.theme_manager.apply_toolbar_theme()
        self.plot_manager.plot_data()

    def load_icons(self):
        try:
            self.light_icon = ImageTk.PhotoImage(Image.open("images/moon.png").resize((20, 20)))
            self.dark_icon = ImageTk.PhotoImage(Image.open("images/sun.png").resize((20, 20)))
            self.gear_icon = ImageTk.PhotoImage(Image.open("images/gear.png").resize((20, 20)))
            self.check_icon = ImageTk.PhotoImage(Image.open("images/check.png").resize((20, 20)))
        except:
            self.light_icon = None
            self.dark_icon = None
            self.bg_icon = None
            self.clock_icon = None
            self.gear_icon = None
            self.table_icon = None
            self.check_icon = None

    def window_size(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.update()
        if sys.platform == "win32":
            self.root.state("zoomed")