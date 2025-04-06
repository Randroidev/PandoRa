import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class RandomDemoGenerator:
    def __init__(self, rows=100, cols=9):
        if cols < 5:
            cols = 5
        self.rows = rows
        self.cols = cols-2
        self.numeric_cols = max(1, cols // 3)
        self.flag_cols = max(1, cols // 3)
        self.bool_cols = max(1, cols - self.numeric_cols - self.flag_cols)

    def generate_data(self):
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(days=self.rows),
            end=datetime.now(),
            periods=self.rows
        )

        data = {'Timestamp': timestamps}

        # Числовые данные (могут быть любыми числами)
        for i in range(self.numeric_cols):
            base = random.uniform(-20000, 20000)
            values = np.random.normal(base, 5000, self.rows)
            data[f'Value_{i + 1}'] = values

        # Флаги (F- префикс, должны быть 0/1)
        for i in range(self.flag_cols):
            flags = np.random.choice([0, 1], self.rows, p=[0.7, 0.3])  # Явно 0 и 1
            data[f'F-Process_{i + 1}'] = flags

        # Булевы состояния (True/False)
        for i in range(self.bool_cols):
            states = np.random.choice([True, False], self.rows, p=[0.3, 0.7])
            data[f'State_{i + 1}'] = states

        # Создаем DataFrame, гарантируя одинаковую длину всех массивов
        df = pd.DataFrame(data)

        # Добавляем процентные данные
        df['PRC1 %'] = 100 * (df['Value_1'] - df['Value_2']) / (df['Value_2'])
        df['PRC2 %'] = np.clip(90 + 10 * np.sin(np.linspace(0, 10 * np.pi, len(df))), 70, 100)

        return df
