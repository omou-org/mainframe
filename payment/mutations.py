import graphene
from graphene import Field, ID, Int, List, String, Float
from graphql import GraphQLError

from account.models import Parent
from payment.models import Payment, RegistrationCart
from payment.serializers import PaymentSerializer
from payment.schema import PaymentType, CartType
from pricing.schema import price_quote_total, ClassQuote, TutoringQuote

from graphql_jwt.decorators import login_required, staff_member_required


class EnrollmentQuote(graphene.InputObjectType):     
    enrollment = Int()
    num_sessions = Int()


class CreatePayment(graphene.Mutation):
    class Arguments:
        method = String(required=True)
        disabled_discounts = List(ID)
        price_adjustment = Float()
        classes = List(ClassQuote)
        tutoring = List(TutoringQuote)
        parent = ID(required=True)
        registrations = List(EnrollmentQuote)
    
    payment = Field(PaymentType)

    @staticmethod
    @login_required
    @staff_member_required
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
        
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return CreatePayment(payment=payment)


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
    create_payment = CreatePayment.Field()
    create_registration_cart = CreateRegistrationCart.Field()
