from pathlib import Path
from extract import extract_image
from transform import validate_and_prepare
from load import load_to_minio, insert_metadata
import tkinter as tk
from tkinter import messagebox


class ETlModel:
    def run_etl(self, s3_path: str, folder: str, metadata: dict):
        try:
            s3_path = s3_path.strip()
            folder = folder.strip()

            if not s3_path:
                messagebox.showerror("Ошибка", "Выберите файл!")
                return

            if not folder:
                messagebox.showerror("Ошибка", "Введите название папки!")
                return

            # ETL
            path = extract_image(s3_path)
            object_path = validate_and_prepare(path, folder)
            load_to_minio(path, object_path)
            insert_metadata(
                "dbname=microscopy_db user=microscopy password=microscopy host=localhost",
                metadata,
                object_path,
            )

            messagebox.showinfo("Успех", "Файл и метаданные успешно загружены!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
