from pathlib import Path
from minio import Minio
import psycopg
import logging

logger = logging.getLogger(__name__)

_MINIO_ENDPOINT = "localhost:9000"
_MINIO_ACCESS_KEY = "microscopy"
_MINIO_SECRET_KEY = "microscopy123"
_BUCKET = "testbucket"
_PREFIX = "staging"


def _minio_client() -> Minio:
    return Minio(
        _MINIO_ENDPOINT,
        access_key=_MINIO_ACCESS_KEY,
        secret_key=_MINIO_SECRET_KEY,
        secure=False,
    )


def load_to_minio(local_path) -> str:
    client = _minio_client()
    if not client.bucket_exists(_BUCKET):
        client.make_bucket(_BUCKET)
    filename = Path(local_path).name
    object_name = f"{_PREFIX}/{filename}"
    client.fput_object(_BUCKET, object_name, str(local_path))
    return f"{_BUCKET}/{object_name}"


def remove_from_minio(s3_path: str) -> None:
    """Remove an object from MinIO given its s3_path (bucket/object_name).
    Called to clean up an orphaned file when the DB insert fails after a successful upload.
    """
    parts = s3_path.split("/", 1)
    if len(parts) != 2:
        logger.warning("Cannot parse s3_path for cleanup: %s", s3_path)
        return
    bucket, object_name = parts
    try:
        _minio_client().remove_object(bucket, object_name)
        logger.info("Cleaned up orphaned MinIO object: %s", s3_path)
    except Exception as exc:
        logger.error("Failed to remove MinIO object %s: %s", s3_path, exc)


def insert_metadata(conn_string: str, metadata: dict, s3_path: str) -> None:
    """
    metadata: словарь с данными мыши и эксперимента
    s3_path: путь к файлу в S3 (например testbucket/staging/file.tiff)
    """
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cursor:

            # Lookup or insert mouse — avoid duplicates for the same subject
            cursor.execute(
                """
                SELECT id FROM mice
                WHERE user_id=%s AND genetic_line=%s AND sex=%s
                  AND age_weeks=%s AND device_id=%s
                """,
                (
                    metadata["user_id"],
                    metadata["genetic_line"],
                    metadata["sex"],
                    metadata["age_weeks"],
                    metadata["device_id"],
                ),
            )
            row = cursor.fetchone()
            if row:
                mouse_id = row[0]
            else:
                cursor.execute(
                    """
                    INSERT INTO mice (user_id, genetic_line, sex, age_weeks, device_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        metadata["user_id"],
                        metadata["genetic_line"],
                        metadata["sex"],
                        metadata["age_weeks"],
                        metadata["device_id"],
                    ),
                )
                mouse_id = cursor.fetchone()[0]

            # Lookup or insert experiment by name — avoid creating duplicates
            cursor.execute(
                "SELECT id FROM experiments WHERE name=%s",
                (metadata["name"],),
            )
            row = cursor.fetchone()
            if row:
                experiment_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO experiments (name) VALUES (%s) RETURNING id",
                    (metadata["name"],),
                )
                experiment_id = cursor.fetchone()[0]

            # Link mouse ↔ experiment; ignore if the association already exists
            cursor.execute(
                """
                INSERT INTO mice_experiments (mouse_id, experiment_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (mouse_id, experiment_id),
            )

            # Structures record — always new per image upload
            cursor.execute(
                """
                INSERT INTO structures (mouse_id, meninges, brain)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (mouse_id, metadata["meninges"], metadata["brain"]),
            )
            structure_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO structures_meninges
                    (structures_id, superior_sagittal_sinus, confluence_of_sinuses, transverse_sinus)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    structure_id,
                    metadata["superior_sagittal_sinus"],
                    metadata["confluence_of_sinuses"],
                    metadata["transverse_sinus"],
                ),
            )

            cursor.execute(
                """
                INSERT INTO structures_brain (structures_id, cortex, thalamus, hypothalamus)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    structure_id,
                    metadata["cortex"],
                    metadata["thalamus"],
                    metadata["hypothalamus"],
                ),
            )

            cursor.execute(
                """
                INSERT INTO images (mouse_id, experiment_id, structure_id, s3_path)
                VALUES (%s, %s, %s, %s)
                """,
                (mouse_id, experiment_id, structure_id, s3_path),
            )
