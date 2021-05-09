from django.conf import settings
from django_graphene_permissions.permissions import (
    BasePermission as GrapheneBasePermission,
)
from rest_framework.permissions import BasePermission, SAFE_METHODS

from account.models import (
    Student,
    Parent,
    Instructor,
    Admin,
)


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
        return (
            Admin.objects.filter(user_id=user_id).exists()
            or Instructor.objects.filter(user_id=user_id).exists()
        )


class IsOwner(GrapheneBasePermission):
    @staticmethod
    def has_permission(context):
        user_id = context.user.id
        admin = Admin.objects.filter(user_id=user_id)
        return admin.exists() and admin[0].admin_type == "owner"


def get_user_type_object(user_id):
    if Student.objects.filter(user=user_id).exists():
        return Student.objects.get(user=user_id)
    if Instructor.objects.filter(user=user_id).exists():
        return Instructor.objects.get(user=user_id)
    if Parent.objects.filter(user=user_id).exists():
        return Parent.objects.get(user=user_id)
    if Admin.objects.filter(user=user_id).exists():
        return Admin.objects.get(user=user_id)


def has_org_permission(user_id, resource_user_id):
    if (
        get_user_type_object(user_id).business
        == get_user_type_object(resource_user_id).business
    ):
        return True
    return False
