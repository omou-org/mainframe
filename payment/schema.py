from graphene import Field, ID, List, String
from graphene_django.types import DjangoObjectType

from datetime import datetime
import arrow

from course.schema import EnrollmentType
from course.models import Course, Enrollment
from payment.models import (
    Payment,
    Deduction,
    Registration,
    RegistrationCart
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


class CartType(DjangoObjectType):
    class Meta:
        model = RegistrationCart


class Query(object):
    payment = Field(PaymentType, payment_id=ID())
    deduction = Field(DeductionType, deduction_id=ID())
    registration = Field(RegistrationType, registration_id=ID())
    registration_cart = Field(CartType, cart_id=ID(), parent_id=ID())

    payments = List(PaymentType, parent_id=ID(), start_date=String(), end_date=String())
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
    
    def resolve_registration_cart(self, info, **kwargs):
        cart_id = kwargs.get('cart_id')
        parent_id = kwargs.get('parent_id')

        if cart_id:
            return RegistrationCart.objects.get(id=cart_id)
        
        if parent_id:
            return RegistrationCart.objects.get(parent=parent_id)

        return None

    def resolve_payments(self, info, **kwargs):
        parent_id = kwargs.get('parent_id')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')

        if parent_id:
            if start_date and end_date:
                return Payment.objects.filter(
                    created_at__gt=arrow.get(start_date).datetime,
                    created_at__lt=arrow.get(end_date).datetime,
                    parent=parent_id
                )
            return Payment.objects.filter(parent=parent_id)
        if start_date and end_date:
            return Payment.objects.filter(
                created_at__gt=datetime.date(start_date),
                created_at__lt=datetime.date(end_date)
            )
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
