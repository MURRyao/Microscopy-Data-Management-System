import uuid
from PIL import Image


def validate_and_prepare(path, experiment_dir):
    # Проверяем формат
    try:
        Image.open(path)
    except:
        raise ValueError("Файл не является корректным изображением.")

    # Генерируем новое имя файла
    ext = path.suffix
    new_name = f"{uuid.uuid4()}{ext}"
    object_path = f"{experiment_dir}/{new_name}"

    return object_path
