from pathlib import Path
from extract import extract_image
from load import load_to_minio, insert_metadata
import tkinter as tk
from tkinter import messagebox


class ETlModel:
    def run_etl(self, s3_path: str, metadata: dict):
        try:
            s3_path = s3_path.strip()

            if not s3_path:
                messagebox.showerror("Ошибка", "Выберите файл!")
                return

            # Extract
            local_path = extract_image(s3_path)  # возвращает локальный путь
            print("DEBUG local_path:", local_path)

            # Load
            s3_object_path = load_to_minio(local_path)
            print("DEBUG s3_object_path:", s3_object_path)

            # Insert metadata в БД
            insert_metadata(
                "dbname=microscopy_db user=microscopy password=microscopy host=localhost",
                metadata,
                s3_object_path,  # путь к файлу в S3
            )

            messagebox.showinfo("Успех", "Файл и метаданные успешно загружены!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))