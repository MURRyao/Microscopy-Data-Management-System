import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from extract import extract_image
from transform import validate_and_prepare
from load import load_to_minio, insert_metadata


class ETLGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Microscopy ETL Uploader")
        self.root.geometry("500x550")

        # ----------------------------
        # Выбор файла
        # ----------------------------
        tk.Label(root, text="1. Выберите изображение", font=("Arial", 12, "bold")).pack(
            pady=5
        )

        self.file_path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.file_path_var, width=50).pack(pady=5)

        tk.Button(root, text="Выбрать файл", command=self.choose_file).pack(pady=5)

        # ----------------------------
        # Указание папки (эксперимента)
        # ----------------------------
        tk.Label(
            root, text="2. Название папки (эксперимента)", font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.folder_var = tk.StringVar()
        tk.Entry(root, textvariable=self.folder_var, width=40).pack(pady=5)

        # ----------------------------
        # Галочки структуры
        # ----------------------------
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

        # ----------------------------
        # Кнопка загрузки
        # ----------------------------
        tk.Button(
            root,
            text="Загрузить в систему",
            command=self.run_etl,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(pady=20)

    # ----------------------------------------------------------------------
    def choose_file(self):
        s3_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("TIFF files", "*.tif *.tiff"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("All files", "*.*"),
            ],
        )
        if s3_path:
            self.file_path_var.set(s3_path)

    # ----------------------------------------------------------------------
    def run_etl(self):
        try:
            s3_path = self.file_path_var.get().strip()
            folder = self.folder_var.get().strip()

            if not s3_path:
                messagebox.showerror("Ошибка", "Выберите файл!")
                return

            if not folder:
                messagebox.showerror("Ошибка", "Введите название папки!")
                return

            # Собираем флаги
            metadata = {
                "mouse_id": 1,  # временно статично — можно сделать выбор мыши
                "experiment_id": 1,  # тоже можно сделать выпадающий список
                "meninges": self.flags["meninges"].get(),
                "brain": self.flags["brain"].get(),
                "sss": self.flags["sss"].get(),
                "transverse_sinus": self.flags["transverse_sinus"].get(),
                "cortex": self.flags["cortex"].get(),
                "thalamus": self.flags["thalamus"].get(),
            }

            # ETL
            path = extract_image(s3_path)
            object_path = validate_and_prepare(path, folder)
            load_to_minio(path, object_path)
            # insert_metadata(
            # "dbname=microscopy_db user=microscopy password=microscopy host=localhost",
            # metadata,
            # object_path,
            # )

            messagebox.showinfo("Успех", "Файл и метаданные успешно загружены!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ETLGUI(root)
    root.mainloop()
