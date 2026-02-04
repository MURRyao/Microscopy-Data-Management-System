import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ETLView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Microscopy ETL Uploader")
        self.root.geometry("600x700")

        # Выбор файла
        tk.Label(root, text="Выберите изображение", font=("Arial", 12, "bold")).pack(
            pady=5
        )

        self.file_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.file_path_var, width=50).pack(pady=5)

        tk.Button(root, text="Выбрать файл", command=self.controller.choose_file).pack(
            pady=5
        )
        #Указание генетической линии
        tk.Label(
            root,
            text="Укажите генетическую линию",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        # известные значения
        genetic_lines = [
            "C57BL/6",
            "BALB/c",
            "DBA/2",
            "FVB/N",
            "129/Sv"
]

        self.genetic_line = tk.StringVar()
        combobox = ttk.Combobox(
            root,
            textvariable=self.genetic_line,
            values=genetic_lines,
             width=47,
            state="readonly"
)
        combobox.pack(pady=5)


        tk.Label(
            root, text="Введите название эксперимента", font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.name_var = tk.StringVar()
        tk.Entry(root, textvariable=self.name_var, width=40).pack(pady=5)

        # Галочки структуры
        tk.Label(root, text="Отметьте структуры", font=("Arial", 12, "bold")).pack(
            pady=10
        )

        self.flags = {
            "meninges": tk.BooleanVar(),
            "brain": tk.BooleanVar(),
            "sss": tk.BooleanVar(),
            "transverse_sinus": tk.BooleanVar(),
            "cortex": tk.BooleanVar(),
            "thalamus": tk.BooleanVar(),
        }

        tk.Checkbutton(
            root, text="Оболочки (meninges)", variable=self.flags["meninges"]
        ).pack(anchor="w", padx=30)
        tk.Checkbutton(
            root, text="Головной мозг (brain)", variable=self.flags["brain"]
        ).pack(anchor="w", padx=30)

        tk.Label(root, text="Уточнение оболочек:", font=("Arial", 10, "italic")).pack(
            anchor="w", padx=30
        )
        tk.Checkbutton(
            root, text="Верхний сагиттальный синус (SSS)", variable=self.flags["sss"]
        ).pack(anchor="w", padx=40)
        tk.Checkbutton(
            root, text="Поперечный синус", variable=self.flags["transverse_sinus"]
        ).pack(anchor="w", padx=40)

        tk.Label(root, text="Уточнение мозга:", font=("Arial", 10, "italic")).pack(
            anchor="w", padx=30
        )
        tk.Checkbutton(root, text="Кора (cortex)", variable=self.flags["cortex"]).pack(
            anchor="w", padx=40
        )
        tk.Checkbutton(
            root, text="Таламус (thalamus)", variable=self.flags["thalamus"]
        ).pack(anchor="w", padx=40)
        # общий контейнер для строки
        row_frame = tk.Frame(root)
        row_frame.pack(pady=10)

        # ---------- ЛЕВАЯ КОЛОНКА: ПОЛ ----------
        sex_frame = tk.Frame(row_frame)
        sex_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            sex_frame,
            text="Укажите пол",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        sexes = ["male", "female"]

        self.sex = tk.StringVar()
        ttk.Combobox(
            sex_frame,
            textvariable=self.sex,
            values=sexes,
            width=15,
            state="readonly"
        ).pack(pady=5)

        # ---------- ПРАВАЯ КОЛОНКА: ВОЗРАСТ ----------
        age_frame = tk.Frame(row_frame)
        age_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(
            age_frame,
            text="Укажите возраст (в неделях)",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        self.age_weeks = tk.StringVar()
        tk.Entry(
            age_frame,
            textvariable=self.age_weeks,
            width=15
        ).pack(pady=5)

        # Кнопка загрузки
        tk.Button(
            root,
            text="Загрузить в систему",
            command=self.controller.run_etl,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 12, "bold"),
        ).pack(pady=20)

    def choose_file(self):
        s3_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("TIFF files", "*.tif *.tiff"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("All files", "*.*"),
                ("Microscope files", "*nd2*"),
            ],
        )
        if s3_path:
            self.file_path_var.set(s3_path)
    def show_error(self, message: str):
        messagebox.showerror("Ошибка", message)

    def show_success(self, message: str):
        messagebox.showinfo("Успех", message)