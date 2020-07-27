from django.conf import settings
import graphene

from comms.models import Email, ParentNotificationSettings, InstructorNotificationSettings
from comms.templates import (
    SCHEDULE_UPDATE_INSTRUCTOR_TEMPLATE,
    SCHEDULE_UPDATE_PARENT_TEMPLATE,
)
from scheduler.models import Session
from scheduler.schema import SessionType

from graphene import Boolean, DateTime, ID, String
from graphql_jwt.decorators import staff_member_required


class CreateSession(graphene.Mutation):
    class Arguments:
        session_id = ID(name='id')
        course_id = ID(name='course')
        title = String()
        details = String()
        instructor_id = ID(name='instructor')
        start_datetime = DateTime()
        end_datetime = DateTime()
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

        # send email for updated schedule
        if not created and 'start_datetime' in validated_data:
            for enrollment in session.course.enrollment_set:
                parent = enrollment.student.primary_parent
                Email.objects.create(
                    template_id=SCHEDULE_UPDATE_PARENT_TEMPLATE,
                    recipient=parent.user.email,
                    data={
                        'parent_name': parent.user.first_name,
                        'student_name': enrollment.student.user.first_name,
                        'business_name': settings.BUSINESS_NAME,
                        'schedule_updates': [
                            {
                                'scheduling_status': 'Update',
                                'course_name': enrollment.course.title,
                                'new_date': session.start_datetime.strftime('%m/%d/%Y'),
                                'new_time': session.start_datetime.strftime('%I:%M %p')
                            }
                        ]
                    }
                )

                instructor = session.instructor
                Email.objects.create(
                    template_id=SCHEDULE_UPDATE_INSTRUCTOR_TEMPLATE,
                    recipient=instructor.user.email,
                    data={
                        'instructor_name': instructor.user.first_name,
                        'business_name': settings.BUSINESS_NAME,
                        'schedule_updates': [
                            {
                                'scheduling_status': 'Update',
                                'course_name': enrollment.course.title,
                                'new_date': session.start_datetime.strftime('%m/%d/%Y'),
                                'new_time': session.start_datetime.strftime('%I:%M %p')
                            }
                        ]
                    }
                )

        return CreateSession(session=session, created=created)


class Mutation(graphene.ObjectType):
    create_session = CreateSession.Field()
