from graphene import Enum, Field, Int, ID, List, ObjectType, String
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required

from django.db.models import Q, CharField
from django.db.models.functions import Cast

from datetime import datetime
import arrow

from account.models import Parent
from course.schema import EnrollmentType
from course.models import Course, Enrollment
from invoice.models import (
    Invoice,
    Deduction,
    Registration,
    RegistrationCart
)
from search.schema import paginate


class PaymentChoiceEnum(Enum):
    PAID = 'paid'
    UNPAID = 'unpaid'
    CANCELED = 'canceled'


class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice


class DeductionType(DjangoObjectType):
    class Meta:
        model = Deduction


class RegistrationType(DjangoObjectType):
    class Meta:
        model = Registration


class CartType(DjangoObjectType):
    class Meta:
        model = RegistrationCart


class InvoiceResults(ObjectType):
    results = List(InvoiceType, required=True)
    total = Int()


class Query(object):
    invoice = Field(InvoiceType, invoice_id=ID())
    deduction = Field(DeductionType, deduction_id=ID())
    registration = Field(RegistrationType, registration_id=ID())
    registration_cart = Field(CartType, cart_id=ID(), parent_id=ID())

    invoices = Field(InvoiceResults,
                    query=String(),
                    start_date=String(),
                    end_date=String(),
                    payment_status=PaymentChoiceEnum(),
                    page=Int(),
                    page_size=Int())

    deductions = List(DeductionType, invoice_id=ID())
    registrations = List(RegistrationType, invoice_id=ID())

    unpaid_sessions = List(EnrollmentType)

    def resolve_invoice(self, info, **kwargs):
        invoice_id = kwargs.get('invoice_id')

        if invoice_id:
            return Invoice.objects.get(id=invoice_id)

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

    @login_required
    def resolve_invoices(self, info, **kwargs):
        query = kwargs.get('query')
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        payment_status = kwargs.get('payment_status')

        user_id = info.context.user.id
        if Parent.objects.filter(user__id=user_id).exists():
            invoices = Invoice.objects.filter(parent__user__id=user_id)
        else: # admin
            invoices = Invoice.objects.all()
        
        if query: # parent name and/or invoice id
            for token in query.split():
                if all(char.isdigit() for char in token):
                    invoices = invoices.annotate(id_str=Cast('id', CharField())).filter(id_str__startswith=token)
                else:
                    invoices = invoices.filter(
                        Q(parent__user__first_name__icontains = token) |
                        Q(parent__user__last_name__icontains = token) |
                        Q(parent__user__username__iexact = token)
                    )

        if start_date and end_date:
            invoices = invoices.filter(
                created_at__gt=arrow.get(start_date).datetime,
                created_at__lt=arrow.get(end_date).datetime
            )
        
        if payment_status:
            invoices = invoices.filter(payment_status=payment_status)

        paginated = paginate(invoices, kwargs.get('page'), kwargs.get('page_size'))
        return InvoiceResults(results=paginated, total=invoices.count())

    def resolve_deductions(self, info, **kwargs):
        invoice_id = kwargs.get('invoice_id')

        if invoice_id:
            return Deduction.objects.filter(payament=invoice_id)
        return Deduction.objects.all()

    def resolve_registrations(self, info, **kwargs):
        invoice_id = kwargs.get('invoice_id')

        if invoice_id:
            return Registration.objects.filter(payament=invoice_id)
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
