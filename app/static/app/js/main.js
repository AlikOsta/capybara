/**
 * Основной JavaScript файл приложения Capybara
 * Содержит общие функции и инициализацию Telegram Mini App
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Telegram Mini App
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
        tg.expand();
        tg.enableClosingConfirmation()
        
        // Адаптация темы к настройкам Telegram
        adaptThemeToTelegram(tg);
    }
    
    // Инициализация предпросмотра изображений при загрузке
    initImagePreview();
    
    // Инициализация кнопки "Наверх"
    initBackToTopButton();
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
    
    // Добавляем RGB версии для использования с opacity
    const rgbButton = hexToRgb(colors.button_color);
    if (rgbButton) {
        document.documentElement.style.setProperty('--tg-theme-button-color-rgb', `${rgbButton.r}, ${rgbButton.g}, ${rgbButton.b}`);
    }
    
    // Устанавливаем тему Bootstrap в зависимости от яркости фона
    const brightness = getBrightness(colors.bg_color);
    if (brightness < 128) {
        document.body.setAttribute('data-bs-theme', 'dark');
    } else {
        document.body.setAttribute('data-bs-theme', 'light');
    }
}

// Расчет яркости цвета
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

// Преобразование HEX в RGB
function hexToRgb(hex) {
    // Удаляем # если есть
    hex = hex.replace('#', '');
    
    // Парсим значения RGB
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    
    return {r, g, b};
}

// Инициализация предпросмотра изображений при загрузке
function initImagePreview() {
    const fileInput = document.getElementById('id_image');
    const previewContainer = document.querySelector('.image-preview-container');
    
    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            // Очищаем контейнер
            previewContainer.innerHTML = '';
            
            // Проверяем, выбран ли файл
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Создаем элемент img для предпросмотра
                const img = document.createElement('img');
                img.classList.add('img-preview', 'img-fluid', 'rounded');
                
                // Создаем URL для предпросмотра
                const objectUrl = URL.createObjectURL(file);
                img.src = objectUrl;
                
                // Добавляем изображение в контейнер
                previewContainer.appendChild(img);
                
                // Освобождаем URL после загрузки изображения
                img.onload = function() {
                    URL.revokeObjectURL(objectUrl);
                };
            } else {
                // Если файл не выбран, показываем плейсхолдер
                const placeholder = document.createElement('div');
                placeholder.classList.add('img-preview-placeholder', 'd-flex', 'align-items-center', 'justify-content-center', 'rounded');
                placeholder.innerHTML = '<i class="bi bi-image text-muted fs-1"></i>';
                previewContainer.appendChild(placeholder);
            }
        });
    }
}

// Инициализация кнопки "Наверх"
function initBackToTopButton() {
    const backToTopButton = document.getElementById('back-to-top');
    
    if (backToTopButton) {
        // Показываем/скрываем кнопку при прокрутке
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 1000) {
                backToTopButton.style.display = 'flex';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        // Обработчик клика по кнопке
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
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

// Экспортируем функции для использования в других скриптах
window.getCookie = getCookie;
