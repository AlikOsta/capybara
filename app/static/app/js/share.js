/**
 * Модуль для шеринга объявлений и связи с продавцами.
 * Содержит функции для работы с Telegram API и запасной функционал для случаев недоступности API.
 */
const ShareModule = {
    /**
     * Инициализация модуля.
     */
    init: function() {
        // Проверяем доступность Telegram Web App API
        this.telegramApp = window.Telegram && window.Telegram.WebApp;
        // Инициализируем обработчики событий
        this.initEventListeners();
    },

    /**
     * Инициализация обработчиков событий для кнопок шеринга и связи с продавцом.
     */
    initEventListeners: function() {
        // Обработчики для кнопок шеринга
        const shareButtons = document.querySelectorAll('[data-action="share"]');
        shareButtons.forEach((button) => {
            button.addEventListener('click', (event) => {
                event.preventDefault();
                const productId = button.dataset.productId;
                const productTitle = button.dataset.productTitle;
                this.shareProduct(event, productId, productTitle);
            });
        });

        // Обработчики для кнопок связи с продавцом
        const contactButtons = document.querySelectorAll('[data-action="contact"]');
        contactButtons.forEach((button) => {
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
     * Делает шеринга объявления через Telegram.
     * @param {Event} event - Событие клика.
     * @param {number} productId - ID объявления.
     * @param {string} productTitle - Название объявления.
     */
    shareProduct: function(event, productId, productTitle) {
        event.preventDefault();
        // Проверяем, доступен ли Telegram Web App API
        if (this.telegramApp) {
            // Формируем ссылку на бота с параметром start
            const shareUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
            
            // Используем правильный метод Telegram API
            if (typeof this.telegramApp.shareUrl === 'function') {
                // Если метод shareUrl существует (возможно в новых версиях)
                this.telegramApp.shareUrl(shareUrl);
            } else if (typeof this.telegramApp.openTelegramLink === 'function') {
                // Для открытия ссылок внутри Telegram
                this.telegramApp.openTelegramLink(shareUrl);
            } else if (typeof this.telegramApp.openLink === 'function') {
                // Для открытия внешних ссылок
                this.telegramApp.openLink(shareUrl);
            } else {
                // Если ни один из методов не доступен, используем запасной вариант
                this.showShareFallback(productId, productTitle);
            }
        } else {
            // Запасной вариант, если API недоступен
            this.showShareFallback(productId, productTitle);
        }
    },

    /**
     * Открывает чат с продавцом через Telegram.
     * @param {Event} event - Событие клика.
     * @param {string} username - Имя пользователя Telegram продавца.
     * @param {number} productId - ID объявления.
     * @param {string} productTitle - Название объявления.
     * @param {string} productPrice - Цена объявления.
     */
    contactSeller: function(event, username, productId, productTitle, productPrice) {
        event.preventDefault();
        if (!username) {
            this.showToast('Не удалось получить контакт продавца', true);
            return;
        }
        const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
        let messageText = `Здравствуйте! Меня интересует "${productTitle}" за ${productPrice}.\nЕщё актуально?\n\n`;
        messageText += `Ссылка на объявление: ${productUrl}`;
        const encodedText = encodeURIComponent(messageText);
        const contactUrl = `https://t.me/${username}?text=${encodedText}`;
        window.open(contactUrl, '_blank');
    },

    /**
     * Запасной вариант шеринга – выводит модальное окно с ссылкой.
     * @param {number} productId - ID объявления.
     * @param {string} productTitle - Название объявления.
     */
    showShareFallback: function(productId, productTitle) {
        const modalId = 'shareModal';
        let modal = document.getElementById(modalId);
        if (modal) {
            modal.remove();
        }
        const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
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
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        modal = document.getElementById(modalId);
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();

        const copyButton = document.getElementById('copyShareUrl');
        if (copyButton) {
            copyButton.addEventListener('click', () => {
                const shareUrlInput = document.getElementById('shareUrl');
                if (shareUrlInput) {
                    shareUrlInput.select();
                    document.execCommand('copy');
                    const originalContent = copyButton.innerHTML;
                    copyButton.innerHTML = '<i class="bi bi-check"></i>';
                    copyButton.classList.add('btn-success');
                    copyButton.classList.remove('btn-outline-primary');
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
     * Показывает уведомление (toast) на экране.
     * @param {string} message - Текст уведомления.
     * @param {boolean} [isError=false] - Флаг ошибки (если true, уведомление будет красным).
     */
    showToast: function(message, isError = false) {
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 start-50 translate-middle-x p-3';
            toastContainer.style.zIndex = '1080';
            document.body.appendChild(toastContainer);
        }
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
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 2000 });
        toast.show();
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }
};

// Инициализация модуля после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    ShareModule.init();
});

// Экспорт функций для использования в HTML через атрибуты onclick
window.shareProduct = function(event, productId, productTitle) {
    ShareModule.shareProduct(event, productId, productTitle);
};

window.contactSeller = function(event, username, productId, productTitle, productPrice) {
    ShareModule.contactSeller(event, username, productId, productTitle, productPrice);
};

/**
 * Функция для обработки жалоб на объявление.
 * Открывает модальное окно с выбором причины жалобы.
 */
window.reportProduct = function(event) {
    event.preventDefault();
    const modalId = 'reportModal';
    let modal = document.getElementById(modalId);
    if (modal) {
        modal.remove();
    }
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
                            <label class="form-check-label" for="reason1">Спам или мошенничество</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason2" value="prohibited">
                            <label class="form-check-label" for="reason2">Запрещенные товары или услуги</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason3" value="incorrect">
                            <label class="form-check-label" for="reason3">Неверная информация</label>
                        </div>
                        <div class="form-check mb-3">
                            <input class="form-check-input" type="radio" name="reportReason" id="reason4" value="other">
                            <label class="form-check-label" for="reason4">Другое</label>
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
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    modal = document.getElementById(modalId);
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
    const submitButton = document.getElementById('submitReport');
    if (submitButton) {
        submitButton.addEventListener('click', () => {
            // Здесь можно добавить логику отправки жалобы на сервер
            modalInstance.hide();
            ShareModule.showToast('Жалоба отправлена. Спасибо за обращение!');
        });
    }
};
