from rest_framework import permissions


class AllowAnyOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return True
