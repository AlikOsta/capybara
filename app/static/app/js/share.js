/**
 * Модуль для функциональности "Поделиться".
 * Обрабатывает кнопки для шеринга объявлений в социальных сетях и мессенджерах.
 */

// Импортируем функции из других модулей
import { debounce } from './main.js';

// Конфигурация
const CONFIG = {
    COPY_FEEDBACK_DURATION: 2000, // Длительность показа сообщения о копировании в мс
    DEBOUNCE_DELAY: 300 // Задержка для debounce функций в мс
};

/**
 * Инициализирует кнопки "Поделиться".
 */
function initShareButtons() {
    // Инициализируем кнопки для шеринга в социальных сетях
    initSocialShareButtons();
    
    // Инициализируем кнопку копирования ссылки
    initCopyLinkButton();
    
    // Инициализируем кнопку шеринга через Web Share API
    initWebShareButton();
}

/**
 * Инициализирует кнопки для шеринга в социальных сетях.
 */
function initSocialShareButtons() {
    const socialButtons = document.querySelectorAll('.social-share-btn');
    
    socialButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.dataset.platform;
            const url = encodeURIComponent(this.dataset.url || window.location.href);
            const title = encodeURIComponent(this.dataset.title || document.title);
            const description = encodeURIComponent(this.dataset.description || '');
            const image = encodeURIComponent(this.dataset.image || '');
            
            let shareUrl = '';
            
            // Формируем URL для шеринга в зависимости от платформы
            switch (platform) {
                case 'telegram':
                    shareUrl = `https://t.me/share/url?url=${url}&text=${title}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://api.whatsapp.com/send?text=${title}%20${url}`;
                    break;
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'vk':
                    shareUrl = `https://vk.com/share.php?url=${url}&title=${title}&description=${description}&image=${image}`;
                    break;
                case 'email':
                    shareUrl = `mailto:?subject=${title}&body=${description}%20${url}`;
                    break;
            }
            
            // Открываем окно для шеринга
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
}

/**
 * Инициализирует кнопку копирования ссылки.
 */
function initCopyLinkButton() {
    const copyButtons = document.querySelectorAll('.copy-link-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.dataset.url || window.location.href;
            
            // Копируем ссылку в буфер обмена
            copyToClipboard(url)
                .then(() => {
                    // Показываем сообщение об успешном копировании
                    showCopyFeedback(this, true);
                })
                .catch(err => {
                    console.error('Ошибка при копировании:', err);
                    // Показываем сообщение об ошибке
                    showCopyFeedback(this, false);
                });
        });
    });
}

/**
 * Инициализирует кнопку шеринга через Web Share API.
 */
function initWebShareButton() {
    const webShareButtons = document.querySelectorAll('.web-share-btn');
    
    // Проверяем поддержку Web Share API
    if (!navigator.share) {
        // Если API не поддерживается, скрываем кнопки
        webShareButtons.forEach(button => {
            button.style.display = 'none';
        });
        return;
    }
    
    webShareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const shareData = {
                title: this.dataset.title || document.title,
                text: this.dataset.description || '',
                url: this.dataset.url || window.location.href
            };
            
            // Используем Web Share API
            navigator.share(shareData)
                .catch(err => {
                    console.error('Ошибка при шеринге:', err);
                });
        });
    });
}

/**
 * Копирует текст в буфер обмена.
 * 
 * @param {string} text - Текст для копирования
 * @returns {Promise} Промис, который разрешается при успешном копировании
 */
function copyToClipboard(text) {
    // Проверяем поддержку Clipboard API
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text);
    }
    
    // Запасной вариант для старых браузеров
    return new Promise((resolve, reject) => {
        try {
            // Создаем временный элемент
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            
            // Выделяем и копируем текст
            textarea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            
            if (successful) {
                resolve();
            } else {
                reject(new Error('Не удалось скопировать текст'));
            }
        } catch (err) {
            reject(err);
        }
    });
}

/**
 * Показывает сообщение о результате копирования.
 * 
 * @param {HTMLElement} button - Кнопка копирования
 * @param {boolean} success - Флаг успешного копирования
 */
function showCopyFeedback(button, success) {
    // Сохраняем оригинальный текст кнопки
    const originalText = button.innerHTML;
    const originalTitle = button.getAttribute('title');
    
    // Меняем текст и иконку в зависимости от результата
    if (success) {
        button.innerHTML = '<i class="bi bi-check"></i> Скопировано';
        button.setAttribute('title', 'Ссылка скопирована');
    } else {
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Ошибка';
        button.setAttribute('title', 'Не удалось скопировать ссылку');
    }
    
    // Добавляем класс для анимации
    button.classList.add(success ? 'copy-success' : 'copy-error');
    
    // Возвращаем оригинальный текст через некоторое время
    setTimeout(() => {
        button.innerHTML = originalText;
        button.setAttribute('title', originalTitle);
        button.classList.remove('copy-success', 'copy-error');
    }, CONFIG.COPY_FEEDBACK_DURATION);
}

/**
 * Создает URL для шеринга в Telegram.
 * 
 * @param {number} productId - ID объявления
 * @returns {string} URL для шеринга
 */
function createTelegramShareUrl(productId) {
    // Создаем URL для шеринга через бота
    return `https://t.me/CapybaraMPRobot?start=product_${productId}`;
}

/**
 * Обновляет URL для шеринга в кнопках.
 * 
 * @param {string} url - Новый URL для шеринга
 */
function updateShareUrls(url) {
    const shareButtons = document.querySelectorAll('[data-share-url]');
    
    shareButtons.forEach(button => {
        button.dataset.url = url;
    });
}

// Экспортируем функции для использования в других модулях
export {
    initShareButtons,
    copyToClipboard,
    createTelegramShareUrl,
    updateShareUrls
};
