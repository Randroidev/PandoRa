from ttkthemes import ThemedStyle

class ThemeManager:
    def __init__(self, app):
        self.app = app

    def apply_window_theme(self):
        # Цвет заголовка окна
        self.app.root._set_appearance_mode(self.app.theme)

        # Применение темы к окну и элементам в нём
        window_theme = "default" if self.app.theme == "light" else "equilux"
        style = ThemedStyle(self.app.root)
        style.set_theme(window_theme)

    def apply_toolbar_theme(self):
        # Определение цветов
        bg_color = self.app.light_bg_color if self.app.theme == "light" else self.app.dark_bg_color

        self.app.toolbar.config(bg=bg_color)  # цвет фона тулбара
        self.app.fig.set_facecolor(bg_color)
        self.app.ax_main.set_facecolor(bg_color)
        for ax in self.app.flag_axes:
            ax.set_facecolor(bg_color)

    def apply_theme(self):
        # Определение цветов
        bg_color = self.app.light_bg_color if self.app.theme == "light" else self.app.dark_bg_color
        font_color = self.app.light_font_color if self.app.theme == "light" else self.app.dark_font_color
        axis_color = self.app.light_axis_color if self.app.theme == "light" else self.app.dark_axis_color

        for ax in [self.app.ax_main] + self.app.flag_axes:
            ax.tick_params(axis="x", colors=font_color, labelsize=self.app.font_size)
            ax.tick_params(axis="y", colors=font_color, labelsize=self.app.font_size)
            ax.spines["bottom"].set_color(axis_color)
            ax.spines["top"].set_color(axis_color)
            ax.spines["left"].set_color(axis_color)
            ax.spines["right"].set_color(axis_color)
            ax.xaxis.label.set_color(font_color)
            ax.yaxis.label.set_color(font_color)
            ax.title.set_color(font_color)

        if self.app.ax_percent:
            self.app.ax_percent.set_facecolor(bg_color)
            self.app.ax_percent.spines['right'].set_color(font_color)
            self.app.ax_percent.yaxis.label.set_color(font_color)
            self.app.ax_percent.tick_params(axis='y', colors=font_color, labelsize=self.app.font_size)

        self.app.canvas.draw()

    def toggle_theme(self):
        self.app.theme = "dark" if self.app.theme == "light" else "light"
        self.app.theme_button.config(image=self.app.dark_icon if self.app.theme == "dark" else self.app.light_icon)
        self.apply_window_theme()
        self.apply_toolbar_theme()
        self.apply_theme()
        self.app.config.save_app_config(self.app)