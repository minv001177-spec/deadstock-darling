import sqlite3
from collections import defaultdict

# Подключаемся к базе данных
conn = sqlite3.connect('instance/vintage.db')
cursor = conn.cursor()

# Получаем все записи из корзины
cursor.execute('SELECT id, user_id, product_id, color, size, quantity FROM cart_items ORDER BY user_id, product_id, color, size, id')
rows = cursor.fetchall()

# Группируем по user_id, product_id, color, size
groups = defaultdict(list)
for row in rows:
    key = (row[1], row[2], row[3], row[4])  # user_id, product_id, color, size
    groups[key].append(row)

# Обрабатываем каждую группу
deleted_count = 0
updated_count = 0
for key, items in groups.items():
    if len(items) > 1:
        # Суммируем количество
        total_quantity = sum(item[5] for item in items)
        # Оставляем первый (с наименьшим ID)
        first_id = items[0][0]
        # Обновляем количество в первом
        cursor.execute('UPDATE cart_items SET quantity = ? WHERE id = ?', (total_quantity, first_id))
        updated_count += 1
        # Удаляем остальные
        for item in items[1:]:
            cursor.execute('DELETE FROM cart_items WHERE id = ?', (item[0],))
            deleted_count += 1
            print(f"🗑️ Удален дубликат ID: {item[0]}")

conn.commit()
conn.close()

print(f"\n✅ Обновлено записей: {updated_count}")
print(f"✅ Удалено дубликатов: {deleted_count}")
print("🎉 Корзина очищена от дубликатов!")