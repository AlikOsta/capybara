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
    mainButton.setText(document.body.dataset.isEdit === 'true' ? 'Сохранить изменения' : 'Опубликовать');
    mainButton.hide();
    
    // Получаем форму и все поля ввода
    const form = document.getElementById('productForm');
    const inputs = form.querySelectorAll('input, textarea, select');
    
    // Для редактирования: сохраняем начальные значения полей
    const initialValues = {};
    if (document.body.dataset.isEdit === 'true') {
        inputs.forEach(input => {
            if (input.type === 'file') return;
            initialValues[input.name] = input.value;
        });
    }
    
    // Функция проверки валидности формы
    function validateForm() {
        let isValid = true;
        let hasChanges = false;
        
        // Проверяем все обязательные поля
        inputs.forEach(input => {
            // Пропускаем поле файла при проверке валидности
            if (input.type === 'file') return;
            
            // Проверка на заполненность
            if (input.required && !input.value.trim()) {
                isValid = false;
            }
            
            // Для редактирования: проверяем, есть ли изменения
            if (document.body.dataset.isEdit === 'true') {
                if (initialValues[input.name] !== input.value) {
                    hasChanges = true;
                }
            }
        });
        
        // Для создания нового объявления всегда считаем, что есть изменения
        if (document.body.dataset.isEdit !== 'true') {
            hasChanges = true;
        }
        
        // Проверка изображения
        const imageInput = document.getElementById('id_image');
        const hasImage = document.body.dataset.hasImage === 'true';
        
        // Если это новое объявление или изменено изображение
        if (imageInput.files.length > 0) {
            hasChanges = true;
        }
        
        // Для нового объявления требуется изображение
        if (!hasImage && imageInput.files.length === 0 && document.body.dataset.isEdit !== 'true') {
            isValid = false;
        }
        
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
    
    // Обработчик изменения файла изображения
    const imageInput = document.getElementById('id_image');
    imageInput.addEventListener('change', updateButtonState);
    
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

