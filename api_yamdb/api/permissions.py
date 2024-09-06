from rest_framework import permissions


class IsHasPermission(permissions.BasePermission):
    """
    Этот класс разрешений предоставляет доступ к объектам
    на уровне записи пользователю, если он автор объекта,
    администратор, модератор или если запрос выполняется
    безопасным методом (например, для чтения).
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Этот класс разрешений предоставляет доступ ко всему
    ресурсу только администраторам и суперпользователям
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin)
        )

