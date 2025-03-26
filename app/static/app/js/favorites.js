document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки добавления в избранное
    const favoriteBtns = document.querySelectorAll('.favorite-btn');
    
    // Добавляем обработчик для каждой кнопки
    favoriteBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const isFavorite = this.dataset.isFavorite === 'true';
            
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
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновляем состояние кнопки
                    this.dataset.isFavorite = data.is_favorite.toString();
                    
                    // Обновляем иконку
                    const icon = this.querySelector('i');
                    if (data.is_favorite) {
                        icon.classList.remove('bi-heart');
                        icon.classList.add('bi-heart-fill');
                    } else {
                        icon.classList.remove('bi-heart-fill');
                        icon.classList.add('bi-heart');
                    }
                    
                    // Если мы на странице избранного и удалили из избранного, удаляем карточку
                    if (!data.is_favorite && window.location.pathname.includes('/favorites/')) {
                        const productCard = this.closest('.col-6');
                        if (productCard) {
                            // Анимация удаления
                            productCard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                            productCard.style.opacity = '0';
                            productCard.style.transform = 'scale(0.9)';
                            
                            // Удаляем элемент после анимации
                            setTimeout(() => {
                                productCard.remove();
                                
                                // Проверяем, остались ли еще карточки
                                const remainingCards = document.querySelectorAll('.favorites-page .col-6');
                                if (remainingCards.length === 0) {
                                    // Если карточек не осталось, показываем пустое состояние
                                    const row = document.querySelector('.favorites-page .row');
                                    row.innerHTML = `
                                        <div class="col-12">
                                            <div class="empty-favorites text-center py-5">
                                                <div class="empty-icon mb-3">
                                                    <i class="bi bi-heart text-danger fs-1"></i>
                                                </div>
                                                <h5 class="mb-3">Нет избранных объявлений</h5>
                                                <p class="text-muted mb-4">Добавляйте понравившиеся объявления в избранное, чтобы быстро находить их позже</p>
                                                <a href="/" class="btn btn-primary">
                                                    <i class="bi bi-search me-2"></i>Найти объявления
                                                </a>
                                            </div>
                                        </div>
                                    `;
                                }
                            }, 300);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        });
    });
    
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
});
