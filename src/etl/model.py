import logging
from extract import extract_image
from load import load_to_minio, insert_metadata, remove_from_minio

logger = logging.getLogger(__name__)

_CONN_STRING = "dbname=microscopy_db user=microscopy password=microscopy host=localhost"


class ETLModel:
    def run_etl(self, s3_path: str, metadata: dict) -> None:
        s3_path = s3_path.strip()
        if not s3_path:
            raise ValueError("Выберите файл!")

        local_path = extract_image(s3_path)
        logger.debug("local_path: %s", local_path)

        s3_object_path = load_to_minio(local_path)
        logger.debug("s3_object_path: %s", s3_object_path)

        try:
            insert_metadata(_CONN_STRING, metadata, s3_object_path)
        except Exception:
            # DB insert failed — remove the already-uploaded file to avoid orphaned objects
            remove_from_minio(s3_object_path)
            raise
