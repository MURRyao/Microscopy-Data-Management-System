import psycopg
import os
from psycopg import sql

# Параметры подключения
DB_HOST = "localhost"        
DB_NAME = "microscopy_db"
DB_USER = "microscopy"
DB_PASSWORD = "microscopy"
DB_PORT = 5432              


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /src/init
SQL_FILE = os.path.join(BASE_DIR, "..", "..", "config", "postgres_init.sql")
SQL_FILE = os.path.abspath(SQL_FILE)  

# Читаем SQL файл
with open(SQL_FILE, "r") as f:
    sql = f.read()

# Подключение к Postgres
conn = psycopg.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT
)

try:
    with conn:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
            cur.execute(sql.SQL(sql))  # исполняем весь файл
            cur.execute("COMMIT;")
finally:
    conn.close()
