/**
 * Модуль для шеринга объявлений и связи с продавцами
 * Содержит функции для работы с Telegram API
 */

const ShareModule = {
    // Инициализация модуля
    init: function() {
        // Проверяем доступность Telegram Web App API
        this.telegramApp = window.Telegram && window.Telegram.WebApp;
        
        // Инициализируем обработчики событий
        this.initEventListeners();
    },
    
    // Инициализация обработчиков событий
    initEventListeners: function() {
        // Находим все кнопки шеринга
        const shareButtons = document.querySelectorAll('[data-action="share"]');
        
        // Добавляем обработчики для кнопок шеринга
        shareButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const productId = button.dataset.productId;
                const productTitle = button.dataset.productTitle;
                this.shareProduct(event, productId, productTitle);
            });
        });
        
        // Находим все кнопки связи с продавцом
        const contactButtons = document.querySelectorAll('[data-action="contact"]');
        
        // Добавляем обработчики для кнопок связи с продавцом
        contactButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const username = button.dataset.username;
                const productId = button.dataset.productId;
                const productTitle = button.dataset.productTitle;
                const productPrice = button.dataset.productPrice;
                this.contactSeller(event, username, productId, productTitle, productPrice);
            });
        });
    },
    
    /**
     * Функция для шеринга объявления через Telegram
     * @param {Event} event - Событие клика
     * @param {number} productId - ID объявления
     * @param {string} productTitle - Название объявления
     */
    shareProduct: function(event, productId, productTitle) {
        event.preventDefault();
        
        // Проверяем, доступен ли Telegram Web App API
        if (this.telegramApp) {
            // Формируем текст для шеринга
            const shareText = `Объявление "${productTitle}" в Capybara\n\n`;
            
            // Формируем ссылку на бота с параметром start
            const shareUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
            
            // Используем Telegram API для шеринга
            this.telegramApp.shareUrl(shareUrl);
        } else {
            // Запасной вариант, если API недоступен
            this.showShareFallback(productId, productTitle);
        }
    },
    
    /**
     * Функция для связи с продавцом через Telegram
     * @param {Event} event - Событие клика
     * @param {string} username - Имя пользователя Telegram продавца
     * @param {number} productId - ID объявления
     * @param {string} productTitle - Название объявления
     * @param {string} productPrice - Цена объявления
     */
    contactSeller: function(event, username, productId, productTitle, productPrice) {
        event.preventDefault();
        
        if (!username) {
            this.showToast('Не удалось получить контакт продавца', true);
            return;
        }
        
        // Формируем ссылку на товар
        const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
        
        // Формируем текст сообщения
        let messageText = `Здравствуйте! Меня интересует "${productTitle}" за ${productPrice}.\nЕщё актуально?\n\n`;
        messageText += `Ссылка на объявление: ${productUrl}`;
        
        // Кодируем текст для URL
        const encodedText = encodeURIComponent(messageText);
        
        // Формируем ссылку для открытия чата с продавцом
        const contactUrl = `https://t.me/${username}?text=${encodedText}`;
        
        // Открываем ссылку
        window.open(contactUrl, '_blank');
    },
    
    /**
     * Запасной вариант для шеринга, если Telegram API недоступен
     * @param {number} productId - ID объявления
     * @param {string} productTitle - Название объявления
     */
    showShareFallback: function(productId, productTitle) {
        // Создаем модальное окно для шеринга
        const modalId = 'shareModal';
        let modal = document.getElementById(modalId);
        
        // Если модальное окно уже существует, удаляем его
        if (modal) {
            modal.remove();
        }
        
        // Формируем ссылку на товар
        const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
        
        // Создаем HTML для модального окна
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">Поделиться объявлением</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Скопируйте ссылку на объявление "${productTitle}":</p>
                            <div class="input-group mb-3">
                                <input type="text" class="form-control" id="shareUrl" value="${productUrl}" readonly>
                                <button class="btn btn-outline-primary" type="button" id="copyShareUrl">
                                    <i class="bi bi-clipboard"></i>
                                </button>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Добавляем модальное окно в DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Получаем созданное модальное окно
        modal = document.getElementById(modalId);
        
        // Инициализируем модальное окно
        const modalInstance = new bootstrap.Modal(modal);
        
        // Показываем модальное окно
        modalInstance.show();
        
        // Добавляем обработчик для кнопки копирования
        const copyButton = document.getElementById('copyShareUrl');
        if (copyButton) {
            copyButton.addEventListener('click', () => {
                const shareUrlInput = document.getElementById('shareUrl');
                if (shareUrlInput) {
                    shareUrlInput.select();
                    document.execCommand('copy');
                    
                    // Меняем иконку и текст кнопки на время
                    const originalContent = copyButton.innerHTML;
                    copyButton.innerHTML = '<i class="bi bi-check"></i>';
                    copyButton.classList.add('btn-success');
                    copyButton.classList.remove('btn-outline-primary');
                    
                    // Возвращаем оригинальный вид через 2 секунды
                    setTimeout(() => {
                        copyButton.innerHTML = originalContent;
                        copyButton.classList.remove('btn-success');
                        copyButton.classList.add('btn-outline-primary');
                    }, 2000);
                }
            });
        }
    },
    
    /**
     * Показать уведомление
     * @param {string} message - Текст уведомления
     * @param {boolean} isError - Флаг ошибки
     */
    showToast: function(message, isError = false) {
        // Проверяем, существует ли контейнер для уведомлений
        let toastContainer = document.getElementById('toast-container');
        
        // Если контейнера нет, создаем его
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 start-50 translate-middle-x p-3';
            toastContainer.style.zIndex = '1080';
            document.body.appendChild(toastContainer);
        }
        
        // Создаем уведомление
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center ${isError ? 'bg-danger' : 'bg-success'} text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Добавляем уведомление в контейнер
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        // Инициализируем и показываем уведомление
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 2000
        });
        toast.show();
        
        // Удаляем уведомление после скрытия
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }
};

// Инициализация модуля при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    ShareModule.init();
});

// Экспортируем функции для использования в HTML через атрибуты onclick
window.shareProduct = function(event, productId, productTitle) {
    ShareModule.shareProduct(event, productId, productTitle);
};

window.contactSeller = function(event, username, productId, productTitle, productPrice) {
    ShareModule.contactSeller(event, username, productId, productTitle, productPrice);
};

// Функция для обработки жалоб на объявление
window.reportProduct = function(event) {
    event.preventDefault();
    
    // Создаем модальное окно для отправки жалобы
    const modalId = 'reportModal';
    let modal = document.getElementById(modalId);
    
    // Если модальное окно уже существует, удаляем его
    if (modal) {
        modal.remove();
    }
    
    // Создаем HTML для модального окна
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${modalId}Label">Пожаловаться на объявление</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>Выберите причину жалобы:</p>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason1" value="spam" checked>
                            <label class="form-check-label" for="reason1">
                                Спам или мошенничество
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason2" value="prohibited">
                            <label class="form-check-label" for="reason2">
                                Запрещенные товары или услуги
                            </label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason3" value="incorrect">
                            <label class="form-check-label" for="reason3">
                                Неверная информация
                            </label>
                        </div>
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason4" value="other">
                            <label class="form-check-label" for="reason4">
                                Другое
                            </label>
                        </div>
                        <div class="mb-3">
                            <label for="reportComment" class="form-label">Комментарий (необязательно):</label>
                            <textarea class="form-control" id="reportComment" rows="3"></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                        <button type="button" class="btn btn-danger" id="submitReport">Отправить</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Добавляем модальное окно в DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Получаем созданное модальное окно
    modal = document.getElementById(modalId);
    
    // Инициализируем модальное окно
    const modalInstance = new bootstrap.Modal(modal);
    
    // Показываем модальное окно
    modalInstance.show();
    
    // Добавляем обработчик для кнопки отправки жалобы
    const submitButton = document.getElementById('submitReport');
    if (submitButton) {
        submitButton.addEventListener('click', () => {
            // Здесь можно добавить логику отправки жалобы на сервер
            
            // Закрываем модальное окно
            modalInstance.hide();
            
            // Показываем уведомление
            ShareModule.showToast('Жалоба отправлена. Спасибо за обращение!');
        });
    }
};
