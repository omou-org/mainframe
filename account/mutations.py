import graphene

from account.models import School
from account.schema import SchoolType
from account.serializers import (
    StudentSerializer,
    AdminSerializer,
)

from graphene_django.rest_framework.mutation import SerializerMutation


class CreateSchool(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        zipcode = graphene.String()
        district = graphene.String()

    ok = graphene.Boolean()
    school = graphene.Field(lambda: SchoolType)

    def mutate(self, info, name, zipcode, district):
        school = School.objects.create(name=name, zipcode=zipcode, district=district)
        ok = True
        return CreateSchool(school=school, ok=ok)


class CreateStudent(graphene.Mutation):
    class Arg
    class Meta:
        serializer_class = StudentSerializer
        convert_choices_to_enum = False


class CreateAdmin(SerializerMutation):
    class Meta:
        serializer_class = AdminSerializer


class Mutation(graphene.ObjectType):
    create_school = CreateSchool.Field()
    create_student = CreateStudent.Field()
