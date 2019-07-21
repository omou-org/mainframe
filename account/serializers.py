from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.db import transaction
from django.contrib.auth.models import User

from account.models import (
    Admin,
    Student,
    Parent,
    Instructor
)


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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'first_name',
            'last_name',
        )
        extra_kwargs = {'password': {'write_only': True}}


class AdminSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def create(self, validated_data):
        with transaction.atomic():
            # create user and token
            user_info = validated_data.pop('user')
            user = User.objects.create_user(
                email=user_info['email'],
                username=user_info['email'],
                password=user_info['password'],
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
            )
            Token.objects.get_or_create(user=user)

            # create account
            admin = Admin.objects.create(user=user, **validated_data)
            return admin

    class Meta:
        model = Admin
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'token',
            'admin_type',
            'gender',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
        )
