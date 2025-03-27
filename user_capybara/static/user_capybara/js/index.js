// document.addEventListener('DOMContentLoaded', function() {
//     // Инициализация Telegram WebApp
//     const tg = window.Telegram && window.Telegram.WebApp;
    
//     if (tg) {
//         // Расширяем WebApp на весь экран
//         tg.expand();
        
//         // Применяем цветовую схему Telegram
//         applyTelegramTheme();
        
//         // Обрабатываем изменение темы
//         tg.onEvent('themeChanged', applyTelegramTheme);
//     }
    
//     // Обработка кнопок избранного на всех страницах
//     initFavoriteButtons();
    
//     // Инициализация всплывающих подсказок
//     initTooltips();
    
//     // Обработка навигации
//     handleNavigation();
// });

// // Применение цветовой схемы Telegram
// function applyTelegramTheme() {
//     const tg = window.Telegram && window.Telegram.WebApp;
//     if (!tg) return;
    
//     // Получаем цвета из Telegram WebApp
//     document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
//     document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
//     document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
//     document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
//     document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
//     document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
//     document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
    
//     // Создаем RGB версии для использования с opacity
//     const buttonColor = tg.themeParams.button_color || '#2481cc';
//     const r = parseInt(buttonColor.slice(1, 3), 16);
//     const g = parseInt(buttonColor.slice(3, 5), 16);
//     const b = parseInt(buttonColor.slice(5, 7), 16);
//     document.documentElement.style.setProperty('--tg-theme-button-color-rgb', `${r}, ${g}, ${b}`);
// }

// // Инициализация кнопок избранного
// function initFavoriteButtons() {
//     const favoriteBtns = document.querySelectorAll('.favorite-btn');
    
//     favoriteBtns.forEach(btn => {
//         btn.addEventListener('click', function(e) {
//             e.preventDefault();
//             e.stopPropagation();
            
//             const productId = this.dataset.productId;
//             const isFavorite = this.dataset.isFavorite === 'true';
            
//             // Отправляем AJAX запрос
//             fetch(`/product/${productId}/favorite/`, {
//                 method: 'POST',
//                 headers: {
//                     'X-Requested-With': 'XMLHttpRequest',
//                     'X-CSRFToken': getCookie('csrftoken'),
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify({})
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.success) {
//                     // Обновляем состояние кнопки
//                     this.dataset.isFavorite = data.is_favorite.toString();
                    
//                     // Обновляем иконку
//                     const icon = this.querySelector('i');
//                     if (data.is_favorite) {
//                         icon.classList.remove('bi-heart');
//                         icon.classList.add('bi-heart-fill');
//                     } else {
//                         icon.classList.remove('bi-heart-fill');
//                         icon.classList.add('bi-heart');
//                     }
//                 }
//             })
//             .catch(error => {
//                 console.error('Ошибка:', error);
//             });
//         });
//     });
// }

// // Инициализация всплывающих подсказок
// function initTooltips() {
//     const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
//     tooltipTriggerList.map(function (tooltipTriggerEl) {
//         return new bootstrap.Tooltip(tooltipTriggerEl);
//     });
// }

// // Обработка навигации
// function handleNavigation() {
//     // Добавляем анимацию загрузки при переходе по ссылкам
//     const links = document.querySelectorAll('a:not([target="_blank"])');
//     links.forEach(link => {
//         link.addEventListener('click', function(e) {
//             // Пропускаем, если это AJAX-запрос или действие JavaScript
//             if (this.getAttribute('href').startsWith('#') || 
//                 this.getAttribute('href') === 'javascript:void(0)' ||
//                 this.classList.contains('no-loader')) {
//                 return;
//             }
            
//             // Показываем индикатор загрузки
//             showPageLoader();
//         });
//     });
    
//     // Добавляем анимацию загрузки при отправке форм
//     const forms = document.querySelectorAll('form:not(.no-loader)');
//     forms.forEach(form => {
//         form.addEventListener('submit', function(e) {
//             // Показываем индикатор загрузки
//             showPageLoader();
//         });
//     });
// }

// // Показать индикатор загрузки страницы
// function showPageLoader() {
//     // Создаем элемент загрузки, если его еще нет
//     if (!document.getElementById('page-loader')) {
//         const loader = document.createElement('div');
//         loader.id = 'page-loader';
//         loader.innerHTML = `
//             <div class="page-loader-spinner">
//                 <div class="spinner-border text-primary" role="status">
//                     <span class="visually-hidden">Загрузка...</span>
//                 </div>
//             </div>
//         `;
//         document.body.appendChild(loader);
        
//         // Добавляем стили для загрузчика
//         const style = document.createElement('style');
//         style.textContent = `
//             #page-loader {
//                 position: fixed;
//                 top: 0;
//                 left: 0;
//                 width: 100%;
//                 height: 100%;
//                 background-color: rgba(255, 255, 255, 0.7);
//                 display: flex;
//                 justify-content: center;
//                 align-items: center;
//                 z-index: 9999;
//             }
//             .page-loader-spinner {
//                 padding: 20px;
//                 background-color: white;
//                 border-radius: 10px;
//                 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
//             }
//         `;
//         document.head.appendChild(style);
//     } else {
//         document.getElementById('page-loader').style.display = 'flex';
//     }
// }

// // Получение CSRF токена из cookies
// function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
