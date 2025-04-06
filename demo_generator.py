from demo_batt import BatteryDemoGenerator
from demo_rand import RandomDemoGenerator
import tempfile
import os


class DemoGenerator:
    @staticmethod
    def generate_demo_data(mode, *args):
        """
        Генерирует демо-данные и сохраняет во временный Excel-файл
        Возвращает путь к временному файлу и DataFrame
        """
        if mode == 'batt':
            generator = BatteryDemoGenerator()
        elif mode == 'rand':
            points, signals = args
            generator = RandomDemoGenerator(rows=points, cols=signals)
        else:
            raise ValueError(f"Unknown demo mode: {mode}")

        df = generator.generate_data()

        # Создаем временный файл
        temp_dir = tempfile.gettempdir()
        #temp_file = os.path.join(temp_dir, f"pandora_demo_{mode}_{os.getpid()}.xlsx")
        temp_file = os.path.join("", f"pandora_demo_{mode}_{os.getpid()}.xlsx")
        df.to_excel(temp_file, index=False)

        return temp_file, df