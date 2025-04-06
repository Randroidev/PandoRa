from matplotlib.dates import DateFormatter, AutoDateLocator

class TimeManager:
    def __init__(self, app):
        self.app = app

    def update_time_format(self):
        time_format = '%H:%M:%S' if self.app.show_time_only.get() else '%Y-%m-%d %H:%M'
        self.app.ax_main.xaxis.set_major_formatter(DateFormatter(time_format))
        for ax in self.app.flag_axes:
            ax.xaxis.set_major_formatter(DateFormatter(time_format))

        self.app.ax_main.xaxis.set_major_locator(AutoDateLocator())
        for ax in self.app.flag_axes:
            ax.xaxis.set_major_locator(AutoDateLocator())

        self.app.canvas.draw()

    def toggle_time_format(self):
        self.app.show_time_only.set(not self.app.show_time_only.get())
        self.update_time_format()
        first_timestamp = self.app.data_loader.timestamps.iloc[0]
        year = first_timestamp.year
        time_str = first_timestamp.strftime('%H:%M')
        self.app.time_format_button.config(text=str(year) if self.app.show_time_only.get() else time_str)