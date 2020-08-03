import graphene
from django.conf import settings
from django.contrib.auth.models import User

from account.models import Admin
from comms.models import Announcement, Email, ParentNotificationSettings, InstructorNotificationSettings
from comms.schema import AnnouncementType, ParentNotificationSettingsType, InstructorNotificationSettingsType 
from comms.templates import ANNOUNCEMENT_EMAIL_TEMPLATE, SEND_EMAIL_TO_PARENT_TEMPLATE
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
            course = Course.objects.get(id=validated_data.get('course_id'))
            for enrollment in course.enrollment_set.all():
                primary_parent = enrollment.student.primary_parent
                email_address = primary_parent.user.email
                primary_parent_fullname = primary_parent.user.first_name + ' ' +primary_parent.user.last_name
                user = User.objects.get(id=validated_data.get('poster_id'))
                poster = user.first_name + ' ' + user.last_name
                email = Email.objects.create(
                    template_id=ANNOUNCEMENT_EMAIL_TEMPLATE,
                    recipient=email_address,
                    data={'subject': validated_data.get('subject'), 'body': validated_data.get('body'), 'poster_name': poster, 'course': course.title, 'parent_name': primary_parent_fullname}
                )
                email.save()
        return CreateAnnouncement(announcement=announcement, created=created)



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
        announcement_obj.delete()
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


class SendEmail(graphene.Mutation):
    class Arguments:
        subject = String()
        body = String()
        user_id = ID(name="userId")
        poster_id = ID(name='posterId')

    created = Boolean()
    
    @staticmethod
    def mutate(root, info, **validated_data):    
        poster = User.objects.get(id=validated_data.get('poster_id'))
        user = User.objects.get(id=validated_data.get('user_id'))
        poster_fullname = poster.first_name + ' ' + poster.last_name
        user_email = user.email
        user_fullname = user.first_name + ' ' + user.last_name
        email = Email.objects.create(
            template_id=SEND_EMAIL_TO_PARENT_TEMPLATE,
            recipient=user_email,
            data={'subject': validated_data.get('subject'), 'body': validated_data.get('body'), 'poster_name': poster_fullname, 'user_name': user_fullname, 'business_name': settings.BUSINESS_NAME}            
        )
        email.save()
        return SendEmail(created=True)


class Mutation(graphene.ObjectType):
    create_announcement = CreateAnnouncement.Field()
    create_parent_notification_setting = MutateParentNotificationSettings.Field()
    create_instructor_notification_setting = MutateInstructorNotificationSettings.Field()
    send_email = SendEmail.Field()

    delete_announcement = DeleteAnnouncement.Field()