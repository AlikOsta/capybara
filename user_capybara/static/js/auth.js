// // Функция для получения токена из localStorage
// function getAccessToken() {
//     return localStorage.getItem('access_token');
// }

// // Функция для получения refresh-токена из localStorage
// function getRefreshToken() {
//     return localStorage.getItem('refresh_token');
// }

// // Функция для установки токенов в localStorage
// function setTokens(accessToken, refreshToken) {
//     localStorage.setItem('access_token', accessToken);
//     localStorage.setItem('refresh_token', refreshToken);
// }

// // Функция для очистки токенов (выход из системы)
// function clearTokens() {
//     localStorage.removeItem('access_token');
//     localStorage.removeItem('refresh_token');
// }

// // Функция для проверки, авторизован ли пользователь
// function isAuthenticated() {
//     return !!getAccessToken();
// }

// // Функция для обновления токена
// async function refreshAccessToken() {
//     const refreshToken = getRefreshToken();
//     if (!refreshToken) {
//         clearTokens();
//         return false;
//     }
    
//     try {
//         const response = await fetch('/api/token/refresh/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ refresh: refreshToken }),
//         });
        
//         if (!response.ok) {
//             clearTokens();
//             return false;
//         }
        
//         const data = await response.json();
//         setTokens(data.access, data.refresh || refreshToken);
//         return true;
//     } catch (error) {
//         console.error('Error refreshing token:', error);
//         clearTokens();
//         return false;
//     }
// }

// // Функция для выполнения аутентифицированных запросов
// async function fetchWithAuth(url, options = {}) {
//     // Добавляем токен в заголовки
//     const accessToken = getAccessToken();
//     if (accessToken) {
//         options.headers = {
//             ...options.headers,
//             'Authorization': `Bearer ${accessToken}`,
//         };
//     }
    
//     // Выполняем запрос
//     let response = await fetch(url, options);
    
//     // Если получили 401 (Unauthorized), пробуем обновить токен
//     if (response.status === 401) {
//         const refreshSuccess = await refreshAccessToken();
//         if (refreshSuccess) {
//             // Повторяем запрос с новым токеном
//             const newAccessToken = getAccessToken();
//             options.headers = {
//                 ...options.headers,
//                 'Authorization': `Bearer ${newAccessToken}`,
//             };
//             response = await fetch(url, options);
//         } else {
//             // Если не удалось обновить токен, перенаправляем на страницу авторизации
//             window.location.href = '/user/auth/telegram/';
//         }
//     }
    
//     return response;
// }
