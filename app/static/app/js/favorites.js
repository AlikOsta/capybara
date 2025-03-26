/**
 * Модуль для управления избранными объявлениями.
 * Обрабатывает добавление/удаление объявлений из избранного.
 */

// Ждем загрузку DOM перед инициализацией
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация обработчиков для кнопок избранного
    initFavoriteButtons();
});

/**
 * Инициализирует обработчики для кнопок избранного.
 * Находит все кнопки добавления в избранное и добавляет им обработчики событий.
 */
function initFavoriteButtons() {
    const favoriteBtns = document.querySelectorAll('.favorite-btn');
    
    favoriteBtns.forEach(btn => {
        // Пропускаем уже инициализированные кнопки
        if (btn.classList.contains('initialized')) {
            return;
        }
        
        btn.classList.add('initialized');
        btn.addEventListener('click', handleFavoriteClick);
    });
}

/**
 * Обрабатывает клик по кнопке избранного.
 * Отправляет AJAX запрос для добавления/удаления объявления из избранного.
 * 
 * @param {Event} e - Событие клика
 */
function handleFavoriteClick(e) {
    e.preventDefault();
    e.stopPropagation();
    
    const btn = e.currentTarget;
    const productId = btn.dataset.productId;
    
    // Отправляем AJAX запрос
    fetch(`/product/${productId}/favorite/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateFavoriteButton(btn, data.is_favorite);
            
            // Если мы на странице избранного и удалили из избранного, удаляем карточку
            if (!data.is_favorite && window.location.pathname.includes('/favorites/')) {
                removeProductCard(btn);
            }
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

/**
 * Обновляет внешний вид кнопки избранного.
 * 
 * @param {HTMLElement} button - Кнопка избранного
 * @param {boolean} isFavorite - Флаг, показывающий, добавлено ли объявление в избранное
 */
function updateFavoriteButton(button, isFavorite) {
    // Обновляем состояние кнопки
    button.dataset.isFavorite = isFavorite.toString();
    
    // Обновляем иконку
    const icon = button.querySelector('i');
    if (isFavorite) {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
    } else {
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
    }
}

/**
 * Удаляет карточку объявления со страницы избранного.
 * 
 * @param {HTMLElement} button - Кнопка избранного
 */
function removeProductCard(button) {
    const productCard = button.closest('.col-6');
    if (productCard) {
        // Анимация удаления
        productCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        productCard.style.opacity = '0';
        productCard.style.transform = 'scale(0.9)';
        
        // Удаляем элемент после анимации
        setTimeout(() => {
            productCard.remove();
            
            // Проверяем, остались ли еще карточки
            const remainingCards = document.querySelectorAll('.favorites-page .col-6');
            if (remainingCards.length === 0) {
                showEmptyState();
            }
        }, 300);
    }
}

/**
 * Показывает пустое состояние на странице избранного.
 */
function showEmptyState() {
    const row = document.querySelector('.favorites-page .row');
    if (row) {
        row.innerHTML = `
            <div class="col-12">
                <div class="empty-favorites text-center py-5">
                    <div class="empty-icon mb-3">
                        <i class="bi bi-heart text-danger fs-1"></i>
                    </div>
                    <h5 class="mb-3">Нет избранных объявлений</h5>
                    <p class="text-muted mb-4">Добавляйте понравившиеся объявления в избранное, чтобы быстро находить их позже</p>
                    <a href="/" class="btn btn-primary">
                        <i class="bi bi-search me-2"></i>Найти объявления
                    </a>
                </div>
            </div>
        `;
    }
}

/**
 * Получает значение CSRF токена из cookies.
 * 
 * @param {string} name - Имя cookie
 * @returns {string} Значение CSRF токена
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Экспортируем функции для использования в других модулях
export { initFavoriteButtons, handleFavoriteClick, updateFavoriteButton };
