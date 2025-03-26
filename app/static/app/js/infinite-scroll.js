/**
 * Модуль бесконечной ленты для загрузки объявлений
 * Зависит от функций из main.js
 */

const InfiniteScrollModule = {
    // Параметры
    settings: {
        isLoading: false,
        offset: 0,
        limit: 6,
        hasMore: true,
        loadThreshold: 80, // Процент прокрутки для загрузки
        observerThreshold: 0.2, // Порог видимости для IntersectionObserver
        animationDelay: 10, // Задержка для анимации появления элементов
        loadingTimeout: null // Таймаут для предотвращения частых запросов
    },
    
    // Элементы DOM
    elements: {
        productsContainer: null,
        loaderElement: null,
        endMessageElement: null,
        errorElement: null,
        backToTopButton: null,
        retryButton: null
    },
    
    // Инициализация модуля
    init: function() {
        // Получаем элементы DOM
        this.elements.productsContainer = document.getElementById('products-container');
        this.elements.loaderElement = document.getElementById('loader');
        this.elements.endMessageElement = document.getElementById('end-message');
        this.elements.errorElement = document.getElementById('error-message');
        this.elements.backToTopButton = document.getElementById('back-to-top');
        this.elements.retryButton = document.getElementById('retry-button');
        
        // Если нет контейнера для продуктов, выходим
        if (!this.elements.productsContainer) return;
        
        // Получаем параметры из data-атрибутов
        this.settings.offset = parseInt(this.elements.productsContainer.dataset.offset || 20);
        this.settings.hasMore = this.elements.productsContainer.dataset.hasMore === 'true';
        
        // Инициализируем Intersection Observer
        this.initIntersectionObserver();
        
        // Инициализируем обработчики событий
        this.initEventListeners();
    },
    
    // Инициализация Intersection Observer
    initIntersectionObserver: function() {
        if (!this.elements.loaderElement) return;
        
        const observer = new IntersectionObserver((entries) => {
            // Если загрузчик виден и не идет загрузка и есть еще объявления
            if (entries[0].isIntersecting && !this.settings.isLoading && this.settings.hasMore) {
                this.loadMoreProducts();
            }
        }, { threshold: this.settings.observerThreshold });
        
        // Начинаем наблюдение за загрузчиком
        observer.observe(this.elements.loaderElement);
    },
    
    // Инициализация обработчиков событий
    initEventListeners: function() {
        // Отслеживание прокрутки страницы
        window.addEventListener('scroll', this.handleScroll.bind(this));
        
        // Обработчик для кнопки повторной попытки
        if (this.elements.retryButton) {
            this.elements.retryButton.addEventListener('click', () => {
                if (this.elements.errorElement) {
                    this.elements.errorElement.style.display = 'none';
                }
                this.loadMoreProducts();
            });
        }
    },
    
    // Обработчик прокрутки
    handleScroll: function() {
        // Вычисляем процент прокрутки
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
        
        // Если прокручено достаточно и не идет загрузка и есть еще объявления
        if (scrollPercentage >= this.settings.loadThreshold && !this.settings.isLoading && this.settings.hasMore) {
            // Используем debounce для предотвращения частых запросов
            clearTimeout(this.settings.loadingTimeout);
            this.settings.loadingTimeout = setTimeout(() => {
                this.loadMoreProducts();
            }, 100);
        }
    },
    
    // Функция для загрузки дополнительных объявлений
    loadMoreProducts: function() {
        if (this.settings.isLoading || !this.settings.hasMore) return;
        
        this.settings.isLoading = true;
        this.showLoader();
        
        // Определяем URL для запроса в зависимости от текущей страницы
        const apiUrl = this.getApiUrl();
        if (!apiUrl) {
            this.hideLoader();
            this.settings.isLoading = false;
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
                    this.appendNewProducts(data.html);
                    
                    // Обновляем параметры
                    this.settings.offset = data.next_offset || this.settings.offset;
                    this.settings.hasMore = data.has_more;
                    
                    // Показываем сообщение о конце списка, если больше нет объявлений
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
    },
    
    // Получение URL API в зависимости от текущей страницы
    getApiUrl: function() {
        // Получаем текущие параметры URL
        const urlParams = new URLSearchParams(window.location.search);
        const params = new URLSearchParams();
        
        // Добавляем параметры пагинации
        params.append('offset', this.settings.offset);
        params.append('limit', this.settings.limit);
        
        // Добавляем все текущие параметры URL
        for (const [key, value] of urlParams.entries()) {
            if (key !== 'page') { // Исключаем параметр page, так как используем offset
                params.append(key, value);
            }
        }
        
        // Определяем URL API в зависимости от текущей страницы
        const path = window.location.pathname;
        let apiUrl;
        
        if (path.includes('/category/')) {
            const categorySlug = path.split('/category/')[1].replace('/', '');
            apiUrl = `/api/category/${categorySlug}/products/?${params.toString()}`;
        } else if (path === '/' || path === '') {
            apiUrl = `/api/products/?${params.toString()}`;
        } else if (path.includes('/favorites/')) {
            apiUrl = `/api/favorites/?${params.toString()}`;
        } else {
            // Если мы на странице, которая не поддерживает бесконечную ленту
            return null;
        }
        
        return apiUrl;
    },
    
    // Добавление новых продуктов на страницу
    appendNewProducts: function(html) {
        // Создаем временный контейнер для парсинга HTML
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = html;
        
        // Добавляем новые элементы с анимацией
        const productItems = tempContainer.querySelectorAll('.product-item');
        productItems.forEach((item, index) => {
            // Начальное состояние для анимации
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            
            // Добавляем элемент в контейнер
            this.elements.productsContainer.appendChild(item);
            
            // Анимируем появление с небольшой задержкой для каждого элемента
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, this.settings.animationDelay * (index + 1));
        });
        
        // Инициализируем обработчики для кнопок избранного
        if (typeof window.initFavoriteButtons === 'function') {
            window.initFavoriteButtons();
        }
    },
    
    // Функция для показа индикатора загрузки
    showLoader: function() {
        if (this.elements.loaderElement) {
            this.elements.loaderElement.style.display = 'block';
        }
    },
    
    // Функция для скрытия индикатора загрузки
    hideLoader: function() {
        if (this.elements.loaderElement) {
            this.elements.loaderElement.style.display = 'none';
        }
    }
};

// Инициализация модуля при загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    InfiniteScrollModule.init();
});
