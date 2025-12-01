from minio import Minio
import psycopg2


def load_to_minio(local_path, object_path):
    client = Minio(
        "localhost:9000",
        access_key="microscopy",
        secret_key="microscopy123",
        secure=False,
    )

    bucket = object_path.split("/")[0]
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    client.fput_object(bucket, "/".join(object_path.split("/")[1:]), local_path)


def insert_metadata(conn_string, metadata, object_path):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    sql = """
    INSERT INTO images (mouse_id, experiment_id, s3_path)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(
        sql,
        (
            metadata["mouse_id"],
            metadata["experiment_id"],
            object_path,
            metadata["meninges"],
            metadata["brain"],
            metadata["sss"],
            metadata["transverse_sinus"],
            metadata["cortex"],
            metadata["thalamus"],
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()
