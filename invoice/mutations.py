from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

import graphene
import stripe
from graphene import Field, ID, Int, List, String, Float, Boolean
from graphql import GraphQLError

from account.models import Parent
from course.models import Enrollment
from invoice.models import Invoice, RegistrationCart
from invoice.serializers import InvoiceSerializer
from invoice.schema import InvoiceType, CartType
from pricing.schema import price_quote_total, ClassQuote, TutoringQuote

from graphql_jwt.decorators import login_required, staff_member_required


class EnrollmentQuote(graphene.InputObjectType):     
    enrollment = Int()
    num_sessions = Int()


class CreateInvoice(graphene.Mutation):
    class Arguments:
        method = String(required=True)
        disabled_discounts = List(ID)
        price_adjustment = Float()
        classes = List(ClassQuote)
        tutoring = List(TutoringQuote)
        parent = ID(required=True)
        registrations = List(EnrollmentQuote)
        payment_status = Boolean(name="isPaid")
    
    invoice = Field(InvoiceType)
    stripe_connected_account = String()
    stripe_checkout_id = String()
    created = Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, **validated_data):
        data = validated_data
        data.update(price_quote_total(data))    
        
        discounts = data.pop("discounts")
        data["deductions"] = []
        for discount in discounts:
            data["deductions"].append(
                {
                    "discount": discount["id"],
                    "amount": discount["amount"]
                }
            )

        serializer = InvoiceSerializer(data=data, context={'user_id': info.context.user.id})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        stripe_checkout_id = None
        if validated_data['method'] == 'credit_card':
            stripe.api_key = settings.STRIPE_API_KEY
            line_items = []
            for registration in data["registrations"]:
                enrollment = Enrollment.objects.get(id=registration["enrollment"])
                course = enrollment.course
                line_items.append({
                    'name': course.title,
                    'amount': round(course.total_tuition * registration["num_sessions"] / course.num_sessions),
                    'currency': 'usd',
                    'quantity': 1,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                success_url=f'http://localhost:3000/registration/receipt/{invoice.id}/',
                cancel_url='http://localhost:3000/registration/cart/',
                stripe_account='acct_1HqSAYETk4EmXsx3',
            )
            stripe_checkout_id = session.id

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Invoice).pk,
            object_id=invoice.id,
            object_repr=f"{invoice.parent.user.first_name} {invoice.parent.user.last_name}, {invoice.method}",
            action_flag=ADDITION
        )
        return CreateInvoice(
            invoice=invoice,
            stripe_connected_account='acct_1HqSAYETk4EmXsx3',
            stripe_checkout_id=stripe_checkout_id,
            created=True
        )


class CreateRegistrationCart(graphene.Mutation):
    class Arguments:
        parent = ID(required=True)
        registration_preferences = String()
    
    registrationCart = Field(CartType)

    @staticmethod
    @login_required
    def mutate(root, info, **validated_data):
        parent_queryset = Parent.objects.filter(user__id = validated_data["parent"])
        if parent_queryset.count() == 0:
            raise GraphQLError('Failed mutation. Parent does not exist.')
        validated_data.update({"parent":parent_queryset[0]})    

        cart_queryset = RegistrationCart.objects.filter(parent = parent_queryset[0])   
        cart, created = RegistrationCart.objects.update_or_create(
            id=cart_queryset[0].id if cart_queryset.count() > 0 else None,
            defaults=validated_data
        )
        return CreateRegistrationCart(registrationCart=cart)


class Mutation(graphene.ObjectType):
    create_invoice = CreateInvoice.Field()
    create_registration_cart = CreateRegistrationCart.Field()
