from rest_framework import serializers
from django.db import models

from account.models import (
    Student,
    Admin,
    Parent,
    Instructor
)

from course.models import (
    Course,
)

from scheduler.models import (
    Session,
)

from account.serializers import (
    StudentSerializer,
    AdminSerializer,
    ParentSerializer,
    InstructorSerializer
)

from course.serializers import (
    CourseSerializer,
)

from rest_framework.request import Request

class SearchViewSerializer(serializers.Serializer):
    
    def to_representation(self, value):
        if isinstance(value, Student): 
            serializer = StudentSerializer(value)
        elif isinstance(value, Instructor):
            serializer = InstructorSerializer(value)
        elif isinstance(value, Parent):
            serializer = ParentSerializer(value)
        elif isinstance(value, Admin):
            serializer = AdminSerializer(value)
        elif isinstance(value, Course):
            serializer = CourseSerializer(value)
        else:
            raise Exception("Not recognized model instance!")
        return serializer.data
