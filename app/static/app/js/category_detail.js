document.addEventListener('DOMContentLoaded', function() {
    // Проверяем доступность Telegram Web App API
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg && tg.BackButton) {
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

    // Инициализация динамической фильтрации
    initDynamicFiltering();
});

function initDynamicFiltering() {
    // Получаем элементы фильтров
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');
    const citySelect = document.getElementById('city-select');
    const currencySelect = document.getElementById('currency-select');
    const resetButton = document.getElementById('reset-filters');
    const productsContainer = document.getElementById('products-container');
    
    // Получаем slug категории из URL
    const pathParts = window.location.pathname.split('/');
    const categorySlug = pathParts[pathParts.indexOf('category') + 1];
    
    // Текущие параметры фильтрации
    let currentFilters = {
        q: searchInput.value || '',
        sort: sortSelect.value || '',
        city: citySelect.value || '',
        currency: currencySelect.value || '',
        offset: 0,
        limit: 20
    };
    
    // Функция для обновления списка товаров
    function updateProductsList() {
        // Показываем индикатор загрузки
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'block';
        
        // Формируем URL для API запроса
        const params = new URLSearchParams();
        for (const [key, value] of Object.entries(currentFilters)) {
            if (value) params.append(key, value);
        }
        
        const apiUrl = `/api/category/${categorySlug}/products/?${params.toString()}`;
        
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
                                <button id="clear-filters-btn" class="btn btn-outline-primary mt-2">Сбросить фильтры</button>
                            </div>
                        </div>
                    `;
                    document.getElementById('clear-filters-btn').addEventListener('click', resetFilters);
                }
                
                // Обновляем счетчик товаров, если он есть
                const countBadge = document.querySelector('.badge.bg-light.text-dark.rounded-pill');
                if (countBadge) {
                    countBadge.textContent = data.total_count;
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                // Показываем сообщение об ошибке
                const errorElement = document.getElementById('error-message');
                if (errorElement) errorElement.style.display = 'block';
            })
            .finally(() => {
                // Скрываем индикатор загрузки
                if (loader) loader.style.display = 'none';
                
                // Обновляем блок активных фильтров
                updateActiveFilters();
            });
    }
    
    // Функция для сброса всех фильтров
    function resetFilters() {
        searchInput.value = '';
        sortSelect.value = '';
        citySelect.value = '';
        currencySelect.value = '';
        
        currentFilters = {
            q: '',
            sort: '',
            city: '',
            currency: '',
            offset: 0,
            limit: 20
        };
        
        updateProductsList();
    }
    
    // Функция для обновления блока активных фильтров
    function updateActiveFilters() {
        // Находим или создаем контейнер для активных фильтров
        let activeFiltersContainer = document.querySelector('.active-filters');
        if (!activeFiltersContainer) {
            const filtersSection = document.querySelector('.filters-section');
            activeFiltersContainer = document.createElement('div');
            activeFiltersContainer.className = 'active-filters mt-3';
            filtersSection.appendChild(activeFiltersContainer);
        }
        
        // Проверяем, есть ли активные фильтры
        const hasActiveFilters = currentFilters.q || currentFilters.sort || 
                                currentFilters.city || currentFilters.currency;
        
        // Если нет активных фильтров, скрываем контейнер
        if (!hasActiveFilters) {
            activeFiltersContainer.style.display = 'none';
            return;
        }
        
        // Создаем HTML для активных фильтров
        let filtersHTML = '<div class="d-flex flex-wrap gap-2">';
        
        // Фильтр поиска
        if (currentFilters.q) {
            filtersHTML += `
                <span class="badge bg-light text-dark text-decoration-none py-2 px-3 filter-badge" data-filter="q">
                    Поиск: ${currentFilters.q} <i class="bi bi-x-circle ms-1"></i>
                </span>
            `;
        }
        
        // Фильтр сортировки
        if (currentFilters.sort) {
            let sortText = '';
            switch (currentFilters.sort) {
                case 'price_asc': sortText = 'Сначала дешевле'; break;
                case 'price_desc': sortText = 'Сначала дороже'; break;
                case 'date_desc': sortText = 'Сначала новые'; break;
                case 'date_asc': sortText = 'Сначала старые'; break;
            }
            filtersHTML += `
                <span class="badge bg-light text-dark text-decoration-none py-2 px-3 filter-badge" data-filter="sort">
                    ${sortText} <i class="bi bi-x-circle ms-1"></i>
                </span>
            `;
        }
        
        // Фильтр города
        if (currentFilters.city) {
            const cityOption = citySelect.querySelector(`option[value="${currentFilters.city}"]`);
            const cityName = cityOption ? cityOption.textContent.trim() : 'Выбранный город';
            filtersHTML += `
                <span class="badge bg-light text-dark text-decoration-none py-2 px-3 filter-badge" data-filter="city">
                    ${cityName} <i class="bi bi-x-circle ms-1"></i>
                </span>
            `;
        }
        
        // Фильтр валюты
        if (currentFilters.currency) {
            const currencyOption = currencySelect.querySelector(`option[value="${currentFilters.currency}"]`);
            const currencyName = currencyOption ? currencyOption.textContent.trim() : 'Выбранная валюта';
            filtersHTML += `
                <span class="badge bg-light text-dark text-decoration-none py-2 px-3 filter-badge" data-filter="currency">
                    ${currencyName} <i class="bi bi-x-circle ms-1"></i>
                </span>
            `;
        }
        
        // Кнопка сброса всех фильтров
        filtersHTML += `
            <button id="reset-filters" class="badge bg-danger text-white text-decoration-none py-2 px-3">
                Сбросить все <i class="bi bi-x-circle ms-1"></i>
            </button>
        `;
        
        filtersHTML += '</div>';
        
        // Обновляем содержимое контейнера
        activeFiltersContainer.innerHTML = filtersHTML;
        activeFiltersContainer.style.display = 'block';
        
        // Добавляем обработчик для кнопки сброса фильтров
        document.getElementById('reset-filters').addEventListener('click', resetFilters);
        
        // Добавляем обработчики для отдельных фильтров
        document.querySelectorAll('.filter-badge').forEach(badge => {
            badge.addEventListener('click', function() {
                const filterType = this.dataset.filter;
                
                switch (filterType) {
                    case 'q':
                        searchInput.value = '';
                        currentFilters.q = '';
                        break;
                    case 'sort':
                        sortSelect.value = '';
                        currentFilters.sort = '';
                        break;
                    case 'city':
                        citySelect.value = '';
                        currentFilters.city = '';
                        break;
                    case 'currency':
                        currencySelect.value = '';
                        currentFilters.currency = '';
                        break;
                }
                
                currentFilters.offset = 0;
                updateProductsList();
            });
        });
    }
    
    // Обработчики событий для фильтров
    
    // Поиск
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentFilters.q = searchInput.value;
        currentFilters.offset = 0; // Сбрасываем пагинацию
        updateProductsList();
    });
    
    // Сортировка
    sortSelect.addEventListener('change', function() {
        currentFilters.sort = this.value;
        currentFilters.offset = 0;
        updateProductsList();
    });
    
    // Город
    citySelect.addEventListener('change', function() {
        currentFilters.city = this.value;
        currentFilters.offset = 0;
        updateProductsList();
    });
    
    // Валюта
    currencySelect.addEventListener('change', function() {
        currentFilters.currency = this.value;
        currentFilters.offset = 0;
        updateProductsList();
    });
    
    // Сброс фильтров
    if (resetButton) {
        resetButton.addEventListener('click', resetFilters);
    }
    
    // Обработчик для динамически созданных кнопок сброса отдельных фильтров
    document.addEventListener('click', function(e) {
        const badge = e.target.closest('.filter-badge');
        if (badge) {
            const filterType = badge.dataset.filter;
            
            switch (filterType) {
                case 'q':
                    searchInput.value = '';
                    currentFilters.q = '';
                    break;
                case 'sort':
                    sortSelect.value = '';
                    currentFilters.sort = '';
                    break;
                case 'city':
                    citySelect.value = '';
                    currentFilters.city = '';
                    break;
                case 'currency':
                    currencySelect.value = '';
                    currentFilters.currency = '';
                    break;
            }
            
            currentFilters.offset = 0;
            updateProductsList();
        }
    });
    
    // Инициализация InfiniteScrollModule с учетом динамической фильтрации
    if (window.InfiniteScrollModule) {
        const originalLoadMoreProducts = window.InfiniteScrollModule.loadMoreProducts;
        
        window.InfiniteScrollModule.loadMoreProducts = function() {
            if (this.settings.isLoading || !this.settings.hasMore) return;
            
            this.settings.isLoading = true;
            this.showLoader();
            
            // Используем текущие фильтры для загрузки следующей страницы
            const params = new URLSearchParams();
            for (const [key, value] of Object.entries(currentFilters)) {
                if (value) params.append(key, value);
            }
            params.set('offset', this.settings.offset);
            params.set('limit', this.settings.limit);
            
            const apiUrl = `/api/category/${categorySlug}/products/?${params.toString()}`;
            
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
    
    // Обработка изменения поискового запроса при вводе (для мгновенного поиска)
    searchInput.addEventListener('input', function() {
        // Добавляем debounce для предотвращения слишком частых запросов
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            currentFilters.q = this.value;
            currentFilters.offset = 0;
            updateProductsList();
        }, 500); // Задержка 500 мс
    });

    // Обработка нажатия клавиши Enter в поле поиска
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            currentFilters.q = this.value;
            currentFilters.offset = 0;
            updateProductsList();
        }
    });

    // Обработка кнопки "Наверх"
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        // Показываем кнопку при прокрутке
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'flex';
            } else {
                backToTopButton.style.display = 'none';
            }
        });

        // Прокрутка наверх при клике
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Инициализация при загрузке страницы
    // Получаем начальные параметры из URL
    const urlParams = new URLSearchParams(window.location.search);
    currentFilters = {
        q: urlParams.get('q') || '',
        sort: urlParams.get('sort') || '',
        city: urlParams.get('city') || '',
        currency: urlParams.get('currency') || '',
        offset: 0,
        limit: 20
    };

    // Устанавливаем значения в элементы формы
    searchInput.value = currentFilters.q;
    sortSelect.value = currentFilters.sort;
    citySelect.value = currentFilters.city;
    currencySelect.value = currentFilters.currency;

    // Инициализируем блок активных фильтров
    updateActiveFilters();

    // Добавляем анимацию для элементов списка товаров
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

    // Анимируем элементы при первой загрузке
    animateProductItems();

    // Добавляем обработчик для кнопки повторной попытки при ошибке
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

    // Обработка изменения размера окна (для адаптивности)
    window.addEventListener('resize', function() {
        // Можно добавить дополнительную логику при изменении размера окна
        // Например, изменение количества колонок в мобильном виде
    });

    // Функция для отображения уведомлений
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = message;
        document.body.appendChild(notification);
        
        // Анимация появления
        setTimeout(() => {
            notification.style.transform = 'translateY(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            notification.style.transform = 'translateY(-20px)';
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }

    // Добавляем стили для уведомлений
    const notificationStyles = document.createElement('style');
    notificationStyles.textContent = `
        .notification-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            min-width: 250px;
            transform: translateY(-20px);
            opacity: 0;
            transition: transform 0.3s ease, opacity 0.3s ease;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
    `;
    document.head.appendChild(notificationStyles);

    // Функция для проверки наличия интернет-соединения
    function checkConnection() {
        if (!navigator.onLine) {
            showNotification('Отсутствует подключение к интернету. Проверьте соединение и попробуйте снова.', 'warning');
            return false;
        }
        return true;
    }

    // Обработчик события потери соединения
    window.addEventListener('offline', function() {
        showNotification('Соединение с интернетом потеряно. Некоторые функции могут быть недоступны.', 'warning');
    });

    // Обработчик события восстановления соединения
    window.addEventListener('online', function() {
        showNotification('Соединение с интернетом восстановлено.', 'success');
    });
}

