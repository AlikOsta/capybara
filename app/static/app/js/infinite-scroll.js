/**
 * Модуль для реализации бесконечной ленты объявлений.
 * Автоматически загружает новые объявления при прокрутке страницы.
 */

// Импортируем функции из других модулей
import { initFavoriteButtons } from './favorites.js';

// Конфигурация
const CONFIG = {
    LOAD_THRESHOLD: 80, // Процент прокрутки для загрузки новых объявлений
    SCROLL_TOP_THRESHOLD: 1000, // Порог прокрутки для показа кнопки "Наверх"
    ANIMATION_DELAY: 10, // Задержка перед анимацией новых элементов
    REMOVE_DELAY: 300, // Задержка перед удалением элементов
    INTERSECTION_THRESHOLD: 0.2, // Порог видимости для Intersection Observer
    LIMIT: 20 // Количество загружаемых объявлений за один запрос
};

// Состояние
let state = {
    isLoading: false,
    offset: 0,
    hasMore: true
};

// DOM элементы
let elements = {
    productsContainer: null,
    loader: null,
    endMessage: null,
    errorMessage: null,
    backToTopButton: null,
    retryButton: null
};

/**
 * Инициализирует бесконечную ленту.
 * Настраивает обработчики событий и Intersection Observer.
 */
function initInfiniteScroll() {
    // Получаем элементы DOM
    elements.productsContainer = document.getElementById('products-container');
    elements.loader = document.getElementById('loader');
    elements.endMessage = document.getElementById('end-message');
    elements.errorMessage = document.getElementById('error-message');
    elements.backToTopButton = document.getElementById('back-to-top');
    elements.retryButton = document.getElementById('retry-button');
    
    // Если нет контейнера для продуктов, выходим
    if (!elements.productsContainer) {
        return;
    }
    
    // Инициализируем состояние
    state.offset = parseInt(elements.productsContainer.dataset.offset || CONFIG.LIMIT);
    state.hasMore = elements.productsContainer.dataset.hasMore === 'true';
    
    // Создаем Intersection Observer для отслеживания прокрутки
    if (elements.loader) {
        const observer = new IntersectionObserver((entries) => {
            // Если загрузчик виден и не идет загрузка и есть еще объявления
            if (entries[0].isIntersecting && !state.isLoading && state.hasMore) {
                loadMoreProducts();
            }
        }, { threshold: CONFIG.INTERSECTION_THRESHOLD });
        
        // Начинаем наблюдение за загрузчиком
        observer.observe(elements.loader);
    }
    
    // Добавляем отслеживание процента прокрутки страницы
    window.addEventListener('scroll', handleScroll);
    
    // Обработчик для кнопки "Наверх"
    if (elements.backToTopButton) {
        elements.backToTopButton.addEventListener('click', scrollToTop);
        updateBackToTopButton();
    }
    
    // Обработчик для кнопки повторной попытки
    if (elements.retryButton) {
        elements.retryButton.addEventListener('click', retryLoading);
    }
}

/**
 * Обрабатывает событие прокрутки страницы.
 * Загружает новые объявления при достижении определенного процента прокрутки.
 */
function handleScroll() {
    // Вычисляем процент прокрутки
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;
    
    // Если прокручено достаточно и не идет загрузка и есть еще объявления
    if (scrollPercentage >= CONFIG.LOAD_THRESHOLD && !state.isLoading && state.hasMore) {
        loadMoreProducts();
    }
    
    // Обновляем видимость кнопки "Наверх"
    updateBackToTopButton();
}

/**
 * Обновляет видимость кнопки "Наверх" в зависимости от прокрутки.
 */
function updateBackToTopButton() {
    if (elements.backToTopButton) {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        elements.backToTopButton.style.display = scrollTop > CONFIG.SCROLL_TOP_THRESHOLD ? 'block' : 'none';
    }
}

/**
 * Прокручивает страницу наверх с плавной анимацией.
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Повторяет загрузку объявлений после ошибки.
 */
function retryLoading() {
    if (elements.errorMessage) {
        elements.errorMessage.style.display = 'none';
    }
    loadMoreProducts();
}

/**
 * Загружает дополнительные объявления.
 * Отправляет AJAX запрос и добавляет новые объявления на страницу.
 */
function loadMoreProducts() {
    if (state.isLoading || !state.hasMore) return;
    
    state.isLoading = true;
    showLoader();
    
    // Определяем URL для запроса в зависимости от текущей страницы
    const apiUrl = getApiUrl();
    if (!apiUrl) {
        hideLoader();
        state.isLoading = false;
        return;
    }
    
    // Выполняем AJAX-запрос
    fetch(apiUrl)
        .then(handleResponse)
        .then(handleData)
        .catch(handleError)
        .finally(() => {
            hideLoader();
            state.isLoading = false;
        });
}

/**
 * Получает URL API в зависимости от текущей страницы.
 * 
 * @returns {string|null} URL для API запроса или null, если страница не поддерживает бесконечную ленту
 */
function getApiUrl() {
    // Получаем текущие параметры URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Добавляем параметры пагинации
    const params = new URLSearchParams();
    params.append('offset', state.offset);
    params.append('limit', CONFIG.LIMIT);
    
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
        return `/api/category/${categorySlug}/products/?${params.toString()}`;
    } else if (path === '/' || path === '') {
        return `/api/products/?${params.toString()}`;
    } else if (path.includes('/favorites/')) {
        return `/api/favorites/?${params.toString()}`;
    }
    
    // Если мы на странице, которая не поддерживает бесконечную ленту
    return null;
}

/**
 * Обрабатывает ответ от сервера.
 * 
 * @param {Response} response - Ответ от сервера
 * @returns {Promise} Промис с данными ответа
 * @throws {Error} Ошибка, если ответ не успешный
 */
function handleResponse(response) {
    if (!response.ok) {
        throw new Error('Ошибка загрузки данных');
    }
    return response.json();
}

/**
 * Обрабатывает полученные данные.
 * Добавляет новые объявления на страницу.
 * 
 * @param {Object} data - Данные, полученные от сервера
 */
function handleData(data) {
    // Обновляем состояние
    state.offset += data.results.length;
    state.hasMore = data.has_more;
    
    // Если нет новых объявлений, показываем сообщение о конце списка
    if (data.results.length === 0) {
        showEndMessage();
        return;
    }
    
    // Добавляем новые объявления на страницу
    appendProducts(data.results);
    
    // Если больше нет объявлений, показываем сообщение о конце списка
    if (!state.hasMore) {
        showEndMessage();
    }
}

/**
 * Обрабатывает ошибку загрузки.
 * 
 * @param {Error} error - Объект ошибки
 */
function handleError(error) {
    console.error('Ошибка при загрузке объявлений:', error);
    showErrorMessage();
}

/**
 * Добавляет новые объявления на страницу.
 * 
 * @param {Array} products - Массив объявлений
 */
function appendProducts(products) {
    // Создаем фрагмент для добавления всех объявлений сразу
    const fragment = document.createDocumentFragment();
    
    // Создаем элементы для каждого объявления
    products.forEach(product => {
        const productElement = createProductElement(product);
        fragment.appendChild(productElement);
    });
    
    // Добавляем все объявления на страницу
    elements.productsContainer.appendChild(fragment);
    
    // Инициализируем кнопки избранного для новых объявлений
    initFavoriteButtons();
    
    // Анимируем появление новых объявлений
    animateNewProducts();
}

/**
 * Создает элемент объявления.
 * 
 * @param {Object} product - Данные объявления
 * @returns {HTMLElement} Элемент объявления
 */
function createProductElement(product) {
    // Создаем колонку для объявления
    const col = document.createElement('div');
    col.className = 'col-6 new-product';
    col.style.opacity = '0';
    col.style.transform = 'translateY(20px)';
    
    // Создаем HTML для объявления
    col.innerHTML = `
        <div class="product-card position-relative">
            <a href="/product/${product.id}/" class="text-decoration-none text-dark">
                <div class="card h-100 product-card-inner">
                    <div class="product-image-container">
                        <img src="${product.image}" class="card-img-top product-image" alt="${product.title}">
                        ${product.status !== 3 ? getStatusBadgeHTML(product.status) : ''}
                    </div>
                    <div class="card-body p-3">
                        <h6 class="card-title text-truncate mb-1">${product.title}</h6>
                        <p class="card-text fw-bold mb-2">${product.price} ${product.currency}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted d-flex align-items-center">
                                <i class="bi bi-geo-alt me-1"></i>
                                <span class="text-truncate">${product.city}</span>
                            </small>
                            <small class="text-muted d-flex align-items-center">
                                <i class="bi bi-eye me-1"></i>
                                <span>${product.views_count}</span>
                            </small>
                        </div>
                        <small class="text-muted d-block mt-1">
                            <i class="bi bi-clock me-1"></i>${product.created_at}
                        </small>
                    </div>
                </div>
            </a>
            
            ${product.can_favorite ? getFavoriteButtonHTML(product) : ''}
        </div>
    `;
    
    return col;
}

/**
 * Возвращает HTML для бейджа статуса объявления.
 * 
 * @param {number} status - Статус объявления
 * @returns {string} HTML для бейджа статуса
 */
function getStatusBadgeHTML(status) {
    const statusClasses = {
        0: 'badge-pending',
        1: 'badge-approved',
        2: 'badge-rejected',
        4: 'badge-archived'
    };
    
    const statusTexts = {
        0: 'На модерации',
        1: 'Одобрено',
        2: 'Отклонено',
        4: 'В архиве'
    };
    
    return `
        <div class="product-status-badge ${statusClasses[status]}">
            <span>${statusTexts[status]}</span>
        </div>
    `;
}

/**
 * Возвращает HTML для кнопки избранного.
 * 
 * @param {Object} product - Данные объявления
 * @returns {string} HTML для кнопки избранного
 */
function getFavoriteButtonHTML(product) {
    return `
        <button class="btn btn-sm position-absolute top-0 end-0 m-2 text-danger bg-white rounded-circle p-2 shadow-sm favorite-btn" 
                data-product-id="${product.id}" 
                data-is-favorite="${product.is_favorite ? 'true' : 'false'}">
            <i class="bi ${product.is_favorite ? 'bi-heart-fill' : 'bi-heart'}"></i>
        </button>
    `;
}

/**
 * Анимирует появление новых объявлений.
 */
function animateNewProducts() {
    const newProducts = document.querySelectorAll('.new-product');
    
    // Добавляем анимацию с небольшой задержкой для каждого элемента
    newProducts.forEach((product, index) => {
        setTimeout(() => {
            product.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            product.style.opacity = '1';
            product.style.transform = 'translateY(0)';
            product.classList.remove('new-product');
        }, CONFIG.ANIMATION_DELAY * index);
    });
}

/**
 * Показывает индикатор загрузки.
 */
function showLoader() {
    if (elements.loader) {
        elements.loader.style.display = 'block';
    }
}

/**
 * Скрывает индикатор загрузки.
 */
function hideLoader() {
    if (elements.loader) {
        elements.loader.style.display = 'none';
    }
}

/**
 * Показывает сообщение о конце списка объявлений.
 */
function showEndMessage() {
    if (elements.endMessage) {
        elements.endMessage.style.display = 'block';
    }
}

/**
 * Показывает сообщение об ошибке загрузки.
 */
function showErrorMessage() {
    if (elements.errorMessage) {
        elements.errorMessage.style.display = 'block';
    }
}

// Инициализируем бесконечную ленту при загрузке DOM
document.addEventListener('DOMContentLoaded', initInfiniteScroll);

// Экспортируем функции для использования в других модулях
export { initInfiniteScroll, loadMoreProducts };

