import warnings
import pandas as pd
from matplotlib.dates import AutoDateLocator


class PlotManager:
    def __init__(self, app):
        self.app = app

    def safe_add_legend(self, ax):
        """Безопасное добавление легенды с обработкой предупреждений"""
        lines, labels = ax.get_legend_handles_labels()
        if self.app.ax_percent:
            lines_p, labels_p = self.app.ax_percent.get_legend_handles_labels()
            lines += lines_p
            labels += labels_p

        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                legend = ax.legend(lines, labels, loc='best')

                if any("Creating legend with loc=\"best\" can be slow" in str(warn.message) for warn in w):
                    self.app.legend_warning_occurred = True
                    legend.remove()
                    return ax.legend(lines, labels, loc='upper right', fontsize=self.app.font_size)

                return legend
        except Exception:
            return ax.legend(lines, labels, loc='upper right', fontsize=self.app.font_size)

    def plot_data(self):
        self.app.ax_main.clear()
        if self.app.ax_percent:
            self.app.ax_percent.clear()

        self.plot_data_main()
        self.plot_data_flags()
        self.plot_data_time_lines()

        self.app.time_manager.update_time_format()
        self.safe_add_legend(self.app.ax_main)
        self.app.fig.autofmt_xdate()
        self.app.theme_manager.apply_theme()
        self.app.canvas.draw()

    def plot_data_main(self):
        # Получаем выбранные столбцы (если выбор не сделан, используем все)
        selected = getattr(self.app, 'selected_columns', {})

        # Построение числовых данных (только выбранные)
        numeric_cols = selected.get('numerics', self.app.data_loader.numeric_columns)
        for col in numeric_cols:
            if col in self.app.data_loader.numeric_columns:
                self.app.ax_main.plot(self.app.data_loader.timestamps,
                                      self.app.data_loader.df[col],
                                      label=col)

        y_min, y_max = self.app.ax_main.get_ylim()
        y_range = y_max - y_min
        y_min_extended = y_min - 0.05 * y_range
        y_max_extended = y_max + 0.05 * y_range
        self.app.ax_main.set_ylim(y_min_extended, y_max_extended)

        # Построение процентных данных (только выбранные)
        if hasattr(self.app.data_loader, 'percent_columns'):
            percent_cols = selected.get('percents', self.app.data_loader.percent_columns)
            for col in percent_cols:
                if col in self.app.data_loader.percent_columns:
                    self.app.ax_percent.plot(
                        self.app.data_loader.timestamps,
                        self.app.data_loader.df[col],
                        linestyle='--',
                        alpha=0.7,
                        label=col
                    )

        # Настройка оси процентов после построения графиков
        if self.app.lock_percent_scale.get():
            self.app.ax_percent.set_ylim(0, 100)
            self.app.ax_percent.set_autoscale_on(False)
        else:
            self.app.ax_percent.set_autoscale_on(True)
            self.app.ax_percent.relim()
            self.app.ax_percent.autoscale_view(scaley=True)

        # Построение булевых данных (только выбранные)
        bool_cols = selected.get('bools', self.app.data_loader.bool_columns)
        for i, col in enumerate(bool_cols):
            if col in self.app.data_loader.bool_columns:
                color = self.app.bool_colors[i] if i < len(self.app.bool_colors) else f"C{i}"
                alpha = self.app.bool_alphas[i] if i < len(self.app.bool_alphas) else 0.2
                mask = self.app.data_loader.df[col].astype(bool)

                self.app.ax_main.fill_between(
                    self.app.data_loader.timestamps,
                    y_min_extended,
                    y_max_extended,
                    where=mask,
                    color=color,
                    alpha=alpha,
                    step="pre",
                    label=f'[{col}]'
                )

                if self.app.show_processes_labels and mask.any():
                    first_true_idx = mask.idxmax()
                    middle_x = self.app.data_loader.timestamps[first_true_idx]
                    xlim = self.app.ax_main.get_xlim()
                    xmin = pd.to_datetime(xlim[0], unit='D')
                    xmax = pd.to_datetime(xlim[1], unit='D')

                    if xmin <= middle_x <= xmax:
                        label_y = y_min_extended + 0.02 * y_range
                        label_x = middle_x
                        self.app.ax_main.text(
                            label_x, label_y, col,
                            color='black', ha='left', va='bottom',
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                            fontsize=self.app.font_size - 2,
                            rotation=0
                        )


    def plot_data_flags(self):
        # Получаем выбранные столбцы (если выбор не сделан, используем все)
        selected = getattr(self.app, 'selected_columns', {})

        # Построение флагов (только выбранные)
        flag_cols = selected.get('flags', self.app.data_loader.flag_columns)
        for ax, col in zip(self.app.flag_axes[:len(flag_cols)], flag_cols):
            if col in self.app.data_loader.flag_columns:
                ax.clear()

                # Показать график
                ax.set_visible(True)

                # Добавить обработчик клика (один раз на ось)
                # Отключаем предыдущие обработчики, чтобы избежать дублирования
                if hasattr(ax, 'flag_click_cid'):
                    ax.figure.canvas.mpl_disconnect(ax.flag_click_cid)
                cid = ax.figure.canvas.mpl_connect("button_press_event", self.app.flag_manager.on_flag_click)
                ax.flag_click_cid = cid  # Сохраняем CID для последующего отключения

                # Рисовать ли фон?
                if self.app.show_flag_background.get():
                    ax.fill_between(
                        self.app.data_loader.timestamps,
                        0,
                        1,
                        color=self.app.flag_bg_color,
                        alpha=self.app.flag_bg_alpha,
                    )

                # Закрасить область между двумя кривыми
                ax.fill_between(
                    self.app.data_loader.timestamps,
                    0,
                    self.app.data_loader.df[col].astype(int),
                    color=self.app.flag_color,
                    alpha=self.app.flag_alpha,
                )

                # Название флага слева
                ax.set_ylim(0, 1)
                ax.set_yticks([])
                display_name = col.replace("F-", "") if col.startswith("F-") else col
                ax.set_ylabel(display_name, rotation=0, ha="right", va="center",
                              fontsize=self.app.font_size, fontweight="bold" if self.app.legend_bold else "normal")

                # Спрятать легенду оси времени
                ax.set_xticks([])
                ax.set_xlabel("")
                ax.tick_params(axis="x", labelsize=1, pad=1200, bottom=False, labelbottom=False,
                               top=True, labeltop=True, labelcolor=(0, 0, 0, 0))

            # Скрываем неиспользуемые оси флагов
            for ax in self.app.flag_axes[len(flag_cols):]:
                ax.set_visible(False)
                # Снимаем обработчик клика
                if hasattr(ax, 'flag_click_cid'):
                    ax.figure.canvas.mpl_disconnect(ax.flag_click_cid)
                    delattr(ax, 'flag_click_cid')


    def plot_data_time_lines(self):
        # Получаем выбранные столбцы (если выбор не сделан, используем все)
        selected = getattr(self.app, 'selected_columns', {})
        flag_cols = selected.get('flags', self.app.data_loader.flag_columns)

        # Прорисовка вертикальных линий по меткам времени
        if self.app.show_vertical_lines.get():
            for timestamp in self.app.data_loader.timestamps:
                # Прорисовка линий на основном графике
                self.app.ax_main.axvline(timestamp, color="gray", linestyle="--", alpha=0.3)
                # Прорисовка линий на графиках флагов
                for ax in self.app.flag_axes[:len(flag_cols)]:
                    ax.axvline(timestamp, color="gray", linestyle="--", alpha=0.3)

            # Настройка оси времени
            self.app.ax_main.xaxis.set_minor_locator(AutoDateLocator())
            self.app.ax_main.tick_params(axis="x", rotation=0)
        else:
            # Настройка без линий
            self.app.ax_main.xaxis.set_major_locator(AutoDateLocator())
            self.app.ax_main.tick_params(axis="x", rotation=0)

        # Обновляем позицию основного графика с учетом текущего количества флагов
        num_active_flags = len(flag_cols)
        screen_height = self.app.root.winfo_screenheight()

        # Вычисляем суммарную высоту флагов в долях от экрана
        total_flag_height = num_active_flags * self.app.flag_height_px / screen_height

        # Добавляем отступ между флагами и основным графиком (32 пикселей)
        gap = 32 / screen_height

        # Вычисляем новую нижнюю границу основного графика
        main_bottom = self.app.rectangle_bottom + self.app.rectangle_top
        main_height = (1.0 - total_flag_height - gap - main_bottom - self.app.rectangle_top)

        # Устанавливаем новую позицию
        self.app.ax_main.set_position([
            self.app.rectangle_left,
            main_bottom,
            1.0 - self.app.rectangle_right,
            max(0.1, main_height)  # Защита от отрицательной высоты
        ])
