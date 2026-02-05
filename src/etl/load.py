from minio import Minio
import psycopg, os


def load_to_minio(local_path: str):
    client = Minio(
        "localhost:9000",
        access_key="microscopy",
        secret_key="microscopy123",
        secure=False,
    )

    bucket = 'testbucket'
    prefix = 'staging'
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    filename = os.path.basename(local_path)
    object_name = f'{prefix}/{filename}'

    client.fput_object(bucket, object_name, local_path)
    # Возвращаем S3-путь для сохранения в БД
    return f'{bucket}/{object_name}'


def insert_metadata(conn_string, metadata, s3_path: str):
    """
    metadata: словарь с данными мыши и эксперимента
    s3_path: путь к файлу в S3 (например testbucket/staging/file.tiff)
    """
    conn = psycopg.connect(conn_string)
    cursor = conn.cursor()

    # Вставка мыши
    sql_mice = """
    INSERT INTO mice (user_id, genetic_line, sex, age_weeks, device_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
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

    # Вставка эксперимента
    sql_experiments = """
    INSERT INTO experiments (name)
    VALUES (%s)
    RETURNING id
    """
    cursor.execute(sql_experiments, (metadata["name"],))
    experiment_id = cursor.fetchone()[0]

    # Связь мышь-эксперимент
    sql_mice_experiments = """
    INSERT INTO mice_experiments (mouse_id, experiment_id)
    VALUES (%s, %s)
    """
    cursor.execute(sql_mice_experiments, (mouse_id, experiment_id))

    # Структуры
    sql_structures = """
    INSERT INTO structures (mouse_id, meninges, brain)
    VALUES (%s, %s, %s)
    RETURNING id
    """
    cursor.execute(sql_structures, (mouse_id, metadata["meninges"], metadata["brain"]))
    structure_id = cursor.fetchone()[0]

    sql_structures_meninges = """
    INSERT INTO structures_meninges (structures_id, superior_sagittal_sinus, confluence_of_sinuses, transverse_sinus)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        sql_structures_meninges,
        (
            structure_id,
            metadata["superior_sagittal_sinus"],
            metadata["confluence_of_sinuses"],
            metadata["transverse_sinus"],
        ),
    )

    sql_structures_brain = """
    INSERT INTO structures_brain (structures_id, cortex, thalamus, hypothalamus)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        sql_structures_brain,
        (
            structure_id,
            metadata["cortex"],
            metadata["thalamus"],
            metadata["hypothalamus"],
        ),
    )

    # Вставка пути к файлу в S3
    sql_images = """
    INSERT INTO images (mouse_id, experiment_id, structure_id, s3_path)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(
        sql_images, 
        (
            mouse_id, 
            experiment_id,
            structure_id, 
            s3_path,
            )
            )

    conn.commit()
    cursor.close()
    conn.close()