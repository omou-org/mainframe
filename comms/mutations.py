import graphene

from comms.models import ParentNotificationSettings, InstructorNotificationSettings, Announcement
from comms.schema import ParentNotificationSettingsType, InstructorNotificationSettingsType, AnnouncementType
from comms.templates import ANNOUNCEMENT_EMAIL_TEMPLATE
from course.models import Course

from graphene import Boolean, DateTime, ID, String
from graphql_jwt.decorators import staff_member_required


class CreateAnnouncement(graphene.Mutation):
    class Arguments:
        announcement_id = ID(name='id')
        subject = String()
        body = String()
        course_id = ID(name='course')
        poster_id = ID(name='user')
        should_email = Boolean()
        should_sms = Boolean()       

    announcement = graphene.Field(AnnouncementType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        should_email = validated_data.pop('should_email', False)
        should_sms = validated_data.pop('should_sms', False)
        announcement, created = Announcement.objects.update_or_create(
            id=validated_data.pop('announcement_id', None),
            defaults=validated_data
        )
        if should_email:
            course = Course.objects.get(validated_data.get('course_id'))
            for enrollemnt.student in course.enrollemnt_set:
                primary_parent = enrollment.student.primary_parent
                email_address = primary_parent.user.email

            email = Email.objects.create(
                template_id=ANNOUNCEMENT_EMAIL_TEMPLATE,
                recipient=email_address,
                data={'username': user.first_name, 'token': token}
            )
            email.save()
        return CreateAnnoucement(announcement=announcement, created=created)


class DeleteAnnouncement(graphene.Mutation):
    class Arguments:
        announcement_id = graphene.ID(name='id')

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            announcement_obj = Announcement.objects.get(id=validated_data.get('announcement_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. Announcement does not exist.')
        annoucement_obj.delete()
        return DeleteAnnouncement(deleted=True)

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
        instructor_id = ID(name="instructor", required=True)
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
    create_announcement = CreateAnnouncement.Field()
    create_parent_notification_setting = MutateParentNotificationSettings.Field()
    create_instructor_notification_setting = MutateInstructorNotificationSettings.Field()

    delete_announcement = DeleteAnnouncement.Field()