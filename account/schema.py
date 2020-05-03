import graphene

from graphene_django.types import DjangoObjectType

from account.models import Student, School


# class UserType(DjangoObjectType):
#     class Meta:
#         model = User


class StudentType(DjangoObjectType):
    class Meta:
        model = Student


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class Query(object):
    student = graphene.Field(StudentType, user=graphene.Int(), email=graphene.String())
    school = graphene.Field(SchoolType, id=graphene.Int(), name=graphene.String())
    all_students = graphene.List(StudentType, grade=graphene.Int())
    all_schools = graphene.List(SchoolType, district=graphene.String())

    def resolve_student(self, info, **kwargs):
        user = kwargs.get('user')
        email = kwargs.get('email')

        if user:
            return Student.objects.get(user=user)

        if email:
            return Student.objects.get(user__email=email)

        return None

    def resolve_school(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')

        if id:
            return School.objects.get(id=id)

        if name:
            return School.objects.get(name=name)

        return None

    def resolve_all_students(self, info, **kwargs):
        grade = kwargs.get('grade')

        if grade:
            return Student.objects.filter(grade=grade)
        return Student.objects.all()

    def resolve_all_schools(self, info, **kwargs):
        district = kwargs.get('district')
        queryset = School.objects

        if district:
            queryset = queryset.filter(district=district)

        return queryset.all()
