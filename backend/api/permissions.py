from rest_framework import permissions


class AllowAnyOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return False

        if view.action == 'me':
            return (request.user.is_authenticated and request.method == 'GET')

        if view.kwargs.get('id'):
            return (request.method in permissions.SAFE_METHODS)

        return (
            request.method in permissions.SAFE_METHODS
            and request.user.is_authenticated
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
