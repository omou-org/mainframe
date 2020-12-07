from onboarding.models import Business
from graphene import Field, ID, String
from graphene_django.types import DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required

class BusinessType(DjangoObjectType):
    class Meta:
        model = Business


class Query(object):
    business = Field(BusinessType, business_id=ID(), name=String())

    @login_required
    @staff_member_required
    def resolve_business(self, info, **kwargs):
        business_id = kwargs.get('business_id')
        name = kwargs.get('name')

        if business_id:
            return Business.objects.get(id=business_id)

        if name:
            return Business.objects.get(name=name)

        return None