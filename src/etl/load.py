from minio import Minio
import psycopg


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
    conn = psycopg.connect(conn_string)
    cursor = conn.cursor()

    sql_mice = """
    INSERT INTO mice (user_id, genetic_line, sex, age_weeks, device_id)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(
        sql_mice,
        (
            metadata["user_id"],
            metadata["genetic_line"],
            metadata["sex"],
            metadata["age_weeks"],
            metadata["device_id"],
        ),
    )
    mouse_id = cursor.fetchone()[0]

    sql_experiments = """
    INSERT INTO experiments (name)
    VALUES (%s)
    """
    cursor.execute(sql_experiments, (metadata["name"],))
    experiments_id = cursor.fetchone()[0]

    sql_mice_experiments = """
    INSERT INTO mice_experiments (mouse_id, experiments_id)
    VALUES (%s, %s)
    """
    cursor.execute(
        sql_mice_experiments,
        (
            mouse_id,
            experiments_id,
        ),
    )

    sql_structures = """
    INSERT INTO structures (mouse_id, meninges, brain)
    VALUES (%s, %s, %s)
    """
    cursor.execute(
        sql_structures,
        (
            mouse_id,
            metadata["meninges"],
            metadata["brain"],
        ),
    )

    structures_id = cursor.fetchone()[0]

    sql_structures_meninges = """
    INSERT INTO structures_meninges (structure_id, superior_saggital_sinus, confluense_of_sinuses, transverse_sinus)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        sql_structures_meninges,
        (
            structures_id,
            metadata["superior_saggital_sinus"],
            metadata["confluense_od_sinuses"],
            metadata["transverse_sinus"],
        ),
    )
    structures_meninges_id = cursor.fetchone()[0]

    sql_structures_brain = """
    INSERT INTO structures_brain (structures_id, cortex, thalamus, hypothalamus)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        sql_structures_brain,
        (
            structures_id,
            metadata["cortex"],
            metadata["thalamus"],
            metadata["hypothalamus"],
        ),
    )
    structures_brain_id = cursor.fetchone()[0]

    sql_images = """
    INSERT INTO images (mouse_id, experiment_id, s3_path)
    VALUES (%s,%s,%s)
    """

    cursor.execute(
        sql_images,
        (
            mouse_id,
            metadata["experiment_id"],
            object_path,
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()
