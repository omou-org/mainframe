import graphene
from graphql import GraphQLError

from django.conf import settings
from onboarding.models import Business
from onboarding.schema import BusinessType
from graphql_jwt.decorators import login_required, staff_member_required

import stripe


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


class RequestCreateStripe(graphene.Mutation):
    class Arguments:
        business_id = graphene.ID(name='business')

    onboarding_url = graphene.String()
    created = graphene.Boolean()

    @staticmethod
    @login_required
    @staff_member_required
    def mutate(root, info, business_id):
        try:
            business = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            raise GraphQLError("Failed mutation. Business with id does not exist.")

        stripe.api_key = settings.STRIPE_API_KEY
        account = stripe.Account.create(
            type='standard',
            country='US',
            email=business.email
        )

        account_links = stripe.AccountLink.create(
            account=account.id,
            refresh_url='https://omoulearning.com',
            return_url='https://omoulearning.com/onboarding/complete',
            type='account_onboarding'
        )

        return RequestCreateStripe(onboarding_url=account_links.url, created=True)


class Mutation(graphene.ObjectType):
    request_create_stripe = RequestCreateStripe.Field()
    create_business = CreateBusiness.Field()
