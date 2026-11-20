
import sqlite3
from app import get_postgres_db

# Read existing tasks from SQLite
sqlite_conn = sqlite3.connect("tasks.db")
sqlite_conn.row_factory = sqlite3.Row

tasks = sqlite_conn.execute(
    "SELECT id, name, done, priority FROM tasks"
).fetchall()

sqlite_conn.close()

print(f"Found {len(tasks)} tasks in SQLite.")

# Connect to PostgreSQL
pg_conn = get_postgres_db()

try:
    with pg_conn.cursor() as cur:
        for task in tasks:
            cur.execute(
                """
                INSERT INTO tasks (id, name, done, priority)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    task["id"],
                    task["name"],
                    bool(task["done"]),
                    task["priority"],
                ),
            )

    pg_conn.commit()
    print("Migration completed successfully!")

except Exception:
    pg_conn.rollback()
    raise

finally:
    pg_conn.close()
