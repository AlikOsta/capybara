/**
 * Основной JavaScript файл приложения Capybara
 * Содержит общие функции и инициализацию Telegram Mini App
 */

document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram && window.Telegram.WebApp;

    // Инициализация Telegram Mini App
    if (tg) {
        // Скрываем кнопки и расширяем приложение
        if (tg.BackButton) tg.BackButton.hide();
        if (tg.MainButton) tg.MainButton.hide();
        tg.expand();
        tg.enableClosingConfirmation();

        // Адаптация темы к настройкам Telegram
        adaptThemeToTelegram(tg);
    }
    
    // Инициализация функционала приложения
    initImagePreview();
    initBackToTopButton();
    initMainButtonAnimation();
});

/**
 * Адаптация темы к настройкам Telegram.
 * Получает параметры темы из tg.themeParams и устанавливает CSS-переменные.
 */
function adaptThemeToTelegram(tg) {
    const colors = {
        bg_color: tg.themeParams.bg_color || '#ffffff',
        text_color: tg.themeParams.text_color || '#000000',
        hint_color: tg.themeParams.hint_color || '#999999',
        link_color: tg.themeParams.link_color || '#2481cc',
        button_color: tg.themeParams.button_color || '#2481cc',
        button_text_color: tg.themeParams.button_text_color || '#ffffff',
        secondary_bg_color: tg.themeParams.secondary_bg_color || '#f0f0f0'
    };

    // Устанавливаем CSS-переменные в корневом элементе
    const root = document.documentElement;
    root.style.setProperty('--tg-theme-bg-color', colors.bg_color);
    root.style.setProperty('--tg-theme-text-color', colors.text_color);
    root.style.setProperty('--tg-theme-hint-color', colors.hint_color);
    root.style.setProperty('--tg-theme-link-color', colors.link_color);
    root.style.setProperty('--tg-theme-button-color', colors.button_color);
    root.style.setProperty('--tg-theme-button-text-color', colors.button_text_color);
    root.style.setProperty('--tg-theme-secondary-bg-color', colors.secondary_bg_color);

    // Добавляем RGB версию цвета кнопки для прозрачности (если требуется)
    const rgbButton = hexToRgb(colors.button_color);
    if (rgbButton) {
        root.style.setProperty('--tg-theme-button-color-rgb', `${rgbButton.r}, ${rgbButton.g}, ${rgbButton.b}`);
    }

    // Устанавливаем тему Bootstrap в зависимости от яркости фона
    document.body.setAttribute('data-bs-theme', getBrightness(colors.bg_color) < 128 ? 'dark' : 'light');
}

/**
 * Вычисление яркости HEX цвета.
 */
function getBrightness(hexColor) {
    hexColor = hexColor.replace('#', '');
    const r = parseInt(hexColor.substr(0, 2), 16);
    const g = parseInt(hexColor.substr(2, 2), 16);
    const b = parseInt(hexColor.substr(4, 2), 16);
    return (r * 299 + g * 587 + b * 114) / 1000;
}

/**
 * Преобразование HEX в RGB.
 */
function hexToRgb(hex) {
    hex = hex.replace('#', '');
    const bigint = parseInt(hex, 16);
    return { r: (bigint >> 16) & 255, g: (bigint >> 8) & 255, b: bigint & 255 };
}

/**
 * Инициализация предпросмотра изображений.
 * Добавлена проверка на размер файла (например, 5 Мб).
 */
function initImagePreview() {
    const fileInput = document.getElementById('id_image');
    const previewContainer = document.querySelector('.image-preview-container');
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 Мб

    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';

            if (this.files && this.files[0]) {
                const file = this.files[0];

                // Проверяем размер файла
                if (file.size > MAX_FILE_SIZE) {
                    previewContainer.innerHTML = '<p class="text-danger">Файл слишком большой (макс. 5 Мб).</p>';
                    return;
                }

                const img = document.createElement('img');
                img.classList.add('img-preview', 'img-fluid', 'rounded');
                const objectUrl = URL.createObjectURL(file);
                img.src = objectUrl;
                previewContainer.appendChild(img);

                img.onload = () => URL.revokeObjectURL(objectUrl);
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

/**
 * Инициализация кнопки "Наверх".
 * Показываем кнопку при прокрутке более чем на 1000px.
 */
function initBackToTopButton() {
    const backToTopButton = document.getElementById('back-to-top');
    if (!backToTopButton) return;

    const toggleVisibility = () => {
        backToTopButton.style.display = window.pageYOffset > 1000 ? 'flex' : 'none';
    };

    window.addEventListener('scroll', toggleVisibility);
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Инициализация анимации для MainButton Telegram.
 * Добавляет стили и следит за появлением кнопки в DOM.
 */
function initMainButtonAnimation() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (!tg) return;

    // Добавляем стили анимации, если они еще не добавлены
    if (!document.querySelector('#telegram-main-button-styles')) {
        const style = document.createElement('style');
        style.id = 'telegram-main-button-styles';
        style.textContent = `
            .telegram-main-button {
                transition: transform 0.3s ease, opacity 0.3s ease !important;
                transform: translateY(0) !important;
                opacity: 1 !important;
            }
            .telegram-main-button.hidden {
                transform: translateY(100%) !important;
                opacity: 0 !important;
            }
        `;
        document.head.appendChild(style);
    }

    // Следим за изменениями в DOM и добавляем класс анимации при появлении кнопки
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            if (mutation.addedNodes.length) {
                const mainButtonElement = document.querySelector('.telegram-main-button');
                if (mainButtonElement && !mainButtonElement.classList.contains('telegram-main-button-animation')) {
                    mainButtonElement.classList.add('telegram-main-button-animation');
                }
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

/**
 * Глобальный обработчик для управления нижним меню при навигации.
 * При изменении истории возвращаем нижнее меню и убираем видимость MainButton.
 */
(function() {
    window.addEventListener('popstate', () => {
        const footer = document.querySelector('footer.fixed-bottom');
        if (footer) footer.classList.remove('hidden');
        document.body.classList.remove('main-button-visible');
    });
})();

/**
 * Функция для получения CSRF токена из cookies.
 * Экспортируется для использования в других скриптах.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const trimmedCookie = cookie.trim();
            if (trimmedCookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmedCookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
window.getCookie = getCookie;
