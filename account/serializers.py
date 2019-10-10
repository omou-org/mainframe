from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.db import transaction
from django.contrib.auth.models import User

from account.models import (
    Note,
    Admin,
    Student,
    Parent,
    Instructor
)

class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        read_only_fields = (
            'id',
            'timestamp',
        )
        write_only_fields = (
            'user',
        )
        fields = (
            'id',
            'user',
            'timestamp',
            'title',
            'body',
            'important',
            'complete',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = (
            'id',
            'timestamp',
        )
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
        )
        extra_kwargs = {'password': {'write_only': True}}


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            user_info = validated_data.pop('user')
            user_info['username'] = user_info['email']
            User.objects.filter(email=instance.user.email).update(**user_info)

            Student.objects.filter(user__email=user_info['email']).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

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
            student = Student.objects.create(user=user, **validated_data)
            return student


    class Meta:
        model = Student
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'grade',
            'age',
            'school',
            'parent',
            'updated_at',
            'created_at',
        )


class ParentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            user_info = validated_data.pop('user')
            user_info['username'] = user_info['email']
            User.objects.filter(email=instance.user.email).update(**user_info)

            Parent.objects.filter(user__email=user_info['email']).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

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
            parent = Parent.objects.create(user=user, **validated_data)
            return parent

    class Meta:
        model = Parent
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'relationship',
            'updated_at',
            'created_at',
        )


class InstructorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            user_info = validated_data.pop('user')
            user_info['username'] = user_info['email']
            User.objects.filter(email=instance.user.email).update(**user_info)

            Instructor.objects.filter(user__email=user_info['email']).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

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
            instructor = Instructor.objects.create(user=user, **validated_data)
            return instructor

    class Meta:
        model = Instructor
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'age',
            'updated_at',
            'created_at',
        )


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            user_info = validated_data.pop('user')
            user_info['username'] = user_info['email']
            User.objects.filter(email=instance.user.email).update(**user_info)

            Admin.objects.filter(user__email=user_info['email']).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

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
            'admin_type',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'updated_at',
            'created_at',
        )