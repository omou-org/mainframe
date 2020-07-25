import jwt

from graphene import Field, ID, List, String, Union
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from comms.models import (
    ParentNotificationSettings,
    InstructorNotificationSettings,
)


class ParentNotificationSettingsType(DjangoObjectType):
    class Meta:
        model = ParentNotificationSettings


class InstructorNotificationSettingsType(DjangoObjectType):
    class Meta:
        model = InstructorNotificationSettings


class Query(object):
    parent_notification_settings = Field(ParentNotificationSettingsType, parent_id=ID(required=True))
    instructor_notification_settings = Field(InstructorNotificationSettingsType, instructor_id=ID(required=True))

    def resolve_parent_notification_settings(self, info, parent_id):
        return ParentNotificationSettings.objects.get(parent=parent_id)

    def resolve_instructor_notification_settings(self, info, instructor_id):
        return InstructorNotificationSettings.objects.get(instructor=instructor_id)
