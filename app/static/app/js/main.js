/**
 * Основной JavaScript модуль приложения.
 * Содержит инициализацию и общие функции для всего приложения.
 */

// Импортируем функции из других модулей
import { initFavoriteButtons } from './favorites.js';
import { initShareButtons } from './share.js';

// Конфигурация
const CONFIG = {
    ANIMATION_DURATION: 300, // Длительность анимаций в мс
    DEBOUNCE_DELAY: 300, // Задержка для debounce функций в мс
    SCROLL_THRESHOLD: 100 // Порог прокрутки для показа кнопки "Наверх"
};

// Состояние приложения
const state = {
    isDarkMode: false,
    isLoading: false,
    isMobile: window.innerWidth < 768
};

/**
 * Инициализирует приложение при загрузке DOM.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация Telegram Mini App
    initTelegramMiniApp();
    
    // Инициализация кнопок избранного
    initFavoriteButtons();
    
    // Инициализация кнопок поделиться
    initShareButtons();
    
    // Инициализация всплывающих подсказок
    initTooltips();
    
    // Инициализация обработчиков форм и ссылок
    initFormHandlers();
    initLinkHandlers();
    
    // Инициализация кнопки "Наверх"
    initBackToTopButton();
    
    // Инициализация обработчика изменения размера окна
    initResizeHandler();
    
    // Инициализация обработчика изменения темы
    initThemeHandler();
    
    // Инициализация предпросмотра изображений
    initImagePreview();
});

/**
 * Инициализирует Telegram Mini App.
 * Настраивает взаимодействие с Telegram Web App API.
 */
function initTelegramMiniApp() {
    const tg = window.Telegram && window.Telegram.WebApp;
    
    if (tg) {
        // Расширяем WebApp на весь экран
        tg.expand();
        
        // Применяем цветовую схему Telegram
        applyTelegramTheme(tg);
        
        // Обрабатываем изменение темы
        tg.onEvent('themeChanged', () => applyTelegramTheme(tg));
        
        // Обрабатываем событие закрытия приложения
        tg.onEvent('viewportChanged', handleViewportChange);
        
        // Обрабатываем событие отправки данных
        tg.onEvent('mainButtonClicked', handleMainButtonClick);
    }
}

/**
 * Применяет цветовую схему Telegram к приложению.
 * 
 * @param {Object} tg - Объект Telegram WebApp
 */
function applyTelegramTheme(tg) {
    if (!tg) return;
    
    // Получаем цвета из Telegram WebApp
    const colors = {
        bgColor: tg.themeParams.bg_color || '#ffffff',
        textColor: tg.themeParams.text_color || '#000000',
        hintColor: tg.themeParams.hint_color || '#999999',
        linkColor: tg.themeParams.link_color || '#2481cc',
        buttonColor: tg.themeParams.button_color || '#2481cc',
        buttonTextColor: tg.themeParams.button_text_color || '#ffffff',
        secondaryBgColor: tg.themeParams.secondary_bg_color || '#f0f0f0'
    };
    
    // Устанавливаем CSS переменные
    document.documentElement.style.setProperty('--tg-theme-bg-color', colors.bgColor);
    document.documentElement.style.setProperty('--tg-theme-text-color', colors.textColor);
    document.documentElement.style.setProperty('--tg-theme-hint-color', colors.hintColor);
    document.documentElement.style.setProperty('--tg-theme-link-color', colors.linkColor);
    document.documentElement.style.setProperty('--tg-theme-button-color', colors.buttonColor);
    document.documentElement.style.setProperty('--tg-theme-button-text-color', colors.buttonTextColor);
    document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', colors.secondaryBgColor);
    
    // Создаем RGB версии для использования с opacity
    const buttonColorRGB = hexToRgb(colors.buttonColor);
    if (buttonColorRGB) {
        document.documentElement.style.setProperty(
            '--tg-theme-button-color-rgb', 
            `${buttonColorRGB.r}, ${buttonColorRGB.g}, ${buttonColorRGB.b}`
        );
    }
    
    // Устанавливаем тему Bootstrap в зависимости от яркости фона
    const brightness = getBrightness(colors.bgColor);
    const isDark = brightness < 128;
    
    document.body.setAttribute('data-bs-theme', isDark ? 'dark' : 'light');
    state.isDarkMode = isDark;
}

/**
 * Обрабатывает изменение области просмотра в Telegram Mini App.
 * 
 * @param {Object} event - Событие изменения области просмотра
 */
function handleViewportChange(event) {
    // Адаптируем интерфейс к новому размеру
    const isExpanded = event.isExpanded;
    
    // Если приложение свернуто, скрываем некоторые элементы
    const nonEssentialElements = document.querySelectorAll('.non-essential');
    nonEssentialElements.forEach(el => {
        el.style.display = isExpanded ? 'block' : 'none';
    });
}

/**
 * Обрабатывает нажатие на главную кнопку в Telegram Mini App.
 */
function handleMainButtonClick() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (!tg) return;
    
    // Получаем форму, которая должна быть отправлена
    const form = document.querySelector('form[data-tg-main-button="true"]');
    if (form) {
        form.submit();
    }
}

/**
 * Инициализирует всплывающие подсказки Bootstrap.
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Инициализирует обработчики форм.
 * Добавляет анимацию загрузки при отправке форм.
 */
function initFormHandlers() {
    const forms = document.querySelectorAll('form:not(.no-loader)');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Если форма не валидна, не показываем загрузчик
            if (!this.checkValidity()) {
                return;
            }
            
            // Показываем индикатор загрузки
            showPageLoader();
            
            // Блокируем кнопки отправки
            const submitButtons = this.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(button => {
                button.disabled = true;
                button.classList.add('btn-loading');
            });
        });
    });
}

/**
 * Инициализирует обработчики ссылок.
 * Добавляет анимацию загрузки при переходе по ссылкам.
 */
function initLinkHandlers() {
    // Добавляем анимацию загрузки при переходе по ссылкам
    const links = document.querySelectorAll('a:not([target="_blank"]):not(.no-loader)');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Пропускаем, если это AJAX-запрос или действие JavaScript
            if (this.getAttribute('href').startsWith('#') || 
                this.getAttribute('href') === 'javascript:void(0)') {
                return;
            }
            
            // Показываем индикатор загрузки
            showPageLoader();
        });
    });
}

/**
 * Инициализирует кнопку "Наверх".
 */
function initBackToTopButton() {
    const backToTopButton = document.getElementById('back-to-top');
    if (!backToTopButton) return;
    
    // Скрываем кнопку при загрузке страницы
    backToTopButton.style.display = 'none';
    
    // Добавляем обработчик прокрутки
    window.addEventListener('scroll', debounce(function() {
        if (window.pageYOffset > CONFIG.SCROLL_THRESHOLD) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    }, CONFIG.DEBOUNCE_DELAY));
    
    // Добавляем обработчик клика
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Инициализирует обработчик изменения размера окна.
 */
function initResizeHandler() {
    window.addEventListener('resize', debounce(function() {
        state.isMobile = window.innerWidth < 768;
        
        // Адаптируем интерфейс к новому размеру
        adjustUIForScreenSize();
    }, CONFIG.DEBOUNCE_DELAY));
}

/**
 * Адаптирует интерфейс к текущему размеру экрана.
 */
function adjustUIForScreenSize() {
    // Адаптируем элементы для мобильного/десктопного отображения
    const mobileOnlyElements = document.querySelectorAll('.mobile-only');
    const desktopOnlyElements = document.querySelectorAll('.desktop-only');
    
    mobileOnlyElements.forEach(el => {
        el.style.display = state.isMobile ? 'block' : 'none';
    });
    
    desktopOnlyElements.forEach(el => {
        el.style.display = state.isMobile ? 'none' : 'block';
    });
}

/**
 * Инициализирует обработчик изменения темы.
 */
function initThemeHandler() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Устанавливаем начальное состояние переключателя
    updateThemeToggle();
    
    // Добавляем обработчик клика
    themeToggle.addEventListener('click', function() {
        // Переключаем тему
        state.isDarkMode = !state.isDarkMode;
        
        // Применяем новую тему
        document.body.setAttribute('data-bs-theme', state.isDarkMode ? 'dark' : 'light');
        
        // Обновляем переключатель
        updateThemeToggle();
        
        // Сохраняем предпочтение пользователя
        localStorage.setItem('theme', state.isDarkMode ? 'dark' : 'light');
    });
}

/**
 * Обновляет внешний вид переключателя темы.
 */
function updateThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const icon = themeToggle.querySelector('i');
    if (icon) {
        if (state.isDarkMode) {
            icon.classList.remove('bi-sun');
            icon.classList.add('bi-moon');
        } else {
            icon.classList.remove('bi-moon');
            icon.classList.add('bi-sun');
        }
    }
}

/**
 * Инициализирует предпросмотр изображений.
 */
function initImagePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    fileInputs.forEach(input => {
        const previewContainer = document.querySelector(`[data-preview-for="${input.id}"]`);
        if (!previewContainer) return;
        
        input.addEventListener('change', function() {
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
    });
}

/**
 * Показывает индикатор загрузки страницы.
 */
function showPageLoader() {
    // Создаем элемент загрузки, если его еще нет
    if (!document.getElementById('page-loader')) {
        const loader = document.createElement('div');
        loader.id = 'page-loader';
        loader.innerHTML = `
            <div class="page-loader-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;
        document.body.appendChild(loader);
    } else {
        document.getElementById('page-loader').style.display = 'flex';
    }
}

/**
 * Скрывает индикатор загрузки страницы.
 */
function hidePageLoader() {
    const loader = document.getElementById('page-loader');
    if (loader) {
        loader.style.display = 'none';
    }
}

/**
 * Функция debounce для ограничения частоты вызова функций.
 * 
 * @param {Function} func - Функция для вызова
 * @param {number} wait - Время ожидания в мс
 * @returns {Function} Функция с debounce
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

/**
 * Вычисляет яркость цвета.
 * 
 * @param {string} hexColor - Цвет в формате HEX
 * @returns {number} Яркость цвета (0-255)
 */
function getBrightness(hexColor) {
    const rgb = hexToRgb(hexColor);
    if (!rgb) return 128;
    
    // Вычисляем яркость по формуле
    return (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
}

/**
 * Преобразует цвет из HEX в RGB.
 * 
 * @param {string} hex - Цвет в формате HEX
 * @returns {Object|null} Объект с компонентами RGB или null при ошибке
 */
function hexToRgb(hex) {
    // Удаляем # если есть
    hex = hex.replace('#', '');
    
    // Проверяем формат
    if (hex.length !== 6 && hex.length !== 3) {
        return null;
    }
    
    // Преобразуем сокращенный формат
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    
    // Преобразуем в RGB
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    
    return { r, g, b };
}

/**
 * Получает CSRF токен из cookies.
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
export {
    showPageLoader,
    hidePageLoader,
    getCookie,
    debounce,
    hexToRgb,
    getBrightness
};

