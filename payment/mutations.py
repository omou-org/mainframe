import graphene
from graphene import Field, ID, Int, List, String, Float
from graphene.types.json import JSONString

from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.schema import PaymentType
from pricing.schema import price_quote_total

from graphql_jwt.decorators import login_required, staff_member_required

class CreatePayment(graphene.Mutation):
    class Arguments:
        method=String(required=True)
        disabled_discounts=List(Int)
        price_adjustment=Float()
        classes=List(JSONString)
        tutoring=List(JSONString)
        parent=Int()

    payment = graphene.Field(PaymentType)

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, **validated_data):
        #print(validated_data)
        data = validated_data
        data.update(price_quote_total(data))
        #print(data)

        discounts = data.pop("discounts")
        data["deductions"] = []
        for discount in discounts:
            data["deductions"].append(
                {
                    "discount":discount["id"],
                    "amount":discount["amount"]
                }
            )
        print(data)
        
        return None

        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return CreatePayment(payment=payment)

class Mutation(graphene.ObjectType):
    create_payment = CreatePayment.Field()
