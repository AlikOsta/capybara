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

/**
 * Функция для связи с продавцом через Telegram
 * @param {Event} event - Событие клика
 * @param {string} username - Имя пользователя Telegram продавца
 * @param {number} productId - ID объявления
 * @param {string} productTitle - Название объявления
 * @param {string} productPrice - Цена объявления
 */
function contactSeller(event, username, productId, productTitle, productPrice) {
    event.preventDefault();
    
    if (!username) {
        alert('Не удалось получить контакт продавца');
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
}