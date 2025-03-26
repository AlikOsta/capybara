/**
 * Бесконечная лента для загрузки объявлений
 */
document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const productsContainer = document.getElementById('products-container');
    const loaderElement = document.getElementById('loader');
    const endMessageElement = document.getElementById('end-message');
    const errorElement = document.getElementById('error-message');
    const backToTopButton = document.getElementById('back-to-top');
    
    
    // Параметры
    let isLoading = false;
    let offset = productsContainer ? parseInt(productsContainer.dataset.offset || 20) : 20;
    let limit = 6; // Изменено с 10 на 20
    let hasMore = productsContainer ? productsContainer.dataset.hasMore === 'true' : true;

    // Получаем текущие параметры URL
    const urlParams = new URLSearchParams(window.location.search);

    // Создаем Intersection Observer для отслеживания прокрутки
    if (productsContainer && loaderElement) {
        const observer = new IntersectionObserver((entries) => {
            // Если загрузчик виден и не идет загрузка и есть еще объявления
            if (entries[0].isIntersecting && !isLoading && hasMore) {
                loadMoreProducts();
            }
        }, { threshold: 0.2 }); // Изменено с 0.1 на 0.2
        
        // Начинаем наблюдение за загрузчиком
        observer.observe(loaderElement);
    }

    // Добавляем отслеживание процента прокрутки страницы
    window.addEventListener('scroll', function() {
        // Вычисляем процент прокрутки
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        
        // Если прокручено 80% страницы и не идет загрузка и есть еще объявления
        if (scrollPercentage >= 80 && !isLoading && hasMore) {
            loadMoreProducts();
        }
        
        // Показываем/скрываем кнопку "Наверх"
        if (backToTopButton) {
            if (scrollTop > 1000) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        }
    });
    
    // Функция для загрузки дополнительных объявлений
    function loadMoreProducts() {
        if (isLoading || !hasMore) return;
        
        isLoading = true;
        showLoader();
        
        // Определяем URL для запроса в зависимости от текущей страницы
        let apiUrl;
        let params = new URLSearchParams();
        
        // Добавляем параметры пагинации
        params.append('offset', offset);
        params.append('limit', limit);
        
        // Добавляем все текущие параметры URL
        for (const [key, value] of urlParams.entries()) {
            if (key !== 'page') { // Исключаем параметр page, так как используем offset
                params.append(key, value);
            }
        }
        
        // Определяем URL API в зависимости от текущей страницы
        const path = window.location.pathname;
        if (path.includes('/category/')) {
            const categorySlug = path.split('/category/')[1].replace('/', '');
            apiUrl = `/api/category/${categorySlug}/products/?${params.toString()}`;
        } else if (path === '/' || path === '') {
            apiUrl = `/api/products/?${params.toString()}`;
        } else if (path.includes('/favorites/')) {
            apiUrl = `/api/favorites/?${params.toString()}`;
        } else {
            // Если мы на странице, которая не поддерживает бесконечную ленту
            hideLoader();
            isLoading = false;
            return;
        }
        
        // Выполняем AJAX-запрос
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка загрузки данных');
                }
                return response.json();
            })
            .then(data => {
                // Если есть HTML для добавления
                if (data.html) {
                    // Создаем временный контейнер для парсинга HTML
                    const tempContainer = document.createElement('div');
                    tempContainer.innerHTML = data.html;
                    
                    // Добавляем новые элементы с анимацией
                    const productItems = tempContainer.querySelectorAll('.product-item');
                    productItems.forEach(item => {
                        item.style.opacity = '0';
                        item.style.transform = 'translateY(20px)';
                        productsContainer.appendChild(item);
                        
                        // Анимируем появление
                        setTimeout(() => {
                            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        }, 10);
                    });
                    
                    // Инициализируем обработчики для кнопок избранного
                    initFavoriteButtons();
                    
                    // Обновляем параметры
                    offset = data.next_offset || offset;
                    hasMore = data.has_more;
                    
                    // Показываем сообщение о конце списка, если больше нет объявлений
                    if (!hasMore && endMessageElement) {
                        endMessageElement.style.display = 'block';
                    }
                    
                    // Показываем кнопку "Наверх", если прокрутили достаточно далеко
                    if (backToTopButton && window.pageYOffset > 1000) {
                        backToTopButton.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                if (errorElement) {
                    errorElement.style.display = 'block';
                }
            })
            .finally(() => {
                hideLoader();
                isLoading = false;
            });
    }
    
    // Функция для показа индикатора загрузки
    function showLoader() {
        if (loaderElement) {
            loaderElement.style.display = 'block';
        }
    }
    
    // Функция для скрытия индикатора загрузки
    function hideLoader() {
        if (loaderElement) {
            loaderElement.style.display = 'none';
        }
    }
    
    // Обработчик для кнопки "Наверх"
    if (backToTopButton) {
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Показываем/скрываем кнопку "Наверх" при прокрутке
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 1000) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
    }
    
    // Обработчик для кнопки повторной попытки
    const retryButton = document.getElementById('retry-button');
    if (retryButton) {
        retryButton.addEventListener('click', function() {
            errorElement.style.display = 'none';
            loadMoreProducts();
        });
    }
});

// Функция для инициализации кнопок избранного для новых элементов
function initFavoriteButtons() {
    const newFavoriteButtons = document.querySelectorAll('.favorite-btn:not(.initialized)');
    
    newFavoriteButtons.forEach(btn => {
        btn.classList.add('initialized');
        
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
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
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


