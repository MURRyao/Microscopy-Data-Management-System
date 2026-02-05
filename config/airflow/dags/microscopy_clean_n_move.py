from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
from datetime import datetime, timedelta
from minio import Minio
from minio.commonconfig import CopySource

def cleanup_minio():
    pg = PostgresHook(postgres_conn_id='microscopy_postgres')

    no_flags = pg.get_records("""
        SELECT i.s3_path
        FROM images i
        LEFT JOIN structures s
        ON i.structure_id = s.id
        WHERE meninges = FALSE
            OR brain = FALSE
    """)

    with_flags = pg.get_records("""
        SELECT i.s3_path
        FROM images i
        LEFT JOIN structures s
        ON i.structure_id = s.id
        WHERE meninges = TRUE
            OR brain = TRUE
    """)

    client = Minio(
        endpoint='minio:9000',
        access_key='microscopy',
        secret_key='microscopy123',
        secure=False,
    )
    
    # Bucket всегда 'testbucket'
    bucket_name = 'testbucket'
    
    # Обрабатываем записи без флагов - УДАЛЯЕМ из staging
    for record in no_flags:
        if not record or not record[0]:
            continue
            
        s3_path = record[0]  # Получаем строку из кортежа
        
        # Проверяем, что путь содержит bucket и префикс
        if "/" not in s3_path:
            print(f"Некорректный путь: {s3_path}")
            continue
            
        # Извлекаем путь внутри bucket (без имени bucket)
        object_path = s3_path.split("/", 1)[1] if "/" in s3_path else s3_path
        
        # Удаляем из staging
        if object_path.startswith('staging/'):
            print(f"Удаление: {bucket_name}/{object_path}")
            try:
                client.remove_object(bucket_name, object_path)
                print(f"✓ Успешно удалено: {bucket_name}/{object_path}")
            except Exception as e:
                print(f"✗ Ошибка при удалении: {e}")

    # Обрабатываем записи с флагами - ПЕРЕМЕЩАЕМ из staging в core
    for record in with_flags:
        if not record or not record[0]:
            continue
            
        s3_path = record[0]
        
        if "/" not in s3_path:
            print(f"Некорректный путь: {s3_path}")
            continue
            
        # Извлекаем путь внутри bucket (без имени bucket)
        object_path = s3_path.split("/", 1)[1] if "/" in s3_path else s3_path
        
        # Проверяем, что объект в staging
        if object_path.startswith('staging/'):
            # Создаем новый путь в core
            # Убираем 'staging/' из начала
            object_name = object_path.replace('staging/', '', 1)
            destination_path = f"core/{object_name}"
            
            print(f"\nПеремещение: {object_path} -> {destination_path}")
            
            try:
                # Правильный способ копирования
                source = CopySource(
                    bucket_name=bucket_name,
                    object_name=object_path
                )
                
                # Копируем из staging в core
                client.copy_object(
                    bucket_name=bucket_name,
                    object_name=destination_path,
                    source=source
                )
                print(f"✓ Скопировано: {object_path} -> {destination_path}")
                
                # Удаляем оригинал из staging
                client.remove_object(bucket_name, object_path)
                print(f"✓ Оригинал удален: {object_path}")
                
            except Exception as e:
                print(f"✗ Ошибка при перемещении: {e}")

with DAG(
    dag_id = "microscopy_cleanup_n_copy",
    start_date = datetime(2026, 2, 5),
    schedule_interval = timedelta(minutes = 5),
    catchup = False,
    max_active_runs = 1,
    tags = ['microscopy', 'minio', 'cleanup'],
) as dag:

    cleanup_task = PythonOperator(
        task_id = "cleanup_minio_storage",
        python_callable = cleanup_minio,
    )