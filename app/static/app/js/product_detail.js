document.addEventListener('DOMContentLoaded', function() {
    applyMainButtonAnimation();

    const tg = window.Telegram && window.Telegram.WebApp;
    // if (!tg) return;

    // Настраиваем кнопку "Назад"
    if (tg.BackButton) {
        tg.BackButton.show();
        tg.onEvent('backButtonClicked', function() {
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('medium');
            }
            window.history.back();
        });
    }

    // Инициализируем MainButton
    const mainButton = tg.MainButton;
    if (!mainButton) return;

    // Ссылка на нижнее меню
    const footer = document.querySelector('footer.fixed-bottom');

    // Получаем данные для связи из элемента .product-detail
    const productDetail = document.querySelector('.product-detail');
    if (!productDetail) return;
    const { username, productId, productTitle, productPrice, isAuthor } = productDetail.dataset;

    // Настраиваем MainButton
    mainButton.setText('Связаться с продавцом');
    mainButton.hide(); // Изначально скрываем кнопку

    // Параметры анимации
    const ANIMATION_DURATION = 100;

    // Обработчик клика по MainButton
    mainButton.onClick(function() {
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('medium');
        }
        if (typeof window.contactSeller === 'function') {
            window.contactSeller(new Event('click'), username, productId, productTitle, productPrice);
        } else {
            const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
            let messageText = `Здравствуйте! Меня интересует "${productTitle}" за ${productPrice}.\nЕщё актуально?\n\n`;
            messageText += `Ссылка на объявление: ${productUrl}`;
            const encodedText = encodeURIComponent(messageText);
            const contactUrl = `https://t.me/${username}?text=${encodedText}`;
            window.open(contactUrl, '_blank');
        }
    });

    // Функция показа MainButton с анимацией
    function showMainButton() {
        if (footer) footer.classList.add('hidden');
        setTimeout(() => {
            mainButton.show();
            document.body.classList.add('main-button-visible');
            const btnElem = document.querySelector('.telegram-main-button');
            if (btnElem) btnElem.classList.remove('hidden');
        }, ANIMATION_DURATION / 2);
    }

    function hideMainButton() {
        const btnElem = document.querySelector('.telegram-main-button');
        if (btnElem) btnElem.classList.add('hidden');
        setTimeout(() => {
            mainButton.hide();
            document.body.classList.remove('main-button-visible');
            if (footer) footer.classList.remove('hidden');
        }, ANIMATION_DURATION / 2);
    }

    function updateMainButtonVisibility() {
        if (isAuthor === 'true') {
            hideMainButton();
        } else {
            showMainButton();
        }
    }

    updateMainButtonVisibility();
    
    setTimeout(updateMainButtonVisibility, 1000);
});

// Скрытие кнопок при уходе со страницы
window.addEventListener('beforeunload', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
        if (tg.MainButton) tg.MainButton.hide();
    }
    const footer = document.querySelector('footer.fixed-bottom');
    if (footer) footer.classList.remove('hidden');
    document.body.classList.remove('main-button-visible');
});

// Скрытие MainButton при нажатии кнопки назад браузера
window.addEventListener('popstate', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg && tg.MainButton) tg.MainButton.hide();
    const footer = document.querySelector('footer.fixed-bottom');
    if (footer) footer.classList.remove('hidden');
    document.body.classList.remove('main-button-visible');
});

// Функция для применения анимации к MainButton
function applyMainButtonAnimation() {
    if (!document.querySelector('#telegram-main-button-styles')) {
        const style = document.createElement('style');
        style.id = 'telegram-main-button-styles';
        style.textContent = `
            .telegram-main-button {
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                            opacity 0.3s ease !important;
                transform: translateY(0) !important;
                opacity: 1 !important;
            }
            .telegram-main-button.hidden {
                transform: translateY(100%) !important;
                opacity: 0 !important;
            }
            footer.fixed-bottom {
                transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            footer.fixed-bottom.hidden {
                transform: translateY(100%);
            }
            body.main-button-visible {
                padding-bottom: 70px !important;
                transition: padding-bottom 0.3s ease;
            }
        `;
        document.head.appendChild(style);
    }
}
