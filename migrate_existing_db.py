import sqlite3

from database.engine import DB_PATH


def column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def migrate():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    if not column_exists(cur, "categories", "description"):
        cur.execute("ALTER TABLE categories ADD COLUMN description TEXT")
        print("✅ Добавлен столбец categories.description")

    if not column_exists(cur, "furniture", "kitchen_type"):
        cur.execute("ALTER TABLE furniture ADD COLUMN kitchen_type VARCHAR(50)")
        print("✅ Добавлен столбец furniture.kitchen_type")


    cur.execute("SELECT DISTINCT category_name FROM furniture")
    existing_furniture_categories = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT name FROM categories")
    existing_categories = {row[0] for row in cur.fetchall()}

    added = 0
    for name in existing_furniture_categories:
        if name not in existing_categories:
            cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            added += 1

    if added:
        print(f"✅ Добавлено категорий в таблицу categories: {added}")

    cur.execute(
    "SELECT id, description FROM furniture "
    "WHERE category_name LIKE '%ухон%' AND (kitchen_type IS NULL OR kitchen_type = '')"
    )
    kitchen_rows = cur.fetchall()
    backfilled = 0
    for row_id, description in kitchen_rows:
        lowered = (description or "").lower()
        if "угловая" in lowered or "угловой" in lowered:
            kitchen_type = "Угловая кухня"
        else:
            kitchen_type = "Прямая кухня"
        cur.execute("UPDATE furniture SET kitchen_type = ? WHERE id = ?", (kitchen_type, row_id))
        backfilled += 1

    if backfilled:
        print(f"✅ Заполнено поле kitchen_type для {backfilled} уже существующих товаров категории «Кухонная мебель»")
        print("   Проверьте вручную, что тип кухни определился верно (по ключевым словам 'угловая'/'прямая' в описании).")

    con.commit()
    con.close()
    print("🎉 Миграция завершена.")


if __name__ == "__main__":
    migrate()