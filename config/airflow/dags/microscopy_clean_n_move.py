import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from minio import Minio
from minio.commonconfig import CopySource

logger = logging.getLogger(__name__)


def cleanup_minio():
    pg = PostgresHook(postgres_conn_id='microscopy_postgres')

    # Images with NO structure flags — delete from staging
    no_flags = pg.get_records("""
        SELECT i.s3_path
        FROM images i
        LEFT JOIN structures s ON i.structure_id = s.id
        WHERE meninges = FALSE
          AND brain = FALSE
    """)

    # Images with at least one structure flag — promote to core
    with_flags = pg.get_records("""
        SELECT i.s3_path
        FROM images i
        LEFT JOIN structures s ON i.structure_id = s.id
        WHERE meninges = TRUE
           OR brain = TRUE
    """)

    client = Minio(
        endpoint='minio:9000',
        access_key='microscopy',
        secret_key='microscopy123',
        secure=False,
    )

    bucket_name = 'testbucket'

    # Delete images without any structure flags from staging
    for record in no_flags:
        if not record or not record[0]:
            continue

        s3_path = record[0]

        if "/" not in s3_path:
            logger.warning("Некорректный путь: %s", s3_path)
            continue

        object_path = s3_path.split("/", 1)[1]

        if object_path.startswith('staging/'):
            try:
                client.remove_object(bucket_name, object_path)
            except Exception as e:
                logger.error("Ошибка при удалении %s: %s", object_path, e)

    # Move images with structure flags from staging to core
    for record in with_flags:
        if not record or not record[0]:
            continue

        s3_path = record[0]

        if "/" not in s3_path:
            logger.warning("Некорректный путь: %s", s3_path)
            continue

        object_path = s3_path.split("/", 1)[1]

        if object_path.startswith('staging/'):
            object_name = object_path.replace('staging/', '', 1)
            destination_path = f"core/{object_name}"

            try:
                source = CopySource(
                    bucket_name=bucket_name,
                    object_name=object_path,
                )
                client.copy_object(
                    bucket_name=bucket_name,
                    object_name=destination_path,
                    source=source,
                )
                client.remove_object(bucket_name, object_path)
            except Exception as e:
                logger.error("Ошибка при перемещении %s: %s", object_path, e)


with DAG(
    dag_id="microscopy_cleanup_n_copy",
    start_date=datetime(2026, 2, 5),
    schedule_interval=timedelta(minutes=5),
    catchup=False,
    max_active_runs=1,
    tags=['microscopy', 'minio', 'cleanup'],
) as dag:

    cleanup_task = PythonOperator(
        task_id="cleanup_minio_storage",
        python_callable=cleanup_minio,
    )
