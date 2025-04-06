from gui import DataVisualizationApp
from file_handler import get_file_path
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import customtkinter as ctk


if __name__ == "__main__":
    try:
        file_path, demo_mode, demo_args = get_file_path()

        root = ctk.CTk()
        root.title("Data Visualization App")
        try:
            if demo_mode:
                app = DataVisualizationApp(root, demo_mode=demo_mode, demo_args=demo_args)
            else:
                app = DataVisualizationApp(root, file_path=file_path)

            if sys.platform == "win32":
                root.iconbitmap("images/lines.ico")
            else:
                icon = tk.PhotoImage(file="images/lines.png")
                root.iconphoto(False, icon) # False - для всех окон приложения

            root.mainloop()
        except Exception as e:
            messagebox.showerror("Application Error", str(e))
            root.destroy()
    except Exception as e:
        messagebox.showerror("Application Start Error", str(e))