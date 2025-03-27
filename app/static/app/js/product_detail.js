document.addEventListener('DOMContentLoaded', function() {
    // Проверяем доступность Telegram Web App API
    const tg = window.Telegram && window.Telegram.WebApp;
    if (!tg) return;
    
    // Показываем кнопку назад Telegram
    if (tg.BackButton) {
        tg.BackButton.show();
        
        // Обработчик нажатия на кнопку назад
        tg.onEvent('backButtonClicked', function() {
            // Вызываем тактильную обратную связь при нажатии на кнопку назад
            if (tg.HapticFeedback) {
                tg.HapticFeedback.impactOccurred('medium');
            }
            
            // Возвращаемся на предыдущую страницу
            window.history.back();
        });
    }
    
    // Инициализация Main Button
    const mainButton = tg.MainButton;
    if (!mainButton) return;
    
    // Получаем данные для связи с продавцом из data-атрибутов
    const contactButton = document.querySelector('[data-action="contact"]');
    if (!contactButton) return;
    
    const username = contactButton.dataset.username;
    const productId = contactButton.dataset.productId;
    const productTitle = contactButton.dataset.productTitle;
    const productPrice = contactButton.dataset.productPrice;
    
    // Настройка Main Button
    mainButton.setText('Связаться с продавцом');
    mainButton.hide(); // Изначально скрываем кнопку
    
    // Переменные для плавного появления/исчезновения
    let mainButtonVisibilityTimeout;
    const VISIBILITY_DELAY = 200; // Задержка в миллисекундах
    
    // Обработчик нажатия на Main Button
    mainButton.onClick(function() {
        // Вызываем тактильную обратную связь при нажатии на Main Button
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('medium');
        }
        
        // Используем функцию из share.js для связи с продавцом
        if (typeof window.contactSeller === 'function') {
            window.contactSeller(new Event('click'), username, productId, productTitle, productPrice);
        } else {
            // Запасной вариант, если функция недоступна
            const productUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
            let messageText = `Здравствуйте! Меня интересует "${productTitle}" за ${productPrice}.\nЕщё актуально?\n\n`;
            messageText += `Ссылка на объявление: ${productUrl}`;
            const encodedText = encodeURIComponent(messageText);
            const contactUrl = `https://t.me/${username}?text=${encodedText}`;
            window.open(contactUrl, '_blank');
        }
    });
    
    // Функция для проверки видимости обычной кнопки связи
    function isContactButtonVisible() {
        if (!contactButton) return false;
        
        const rect = contactButton.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Функция для проверки, находится ли пользователь близко к концу страницы
    function isNearBottom() {
        const scrollPosition = window.scrollY + window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const nearBottomThreshold = 300; // Пикселей от низа страницы
        
        return documentHeight - scrollPosition < nearBottomThreshold;
    }
    
    // Функция для обновления состояния Main Button в зависимости от прокрутки
    function updateMainButtonVisibility() {
        // Если мы не автор объявления
        const isAuthor = document.body.dataset.isAuthor === 'true';
        
        if (!isAuthor) {
            // Очищаем предыдущий таймаут, чтобы избежать мерцания
            clearTimeout(mainButtonVisibilityTimeout);
            
            mainButtonVisibilityTimeout = setTimeout(() => {
                // Показываем кнопку, если обычная кнопка не видна ИЛИ пользователь близок к концу страницы
                if (!isContactButtonVisible() || isNearBottom()) {
                    mainButton.show();
                } else {
                    mainButton.hide();
                }
            }, VISIBILITY_DELAY);
        }
    }
    
    // Обработчик события прокрутки с дебаунсингом для производительности
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(updateMainButtonVisibility, 50);
    });
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', function() {
        updateMainButtonVisibility();
    });
    
    // Обработчик изменения ориентации устройства
    window.addEventListener('orientationchange', function() {
        // Небольшая задержка для корректного пересчета размеров
        setTimeout(updateMainButtonVisibility, 300);
    });
    
    // Инициализация при загрузке страницы
    updateMainButtonVisibility();
    
    // Дополнительная проверка через 1 секунду после загрузки
    // для случаев, когда контент загружается асинхронно
    setTimeout(updateMainButtonVisibility, 1000);
});

// Скрываем кнопки при уходе со страницы
window.addEventListener('beforeunload', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
        if (tg.BackButton) tg.BackButton.hide();
        if (tg.MainButton) tg.MainButton.hide();
    }
});
