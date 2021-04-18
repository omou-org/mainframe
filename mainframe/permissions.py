from django.conf import settings
from django_graphene_permissions.permissions import BasePermission as GrapheneBasePermission
from rest_framework.permissions import BasePermission, SAFE_METHODS

from account.models import Admin, Instructor

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsDev(BasePermission):
    def has_permission(self, request, view):
        return settings.DEBUG


class IsEmployee(GrapheneBasePermission):
    @staticmethod
    def has_permission(context):
        user_id = context.user.id
        return Admin.objects.filter(user_id=user_id).exists() or Instructor.objects.filter(user_id=user_id).exists()


class IsOwner(GrapheneBasePermission):
    @staticmethod
    def has_permission(context):
        user_id = context.user.id
        admin = Admin.objects.filter(user_id=user_id)
        return admin.exists() and admin[0].admin_type == "owner"
