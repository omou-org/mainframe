import graphene
from graphql import GraphQLError

from onboarding.models import Business
from onboarding.schema import BusinessType
from graphql_jwt.decorators import login_required, staff_member_required


class CreateBusiness(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        phone = graphene.String()
        email = graphene.String()
        address = graphene.String()

    business = graphene.Field(BusinessType)
    created = graphene.Boolean()

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, **validated_data):
        if (
            "name" in validated_data
            and Business.objects.filter(name=validated_data["name"]).count() > 0
        ):
            raise GraphQLError("Failed mutation. Business with name already exists.")

        business, created = Business.objects.update_or_create(
            id=validated_data.pop('id', None),
            defaults=validated_data
        )
        return CreateBusiness(business=business, created=created)


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()