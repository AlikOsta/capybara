/**
 * Модуль для работы с Telegram Web App API
 * Централизует всю логику взаимодействия с Telegram
 */
const TelegramApp = (function() {
    // Приватные переменные
    let _tg = null;
    let _isInitialized = false;
    let _eventHandlers = {};
    
    // Приватные методы
    const _checkAvailability = function() {
        return window.Telegram && window.Telegram.WebApp;
    };
    
    const _safeExecute = function(callback, fallback) {
        try {
            if (_isInitialized && _tg) {
                return callback(_tg);
            } else {
                console.warn('Telegram WebApp не инициализирован');
                if (typeof fallback === 'function') {
                    return fallback();
                }
            }
        } catch (error) {
            console.error('Ошибка при выполнении операции Telegram WebApp:', error);
            if (typeof fallback === 'function') {
                return fallback();
            }
        }
        return null;
    };
    
    // Публичные методы
    return {
        /**
         * Инициализация Telegram Web App
         * @returns {boolean} - Успешность инициализации
         */
        init: function() {
            if (_isInitialized) return true;
            
            if (_checkAvailability()) {
                _tg = window.Telegram.WebApp;
                _isInitialized = true;
                
                // Расширяем видимую область
                _tg.expand();
                
                // Адаптируем тему
                this.adaptTheme();
                
                console.log('Telegram WebApp успешно инициализирован');
                return true;
            } else {
                console.warn('Telegram WebApp API недоступен');
                return false;
            }
        },
        
        /**
         * Получение объекта Telegram WebApp
         * @returns {Object|null} - Объект Telegram WebApp или null
         */
        getWebApp: function() {
            return _tg;
        },
        
        /**
         * Адаптация темы к настройкам Telegram
         */
        adaptTheme: function() {
            _safeExecute(function(tg) {
                const isDarkTheme = tg.colorScheme === 'dark';
                document.body.setAttribute('data-bs-theme', isDarkTheme ? 'dark' : 'light');
                
                // Применяем цвета Telegram к CSS переменным
                document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
                document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
                document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
                document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
                document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
                document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
                document.documentElement.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
            });
        },
        
        /**
         * Настройка кнопки "Назад"
         * @param {Function} callback - Функция, вызываемая при нажатии кнопки
         * @returns {boolean} - Успешность настройки
         */
        setupBackButton: function(callback) {
            return _safeExecute(function(tg) {
                if (!tg.BackButton) {
                    console.warn('BackButton недоступен');
                    return false;
                }
                
                tg.BackButton.show();
                
                // Удаляем предыдущий обработчик, если он был
                if (_eventHandlers.backButton) {
                    tg.offEvent('backButtonClicked', _eventHandlers.backButton);
                }
                
                // Устанавливаем новый обработчик
                _eventHandlers.backButton = function() {
                    // Вызываем тактильную обратную связь
                    TelegramApp.hapticFeedback('impact', 'medium');
                    
                    if (typeof callback === 'function') {
                        callback();
                    } else {
                        window.history.back();
                    }
                };
                
                tg.onEvent('backButtonClicked', _eventHandlers.backButton);
                return true;
            }, function() {
                return false;
            });
        },
        
        /**
         * Скрытие кнопки "Назад"
         * @returns {boolean} - Успешность операции
         */
        hideBackButton: function() {
            return _safeExecute(function(tg) {
                if (tg.BackButton) {
                    tg.BackButton.hide();
                    return true;
                }
                return false;
            }, function() {
                return false;
            });
        },
        
        /**
         * Настройка главной кнопки
         * @param {Object} options - Настройки кнопки
         * @returns {boolean} - Успешность настройки
         */
        setupMainButton: function(options = {}) {
            return _safeExecute(function(tg) {
                if (!tg.MainButton) {
                    console.warn('MainButton недоступен');
                    return false;
                }
                
                const defaults = {
                    text: 'Продолжить',
                    color: tg.themeParams.button_color || '#2481cc',
                    textColor: tg.themeParams.button_text_color || '#ffffff',
                    onClick: null,
                    isVisible: true,
                    isActive: true,
                    progressVisible: false
                };
                
                const settings = {...defaults, ...options};
                
                tg.MainButton.setText(settings.text);
                tg.MainButton.setParams({
                    color: settings.color,
                    text_color: settings.textColor,
                    is_active: settings.isActive,
                    is_visible: settings.isVisible
                });
                
                // Удаляем предыдущий обработчик, если он был
                if (_eventHandlers.mainButton) {
                    tg.MainButton.offClick(_eventHandlers.mainButton);
                }
                
                // Устанавливаем новый обработчик
                if (settings.onClick) {
                    _eventHandlers.mainButton = function() {
                        // Вызываем тактильную обратную связь
                        TelegramApp.hapticFeedback('impact', 'medium');
                        settings.onClick();
                    };
                    tg.MainButton.onClick(_eventHandlers.mainButton);
                }
                
                if (settings.progressVisible) {
                    tg.MainButton.showProgress();
                } else {
                    tg.MainButton.hideProgress();
                }
                
                if (settings.isVisible) {
                    tg.MainButton.show();
                } else {
                    tg.MainButton.hide();
                }
                
                return true;
            }, function() {
                return false;
            });
        },
        
        /**
         * Скрытие главной кнопки
         * @returns {boolean} - Успешность операции
         */
        hideMainButton: function() {
            return _safeExecute(function(tg) {
                if (tg.MainButton) {
                    tg.MainButton.hide();
                    return true;
                }
                return false;
            }, function() {
                return false;
            });
        },
        
        /**
         * Показ главной кнопки
         * @returns {boolean} - Успешность операции
         */
        showMainButton: function() {
            return _safeExecute(function(tg) {
                if (tg.MainButton) {
                    tg.MainButton.show();
                    return true;
                }
                return false;
            }, function() {
                return false;
            });
        },
        
        /**
         * Вызов тактильной обратной связи
         * @param {string} type - Тип обратной связи ('impact', 'notification', 'selection')
         * @param {string} intensity - Интенсивность ('light', 'medium', 'heavy')
         * @returns {boolean} - Успешность операции
         */
        hapticFeedback: function(type = 'impact', intensity = 'medium') {
            return _safeExecute(function(tg) {
                if (!tg.HapticFeedback) {
                    console.warn('HapticFeedback недоступен');
                    return false;
                }
                
                switch(type) {
                    case 'impact':
                        tg.HapticFeedback.impactOccurred(intensity);
                        break;
                    case 'notification':
                        tg.HapticFeedback.notificationOccurred(intensity);
                        break;
                    case 'selection':
                        tg.HapticFeedback.selectionChanged();
                        break;
                    default:
                        console.warn('Неизвестный тип тактильной обратной связи:', type);
                        return false;
                }
                
                return true;
            }, function() {
                return false;
            });
        },
        
        /**
         * Закрытие Telegram Web App
         */
        close: function() {
            _safeExecute(function(tg) {
                tg.close();
            });
        },
        
        /**
         * Получение данных инициализации
         * @returns {string|null} - Данные инициализации или null
         */
        getInitData: function() {
            return _safeExecute(function(tg) {
                return tg.initData || null;
            }, function() {
                return null;
            });
        },
        
        /**
         * Получение информации о пользователе
         * @returns {Object|null} - Информация о пользователе или null
         */
        getUser: function() {
            return _safeExecute(function(tg) {
                return tg.initDataUnsafe && tg.initDataUnsafe.user ? tg.initDataUnsafe.user : null;
            }, function() {
                return null;
            });
        },
        
        /**
         * Проверка, доступен ли Telegram Web App
         * @returns {boolean} - Доступность Telegram Web App
         */
        isAvailable: function() {
            return _checkAvailability();
        },
        
        /**
         * Проверка, инициализирован ли Telegram Web App
         * @returns {boolean} - Статус инициализации
         */
        isInitialized: function() {
            return _isInitialized;
        },
        
        /**
         * Получение цветовой схемы
         * @returns {string} - 'dark' или 'light'
         */
        getColorScheme: function() {
            return _safeExecute(function(tg) {
                return tg.colorScheme || 'light';
            }, function() {
                return 'light';
            });
        },
        
        /**
         * Получение параметров темы
         * @returns {Object} - Параметры темы
         */
        getThemeParams: function() {
            return _safeExecute(function(tg) {
                return tg.themeParams || {};
            }, function() {
                return {};
            });
        }
    };
})();

// Автоматическая инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    TelegramApp.init();
});
