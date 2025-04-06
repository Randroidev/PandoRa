import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ColumnSelector:
    _instance = None  # Для отслеживания открытого экземпляра

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, parent, config_manager, data_loader, on_apply_callback, theme):
        if self._initialized:
            self.bring_to_front()
            return

        self.theme = theme
        self.parent = parent # root
        self.config_manager = config_manager
        self.data_loader = data_loader
        self.on_apply_callback = on_apply_callback
        self._initialized = True

        self.setup_window()
        self.create_widgets()

    def bring_to_front(self):
        if hasattr(self, 'window') and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()

    def setup_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Column selector")
        self.window.geometry("800x560")
        self.window.minsize(600, 400)

        # Получаем цвета из конфигурации в зависимости от темы
        bg_color = self.config_manager.config["Theme"][f"{self.theme}_bg_color"]
        # Устанавливаю цвет окна
        self.window.configure(bg=bg_color)

        try:
            icon = Image.open("images/check.png")
            icon = ImageTk.PhotoImage(icon)
            self.window.tk.call('wm', 'iconphoto', self.window._w, icon)
        except:
            pass

        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.focus_force()
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        type(self)._instance = None
        self._initialized = False
        self.window.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки управления
        self.create_button_frame(main_frame)

        # Фрейм для чеклистов
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем чеклисты
        self.create_checklist(lists_frame, "Флаги", self.data_loader.flag_columns, 'flag', 0)
        self.create_checklist(lists_frame, "Численные", self.data_loader.numeric_columns, 'numeric', 1)

        if hasattr(self.data_loader, 'percent_columns') and self.data_loader.percent_columns:
            self.create_checklist(lists_frame, "Процентные", self.data_loader.percent_columns, 'percent', 2)

        self.create_checklist(lists_frame, "Состояния", self.data_loader.bool_columns, 'bool', 3)

        # Настройка распределения пространства
        for i in range(4):
            lists_frame.grid_columnconfigure(i, weight=1, uniform="cols")

    def create_button_frame(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 10))

        tk.Button(
            button_frame,
            text="Применить",
            command=self.apply_selection,
            bg="#4CAF50", fg="white"
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            button_frame,
            text="Отмена",
            command=self.close_window,
            bg="#757575", fg="white"
        ).pack(side=tk.RIGHT, padx=5)

    def create_checklist(self, parent, title, columns, col_type, column):
        if not columns:
            return

        group_frame = ttk.LabelFrame(parent, text=title)
        group_frame.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")

        tree_frame = ttk.Frame(group_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем Treeview без заголовков
        tree = ttk.Treeview(
            tree_frame,
            columns=("selected", "name"),
            show="tree",  # Убираем заголовки
            selectmode="none",
            height=22
        )

        # Настройка колонок (1:5 соотношение)
        tree.column("#0", width=0, stretch=tk.NO)  # Скрытая колонка
        tree.column("selected", width=50, anchor=tk.CENTER, stretch=tk.NO)
        tree.column("name", width=250, anchor=tk.W)

        # Добавляем скроллбары
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Заполняем данными
        for col in columns:
            unique_values = self.data_loader.df[col].nunique()
            tree.insert("", tk.END, values=("✓" if unique_values > 1 else "", col))

        # Привязываем обработчики
        tree.bind("<Button-1>", lambda e: self.on_tree_click(e, tree))
        tree.bind("<Return>", lambda e: self.toggle_current_item(tree))

        setattr(self, f"{col_type}_tree", tree)

    def on_tree_click(self, event, tree):
        item = tree.identify_row(event.y)
        if item:  # Клик по любой части строки
            self.toggle_item(tree, item)

    def toggle_item(self, tree, item):
        current = tree.item(item, "values")
        new_value = "✓" if current[0] != "✓" else ""
        tree.item(item, values=(new_value, current[1]))

    def toggle_current_item(self, tree):
        item = tree.focus()
        if item:
            self.toggle_item(tree, item)

    def apply_selection(self):
        selection = {
            'flags': self.get_selected_columns('flag'),
            'numerics': self.get_selected_columns('numeric'),
            'bools': self.get_selected_columns('bool')
        }

        if hasattr(self, 'percent_tree'):
            selection['percents'] = self.get_selected_columns('percent')
        else:
            selection['percents'] = []

        self.on_apply_callback(selection)
        self.close_window()

    def get_selected_columns(self, col_type):
        if not hasattr(self, f"{col_type}_tree"):
            return []

        tree = getattr(self, f"{col_type}_tree")
        selected = []

        for item in tree.get_children():
            values = tree.item(item, "values")
            if values[0] == "✓":
                selected.append(values[1])

        return selected