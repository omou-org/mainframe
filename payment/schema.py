from graphene import Field, Int, ID, List
from graphene_django.types import DjangoObjectType

from course.schema import EnrollmentType
from course.models import Course, Enrollment
from payment.models import (
    Payment,
    Deduction,
    Registration,
)


class PaymentType(DjangoObjectType):
    class Meta:
        model = Payment


class DeductionType(DjangoObjectType):
    class Meta:
        model = Deduction


class RegistrationType(DjangoObjectType):
    class Meta:
        model = Registration


class Query(object):
    payment = Field(PaymentType, payment_id=ID())
    deduction = Field(DeductionType, deduction_id=ID())
    registration = Field(RegistrationType, registration_id=ID())

    payments = List(PaymentType, parent_id=ID())
    deductions = List(DeductionType, payment_id=ID())
    registrations = List(RegistrationType, payment_id=ID())

    unpaid_sessions = List(EnrollmentType)

    def resolve_payment(self, info, **kwargs):
        payment_id = kwargs.get('payment_id')

        if payment_id:
            return Payment.objects.get(id=payment_id)

        return None

    def resolve_deduction(self, info, **kwargs):
        deduction_id = kwargs.get('deduction_id')

        if deduction_id:
            return Deduction.objects.get(id=deduction_id)

        return None

    def resolve_registration(self, info, **kwargs):
        registration_id = kwargs.get('registration_id')

        if registration_id:
            return Registration.objects.get(id=registration_id)

        return None

    def resolve_payments(self, info, **kwargs):
        parent_id = kwargs.get('parent_id')

        if parent_id:
            return Payment.objects.filter(parent=parent_id)
        return Payment.objects.all()

    def resolve_deductions(self, info, **kwargs):
        payment_id = kwargs.get('payment_id')

        if payment_id:
            return Deduction.objects.filter(payament=payment_id)
        return Deduction.objects.all()

    def resolve_registrations(self, info, **kwargs):
        payment_id = kwargs.get('payment_id')

        if payment_id:
            return Registration.objects.filter(payament=payment_id)
        return Registration.objects.all()

    def resolve_unpaid_sessions(self, info, **kwargs):
        enrollments = Enrollment.objects.all()
        final_enrollments = []
        for enrollment in enrollments:
            if enrollment.course.course_type == Course.CLASS and enrollment.sessions_left < 0:
                final_enrollments.append(enrollment)
            elif enrollment.sessions_left <= 0:
                final_enrollments.append(enrollment)

        return final_enrollments
