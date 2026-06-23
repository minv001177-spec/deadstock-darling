import os

# Создаем все необходимые папки
folders = [
    'static/images',
    'static/images/products',
    'static/images/banners',
    'static/images/team'
]

print("📁 СОЗДАНИЕ ПАПОК ДЛЯ ИЗОБРАЖЕНИЙ...")
print("="*50)

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"✅ Создана: {folder}")

print("\n" + "="*50)
print("🎉 ВСЕ ПАПКИ СОЗДАНЫ!")
print("\n📁 ТЕПЕРЬ СКОПИРУЙТЕ ВАШИ ИЗОБРАЖЕНИЯ:")
print("")
print("1. ДЛЯ СТРАНИЦЫ 'О НАС':")
print("   - about-banner.jpg → static/images/about-banner.jpg (фото команды справа)")
print("   - vintage-collection.jpg → static/images/vintage-collection.jpg (баннер)")
print("   - dana.jpg → static/images/dana.jpg (фото Даны)")
print("   - zarina.jpg → static/images/zarina.jpg (фото Зарины)")
print("   - timur.jpg → static/images/timur.jpg (фото Тима)")
print("   - victoria.jpg → static/images/victoria.jpg (фото Виктории)")
print("")
print("2. ДЛЯ ТОВАРОВ:")
print("   - Все фото товаров → static/images/ (например top_japanese.jpg, bag_palms.jpg и т.д.)")
print("")
print("3. ДЛЯ БАННЕРОВ НА ГЛАВНОЙ:")
print("   - hero-banner.jpg → static/images/hero-banner.jpg")
print("   - vintage-collection.jpg → static/images/vintage-collection.jpg")
print("   - y2k-collection.jpg → static/images/y2k-collection.jpg")
print("="*50)