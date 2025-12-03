import tkinter as tk
from tkinter import filedialog


class ETLView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Microscopy ETL Uploader")
        self.root.geometry("500x550")

        # Выбор файла
        tk.Label(root, text="1. Выберите изображение", font=("Arial", 12, "bold")).pack(
            pady=5
        )

        self.file_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.file_path_var, width=50).pack(pady=5)

        tk.Button(root, text="Выбрать файл", command=self.controller.choose_file).pack(
            pady=5
        )

        # Указание папки (эксперимента)
        tk.Label(
            root, text="2. Название папки (эксперимента)", font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.folder_var = tk.StringVar()
        tk.Entry(root, textvariable=self.folder_var, width=40).pack(pady=5)

        tk.Label(
            root, text="Введите название эксперимента", font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.name_var = tk.StringVar()
        tk.Entry(root, textvariable=self.name_var, width=40).pack(pady=5)

        # Галочки структуры
        tk.Label(root, text="3. Отметьте структуры", font=("Arial", 12, "bold")).pack(
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

        # Кнопка загрузки
        tk.Button(
            root,
            text="Загрузить в систему",
            command=self.controller.run_etl,
            bg="#4CAF50",
            fg="white",
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
