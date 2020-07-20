import graphene

from scheduler.models import Session
from scheduler.schema import SessionType

from graphene import Boolean, DateTime, ID, String
from graphql_jwt.decorators import staff_member_required


class CreateSession(graphene.Mutation):
    class Arguments:
        session_id = ID(name='id')
        course_id = ID(name='course', required=True)
        title = String()
        details = String()
        instructor_id = ID(name='instructor')
        start_datetime = DateTime(required=True)
        end_datetime = DateTime(required=True)
        is_confirmed = Boolean()

    session = graphene.Field(SessionType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        session, created = Session.objects.update_or_create(
            id=validated_data.pop('session_id', None),
            defaults=validated_data
        )
        return CreateSession(session=session, created=created)


class Mutation(graphene.ObjectType):
    create_session = CreateSession.Field()
