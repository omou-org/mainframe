import graphene

from comms.models import ParentNotificationSettings, InstructorNotificationSettings
from comms.schema import ParentNotificationSettingsType, InstructorNotificationSettingsType

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

    settings = graphene.Field(ParentNotificationSettingsType)

    @staticmethod
    def mutate(root, info, parent_id, **validated_data):
        settings, created = ParentNotificationSettings.objects.update_or_create(
            parent_id=parent_id,
            defaults=validated_data
        )
        return MutateParentNotificationSettings(settings=settings)


class MutateInstructorNotificationSettings(graphene.Mutation):
    class Arguments:
        instructor_id = ID(name="parent", required=True)
        session_reminder_email = Boolean()
        session_reminder_sms = Boolean()
        schedule_updates_sms = Boolean()
        course_requests_sms = Boolean()

    settings = graphene.Field(InstructorNotificationSettingsType)

    @staticmethod
    def mutate(root, info, instructor_id, **validated_data):
        settings, created = InstructorNotificationSettings.objects.update_or_create(
            instructor_id=instructor_id,
            defaults=validated_data
        )
        return MutateInstructorNotificationSettings(settings=settings)


class Mutation(graphene.ObjectType):
    create_parent_notification_setting = MutateParentNotificationSettings.Field()
    create_instructor_notification_setting = MutateInstructorNotificationSettings.Field()