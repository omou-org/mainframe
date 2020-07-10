import graphene

from comms.models import ParentNotificationSettings
from comms.schema import ParentNotificationSettingsType

from graphene import Boolean, DateTime, ID, String
from graphql_jwt.decorators import staff_member_required


class MutateParentNotificationSettings(graphene.Mutation):
    class Arguments:
        parent_id = ID(name="parent", required=True)
        session_reminder_email = Boolean()
        session_reminder_sms = Boolean()
        payment_reminder_email = Boolean()
        payment_reminder_sms = Boolean()
        schedule_updates_sms = Boolean()
        course_requests_sms = Boolean()

    settings = graphene.Field(ParentNotificationSettingsType)

    @staticmethod
    def mutate(root, info, parent_id, **validated_data):
        settings, created = ParentNotificationSettings.objects.update_or_create(
            parent=parent_id,
            defaults=validated_data
        )
        return MutateParentNotificationSettings(settings=settings)


class Mutation(graphene.ObjectType):
    create_parent_notification_setting = MutateParentNotificationSettings.Field()
