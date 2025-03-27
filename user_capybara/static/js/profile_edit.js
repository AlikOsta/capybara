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
    
    // Функция обновления состояния кнопки
    function updateButtonState() {
        const { isValid, hasChanges } = validateForm();
        
        if (isValid && hasChanges) {
            mainButton.enable();
        } else {
            mainButton.disable();
        }
        
        // Показываем кнопку в любом случае
        mainButton.show();
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
});
