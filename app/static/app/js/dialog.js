;(function() {
    const modalElement = document.getElementById('modal');
    const modal = new bootstrap.Modal(modalElement);
    
    // Функция для инициализации предпросмотра изображения
    function initImagePreview() {
        const fileInput = document.querySelector('#productForm input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    const previewContainer = this.closest('form').querySelector('.image-preview-container');
                    
                    reader.onload = function(e) {
                        previewContainer.innerHTML = `
                            <img src="${e.target.result}" alt="Preview" class="img-preview img-fluid rounded">
                        `;
                    }
                    
                    reader.readAsDataURL(file);
                }
            });
        }
    }
    
    // После загрузки модального окна через HTMX
    htmx.on('htmx:afterSwap', (e) => {
        if (e.detail.target.id === 'dialog') {
            modal.show();
            // Инициализируем предпросмотр изображения после загрузки модального окна
            initImagePreview();
        }
    });

    // Закрываем модальное окно сразу после отправки формы
    htmx.on('htmx:beforeSend', (e) => {
        // Проверяем, что это отправка формы из модального окна
        const form = e.detail.elt.closest('form');
        if (form && form.closest('#dialog')) {
            // Проверяем валидность формы перед закрытием
            if (form.checkValidity()) {
                // Показываем уведомление
                let message = "Объявление отправлено на модерацию";
                
                // Если это форма удаления, меняем сообщение
                if (form.closest('.modal-content').querySelector('.bi-exclamation-triangle-fill')) {
                    message = "Объявление удалено";
                }
                
                const toast = document.createElement('div');
                toast.className = 'position-fixed bottom-0 end-0 p-3';
                toast.style.zIndex = '1070';
                toast.innerHTML = `
                    <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                        <div class="toast-header">
                            <strong class="me-auto">Уведомление</strong>
                            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                        </div>
                        <div class="toast-body">
                            ${message}
                        </div>
                    </div>
                `;
                document.body.appendChild(toast);
                
                // Закрываем модальное окно
                modal.hide();
                
                // Удаляем уведомление через 3 секунды
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }
        }
    });

    // Обработка ошибок при отправке формы
    htmx.on('htmx:responseError', (e) => {
        if (e.detail.target.closest('#dialog')) {
            // После обновления формы с ошибками, нужно заново инициализировать предпросмотр
            initImagePreview();
        }
    });

    // Обработка ошибок сети
    htmx.on('htmx:sendError', (e) => {
        // Показываем уведомление об ошибке
        const toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '1070';
        toast.innerHTML = `
            <div class="toast show bg-danger text-white" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-danger text-white">
                    <strong class="me-auto">Ошибка</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Не удалось выполнить действие. Проверьте подключение к интернету.
                </div>
            </div>
        `;
        document.body.appendChild(toast);
        
        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            toast.remove();
        }, 3000);
    });

    document.addEventListener('click', function(e) {
        const link = e.target.closest('[hx-get][data-bs-dismiss="modal"]');
        
        if (link) {
            e.preventDefault();
            const url = link.getAttribute('hx-get');
            const target = link.getAttribute('hx-target');
        
            modal.hide();

            modalElement.addEventListener('hidden.bs.modal', function handler() {
                modalElement.removeEventListener('hidden.bs.modal', handler);

                htmx.ajax('GET', url, { target: target });
            }, { once: true });
        }
    });
})();

function setActive(clickedBtn) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.remove('text-primary');
    btn.classList.add('text-muted');
  });
  clickedBtn.classList.add('text-primary');
  clickedBtn.classList.remove('text-muted');
}
