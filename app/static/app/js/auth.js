// Функция для проверки авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, есть ли токен в localStorage
    const accessToken = localStorage.getItem('access_token');
    
    if (accessToken) {
        console.log('Токен найден в localStorage');
        
        // Добавляем токен к каждому запросу
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            options = options || {};
            options.headers = options.headers || {};
            
            // Добавляем заголовок Authorization только если его еще нет
            if (!options.headers['Authorization']) {
                options.headers['Authorization'] = 'Bearer ' + accessToken;
            }
            
            // Включаем передачу cookies
            options.credentials = 'include';
            
            return originalFetch(url, options);
        };
        
        // Добавляем токен в заголовок для AJAX запросов jQuery, если jQuery используется
        if (window.jQuery) {
            jQuery.ajaxSetup({
                beforeSend: function(xhr) {
                    xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
                }
            });
        }
        
        // Добавляем токен в мета-тег для использования в CSRF защите Django
        const meta = document.createElement('meta');
        meta.name = 'jwt-token';
        meta.content = accessToken;
        document.head.appendChild(meta);
    }
});
