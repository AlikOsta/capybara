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
});

// Скрываем кнопку назад при уходе со страницы
window.addEventListener('beforeunload', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg && tg.BackButton) {
        tg.BackButton.hide();
    }
});
