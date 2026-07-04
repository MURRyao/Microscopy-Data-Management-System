import psycopg
import os

DB_HOST = "localhost"
DB_NAME = "microscopy_db"
DB_USER = "microscopy"
DB_PASSWORD = "microscopy"
DB_PORT = 5432

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "config", "postgres_init.sql"))

with open(SQL_FILE, "r") as f:
    raw_sql = f.read()

# Filter out psql metacommands (\c) and CREATE DATABASE — those are handled separately.
schema_lines = [
    line for line in raw_sql.splitlines()
    if not line.strip().startswith("\\")
    and not line.strip().upper().startswith("CREATE DATABASE")
]
schema_sql = "\n".join(schema_lines)

# Step 1: Create the database.
# CREATE DATABASE is DDL that cannot run inside a transaction, so autocommit is required.
with psycopg.connect(
    host=DB_HOST,
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
    autocommit=True,
) as conn:
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE {DB_NAME}")

# Step 2: Apply the schema to the new database.
with psycopg.connect(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=DB_PORT,
) as conn:
    with conn.cursor() as cur:
        cur.execute(schema_sql)
