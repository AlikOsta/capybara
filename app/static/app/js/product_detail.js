document.addEventListener('DOMContentLoaded', function() {
    // Получаем данные для связи из элемента .product-detail
    const productDetail = document.querySelector('.product-detail');
    if (!productDetail) return;
    
    const { username, productId, productTitle, productPrice, isAuthor } = productDetail.dataset;
    
    // Находим кнопку "Связаться с продавцом"
    const contactSellerBtn = document.getElementById('contactSellerBtn');
    
    // Если пользователь - автор объявления или кнопка не найдена, выходим
    if (isAuthor === 'true' || !contactSellerBtn) return;
    
    // Добавляем обработчик клика на кнопку
    contactSellerBtn.addEventListener('click', function() {
        // Формируем URL для перехода в Telegram
        const productUrl = `https://t.me/CapybaraMarketplaceRobot?start=product_${productId}`;
        
        let messageText = `Здравствуйте!\n Меня интересует "${productTitle}" за ${productPrice}.\n\nЕщё актуально?\n\n`;
        messageText += `Ссылка на объявление: ${productUrl}`;
        
        // Открываем ссылку на чат с продавцом
        window.open(`https://t.me/${username}?text=${encodeURIComponent(messageText)}`, '_blank');
    });
    
    // Добавляем эффект нажатия на кнопку
    contactSellerBtn.addEventListener('mousedown', function() {
        this.style.transform = 'scale(0.98)';
        this.style.opacity = '0.9';
    });
    
    contactSellerBtn.addEventListener('mouseup', function() {
        this.style.transform = 'scale(1)';
        this.style.opacity = '1';
    });
    
    // Добавляем стили для кнопки
    const style = document.createElement('style');
    style.textContent = `
        #contactSellerBtn {
            transition: transform 0.2s ease, opacity 0.2s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        #contactSellerBtn:hover {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        }
        
        #contactSellerBtn:active {
            transform: scale(0.98);
            opacity: 0.9;
        }
    `;
    document.head.appendChild(style);
});
