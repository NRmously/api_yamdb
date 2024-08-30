from rest_framework import permissions


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
