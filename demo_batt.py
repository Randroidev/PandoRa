import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.signal import savgol_filter      # Реализация фильтра Савицкого-Голея


class BatteryDemoGenerator:
    def __init__(self):
        # Основные параметры батареи
        self.initial_voltage = 10800
        self.full_charge_voltage = 12600
        self.full_discharge_voltage = 9000
        self.max_current = 3000
        self.nominal_capacity = 5000  # мАч
        self.sample_interval = 10  # секунд

        # Параметры старения
        self.capacity_degradation = 0.998  # 0.2% потери за цикл
        self.internal_resistance_growth = 1.005  # 0.5% роста сопротивления за цикл

        # Температурные параметры
        self.ambient_temp = 22
        self.max_temp = 45
        self.heat_coeff = 0.0002
        self.cooling_coeff = 0.0001

    def _generate_charge_curve(self, duration_hours):
        """Генерирует кривые заряда с нелинейными участками"""
        steps = int(duration_hours * 3600 / self.sample_interval)
        x = np.linspace(0, 1, steps)

        # Нелинейное напряжение (логарифмический рост)
        voltage = self.initial_voltage + np.log1p(x * 10) * \
                  (self.full_charge_voltage - self.initial_voltage) / np.log(11)

        # Ток заряда (экспоненциальное снижение)
        current = self.max_current * np.exp(-x * 3)

        # Сглаживание кривых
        voltage = savgol_filter(voltage, window_length=51, polyorder=3)
        current = savgol_filter(current, window_length=51, polyorder=3)

        return voltage, current

    def _generate_discharge_curve(self, duration_hours):
        """Генерирует кривые разряда с ускорением на низких напряжениях"""
        steps = int(duration_hours * 3600 / self.sample_interval)
        x = np.linspace(0, 1, steps)

        # Нелинейное напряжение (ускоренный разряд в конце)
        voltage = self.full_charge_voltage - (x ** 1.7) * \
                  (self.full_charge_voltage - self.full_discharge_voltage)

        # Ток разряда (резкое отключение в конце)
        current = -self.max_current * np.ones(steps)
        cutoff = int(steps * 0.95)
        current[cutoff:] = np.linspace(-self.max_current, 0, steps - cutoff)

        # Сглаживание
        voltage = savgol_filter(voltage, window_length=51, polyorder=3)
        current = savgol_filter(current, window_length=51, polyorder=3)

        return voltage, current

    def _calculate_temperature(self, current, last_temp, elapsed):
        """Расчет температуры с учетом теплообмена"""
        power_loss = (current / 1000) ** 2 * (1.0 + 0.01 * elapsed / 3600)  # Рост сопротивления
        temp_change = power_loss * self.heat_coeff - self.cooling_coeff
        new_temp = last_temp + temp_change
        return np.clip(new_temp, self.ambient_temp, self.max_temp)

    def generate_cycle(self, cycle_num):
        """Генерирует один полный цикл с учетом старения"""
        # Заряд (2 часа)
        charge_v, charge_i = self._generate_charge_curve(2)
        charge_steps = len(charge_v)

        # Пауза после заряда (2 часа)
        pause_steps = int(2 * 3600 / self.sample_interval)
        pause_v = np.full(pause_steps, self.full_charge_voltage)
        pause_i = np.zeros(pause_steps)

        # Разряд (2 часа)
        discharge_v, discharge_i = self._generate_discharge_curve(2)
        discharge_steps = len(discharge_v)

        # Пауза после разряда (5 часов)
        final_pause_steps = int(5 * 3600 / self.sample_interval)
        final_pause_v = np.full(final_pause_steps, self.full_discharge_voltage)
        final_pause_i = np.zeros(final_pause_steps)

        # Объединяем все сегменты
        voltage = np.concatenate([charge_v, pause_v, discharge_v, final_pause_v])
        current = np.concatenate([charge_i, pause_i, discharge_i, final_pause_i])

        # Рассчитываем температуру
        temperature = [self.ambient_temp]
        for i in range(1, len(current)):
            temp = self._calculate_temperature(
                current[i], temperature[-1], i * self.sample_interval
            )
            temperature.append(temp)

        # Эффект старения
        current_capacity = self.nominal_capacity * (self.capacity_degradation ** cycle_num)
        max_error = 5 * (self.internal_resistance_growth ** cycle_num)

        # Режимы работы (числовые 0/1)
        charge_state = (current > 50).astype(int)
        discharge_state = (current < -50).astype(int)

        # Флаги состояния (булевы)
        fc_flag = (np.array(voltage) >= self.full_charge_voltage - 5) & (np.abs(current) < 5)
        fd_flag = (np.array(voltage) <= self.full_discharge_voltage + 5) & (np.abs(current) < 5)

        return {
            'voltage': voltage,
            'current': current,
            'temperature': temperature[:len(voltage)],
            'capacity': current_capacity,
            'max_error': max_error,
            'fc_flag': fc_flag,
            'fd_flag': fd_flag,
            'charge_state': charge_state,
            'discharge_state': discharge_state,
            'steps': len(voltage)
        }

    def generate_data(self, cycles=3):
        """Генерирует полный набор данных"""
        data = {
            'Timestamp': [],
            'Voltage': [],
            'Current': [],
            'Temperature': [],
            'Capacity': [],
            'Max Error': [],
            'Remaining Capacity': [],
            'FC': [],
            'FD': [],
            'F-CHARGE': [],
            'F-DISCHARGE': []
        }

        start_time = datetime.now()
        elapsed = 0

        for cycle in range(cycles):
            cycle_data = self.generate_cycle(cycle)
            cycle_length = cycle_data['steps']

            # Генерация временных меток
            cycle_timestamps = [
                start_time + timedelta(seconds=elapsed + i * self.sample_interval)
                for i in range(cycle_length)
            ]
            data['Timestamp'].extend(cycle_timestamps)
            elapsed += cycle_length * self.sample_interval

            # Заполнение данных
            data['Voltage'].extend(cycle_data['voltage'])
            data['Current'].extend(cycle_data['current'])
            data['Temperature'].extend(cycle_data['temperature'])
            data['Capacity'].extend([cycle_data['capacity']] * cycle_length)
            data['Max Error'].extend([cycle_data['max_error']] * cycle_length)

            # Расчет остаточной емкости
            remaining_cap = np.interp(
                cycle_data['voltage'],
                [self.full_discharge_voltage, self.full_charge_voltage],
                [0, cycle_data['capacity']]
            )
            data['Remaining Capacity'].extend(remaining_cap)

            # Флаги состояния (числовые 0/1)
            data['FC'].extend(cycle_data['fc_flag'])
            data['FD'].extend(cycle_data['fd_flag'])

            # Режимы работы (булевы)
            data['F-CHARGE'].extend(cycle_data['charge_state'])
            data['F-DISCHARGE'].extend(cycle_data['discharge_state'])

        # Создаем DataFrame, гарантируя одинаковую длину всех массивов
        df = pd.DataFrame(data)

        # Добавляем процентные данные
        df['Health %'] = 100 * (df['Voltage'] - self.full_discharge_voltage) / \
                         (self.full_charge_voltage - self.full_discharge_voltage)
        df['Efficiency %'] = np.clip(90 + 10 * np.sin(np.linspace(0, 10 * np.pi, len(df))), 70, 100)

        return df


# Пример использования
if __name__ == "__main__":
    generator = BatteryDemoGenerator()
    df = generator.generate_data(cycles=3)

    # Проверка структуры данных
    print("Структура данных:")
    print(df.dtypes)
    print("\nПервые 5 строк:")
    print(df.head())

    # Сохранение в Excel
    df.to_excel('battery_data.xlsx', index=False)
    print("\nДанные сохранены в battery_data.xlsx")