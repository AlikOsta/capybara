/**
 * Модуль для динамического поиска на главной странице
 */
document.addEventListener('DOMContentLoaded', function() {
    initDynamicSearch();
});

function initDynamicSearch() {
    // Получаем элементы DOM
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const productsContainer = document.getElementById('products-container');
    
    // Если элементы не найдены, выходим
    if (!searchForm || !searchInput || !productsContainer) return;
    
    // Текущий поисковый запрос
    let currentQuery = searchInput.value || '';
    
    // Функция для обновления списка товаров
    function updateProductsList() {
        // Показываем индикатор загрузки
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'block';
        
        // Скрываем сообщение об ошибке, если оно отображается
        const errorElement = document.getElementById('error-message');
        if (errorElement) errorElement.style.display = 'none';
        
        // Формируем URL для API запроса
        const params = new URLSearchParams();
        if (currentQuery) params.append('q', currentQuery);
        params.append('offset', 0);
        params.append('limit', 20);
        
        const apiUrl = `/api/products/?${params.toString()}`;
        
        // Обновляем URL страницы без перезагрузки
        const pageUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.pushState({ path: pageUrl }, '', pageUrl);
        
        // Выполняем AJAX запрос
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка загрузки данных');
                return response.json();
            })
            .then(data => {
                // Обновляем содержимое контейнера
                productsContainer.innerHTML = data.html;
                
                // Обновляем атрибуты для бесконечной прокрутки
                productsContainer.dataset.offset = data.next_offset || 0;
                productsContainer.dataset.hasMore = data.has_more;
                
                // Инициализируем кнопки избранного для новых карточек
                if (typeof window.initFavoriteButtons === 'function') {
                    window.initFavoriteButtons();
                }
                
                // Показываем сообщение, если нет результатов
                if (data.html.trim() === '') {
                    productsContainer.innerHTML = `
                        <div class="col-12 text-center py-5">
                            <div class="empty-state">
                                <i class="bi bi-inbox fs-1 text-muted mb-3"></i>
                                <p class="text-muted">По вашему запросу ничего не найдено</p>
                                ${currentQuery ? `<button id="clear-search-btn" class="btn btn-outline-primary mt-2">Сбросить поиск</button>` : ''}
                            </div>
                        </div>
                    `;
                    
                    // Добавляем обработчик для кнопки сброса поиска
                    const clearSearchBtn = document.getElementById('clear-search-btn');
                    if (clearSearchBtn) {
                        clearSearchBtn.addEventListener('click', function() {
                            searchInput.value = '';
                            currentQuery = '';
                            updateProductsList();
                        });
                    }
                }
                
                // Обновляем счетчик товаров, если он есть
                const countBadge = document.querySelector('.badge.bg-light.text-dark.rounded-pill');
                if (countBadge) {
                    countBadge.textContent = data.total_count;
                }
                
                // Анимируем появление элементов
                animateProductItems();
            })
            .catch(error => {
                console.error('Ошибка:', error);
                // Показываем сообщение об ошибке
                if (errorElement) errorElement.style.display = 'block';
            })
            .finally(() => {
                // Скрываем индикатор загрузки
                if (loader) loader.style.display = 'none';
            });
    }
    
    // Функция для анимации элементов списка
    function animateProductItems() {
        const productItems = document.querySelectorAll('.product-item');
        productItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50 * index);
        });
    }
    
    // Обработчик отправки формы поиска
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentQuery = searchInput.value;
        updateProductsList();
    });
    
    // Обработчик ввода в поле поиска (для мгновенного поиска)
    searchInput.addEventListener('input', function() {
        // Добавляем debounce для предотвращения слишком частых запросов
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            currentQuery = this.value;
            updateProductsList();
        }, 500); // Задержка 500 мс
    });
    
    // Обработчик нажатия клавиши Enter в поле поиска
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            currentQuery = this.value;
            updateProductsList();
        }
    });
    
    // Инициализация InfiniteScrollModule с учетом динамического поиска
    if (window.InfiniteScrollModule) {
        const originalLoadMoreProducts = window.InfiniteScrollModule.loadMoreProducts;
        
        window.InfiniteScrollModule.loadMoreProducts = function() {
            if (this.settings.isLoading || !this.settings.hasMore) return;
            
            this.settings.isLoading = true;
            this.showLoader();
            
            // Используем текущий поисковый запрос для загрузки следующей страницы
            const params = new URLSearchParams();
            if (currentQuery) params.append('q', currentQuery);
            params.append('offset', this.settings.offset);
            params.append('limit', this.settings.limit);
            
            const apiUrl = `/api/products/?${params.toString()}`;
            
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) throw new Error('Ошибка загрузки данных');
                    return response.json();
                })
                .then(data => {
                    if (data.html) {
                        this.appendNewProducts(data.html);
                        this.settings.offset = data.next_offset || this.settings.offset;
                        this.settings.hasMore = data.has_more;
                        
                        if (!this.settings.hasMore && this.elements.endMessageElement) {
                            this.elements.endMessageElement.style.display = 'block';
                        }
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    if (this.elements.errorElement) {
                        this.elements.errorElement.style.display = 'block';
                    }
                })
                .finally(() => {
                    this.hideLoader();
                    this.settings.isLoading = false;
                });
        };
    }
    
    // Обработчик для кнопки повторной попытки при ошибке
    const retryButton = document.getElementById('retry-button');
    if (retryButton) {
        retryButton.addEventListener('click', function() {
            const errorElement = document.getElementById('error-message');
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            updateProductsList();
        });
    }
    
    // Анимируем элементы при первой загрузке
    animateProductItems();
}
