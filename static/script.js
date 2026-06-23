document.addEventListener('DOMContentLoaded', function() {
    // ========== СМЕНА ТЕМЫ (СВЕТЛАЯ/ТЕМНАЯ) ==========
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const body = document.body;
    
    // Функция для применения темы
    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-theme');
            body.classList.remove('light-theme');
            localStorage.setItem('theme', 'dark');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i><span class="theme-text">Темная</span>';
            }
        } else {
            body.classList.add('light-theme');
            body.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i><span class="theme-text">Светлая</span>';
            }
        }
    }
    
    // Загрузка сохраненной темы
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        // Проверяем системные настройки
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark ? 'dark' : 'light');
    }
    
    // Обработчик кнопки переключения темы
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function() {
            const isDark = body.classList.contains('dark-theme');
            setTheme(isDark ? 'light' : 'dark');
            
            // Показываем уведомление о смене темы
            showThemeNotification(isDark ? 'Светлая тема активирована' : 'Темная тема активирована');
        });
    }
    
    // Функция уведомления о смене темы
    function showThemeNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'theme-notification';
        notification.innerHTML = `<div class="theme-notification-content"><i class="fas fa-palette"></i><span>${message}</span></div>`;
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 1500);
    }
    
    // ========== ВЫПАДАЮЩЕЕ МЕНЮ ПРОФИЛЯ ==========
    const profileBtn = document.getElementById('profileBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    
    if (profileBtn && dropdownMenu) {
        profileBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            dropdownMenu.classList.toggle('show');
        });
        
        document.addEventListener('click', function(e) {
            if (profileBtn && dropdownMenu) {
                if (!profileBtn.contains(e.target) && !dropdownMenu.contains(e.target)) {
                    dropdownMenu.classList.remove('show');
                }
            }
        });
    }
    
    // ========== ЗАГРУЗКА КОЛИЧЕСТВА КОРЗИНЫ ==========
    function updateCartCount() {
        fetch('/api/cart/count')
            .then(response => response.json())
            .then(data => {
                const cartCount = document.getElementById('cartCount');
                if (cartCount) cartCount.textContent = data.count;
            })
            .catch(error => console.error('Error:', error));
    }
    
    updateCartCount();
    
    // ========== ТАЙМЕР ==========
    function startTimer() {
        let target = new Date();
        target.setDate(target.getDate() + 3);
        
        const timerInterval = setInterval(() => {
            const now = new Date();
            const diff = target - now;
            
            if (diff <= 0) {
                clearInterval(timerInterval);
                const timerContainer = document.getElementById('mainTimer');
                if (timerContainer) {
                    timerContainer.innerHTML = '<div class="timer-ended">Акция завершена!</div>';
                }
                return;
            }
            
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            const daysSpan = document.getElementById('days');
            const hoursSpan = document.getElementById('hours');
            const minutesSpan = document.getElementById('minutes');
            const secondsSpan = document.getElementById('seconds');
            
            if (daysSpan) daysSpan.textContent = days.toString().padStart(2, '0');
            if (hoursSpan) hoursSpan.textContent = hours.toString().padStart(2, '0');
            if (minutesSpan) minutesSpan.textContent = minutes.toString().padStart(2, '0');
            if (secondsSpan) secondsSpan.textContent = seconds.toString().padStart(2, '0');
        }, 1000);
    }
    
    startTimer();
    
    // ========== ДОБАВЛЕНИЕ В КОРЗИНУ ==========
    function showSimpleNotification(message, type) {
        // Удаляем старые уведомления
        const oldNotifications = document.querySelectorAll('.custom-notification');
        oldNotifications.forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `custom-notification ${type}`;
        notification.innerHTML = `<div class="notification-content"><i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i><span>${message}</span></div>`;
        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 2500);
    }
    
    function addToCartHandler(e) {
        e.stopPropagation();
        const productId = this.dataset.id;
        let productName = 'Товар';
        
        const parent = this.closest('.product-item, .catalog-item, .recommendation-card, .wishlist-card');
        if (parent) {
            const nameEl = parent.querySelector('h4, h3');
            if (nameEl) productName = nameEl.innerText;
        }
        
        if (!productId) {
            console.error('No product ID');
            showSimpleNotification('Ошибка: ID товара не найден', 'error');
            return;
        }
        
        // Блокируем кнопку на время запроса
        const originalText = this.textContent;
        this.textContent = 'Добавление...';
        this.disabled = true;
        
        fetch(`/add_to_cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ color: 'Черный', size: 'M' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSimpleNotification(`${productName} добавлен в корзину`, 'success');
                const cartCount = document.getElementById('cartCount');
                if (cartCount) cartCount.textContent = data.cart_count;
            } else if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                showSimpleNotification('Ошибка при добавлении товара', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showSimpleNotification('Ошибка при добавлении товара', 'error');
        })
        .finally(() => {
            this.textContent = originalText;
            this.disabled = false;
        });
    }
    
    // Навешиваем обработчики на все кнопки добавления в корзину
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.removeEventListener('click', addToCartHandler);
        btn.addEventListener('click', addToCartHandler);
    });
    
    // ========== ПОИСК ==========
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    function performSearch() {
        if (searchInput) {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        }
    }
    
    if (searchBtn) searchBtn.addEventListener('click', performSearch);
    if (searchInput) searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') performSearch();
    });
    
    // ========== УДАЛЕНИЕ ИЗ КОРЗИНЫ ==========
    // Этот код работает на странице корзины
    const deleteButtons = document.querySelectorAll('.btn-remove');
    const deleteModal = document.getElementById('deleteItemModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    let itemToDelete = null;
    
    function openDeleteModal(itemId, productName) {
        itemToDelete = itemId;
        const deleteItemName = document.getElementById('deleteItemName');
        if (deleteItemName) {
            deleteItemName.innerHTML = `Вы уверены, что хотите удалить "${productName}" из корзины?`;
        }
        if (deleteModal) deleteModal.style.display = 'flex';
    }
    
    function closeDeleteModal() {
        if (deleteModal) deleteModal.style.display = 'none';
        itemToDelete = null;
    }
    
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const cartId = this.dataset.cartId;
                const productName = this.dataset.productName || 'товар';
                openDeleteModal(cartId, productName);
            });
        });
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (itemToDelete) {
                fetch(`/remove_from_cart/${itemToDelete}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showSimpleNotification('Товар удален из корзины', 'success');
                        const cartCount = document.getElementById('cartCount');
                        if (cartCount) cartCount.textContent = data.cart_count;
                        setTimeout(() => location.reload(), 500);
                    } else {
                        showSimpleNotification(data.error || 'Ошибка при удалении', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showSimpleNotification('Ошибка при удалении товара', 'error');
                })
                .finally(() => {
                    closeDeleteModal();
                });
            } else {
                closeDeleteModal();
            }
        });
    }
    
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    }
    
    // Закрытие модального окна при клике на overlay
    const modalOverlay = document.querySelector('.custom-modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeDeleteModal);
    }
    
    // Закрытие по ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeDeleteModal();
    });
    
    // ========== ОБНОВЛЕНИЕ КОЛИЧЕСТВА В КОРЗИНЕ ==========
    const cartQuantityInputs = document.querySelectorAll('.cart-quantity');
    if (cartQuantityInputs.length > 0) {
        cartQuantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                let quantity = parseInt(this.value);
                if (quantity < 1) {
                    this.value = 1;
                    quantity = 1;
                }
                const itemId = this.dataset.cartId;
                
                fetch('/update_cart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ item_id: itemId, quantity: quantity })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        showSimpleNotification('Ошибка обновления количества', 'error');
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
    
    // ========== ВЫДЕЛЕНИЕ ТОВАРОВ ДЛЯ ОФОРМЛЕНИЯ ==========
    function updateSelectedTotal() {
        let total = 0;
        const checkboxes = document.querySelectorAll('.item-checkbox:checked');
        checkboxes.forEach(cb => {
            total += parseFloat(cb.dataset.price) * parseInt(cb.dataset.quantity);
        });
        const selectedTotalSpan = document.getElementById('selectedTotal');
        if (selectedTotalSpan) selectedTotalSpan.innerHTML = total + '₽';
        
        const checkoutBtn = document.getElementById('checkoutSelectedBtn');
        if (checkoutBtn) checkoutBtn.disabled = checkboxes.length === 0;
    }
    
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    if (itemCheckboxes.length > 0) {
        itemCheckboxes.forEach(cb => cb.addEventListener('change', updateSelectedTotal));
        
        const selectAllCheckbox = document.getElementById('selectAllCheckbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                document.querySelectorAll('.item-checkbox').forEach(cb => cb.checked = this.checked);
                updateSelectedTotal();
            });
        }
        
        const checkoutSelectedBtn = document.getElementById('checkoutSelectedBtn');
        if (checkoutSelectedBtn) {
            checkoutSelectedBtn.addEventListener('click', function() {
                const selectedItems = [];
                document.querySelectorAll('.item-checkbox:checked').forEach(cb => {
                    selectedItems.push({
                        cart_item_id: parseInt(cb.dataset.cartItemId),
                        product_id: parseInt(cb.dataset.productId),
                        quantity: parseInt(cb.dataset.quantity)
                    });
                });
                if (selectedItems.length === 0) {
                    showSimpleNotification('Выберите товары для оформления', 'error');
                    return;
                }
                
                const ids = selectedItems.map(i => i.cart_item_id).join(',');
                const quantities = selectedItems.map(i => i.quantity).join(',');
                window.location.href = `/checkout?ids=${ids}&quantities=${quantities}`;
            });
        }
        
        updateSelectedTotal();
    }
    
    // ========== ДОБАВЛЕНИЕ В ИЗБРАННОЕ ==========
    const wishlistButtons = document.querySelectorAll('.add-to-wishlist-btn');
    if (wishlistButtons.length > 0) {
        wishlistButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const productId = this.dataset.id;
                
                fetch(`/add_to_wishlist/${productId}`, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => {
                    if (response.ok) {
                        showSimpleNotification('Товар добавлен в избранное', 'success');
                    }
                })
                .catch(error => console.error('Error:', error));
            });
        });
    }
    
    // ========== УДАЛЕНИЕ ИЗ ИЗБРАННОГО ==========
    const removeWishlistButtons = document.querySelectorAll('.remove-wishlist');
    if (removeWishlistButtons.length > 0) {
        removeWishlistButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const productId = this.dataset.id;
                
                if (confirm('Удалить товар из отложенных?')) {
                    fetch(`/remove_from_wishlist/${productId}`, {
                        method: 'GET',
                    })
                    .then(response => {
                        if (response.ok) {
                            const card = this.closest('.wishlist-card');
                            if (card) card.remove();
                            showSimpleNotification('Товар удален из избранного', 'success');
                            if (document.querySelectorAll('.wishlist-card').length === 0) {
                                location.reload();
                            }
                        }
                    })
                    .catch(error => console.error('Error:', error));
                }
            });
        });
    }
    
    // ========== ФОРМА КОНТАКТОВ ==========
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            showSimpleNotification('Сообщение отправлено! Мы свяжемся с вами.', 'success');
            this.reset();
        });
    }
    
    // ========== ВЫБОР ЦВЕТА И РАЗМЕРА НА СТРАНИЦЕ ТОВАРА ==========
    const colorCircles = document.querySelectorAll('.color-circle');
    if (colorCircles.length > 0) {
        colorCircles.forEach(circle => {
            circle.addEventListener('click', function() {
                colorCircles.forEach(c => c.classList.remove('active'));
                this.classList.add('active');
                const color = this.dataset.color;
                const selectedColorInput = document.getElementById('selectedColor');
                if (selectedColorInput) selectedColorInput.value = color;
            });
        });
    }
    
    const sizeOptions = document.querySelectorAll('.size-option');
    if (sizeOptions.length > 0) {
        sizeOptions.forEach(size => {
            size.addEventListener('click', function() {
                sizeOptions.forEach(s => s.classList.remove('active'));
                this.classList.add('active');
                const sizeVal = this.dataset.size;
                const selectedSizeInput = document.getElementById('selectedSize');
                if (selectedSizeInput) selectedSizeInput.value = sizeVal;
            });
        });
    }
    
    // ========== КНОПКА ДОБАВЛЕНИЯ В КОРЗИНУ СО СТРАНИЦЫ ТОВАРА ==========
    const addToCartDetailBtn = document.getElementById('addToCartBtn');
    if (addToCartDetailBtn) {
        addToCartDetailBtn.addEventListener('click', function() {
            const productId = this.dataset.id || window.location.pathname.split('/').pop();
            const colorInput = document.getElementById('selectedColor');
            const sizeInput = document.getElementById('selectedSize');
            const color = colorInput ? colorInput.value : 'Черный';
            const size = sizeInput ? sizeInput.value : 'M';
            
            fetch(`/add_to_cart/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ color: color, size: size })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSimpleNotification(`Товар добавлен в корзину (${color}, ${size})`, 'success');
                    const cartCount = document.getElementById('cartCount');
                    if (cartCount) cartCount.textContent = data.cart_count;
                } else {
                    showSimpleNotification('Ошибка при добавлении товара', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showSimpleNotification('Ошибка при добавлении товара', 'error');
            });
        });
    }
    
    // ========== СТИЛИ ДЛЯ УВЕДОМЛЕНИЯ О ТЕМЕ ==========
    const themeNotificationStyles = document.createElement('style');
    themeNotificationStyles.textContent = `
        .theme-notification {
            position: fixed;
            top: 80px;
            right: 30px;
            background: #4caf50;
            color: white;
            padding: 12px 20px;
            border-radius: 10px;
            z-index: 2000;
            transform: translateX(150%);
            transition: transform 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .theme-notification.show {
            transform: translateX(0);
        }
        .theme-notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .theme-notification-content i {
            font-size: 1.2rem;
        }
        body.dark-theme .theme-notification {
            background: #cc0000;
        }
        @media (max-width: 768px) {
            .theme-notification {
                top: 70px;
                right: 20px;
                left: 20px;
                text-align: center;
            }
        }
    `;
    document.head.appendChild(themeNotificationStyles);
    
    // ========== СТИЛИ ДЛЯ УВЕДОМЛЕНИЙ ==========
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .custom-notification {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1a1a1a;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 2000;
            transform: translateX(120%);
            transition: transform 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
            min-width: 280px;
            max-width: 380px;
            overflow: hidden;
        }
        body.dark-theme .custom-notification {
            background: #2a2a2a;
        }
        .custom-notification.show {
            transform: translateX(0);
        }
        .custom-notification.success {
            border-left: 4px solid #4caf50;
        }
        .custom-notification.error {
            border-left: 4px solid #ff4444;
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
        }
        .custom-notification.success .notification-content i {
            color: #4caf50;
            font-size: 1.2rem;
        }
        .custom-notification.error .notification-content i {
            color: #ff4444;
            font-size: 1.2rem;
        }
        .notification-content span {
            font-size: 0.85rem;
            color: #ffffff;
        }
        @media (max-width: 480px) {
            .custom-notification {
                left: 20px;
                right: 20px;
                min-width: auto;
                max-width: none;
            }
        }
    `;
    document.head.appendChild(notificationStyles);
});