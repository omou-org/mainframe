from django.contrib.auth import get_user_model
from account.models import (
    Student,
    Parent,
    Instructor
)
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email', 'first_name', 'last_name')


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        read_only_fields = (
            'updated_at',
            'created_at'
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

    def create(self, validated_data):
        User = get_user_model()

        user_data = validated_data.pop('user')

        new_user = User.objects.create(
            username=user_data['email'],
            password="omou12312",
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )

        student = Student.objects.create(user=new_user, **validated_data)

        return student


class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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

    def create(self, validated_data):
        User = get_user_model()

        user_data = validated_data.pop('user')

        new_user = User.objects.create(
            username=user_data['email'],
            password="omou12312",
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )

        parent = Parent.objects.create(user=new_user, **validated_data)

        return parent


class InstructorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

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

    def create(self, validated_data):
        User = get_user_model()

        user_data = validated_data.pop('user')

        new_user = User.objects.create(
            username=user_data['email'],
            password="omou12312",
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )

        instructor = Instructor.objects.create(user=new_user, **validated_data)

        return instructor
