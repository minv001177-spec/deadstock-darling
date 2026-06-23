from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vintage-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vintage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

# Создаем папки для изображений при запуске
def create_image_folders():
    folders = [
        'static/images',
        'static/images/products',
        'static/images/products/clothing',
        'static/images/products/shoes',
        'static/images/products/bags',
        'static/images/products/accessories',
        'static/images/banners',
        'static/images/team'
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

create_image_folders()


# ========== МОДЕЛИ БАЗЫ ДАННЫХ ==========

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    old_price = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    rating = db.Column(db.Float, default=5.0)
    reviews = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    is_new = db.Column(db.Boolean, default=False)
    discount = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy=True)
    
    def get_image_url(self):
        if self.image_url:
            return url_for('static', filename=f'images/{self.image_url}')
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'old_price': self.old_price,
            'category': self.category,
            'rating': self.rating,
            'reviews': self.reviews,
            'is_new': self.is_new,
            'discount': self.discount,
            'image_url': self.get_image_url(),
            'description': self.description or 'Стильная вещь из новой коллекции. Отличное качество и уникальный дизайн.'
        }


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    color = db.Column(db.String(50), default='Черный')
    size = db.Column(db.String(10), default='M')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', 'color', 'size', name='unique_cart_item'),)


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_wishlist_item'),)


class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    card_holder = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.String(5), nullable=False)
    card_type = db.Column(db.String(20), default='visa')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ========== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ==========

with app.app_context():
    db.create_all()
    
    if Product.query.count() == 0:
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
            product = Product(
                id=p[0], name=p[1], price=p[2], old_price=p[3], category=p[4],
                image_url=p[5], rating=p[6], reviews=p[7], is_new=p[8], discount=p[9]
            )
            db.session.add(product)
        db.session.commit()
        print(f"✅ Добавлено {len(products_data)} товаров в базу данных")


# ========== МАРШРУТ ДЛЯ ИКОНКИ (FAVICON) ==========

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/favicon.png')
def favicon_png():
    return send_from_directory('static', 'favicon.png', mimetype='image/png')


# ========== МАРШРУТЫ ==========

@app.route('/')
def index():
    new_products = Product.query.filter_by(is_new=True).limit(8).all()
    sale_products = Product.query.filter(Product.discount > 0).limit(8).all()
    all_products = Product.query.limit(12).all()
    return render_template('index.html', 
                         new_products=new_products, 
                         sale_products=sale_products, 
                         all_products=all_products)


@app.route('/new_collection')
def new_collection():
    new_products = Product.query.filter_by(is_new=True).all()
    return render_template('new_collection.html', new_products=new_products)


@app.route('/category/<category_name>')
def category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template('category.html', products=products, category=category_name)


@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter(
        Product.category == product.category, 
        Product.id != id
    ).limit(4).all()
    return render_template('product.html', product=product, related=related)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/privacy')
@login_required
def privacy():
    return render_template('privacy.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже существует', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Регистрация успешна! Теперь войдите', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.update_last_login()
            flash(f'Добро пожаловать, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверный email или пароль', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.address = request.form.get('address')
        current_user.phone = request.form.get('phone')
        
        new_password = request.form.get('new_password')
        if new_password and len(new_password) >= 6:
            current_user.set_password(new_password)
            flash('Пароль обновлен', 'success')
        
        db.session.commit()
        flash('Профиль обновлен', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')


@app.route('/card')
@login_required
def card():
    return render_template('card.html')


@app.route('/cards_list')
@login_required
def cards_list():
    cards = Card.query.filter_by(user_id=current_user.id).all()
    return render_template('cards_list.html', cards=cards)


@app.route('/add_card', methods=['POST'])
@login_required
def add_card():
    card_number = request.form.get('card_number')
    card_holder = request.form.get('card_holder')
    expiry_date = request.form.get('expiry_date')
    card_type = request.form.get('card_type')
    
    if not card_number or not card_holder or not expiry_date:
        flash('Заполните все поля', 'error')
        return redirect(url_for('card'))
    
    existing_cards = Card.query.filter_by(user_id=current_user.id).count()
    is_default = existing_cards == 0
    
    card = Card(
        user_id=current_user.id,
        card_number=card_number.replace(' ', ''),
        card_holder=card_holder.upper(),
        expiry_date=expiry_date,
        card_type=card_type,
        is_default=is_default
    )
    db.session.add(card)
    db.session.commit()
    
    flash('Карта успешно привязана!', 'success')
    return redirect(url_for('cards_list'))


@app.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.user_id == current_user.id:
        db.session.delete(card)
        db.session.commit()
        flash('Карта удалена', 'success')
    return redirect(url_for('cards_list'))


@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')


@app.route('/cart-data')
@login_required
def cart_data():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    items = []
    total = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            item_total = product.price * item.quantity
            total += item_total
            items.append({
                'id': item.id,
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': item.quantity,
                'color': item.color,
                'size': item.size,
                'total': item_total,
                'image_url': url_for('static', filename=f'images/{product.image_url}') if product.image_url else None
            })
    return jsonify({
        'items': items,
        'total': total,
        'cart_count': len(items)
    })


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных'}), 400
            
        color = data.get('color', 'Черный')
        size = data.get('size', 'M')
        
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id,
            color=color,
            size=size
        ).first()
        
        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = CartItem(
                user_id=current_user.id, 
                product_id=product_id,
                color=color,
                size=size,
                quantity=1
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'success': True, 'cart_count': cart_count})
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении в корзину: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get(item_id)
    
    if not cart_item:
        return jsonify({'success': False, 'error': 'Товар не найден в корзине'}), 404
    
    if cart_item.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Нет прав для удаления'}), 403
    
    db.session.delete(cart_item)
    db.session.commit()
    
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'success': True, 'cart_count': cart_count})


@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')
    
    if not item_id or not quantity:
        return jsonify({'success': False})
    
    item = CartItem.query.get(item_id)
    if item and item.user_id == current_user.id and quantity > 0:
        item.quantity = quantity
        db.session.commit()
        product = Product.query.get(item.product_id)
        if product:
            return jsonify({'success': True, 'total': product.price * quantity})
    
    return jsonify({'success': False})


@app.route('/remove_selected_from_cart', methods=['POST'])
@login_required
def remove_selected_from_cart():
    data = request.get_json()
    item_ids = data.get('item_ids', [])
    
    if not item_ids:
        return jsonify({'success': False, 'error': 'Нет товаров для удаления'})
    
    try:
        for item_id in item_ids:
            cart_item = CartItem.query.get(item_id)
            if cart_item and cart_item.user_id == current_user.id:
                db.session.delete(cart_item)
        db.session.commit()
        
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'success': True, 'cart_count': cart_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cart/items')
@login_required
def api_cart_items():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            items.append({
                'id': item.id,
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': item.quantity,
                'color': item.color,
                'size': item.size,
                'total': product.price * item.quantity,
                'image_url': url_for('static', filename=f'images/{product.image_url}') if product.image_url else None
            })
    return jsonify(items)


@app.route('/api/cart/count')
@login_required
def api_cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})


@app.route('/api/clear_duplicates')
@login_required
def api_clear_duplicates():
    try:
        from sqlalchemy import func
        
        subquery = db.session.query(
            CartItem.user_id,
            CartItem.product_id,
            CartItem.color,
            CartItem.size,
            func.min(CartItem.id).label('min_id'),
            func.sum(CartItem.quantity).label('total_quantity')
        ).filter(
            CartItem.user_id == current_user.id
        ).group_by(
            CartItem.user_id,
            CartItem.product_id,
            CartItem.color,
            CartItem.size
        ).having(
            func.count() > 1
        ).subquery()
        
        duplicates = db.session.query(CartItem).join(
            subquery,
            (CartItem.user_id == subquery.c.user_id) &
            (CartItem.product_id == subquery.c.product_id) &
            (CartItem.color == subquery.c.color) &
            (CartItem.size == subquery.c.size) &
            (CartItem.id != subquery.c.min_id)
        ).all()
        
        deleted_count = 0
        for dup in duplicates:
            db.session.delete(dup)
            deleted_count += 1
        
        main_items = db.session.query(
            CartItem,
            subquery.c.total_quantity
        ).join(
            subquery,
            (CartItem.user_id == subquery.c.user_id) &
            (CartItem.product_id == subquery.c.product_id) &
            (CartItem.color == subquery.c.color) &
            (CartItem.size == subquery.c.size) &
            (CartItem.id == subquery.c.min_id)
        ).all()
        
        for item, total_qty in main_items:
            item.quantity = total_qty
        
        db.session.commit()
        
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return jsonify({'success': True, 'cart_count': cart_count, 'deleted': deleted_count})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ========== МАРШРУТЫ ИЗБРАННОГО ==========

@app.route('/wishlist')
@login_required
def wishlist():
    return render_template('wishlist.html')


@app.route('/wishlist-data')
@login_required
def wishlist_data():
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    items = []
    for item in wishlist_items:
        product = Product.query.get(item.product_id)
        if product:
            items.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'reviews': product.reviews,
                'rating': product.rating,
                'image_url': url_for('static', filename=f'images/{product.image_url}') if product.image_url else None
            })
    return jsonify({'items': items})


@app.route('/api/wishlist/check/<int:product_id>')
@login_required
def api_wishlist_check(product_id):
    try:
        exists = WishlistItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first() is not None
        return jsonify({'in_wishlist': exists})
    except Exception as e:
        print(f"Ошибка при проверке избранного: {e}")
        return jsonify({'in_wishlist': False})


@app.route('/add_to_wishlist/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    try:
        existing = WishlistItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Товар уже в избранном'})
        
        wishlist_item = WishlistItem(
            user_id=current_user.id, 
            product_id=product_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Товар добавлен в избранное'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении в избранное: {e}")
        return jsonify({'success': False, 'message': 'Ошибка при добавлении в избранное'})


@app.route('/remove_from_wishlist/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    try:
        wishlist_item = WishlistItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if not wishlist_item:
            return jsonify({'success': False, 'error': 'Товар не найден в избранном'})
        
        db.session.delete(wishlist_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Товар удален из избранного'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при удалении из избранного: {e}")
        return jsonify({'success': False, 'error': 'Ошибка при удалении из избранного'})


@app.route('/checkout')
@login_required
def checkout():
    ids_param = request.args.get('ids', '')
    quantities_param = request.args.get('quantities', '')
    
    selected_items = []
    if ids_param and quantities_param:
        ids = [int(x) for x in ids_param.split(',')]
        quantities = [int(x) for x in quantities_param.split(',')]
        
        for i, item_id in enumerate(ids):
            cart_item = CartItem.query.get(item_id)
            if cart_item and cart_item.user_id == current_user.id:
                product = Product.query.get(cart_item.product_id)
                if product:
                    selected_items.append({
                        'cart_item_id': cart_item.id,
                        'product': product,
                        'quantity': quantities[i] if i < len(quantities) else cart_item.quantity,
                        'color': cart_item.color,
                        'size': cart_item.size
                    })
    
    cards = Card.query.filter_by(user_id=current_user.id).all()
    return render_template('checkout.html', selected_items=selected_items, cards=cards)


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    exact_product = Product.query.filter(Product.name == query).first()
    if exact_product:
        return redirect(url_for('product_detail', id=exact_product.id))
    
    category_map = {
        'куртки': 'clothing',
        'одежда': 'clothing',
        'обувь': 'shoes',
        'аксессуары': 'accessories',
        'сумки': 'bags',
        'рюкзаки': 'bags'
    }
    
    query_lower = query.lower()
    if query_lower in category_map:
        return redirect(url_for('category', category_name=category_map[query_lower]))
    
    products = Product.query.filter(Product.name.contains(query)).all()
    
    if len(products) == 1:
        return redirect(url_for('product_detail', id=products[0].id))
    
    return render_template('search_results.html', products=products, query=query)


@app.route('/api/products')
def api_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


@app.route('/api/products/<int:id>')
def api_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product.to_dict())


# ========== ОБРАБОТЧИКИ ОШИБОК ==========

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)