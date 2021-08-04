from django.conf import settings
import graphene

from comms.models import (
    Email,
    ParentNotificationSettings,
    InstructorNotificationSettings,
)
from comms.templates import (
    SCHEDULE_UPDATE_INSTRUCTOR_TEMPLATE,
    SCHEDULE_UPDATE_PARENT_TEMPLATE,
)
from scheduler.models import Session, SessionNote, Attendance, TutoringRequest
from scheduler.schema import SessionType, SessionNoteType, AttendanceType, TutoringRequestType

from graphene import Boolean, DateTime, ID, String, Enum, Date, Time, Int
from graphql_jwt.decorators import staff_member_required


class AttendanceStatusEnum(Enum):
    PRESENT = "present"
    TARDY = "tardy"
    ABSENT = "absent"
    UNSET = "unset"


class CreateSession(graphene.Mutation):
    class Arguments:
        session_id = ID(name="id")
        course_id = ID(name="course")
        title = String()
        details = String()
        instructor_id = ID(name="instructor")
        start_datetime = DateTime()
        end_datetime = DateTime()
        is_confirmed = Boolean()

    session = graphene.Field(SessionType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        session, created = Session.objects.update_or_create(
            id=validated_data.pop("session_id", None), defaults=validated_data
        )

        # send email for updated schedule
        if not created and "start_datetime" in validated_data:
            for enrollment in session.course.enrollment_set.all():
                parent = enrollment.student.primary_parent
                Email.objects.create(
                    template_id=SCHEDULE_UPDATE_PARENT_TEMPLATE,
                    recipient=parent.user.email,
                    data={
                        "parent_name": parent.user.first_name,
                        "student_name": enrollment.student.user.first_name,
                        "business_name": settings.BUSINESS_NAME,
                        "schedule_updates": [
                            {
                                "scheduling_status": "Update",
                                "course_name": enrollment.course.title,
                                "new_date": session.start_datetime.strftime("%m/%d/%Y"),
                                "new_time": session.start_datetime.strftime("%I:%M %p"),
                            }
                        ],
                    },
                )

                instructor = session.instructor
                Email.objects.create(
                    template_id=SCHEDULE_UPDATE_INSTRUCTOR_TEMPLATE,
                    recipient=instructor.user.email,
                    data={
                        "instructor_name": instructor.user.first_name,
                        "business_name": settings.BUSINESS_NAME,
                        "schedule_updates": [
                            {
                                "scheduling_status": "Update",
                                "course_name": enrollment.course.title,
                                "new_date": session.start_datetime.strftime("%m/%d/%Y"),
                                "new_time": session.start_datetime.strftime("%I:%M %p"),
                            }
                        ],
                    },
                )

        return CreateSession(session=session, created=created)


class CreateSessionNote(graphene.Mutation):
    class Arguments:
        note_id = ID(name="id")
        subject = String()
        body = String()
        poster_id = ID(name="user")
        session_id = ID(name="sessionId")

    session_note = graphene.Field(SessionNoteType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        session_note, created = SessionNote.objects.update_or_create(
            id=validated_data.pop("note_id", None), defaults=validated_data
        )
        return CreateSessionNote(session_note=session_note, created=created)


class DeleteSessionNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.ID(name="id")

    deleted = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        try:
            session_note_obj = SessionNote.objects.get(id=validated_data.get("note_id"))
        except ObjectDoesNotExist:
            raise GraphQLError("Failed delete mutation. Session Note does not exist.")
        session_note_obj.delete()
        return DeleteSessionNote(deleted=True)


class UpdateAttendance(graphene.Mutation):
    class Arguments:
        attendance_id = ID(name="id")
        status = AttendanceStatusEnum()

    attendance = graphene.Field(AttendanceType)

    @staticmethod
    def mutate(root, info, **validated_data):
        attendance, created = Attendance.objects.update_or_create(
            id=validated_data.pop("attendance_id", None), defaults=validated_data
        )
        return UpdateAttendance(attendance=attendance)


class CreateTutoringRequest(graphene.Mutation):
    class Arguments:
        tutoring_request_id = ID(name="id")
        student_id = ID()
        instructor_id = ID()
        course_category_id = ID()
        start_date = Date()
        end_date = Date()
        day_of_week = String()
        start_time = Time()
        duration = Int()
        request_status = String()
        invoice_setting = String()

    tutoring_request = graphene.Field(TutoringRequestType)
    created = Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):
        tutoring_request, created = TutoringRequest.objects.update_or_create(
            id=validated_data.pop("tutoring_request_id", None), defaults=validated_data
        )
        return CreateTutoringRequest(tutoring_request=tutoring_request, created=created)


class Mutation(graphene.ObjectType):
    create_session = CreateSession.Field()
    create_session_note = CreateSessionNote.Field()
    delete_session_note = DeleteSessionNote.Field()
    update_attendance = UpdateAttendance.Field()
    create_tutoring_request = CreateTutoringRequest.Field()

