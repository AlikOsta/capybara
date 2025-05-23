document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing favorite buttons...');
    initFavoriteButtons();
});

// Добавляем обработчик события htmx:afterSwap
document.addEventListener('htmx:afterSwap', function() {
    console.log('HTMX content loaded, reinitializing favorite buttons...');
    initFavoriteButtons();
});

// Функция для инициализации кнопок избранного
function initFavoriteButtons() {
    const favoriteBtns = document.querySelectorAll('.favorite-btn:not(.initialized)');
    console.log(`Found ${favoriteBtns.length} favorite buttons to initialize`);
    
    favoriteBtns.forEach(btn => {
        btn.classList.add('initialized');
        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const isFavorite = this.dataset.isFavorite === 'true';
            
            console.log(`Toggle favorite for product ${productId}, current state: ${isFavorite}`);
            
            // Добавляем визуальный отклик при клике
            this.classList.add('clicked');
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 300);
            
            // Отправляем AJAX запрос
            fetch(`/product/${productId}/favorite/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => {
                console.log(`Server response status: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`Network error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Server response data:', data);
                
                if (data.success) {
                    // Обновляем состояние кнопки
                    this.dataset.isFavorite = data.is_favorite.toString();
                    console.log(`Updated button state to: ${data.is_favorite}`);
                    
                    // Обновляем иконку
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                        
                        // Если мы на странице избранного и удалили из избранного, 
                        // отправляем событие для обновления списка
                        if (window.location.pathname.includes('/favorites/') || 
                            document.querySelector('.favorites-page')) {
                            console.log('Triggering favoriteListChanged event');
                            
                            // Отправляем событие для HTMX
                            document.body.dispatchEvent(
                                new CustomEvent('favoriteListChanged', {
                                    bubbles: true
                                })
                            );
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при обновлении избранного. Пожалуйста, попробуйте еще раз.');
            });
        });
    });
}

// Функция для получения CSRF токена из cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Экспортируем функцию для использования в других скриптах
window.initFavoriteButtons = initFavoriteButtons;

console.log('favorites.js loaded');
