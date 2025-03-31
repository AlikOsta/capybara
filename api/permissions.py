from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее только авторам объекта редактировать его.
    Чтение доступно всем, запись — только автору или администратору.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение разрешены для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Администраторы и суперпользователи имеют полный доступ
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Права на запись разрешены только автору объекта
        if not request.user.is_authenticated:
            return False
        return obj.author == request.user