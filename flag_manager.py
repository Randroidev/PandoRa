import numpy as np
import pandas as pd


class FlagManager:
    def __init__(self, app):
        self.app = app

    def on_flag_click(self, event):
        selected_flags = getattr(self.app, 'selected_columns', {}).get('flags', self.app.data_loader.flag_columns)
        visible_axes = self.app.flag_axes[:len(selected_flags)]

        for ax, col in zip(visible_axes, selected_flags):
            if ax == event.inaxes and col in self.app.data_loader.flag_columns:
                click_time = pd.to_datetime(event.xdata, unit="D", origin="unix")
                idx = np.abs(self.app.data_loader.timestamps - click_time).argmin()
                flag_data = self.app.data_loader.df[col].astype(int)

                left_idx = idx
                while left_idx > 0 and flag_data.iloc[left_idx] == flag_data.iloc[idx]:
                    left_idx -= 1

                right_idx = idx
                while right_idx < len(flag_data) - 1 and flag_data.iloc[right_idx] == flag_data.iloc[idx]:
                    right_idx += 1

                left_boundary = self.app.data_loader.timestamps.iloc[left_idx]
                right_boundary = self.app.data_loader.timestamps.iloc[right_idx]

                self.app.ax_main.set_xlim(left_boundary, right_boundary)
                for visible_ax in visible_axes:
                    visible_ax.set_xlim(left_boundary, right_boundary)

                self.app.canvas.draw()
                break