// Функция для проверки авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли токен в localStorage
    const accessToken = localStorage.getItem('access_token');
    
    if (accessToken) {
        // Добавляем токен к каждому запросу
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            options = options || {};
            options.headers = options.headers || {};
            options.headers['Authorization'] = 'Bearer ' + accessToken;
            options.credentials = 'include';
            return originalFetch(url, options);
        };
    }
});
