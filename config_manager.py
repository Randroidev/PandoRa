import configparser
import os
import tkinter as tk


class ConfigManager:
    def __init__(self, config_file="settings.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_default_config()

    def _create_default_config(self):
        # Основные настройки
        self.config["General"] = {
        }

        # Настройки отображения
        self.config["Display"] = {
            "theme": "dark",
            "font_size": "14",
            "show_time_only": "True",
            "show_vertical_lines": "False",
            "lock_percent_scale": "False",
        }

        # Настройки флагов
        self.config["Flags"] = {
            "flag_color": "#9b0000",
            "flag_alpha": "0.8",
            "flag_bg_color": "green",
            "flag_bg_alpha": "0.2",
            "flag_height_px": "24",
            "show_flag_background": "True",
            "legend_bold": "True",
        }

        # Настройки процессов
        self.config["Processes"] = {
            "show_processes_labels": "False",
            "color_process_1": "green",
            "alpha_process_1": "0.2",
            "color_process_2": "red",
            "alpha_process_2": "0.2",
            "color_process_3": "blue",
            "alpha_process_3": "0.2",
            "color_process_4": "yellow",
            "alpha_process_4": "0.2",
            "color_process_5": "cyan",
            "alpha_process_5": "0.2",
        }

        # Настройки прямоугольников
        self.config["Rectangles"] = {
            "rectangle_top": "-0.015",
            "rectangle_left": "0.06",
            "rectangle_right": "0.085",
            "rectangle_bottom": "0.05",
        }

        # Настройки темы
        self.config["Theme"] = {
            "light_bg_color": "#f0f0f0",
            "dark_bg_color": "#2d2d2d",
            "light_fg_color": "#000000",
            "dark_fg_color": "#ffffff",
            "light_font_color": "#4f5278",
            "dark_font_color": "#d3d5e4",
            "light_axis_color": "#000000",
            "dark_axis_color": "#ffffff",
        }

        # Требуют перезагрузки для приминения
        self.config["NeedRestart"] = {
            "1": "flag_height_px",
            "2": "Rectangles",
        }

        # Не активированы
        self.config["Disabled"] = {
            "1": "lock_percent_scale",
        }

        self.save_settings()

    def save_settings(self):
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def get(self, section, option):
        return self.config.get(section, option)

    def getboolean(self, section, option):
        return self.config.getboolean(section, option)

    def getint(self, section, option):
        return self.config.getint(section, option)

    def getfloat(self, section, option):
        return self.config.getfloat(section, option)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))

    def load_app_config(self, app):
        """Загружает все конфигурационные параметры в приложение"""
        # Параметры отображения
        app.font_size = self.getint("Display", "font_size")
        app.theme = self.get("Display", "theme")
        app.show_time_only = tk.BooleanVar(value=self.getboolean("Display", "show_time_only"))
        app.show_vertical_lines = tk.BooleanVar(value=self.getboolean("Display", "show_vertical_lines"))
        app.lock_percent_scale = tk.BooleanVar(value=self.getboolean("Display", "lock_percent_scale"))

        # Параметры флагов
        app.flag_color = self.get("Flags", "flag_color")
        app.flag_alpha = self.getfloat("Flags", "flag_alpha")
        app.flag_bg_color = self.get("Flags", "flag_bg_color")
        app.flag_bg_alpha = self.getfloat("Flags", "flag_bg_alpha")
        app.flag_height_px = self.getint("Flags", "flag_height_px")
        app.show_flag_background = tk.BooleanVar(value=self.getboolean("Flags", "show_flag_background"))
        app.legend_bold = self.getboolean("Flags", "legend_bold")

        # Параметры процессов
        app.show_processes_labels = self.getboolean("Processes", "show_processes_labels")
        app.bool_colors = [
            self.get("Processes", "color_process_1"),
            self.get("Processes", "color_process_2"),
            self.get("Processes", "color_process_3"),
            self.get("Processes", "color_process_4"),
            self.get("Processes", "color_process_5")
        ]
        app.bool_alphas = [
            self.getfloat("Processes", "alpha_process_1"),
            self.getfloat("Processes", "alpha_process_2"),
            self.getfloat("Processes", "alpha_process_3"),
            self.getfloat("Processes", "alpha_process_4"),
            self.getfloat("Processes", "alpha_process_5")
        ]

        # Параметры прямоугольников
        app.rectangle_top = self.getfloat("Rectangles", "rectangle_top")
        app.rectangle_left = self.getfloat("Rectangles", "rectangle_left")
        app.rectangle_right = self.getfloat("Rectangles", "rectangle_right")
        app.rectangle_bottom = self.getfloat("Rectangles", "rectangle_bottom")

        # Параметры темы
        app.light_bg_color = self.get("Theme", "light_bg_color")
        app.dark_bg_color = self.get("Theme", "dark_bg_color")
        app.light_fg_color = self.get("Theme", "light_fg_color")
        app.dark_fg_color = self.get("Theme", "dark_fg_color")
        app.light_font_color = self.get("Theme", "light_font_color")
        app.dark_font_color = self.get("Theme", "dark_font_color")
        app.light_axis_color = self.get("Theme", "light_axis_color")
        app.dark_axis_color = self.get("Theme", "dark_axis_color")

        # Применяются после перезагрузки
        self.need_restart = []
        if self.config.has_section("NeedRestart"):
            i = 1
            while self.config.has_option("NeedRestart", str(i)):
                self.need_restart.append(self.get("NeedRestart", str(i)))
                i += 1
        #app.need_restart_application = need_restart

        # Не активированы
        self.disabled = []
        if self.config.has_section("Disabled"):
            i = 1
            while self.config.has_option("Disabled", str(i)):
                self.disabled.append(self.get("Disabled", str(i)))
                i += 1
        #app.disabled = disabled

    def save_app_config(self, app):
        """Сохраняет текущие настройки приложения в конфигурационный файл"""
        try:
            # Параметры отображения
            self.set("Display", "font_size", str(app.font_size))
            self.set("Display", "theme", app.theme)
            self.set("Display", "show_time_only", str(app.show_time_only.get()))
            self.set("Display", "show_vertical_lines", str(app.show_vertical_lines.get()))
            self.set("Display", "lock_percent_scale", str(app.lock_percent_scale.get()))

            # Параметры флагов
            self.set("Flags", "flag_color", app.flag_color)
            self.set("Flags", "flag_alpha", str(app.flag_alpha))
            self.set("Flags", "flag_bg_color", app.flag_bg_color)
            self.set("Flags", "flag_bg_alpha", str(app.flag_bg_alpha))
            self.set("Flags", "flag_height_px", str(app.flag_height_px))
            self.set("Flags", "show_flag_background", str(app.show_flag_background.get()))
            self.set("Flags", "legend_bold", str(app.legend_bold))

            # Параметры процессов
            self.set("Processes", "show_processes_labels", str(app.show_processes_labels))
            for i in range(1, 6):
                if hasattr(app, f'color_process_{i}'):
                    self.set("Processes", f"color_process_{i}", getattr(app, f'color_process_{i}'))
                    self.set("Processes", f"alpha_process_{i}", str(getattr(app, f'alpha_process_{i}')))

            # Параметры прямоугольников
            self.set("Rectangles", "rectangle_top", str(app.rectangle_top))
            self.set("Rectangles", "rectangle_left", str(app.rectangle_left))
            self.set("Rectangles", "rectangle_right", str(app.rectangle_right))
            self.set("Rectangles", "rectangle_bottom", str(app.rectangle_bottom))

            # Параметры темы
            self.set("Theme", "light_bg_color", app.light_bg_color)
            self.set("Theme", "dark_bg_color", app.dark_bg_color)
            self.set("Theme", "light_fg_color", app.light_fg_color)
            self.set("Theme", "dark_fg_color", app.dark_fg_color)
            self.set("Theme", "light_font_color", app.light_font_color)
            self.set("Theme", "dark_font_color", app.dark_font_color)
            self.set("Theme", "light_axis_color", app.light_axis_color)
            self.set("Theme", "dark_axis_color", app.dark_axis_color)

            self.save_settings()
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")

    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self._create_default_config()
        self.save_settings()

    def get_var(self, option):
        """Возвращает переменную Tkinter для указанной опции"""
        # Определяем, в какой секции находится опция
        sections = {
            "Display": ["font_size", "theme", "show_time_only", "show_vertical_lines"],
            "Flags": ["flag_alpha", "flag_height_px", "show_flag_background", "legend_bold"],
            "Processes": ["show_processes_labels"],
        }

        section = None
        for sec, opts in sections.items():
            if option in opts:
                section = sec
                break

        if section is None:
            section = "General"  # По умолчанию ищем в General

        if option in ["show_time_only", "show_vertical_lines", "show_processes_labels", "show_flag_background",
                      "legend_bold"]:
            return tk.BooleanVar(value=self.getboolean(section, option))
        elif option in ["font_size", "flag_height_px"]:
            return tk.IntVar(value=self.getint(section, option))
        elif option in ["flag_alpha"]:
            return tk.DoubleVar(value=self.getfloat(section, option))
        else:
            return tk.StringVar(value=self.get(section, option))