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
        writable_fields = (
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
            'parent',
        )
        fields = read_only_fields + writable_fields


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        writable_fields = (
            'user',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'relationship',
        )
        fields = read_only_fields + writable_fields


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        writable_fields = (
            'user',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'age',
        )
        fields = read_only_fields + writable_fields
