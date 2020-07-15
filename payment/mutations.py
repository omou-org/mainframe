import graphene
from graphene import Field, ID, Int, List, String, Float
from graphene.types.json import JSONString

from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.schema import PaymentType
from pricing.schema import price_quote_total, ClassQuote, TutoringQuote

from graphql_jwt.decorators import login_required, staff_member_required


class EnrollmentQuote(graphene.InputObjectType):     
    enrollment = Int()
    num_sessions = Int()


class CreatePayment(graphene.Mutation):
    class Arguments:
        method = String(required=True)
        disabled_discounts = List(Int)
        price_adjustment = Float()
        base_amount = Float()
        classes = List(ClassQuote)
        tutoring = List(TutoringQuote)
        parent = ID(name='parent', required=True)
        registrations = List(EnrollmentQuote)
    
    payment = graphene.Field(PaymentType)

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


class Mutation(graphene.ObjectType):
    create_payment = CreatePayment.Field()
