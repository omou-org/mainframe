import graphene

from account.models import School
from account.schema import SchoolType


class CreateSchool(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        zipcode = graphene.String()
        district = graphene.String()

    ok = graphene.Boolean()
    school = graphene.Field(lambda: SchoolType)

    def mutate(self, info, name, zipcode, district):
        school = School(name=name, zipcode=zipcode, district=district)
        school.save()
        ok = True
        return CreateSchool(school=school, ok=ok)


class Mutation(graphene.ObjectType):
    create_school = CreateSchool.Field()
