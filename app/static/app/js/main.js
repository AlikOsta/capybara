document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Telegram Mini App
    const tg = window.Telegram.WebApp;
    if (tg) {
        tg.expand();
        
        // Адаптация темы к настройкам Telegram
        adaptThemeToTelegram(tg);
        
        // Обработка кнопок избранного
        setupFavoriteButtons();
    }
});

// Функция для адаптации темы к настройкам Telegram
function adaptThemeToTelegram(tg) {
    // Получаем цвета из Telegram
    const colors = {
        bg_color: tg.themeParams.bg_color || '#ffffff',
        text_color: tg.themeParams.text_color || '#000000',
        hint_color: tg.themeParams.hint_color || '#999999',
        link_color: tg.themeParams.link_color || '#2481cc',
        button_color: tg.themeParams.button_color || '#2481cc',
        button_text_color: tg.themeParams.button_text_color || '#ffffff',
        secondary_bg_color: tg.themeParams.secondary_bg_color || '#f0f0f0'
    };
    
    // Устанавливаем CSS переменные
    document.documentElement.style.setProperty('--tg-theme-bg-color', colors.bg_color);
    document.documentElement.style.setProperty('--tg-theme-text-color', colors.text_color);
    document.documentElement.style.setProperty('--tg-theme-hint-color', colors.hint_color);
    document.documentElement.style.setProperty('--tg-theme-link-color', colors.link_color);
    document.documentElement.style.setProperty('--tg-theme-button-color', colors.button_color);
    document.documentElement.style.setProperty('--tg-theme-button-text-color', colors.button_text_color);
    document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', colors.secondary_bg_color);
    
    // Устанавливаем тему Bootstrap в зависимости от яркости фона
    const brightness = getBrightness(colors.bg_color);
    if (brightness < 128) {
        document.body.setAttribute('data-bs-theme', 'dark');
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
    }
}

// Функция для расчета яркости цвета
function getBrightness(hexColor) {
    // Удаляем # если есть
    hexColor = hexColor.replace('#', '');
    
    // Преобразуем в RGB
    const r = parseInt(hexColor.substr(0, 2), 16);
    const g = parseInt(hexColor.substr(2, 2), 16);
    const b = parseInt(hexColor.substr(4, 2), 16);
    
    // Вычисляем яркость
    return (r * 299 + g * 587 + b * 114) / 1000;
}

// Функция для настройки кнопок избранного
function setupFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const isFavorite = this.dataset.isFavorite === 'true';
            
            // Отправляем AJAX запрос
            fetch(`/product/${productId}/favorite/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем иконку
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                        this.dataset.isFavorite = 'true';
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        this.dataset.isFavorite = 'false';
                    }
                }
            });
        });
    });
}

// Функция для получения CSRF токена из cookies
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
