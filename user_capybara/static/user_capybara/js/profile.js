document.addEventListener('DOMContentLoaded', function() {
    // Инициализация вкладок Bootstrap
    const triggerTabList = [].slice.call(document.querySelectorAll('#profileTabs button'));
    triggerTabList.forEach(function(triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });
    
    // Сохранение активной вкладки в localStorage
    const tabs = document.querySelectorAll('#profileTabs button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            localStorage.setItem('activeProfileTab', event.target.id);
        });
    });
    
    // Восстановление активной вкладки при загрузке страницы
    const activeTab = localStorage.getItem('activeProfileTab');
    if (activeTab) {
        const tab = document.querySelector('#' + activeTab);
        if (tab) {
            const bsTab = new bootstrap.Tab(tab);
            bsTab.show();
        }
    }
    
    // Обработка кнопок управления объявлениями
    const editButtons = document.querySelectorAll('.btn-outline-primary');
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Добавляем анимацию при клике
            button.classList.add('btn-loading');
        });
    });
    
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Добавляем анимацию при клике
            button.classList.add('btn-loading');
        });
    });
});
