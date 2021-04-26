import graphene
from graphql import GraphQLError

from account.schema import (
    AdminType
)
from account.mutations import (
    GenderEnum,
    UserInput
)

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


class CreateOwnerAndBusiness(graphene.Mutation):
    class Arguments:
        # User fields
        user = UserInput(required=True)
        gender = GenderEnum()
        birth_date = graphene.Date()
        address = graphene.String()
        city = graphene.String()
        phone_number = graphene.String()
        state = graphene.String()
        zipcode = graphene.String()

    owner = graphene.Field(AdminType)
    owner_created = graphene.Boolean()

    business = graphene.Field(BusinessType)
    business_created = graphene.Boolean()

    @staticmethod
    def mutate(root, info, **validated_data):

        
        pass
        # admin type is Owner


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    create_owner_and_business = CreateOwnerAndBusiness.Field()
