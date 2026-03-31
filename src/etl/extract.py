from pathlib import Path


def extract_image(s3_path: str):
    allowed = [".nd2", ".tif", ".tiff"]
    path = Path(s3_path)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    if path.suffix.lower() not in allowed:
        raise ValueError(f"Неподдерживаемый формат '{path.suffix}'. Допустимые: {', '.join(allowed)}")
    return path
