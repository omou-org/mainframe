from account.models import (
    Student,
    Parent,
    Instructor
)
from rest_framework import serializers


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'grade',
            'age',
            'school',
            'parent'
        )


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'relationship'
        )


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'age'
        )
