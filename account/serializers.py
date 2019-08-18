from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.db import transaction
from django.contrib.auth.models import User

from account.models import (
    StudentNote,
    ParentNote,
    InstructorNote,
    Admin,
    Student,
    Parent,
    Instructor
)


class StudentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentNote
        read_only_fields = (
            'id',
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

class ParentNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentNote
        read_only_fields = (
            'id',
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

class InstructorNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstructorNote
        read_only_fields = (
            'id',
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
    token = serializers.SerializerMethodField()
    user = UserSerializer()
    notes = StudentNoteSerializer(source="studentnote_set", many=True)

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
            student = Student.objects.create(user=user, **validated_data)
            return student

    class Meta:
        model = Student
        read_only_fields = (
            'updated_at',
            'created_at',
            'notes',
        )
        fields = (
            'user',
            'token',
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
            'updated_at',
            'created_at',
            'notes',
        )


class ParentSerializer(serializers.ModelSerializer):
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
            'token',
            'gender',
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
            'token',
            'gender',
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
            'updated_at',
            'created_at',
        )
