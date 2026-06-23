import sqlite3
import os

# Путь к базе данных
DB_PATH = 'instance/vintage.db'

# Создаем папку instance, если её нет
os.makedirs('instance', exist_ok=True)

# Удаляем старую базу, если есть
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("🗑️ Старая база удалена")

# Подключаемся к базе
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ========== СОЗДАНИЕ ТАБЛИЦ ==========

# Таблица пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# Таблица товаров
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    old_price INTEGER,
    category TEXT NOT NULL,
    image_url TEXT,
    rating REAL DEFAULT 5.0,
    reviews INTEGER DEFAULT 0,
    description TEXT,
    is_new INTEGER DEFAULT 0,
    discount INTEGER DEFAULT 0,
    stock INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Таблица карт пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    card_number TEXT NOT NULL,
    card_holder TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    card_type TEXT DEFAULT 'visa',
    is_default INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Таблица корзины (с цветом и размером)
cursor.execute('''
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    color TEXT DEFAULT 'Черный',
    size TEXT DEFAULT 'M',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# Таблица избранного
cursor.execute('''
CREATE TABLE IF NOT EXISTS wishlist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# Таблица заказов
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_number TEXT UNIQUE NOT NULL,
    total_amount INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    delivery_address TEXT NOT NULL,
    delivery_method TEXT DEFAULT 'courier',
    payment_method TEXT DEFAULT 'card',
    card_last4 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

# Таблица товаров в заказе
cursor.execute('''
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    product_price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    color TEXT,
    size TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

print("✅ Таблицы созданы")

# ========== ДОБАВЛЕНИЕ ТОВАРОВ ==========

products_data = [
    ('Топ в японской тематике', 770, None, 'clothing', 4.8, 45, 1, 0),
    ('Сумка с пальмами-костями', 540, 680, 'bags', 4.9, 28, 1, 15),
    ('Портфель-гитара в красном окрасе', 899, None, 'bags', 4.5, 145, 1, 0),
    ('Сумка в виде зуба', 430, 550, 'bags', 4.3, 19, 1, 12),
    ('Обувь с большой подошвой и щепами', 600, 750, 'shoes', 4.5, 32, 1, 20),
    ('Куртка-топ с бархатным мехом', 2200, 2800, 'clothing', 5.0, 67, 1, 25),
    ('Сумка с принтом зубов', 430, 550, 'bags', 4.3, 19, 1, 12),
    ('Лонгслив белая футболка с крестом', 890, 1200, 'clothing', 4.6, 34, 1, 15),
    ('Кепка Y2K стиле', 670, 890, 'accessories', 4.8, 88, 1, 30),
    ('Толстовка оверсайз хлопок на зиму', 1689, 2200, 'clothing', 4.9, 55, 1, 20),
    ('Лонгслив с принтом', 760, 990, 'clothing', 4.5, 42, 1, 10),
    ('Каблуки бархатные красные', 1250, 1600, 'shoes', 4.7, 28, 1, 15),
    ('Футболка с принтом сигарет', 650, 850, 'clothing', 4.6, 38, 0, 15),
    ('Лонгслив-оверсайз утепленный', 990, 1350, 'clothing', 4.7, 42, 0, 12),
    ('Футболка с принтом знак Бэтмена', 690, 890, 'clothing', 4.8, 56, 0, 18),
    ('Лонгслив-оверсайз с принтом аниме', 850, 1100, 'clothing', 4.9, 67, 0, 14),
    ('Толстовка утепленная с принтом', 1450, 1890, 'clothing', 4.8, 89, 0, 10),
    ('Лонгслив с принтом "Крик"', 790, 1050, 'clothing', 4.7, 45, 0, 16),
    ('Футболка с принтом аниме', 690, 890, 'clothing', 4.8, 78, 0, 22),
    ('Футболка-шутка накидка', 590, 790, 'clothing', 4.5, 34, 0, 25),
    ('Футболка с принтом Y2K', 670, 870, 'clothing', 4.7, 56, 0, 20),
    ('Футболка-оверсайз Y2K с шрифтом', 720, 920, 'clothing', 4.6, 43, 0, 18),
    ('Рубашка с черным экскизом', 890, 1150, 'clothing', 4.7, 32, 0, 12),
    ('Сапоги с красным бархатом и каблуком', 1890, 2450, 'shoes', 4.8, 45, 0, 8),
    ('Кроссовки с подошвой и застёжкой', 1350, 1750, 'shoes', 4.6, 56, 0, 15),
    ('Сапоги на застёжке-ремнях', 1650, 2150, 'shoes', 4.7, 34, 0, 10),
    ('Сапоги на молнии-застёжке', 1450, 1890, 'shoes', 4.6, 28, 0, 12),
    ('Кроссовки с большой подошвой', 1160, 1500, 'shoes', 4.9, 89, 0, 20),
    ('Длинные кеды с шнурками', 890, 1150, 'shoes', 4.5, 45, 0, 18),
    ('Серые ботинки с большой подошвой', 1250, 1650, 'shoes', 4.7, 56, 0, 14),
    ('Сапоги с липучками и крестиками', 1550, 1990, 'shoes', 4.8, 34, 0, 9),
    ('Кроссовки с принтом черепов', 1050, 1350, 'shoes', 4.6, 67, 0, 16),
    ('Кеды с высокой подошвой и черепами', 990, 1290, 'shoes', 4.7, 78, 0, 22),
    ('Открытая дышащая обувь Y2K', 890, 1150, 'shoes', 4.5, 34, 0, 15),
    ('Милые ботинки разноцветной подошвой', 1350, 1750, 'shoes', 4.8, 45, 0, 11),
]

for p in products_data:
    cursor.execute('''
        INSERT INTO products (name, price, old_price, category, rating, reviews, is_new, discount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', p)

print(f"✅ Добавлено {len(products_data)} товаров")

# Сохраняем и закрываем
conn.commit()
conn.close()

print("\n" + "="*50)
print("🎉 БАЗА ДАННЫХ ГОТОВА!")
print("="*50)
print("\n📁 Файл: instance/vintage.db")
print("\n📊 Таблицы в базе:")
print("   - users (пользователи)")
print("   - products (товары)")
print("   - cards (карты)")
print("   - cart_items (корзина) - с колонками color и size")
print("   - wishlist_items (избранное)")
print("   - orders (заказы)")
print("   - order_items (товары в заказе)")
print("\n🔢 Всего товаров:", len(products_data))
print("="*50)