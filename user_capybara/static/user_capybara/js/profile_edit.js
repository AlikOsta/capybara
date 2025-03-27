// Добавьте эту функцию в начало файла
function applyMainButtonAnimation() {
    // Получаем элемент MainButton
    const mainButtonElement = document.querySelector('.telegram-main-button');
    
    if (mainButtonElement) {
        // Добавляем класс для анимации
        mainButtonElement.classList.add('telegram-main-button-animation');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Проверяем доступность Telegram Web App API
    const tg = window.Telegram && window.Telegram.WebApp;
    if (!tg) return;
    
    // Показываем кнопку назад Telegram
    if (tg.BackButton) {
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
    
    // Инициализация Main Button
    const mainButton = tg.MainButton;
    if (!mainButton) return;
    
    // Получаем ссылку на нижнее меню
    const footer = document.querySelector('footer.fixed-bottom');
    
    // Настройка Main Button
    mainButton.setText('Сохранить изменения');
    mainButton.hide();
    
    // Получаем форму и все поля ввода
    const form = document.getElementById('profileForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    // Сохраняем начальные значения полей
    const initialValues = {};
    inputs.forEach(input => {
        initialValues[input.name] = input.value;
    });
    
    // Функция проверки валидности формы
    function validateForm() {
        let isValid = true;
        let hasChanges = false;
        
        // Проверяем все поля на валидность и изменения
        inputs.forEach(input => {
            // Проверка на заполненность обязательных полей
            if (input.required && !input.value.trim()) {
                isValid = false;
            }
            
            // Проверка на изменения
            if (initialValues[input.name] !== input.value) {
                hasChanges = true;
            }
        });
        
        return { isValid, hasChanges };
    }
    
    // Обновите функцию updateButtonState
    function updateButtonState() {
        const { isValid, hasChanges } = validateForm();
        
        // Получаем элемент MainButton для анимации
        const mainButtonElement = document.querySelector('.telegram-main-button');
        
        if (isValid && hasChanges) {
            mainButton.enable();
        } else {
            mainButton.disable();
        }
        
        // Сначала скрываем нижнее меню
        if (footer) {
            footer.classList.add('hidden');
        }
        
        // Затем с небольшой задержкой показываем MainButton
        setTimeout(() => {
            // Показываем кнопку в любом случае
            mainButton.show();
            document.body.classList.add('main-button-visible');
            
            // Показываем анимацию появления
            if (mainButtonElement) {
                mainButtonElement.classList.remove('hidden');
            }
        }, 150);
    }
    
    // Обработчик нажатия на Main Button
    mainButton.onClick(function() {
        // Вызываем тактильную обратную связь при нажатии на Main Button
        if (tg.HapticFeedback) {
            tg.HapticFeedback.impactOccurred('medium');
        }
        
        // Проверяем валидность перед отправкой
        const { isValid, hasChanges } = validateForm();
        if (isValid && hasChanges) {
            // Программно нажимаем на скрытую кнопку отправки формы
            document.getElementById('hiddenSubmitButton').click();
        }
    });
    
    // Добавляем обработчики событий для всех полей ввода
    inputs.forEach(input => {
        ['input', 'change', 'blur'].forEach(eventType => {
            input.addEventListener(eventType, updateButtonState);
        });
    });
    
    // Инициализация состояния кнопки при загрузке страницы
    updateButtonState();
});

// Скрываем кнопки при уходе со страницы
window.addEventListener('beforeunload', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg) {
        if (tg.BackButton) tg.BackButton.hide();
        if (tg.MainButton) tg.MainButton.hide();
    }
    
    // Показываем нижнее меню
    const footer = document.querySelector('footer.fixed-bottom');
    if (footer) {
        footer.classList.remove('hidden');
    }
    
    document.body.classList.remove('main-button-visible');
});

// Обработчик для кнопки назад браузера
window.addEventListener('popstate', function() {
    const tg = window.Telegram && window.Telegram.WebApp;
    if (tg && tg.MainButton) {
        tg.MainButton.hide();
    }
    
    // Показываем нижнее меню
    const footer = document.querySelector('footer.fixed-bottom');
    if (footer) {
        footer.classList.remove('hidden');
    }
    
    document.body.classList.remove('main-button-visible');
});
