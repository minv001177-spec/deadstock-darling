import sqlite3
import os

# Удаляем старую базу
if os.path.exists('instance/vintage.db'):
    os.remove('instance/vintage.db')
    print("🗑️ Старая база удалена")

# Создаем папку instance
os.makedirs('instance', exist_ok=True)

# Подключаемся к базе
conn = sqlite3.connect('instance/vintage.db')
cursor = conn.cursor()

# Создаем таблицы
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
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(user_id, product_id, color, size)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS wishlist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE(user_id, product_id)
)
''')

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

# Только товары с изображениями
products_data = [
    (1, 'Топ в японской тематике', 770, None, 'clothing', 'top_japanese.jpg', 4.8, 45, 1, 0),
    (2, 'Сумка с пальмами-костями', 540, 680, 'bags', 'bag_palms.jpg', 4.9, 28, 1, 15),
    (3, 'Портфель-гитара в красном окрасе', 899, None, 'bags', 'bag_guitar_red.jpg', 4.5, 145, 1, 0),
    (4, 'Сумка в виде зуба', 430, 550, 'bags', 'bag_tooth.jpg', 4.3, 19, 1, 12),
    (5, 'Обувь с большой подошвой и щепами', 600, 750, 'shoes', 'shoes_big_soles.jpg', 4.5, 32, 1, 20),
    (6, 'Куртка-топ с бархатным мехом', 2200, 2800, 'clothing', 'jacket_velvet.jpg', 5.0, 67, 1, 25),
    (7, 'Сумка с принтом зубов', 430, 550, 'bags', 'bag_teeth_print.jpg', 4.3, 19, 1, 12),
    (8, 'Лонгслив белая футболка с крестом', 890, 1200, 'clothing', 'longsleeve_cross.jpg', 4.6, 34, 1, 15),
    (9, 'Кепка Y2K стиле', 670, 890, 'accessories', 'cap_y2k.jpg', 4.8, 88, 1, 30),
    (10, 'Толстовка оверсайз хлопок на зиму', 1689, 2200, 'clothing', 'hoodie_oversize.jpg', 4.9, 55, 1, 20),
    (11, 'Лонгслив с принтом', 760, 990, 'clothing', 'longsleeve_print.jpg', 4.5, 42, 1, 10),
    (12, 'Каблуки бархатные красные', 1250, 1600, 'shoes', 'heels_velvet_red.jpg', 4.7, 28, 1, 15),
    (13, 'Футболка с принтом сигарет', 650, 850, 'clothing', 'tshirt_cigarette.jpg', 4.6, 38, 0, 15),
    (14, 'Лонгслив-оверсайз утепленный', 990, 1350, 'clothing', 'longsleeve_warm.jpg', 4.7, 42, 0, 12),
    (15, 'Футболка с принтом знак Бэтмена', 690, 890, 'clothing', 'tshirt_batman.jpg', 4.8, 56, 0, 18),
    (16, 'Лонгслив-оверсайз с принтом аниме', 850, 1100, 'clothing', 'longsleeve_anime.jpg', 4.9, 67, 0, 14),
    (17, 'Толстовка утепленная с принтом', 1450, 1890, 'clothing', 'hoodie_print.jpg', 4.8, 89, 0, 10),
    (18, 'Лонгслив с принтом "Крик"', 790, 1050, 'clothing', 'longsleeve_scream.jpg', 4.7, 45, 0, 16),
    (19, 'Футболка с принтом аниме', 690, 890, 'clothing', 'tshirt_anime.jpg', 4.8, 78, 0, 22),
    (20, 'Футболка-шутка накидка', 590, 790, 'clothing', 'tshirt_joke.jpg', 4.5, 34, 0, 25),
    (21, 'Футболка с принтом Y2K', 670, 870, 'clothing', 'tshirt_y2k.jpg', 4.7, 56, 0, 20),
    (22, 'Футболка-оверсайз Y2K с шрифтом', 720, 920, 'clothing', 'tshirt_y2k_text.jpg', 4.6, 43, 0, 18),
    (23, 'Рубашка с черным экскизом', 890, 1150, 'clothing', 'shirt_sketch.jpg', 4.7, 32, 0, 12),
    (24, 'Сапоги с красным бархатом и каблуком', 1890, 2450, 'shoes', 'boots_velvet_red.jpg', 4.8, 45, 0, 8),
    (25, 'Кроссовки с подошвой и застёжкой', 1350, 1750, 'shoes', 'sneakers_buckle.jpg', 4.6, 56, 0, 15),
    (26, 'Сапоги на застёжке-ремнях', 1650, 2150, 'shoes', 'boots_straps.jpg', 4.7, 34, 0, 10),
    (27, 'Сапоги на молнии-застёжке', 1450, 1890, 'shoes', 'boots_zipper.jpg', 4.6, 28, 0, 12),
    (28, 'Кроссовки с большой подошвой', 1160, 1500, 'shoes', 'sneakers_thick_soles.jpg', 4.9, 89, 0, 20),
    (29, 'Длинные кеды с шнурками', 890, 1150, 'shoes', 'sneakers_long_laces.jpg', 4.5, 45, 0, 18),
    (30, 'Серые ботинки с большой подошвой', 1250, 1650, 'shoes', 'boots_gray_thick.jpg', 4.7, 56, 0, 14),
    (31, 'Сапоги с липучками и крестиками', 1550, 1990, 'shoes', 'boots_velcro_cross.jpg', 4.8, 34, 0, 9),
    (32, 'Кроссовки с принтом черепов', 1050, 1350, 'shoes', 'sneakers_skull.jpg', 4.6, 67, 0, 16),
    (33, 'Кеды с высокой подошвой и черепами', 990, 1290, 'shoes', 'sneakers_high_skull.jpg', 4.7, 78, 0, 22),
    (34, 'Открытая дышащая обувь Y2K', 890, 1150, 'shoes', 'shoes_mesh_y2k.jpg', 4.5, 34, 0, 15),
    (35, 'Милые ботинки разноцветной подошвой', 1350, 1750, 'shoes', 'boots_colorful.jpg', 4.8, 45, 0, 11),
]

for p in products_data:
    cursor.execute('''
        INSERT INTO products (id, name, price, old_price, category, image_url, rating, reviews, is_new, discount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', p)

print(f"✅ Добавлено {len(products_data)} товаров")

conn.commit()
conn.close()

print("\n" + "="*50)
print("🎉 БАЗА ДАННЫХ ГОТОВА!")
print("="*50)
print("\n📁 Файл: instance/vintage.db")
print("\n🔢 Всего товаров с изображениями:", len(products_data))
print("="*50)