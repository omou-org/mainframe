import jwt

from graphene import Field, ID, List, String, Union
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from comms.models import (
    ParentNotificationSettings,
    Annoucement
)

class AnnoucementType(DjangoObjectType):
    class Meta:
        model = Annoucement

class ParentNotificationSettingsType(DjangoObjectType):
    class Meta:
        model = ParentNotificationSettings


class Query(object):
    annoucement = Field(AnnoucementType, annoucement_id=ID())
    parent_notification_settings = Field(ParentNotificationSettingsType, parent_id=ID(required=True))

    annoucements = List(AnnoucementType, course_id=ID(required=True))

    @login_required
    def resolve_annoucement(self, info, **kwargs):
        annoucement_id = kwargs.get('annoucement_id')

        if annoucement_id:
            return Annoucement.objects.get(id=annoucement_id)

        return None

    @login_required
    def resolve_annoucements(self, info, **kwargs):
        course_id = kwargs.get('course_id')

        return Annoucement.objects.filter(course_id=course_id)    

    # @login_required
    # def resolve_annoucements(self, info, **kwargs):
    #     course_id = kwargs.get('course_id')

    #     return Annoucement.objects.filter(course__id=course_id)
        
    def resolve_parent_notification_settings(self, info, parent_id):
        return ParentNotificationSettings.objects.get(parent=parent_id)
