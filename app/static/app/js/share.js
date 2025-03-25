/**
 * Функция для шеринга объявления через Telegram
 * @param {Event} event - Событие клика
 * @param {number} productId - ID объявления
 * @param {string} productTitle - Название объявления
 */
function shareProduct(event, productId, productTitle) {
    event.preventDefault();
    
    // Проверяем, доступен ли Telegram Web App API
    const tg = window.Telegram && window.Telegram.WebApp;
    
    if (tg) {
        // Формируем текст для шеринга
        const shareText = `Объявление "${productTitle}" в Capybara\n\n`;
        
        // Формируем ссылку на бота с параметром start
        const shareUrl = `https://t.me/CapybaraMPRobot?start=product_${productId}`;
        
        // Используем Telegram API для шеринга
        tg.shareUrl(shareUrl);
    } else {
        // Запасной вариант, если API недоступен
        alert('Для шеринга используйте Telegram');
    }
}

