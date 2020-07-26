import jwt

from graphene import Field, ID, List, String, Union
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from comms.models import (
    ParentNotificationSettings,
    Announcement
)

class AnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement

class ParentNotificationSettingsType(DjangoObjectType):
    class Meta:
        model = ParentNotificationSettings


class Query(object):
    announcement = Field(AnnouncementType, announcement_id=ID())
    parent_notification_settings = Field(ParentNotificationSettingsType, parent_id=ID(required=True))

    announcements = List(AnnouncementType, course_id=ID(required=True))

    @login_required
    def resolve_announcement(self, info, **kwargs):
        announcement_id = kwargs.get('announcement_id')

        if announcement_id:
            return Announcement.objects.get(id=announcement_id)

        return None

    @login_required
    def resolve_announcements(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        return Announcement.objects.filter(course_id=course_id)    

    # @login_required
    # def resolve_annoucements(self, info, **kwargs):
    #     course_id = kwargs.get('course_id')

    #     return Annoucement.objects.filter(course__id=course_id)
        
    def resolve_parent_notification_settings(self, info, parent_id):
        return ParentNotificationSettings.objects.get(parent=parent_id)
