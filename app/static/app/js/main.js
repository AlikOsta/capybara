document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram && window.Telegram.WebApp;

    // Инициализация Telegram Mini App
    if (tg) {
        // Скрываем кнопки и расширяем приложение
        if (tg.BackButton) tg.BackButton.hide();
        // Удаляем инициализацию MainButton
        // if (tg.MainButton) tg.MainButton.hide();
        tg.expand();
        tg.enableClosingConfirmation();

        // Адаптация темы к настройкам Telegram
        adaptThemeToTelegram(tg);
    }
    
    // Инициализация функционала приложения
    initImagePreview();
    initBackToTopButton();
    // Удаляем вызов функции инициализации анимации MainButton
    // initMainButtonAnimation();
});

// Функция для адаптации темы к настройкам Telegram
function adaptThemeToTelegram(tg) {
    if (!tg) return;
    
    // Получаем цвета из Telegram WebApp
    const colorScheme = tg.colorScheme || 'light';
    document.body.setAttribute('data-bs-theme', colorScheme);
    
    // Добавляем класс для темы Telegram
    document.body.classList.add(`telegram-theme-${colorScheme}`);
    
    // Применяем цвета из Telegram к CSS-переменным
    document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
    document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
    document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
    document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
    document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
    document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
    document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
}

// Функция для инициализации предпросмотра изображений
function initImagePreview() {
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.querySelector('.image-preview-container');
    
    if (fileInput && previewContainer) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    // Удаляем плейсхолдер, если он есть
                    const placeholder = previewContainer.querySelector('.img-preview-placeholder');
                    if (placeholder) {
                        placeholder.remove();
                    }
                    
                    // Проверяем, есть ли уже изображение предпросмотра
                    let imgPreview = previewContainer.querySelector('.img-preview');
                    
                    if (!imgPreview) {
                        // Если нет, создаем новое
                        imgPreview = document.createElement('img');
                        imgPreview.classList.add('img-preview', 'img-fluid', 'rounded');
                        previewContainer.appendChild(imgPreview);
                    }
                    
                    // Устанавливаем источник изображения
                    imgPreview.src = e.target.result;
                    imgPreview.alt = 'Предпросмотр';
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
}

// Функция для инициализации кнопки "Наверх"
function initBackToTopButton() {
    const backToTopButton = document.getElementById('back-to-top');
    
    if (backToTopButton) {
        // Показываем/скрываем кнопку при прокрутке
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        // Прокручиваем наверх при клике
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Удаляем функцию initMainButtonAnimation полностью
/*
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
*/
