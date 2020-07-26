import graphene

from comms.models import ParentNotificationSettings, Annoucement
from comms.schema import ParentNotificationSettingsType, AnnoucementType

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

class CreateAnnoucement(graphene.Mutation):
    class Arguments:
        annoucement_id = ID(name='id')
        subject = String()
        body = String()
        course_id = graphene.ID(name='courseId')
        user_id = graphene.ID(name='userId')       


    annoucement = graphene.Field(AnnoucementType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        annoucement, created = Annoucement.objects.update_or_create(
            id=validated_data.pop('annoucement_id', None),
            defaults=validated_data
        )
        return CreateAnnoucement(annoucement=annoucement, created=created)


class DeleteAnnoucement(graphene.Mutation):
    class Arguments:
        annoucement_id = graphene.ID(name='id')

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            annoucement_obj = Annoucement.objects.get(id=validated_data.get('annoucement_id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. Annoucement does not exist.')
        annoucement_obj.delete()
        return DeleteAnnoucement(deleted=True)


class Mutation(graphene.ObjectType):
    create_annoucement = CreateAnnoucement.Field()
    create_parent_notification_setting = MutateParentNotificationSettings.Field()

    delete_annoucement = DeleteAnnoucement.Field()
