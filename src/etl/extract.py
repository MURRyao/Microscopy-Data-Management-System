from pathlib import Path


def extract_image(s3_path: str):
    allowed = [".nd2", ".tiff"]
    path = Path(s3_path)
    if not path.exists() and path.suffix.lower() not in allowed:
        raise FileNotFoundError("Указанный файл не найден.")
    return path
