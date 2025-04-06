import pandas as pd
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse
from demo_generator import DemoGenerator


class DataLoader:
    def __init__(self, root, file_path=None, demo_mode=None, demo_args=None):
        self.root = root
        self.file_path = file_path
        self.demo_mode = demo_mode
        self.demo_args = demo_args
        self.temp_file = None
        self.df = None
        self.timestamps = None
        self.numeric_columns = []
        self.percent_columns = []
        self.flag_columns = []
        self.bool_columns = []

        try:
            if demo_mode:
                self.load_demo_data()
            else:
                self.load_data()
        except Exception as e:
            self.cleanup()
            raise ValueError(f"Data loading error: {str(e)}")


    def load_demo_data(self):
        if self.demo_mode == 'batt':
            self.temp_file, self.df = DemoGenerator.generate_demo_data('batt')
        elif self.demo_mode == 'rand':
            points, signals = self.demo_args
            self.temp_file, self.df = DemoGenerator.generate_demo_data('rand', points, signals)
        self.process_data()

    def load_data(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        self.df = pd.read_excel(self.file_path)
        self.process_data()

    def process_data(self):
        if self.df is None or self.df.empty:
            raise ValueError("No data for processing")

        self.timestamps = pd.to_datetime(self.df.iloc[:, 0])
        self.numeric_columns = []
        self.percent_columns = []
        self.flag_columns = []
        self.bool_columns = []

        for col in self.df.columns[1:]:
            if self.df[col].dtype == bool:
                self.flag_columns.append(col)
            elif col.startswith("F-") and pd.api.types.is_numeric_dtype(self.df[col]):
                self.bool_columns.append(col)
                self.df[col] = self.df[col].astype(bool)
            elif '%' in col and pd.api.types.is_numeric_dtype(self.df[col]):  # Процентные данные
                self.percent_columns.append(col)
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                self.numeric_columns.append(col)

    def cleanup(self):
        if hasattr(self, 'temp_file') and self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception as e:
                print(f"Error when deleting a temporary file: {e}")

def get_file_path():
    parser = argparse.ArgumentParser(description="Data Visualization App")
    parser.add_argument("file_path", nargs="?", default=None, help="Path to the data file")
    parser.add_argument("--demo", nargs='+', help="Demo mode: 'batt' or [points signals]")
    args = parser.parse_args()

    # Режим демонстрации
    if args.demo:
        if args.demo[0] == 'batt':
            return None, 'batt', None
        elif len(args.demo) == 2:
            try:
                points = int(args.demo[0])
                signals = int(args.demo[1])
                return None, 'rand', (points, signals)
            except ValueError:
                print("Error: For random demo, points and signals must be integers")
                sys.exit(1)
        else:
            print("Error: Invalid demo arguments. Use '--demo batt' or '--demo points signals'")
            sys.exit(1)

    # Обычный режим с файлом
    if args.file_path and os.path.exists(args.file_path):
        return args.file_path, None, None

    default_file = "data.xls"
    if os.path.exists(default_file):
        return default_file, None, None

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select data-file",
        filetypes=[("Excel files", "*.xls *.xlsx"), ("All files", "*.*")]
    )
    root.destroy()

    if not file_path:
        messagebox.showerror("Error", "Data-file not selected.")
        sys.exit(1)

    return file_path, None, None