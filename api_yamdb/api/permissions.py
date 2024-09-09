from rest_framework import permissions


class IsAdminOrModeratorOrOwnerOrReadOnly(permissions.BasePermission):
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


class IsSuperUserOrIsAdmin(permissions.BasePermission):
    """
    Кастомное разрешение для проверки, является ли пользователь
    суперпользователем или администратором.

    Разрешение предоставляет доступ только аутентифицированным пользователям,
    которые являются либо суперпользователями, либо администраторами.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь права доступа к данному представлению.

        Возвращает True, если пользователь аутентифицирован и является
        суперпользователем или администратором, иначе возвращает False.
        """
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.is_admin
        )
