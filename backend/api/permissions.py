from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    message = 'Изменение чужого контента запрещено!'

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)
