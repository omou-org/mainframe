from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsDev(BasePermission):
    def has_permission(self, request, view):
        return settings.DEBUG
