import uuid

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.db import transaction
from django.contrib.auth.models import User

from account.models import (
    Note,
    Admin,
    Student,
    Parent,
    Instructor,
    InstructorAvailability,
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
            'is_staff',
        )
        fields = (
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'is_staff',
        )
        extra_kwargs = {'password': {'write_only': True}}


class NonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = (
            'id',
            'timestamp',
        )
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
        )


class StudentSerializer(serializers.ModelSerializer):
    user = NonUserSerializer()
    enrollment_id_list = serializers.SerializerMethodField()

    def get_enrollment_id_list(self, obj):
        return obj.enrollment_id_list

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "user" in validated_data:
                user_info = validated_data.pop('user')
                User.objects.filter(id=instance.user.id).update(**user_info)
            Student.objects.filter(user__id=instance.user.id).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

    def create(self, validated_data):
        with transaction.atomic():
            # create user and token
            user_info = validated_data.pop('user')
            user = User.objects.create_user(
                username=uuid.uuid4(),
                password="password",
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
            )
            Token.objects.get_or_create(user=user)

            # create account
            student = Student.objects.create(
                user=user,
                account_type='student',
                **validated_data
            )
            return student

    class Meta:
        model = Student
        read_only_fields = (
            'enrollment_id_list',
            'account_type',
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'user_uuid',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'grade',
            'school',
            'primary_parent',
            'secondary_parent',
            'enrollment_id_list',
            'account_type',
            'updated_at',
            'created_at',
        )


class ParentSerializer(serializers.ModelSerializer):
    user = NonUserSerializer()
    student_list = serializers.SerializerMethodField()

    def get_student_list(self, obj):
        return obj.student_list

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "user" in validated_data:
                user_info = validated_data.pop('user')
                User.objects.filter(id=instance.user.id).update(**user_info)
            Parent.objects.filter(user__id=instance.user.id).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

    def create(self, validated_data):
        with transaction.atomic():
            # create user and token
            user_info = validated_data.pop('user')
            user = User.objects.create_user(
                username=user_info.get("email", uuid.uuid4()),
                email=user_info.get("email", None),
                password="password",
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
            )
            Token.objects.get_or_create(user=user)

            # create account
            parent = Parent.objects.create(
                user=user,
                account_type='parent',
                **validated_data
            )
            return parent

    class Meta:
        model = Parent
        read_only_fields = (
            'student_list',
            'account_type',
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'user_uuid',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'relationship',
            'secondary_phone_number',
            'student_list',
            'account_type',
            'updated_at',
            'created_at',
        )


class InstructorSerializer(serializers.ModelSerializer):
    user = NonUserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "user" in validated_data:
                user_info = validated_data.pop('user')
                User.objects.filter(id=instance.user.id).update(**user_info)
            Instructor.objects.filter(user__id=instance.user.id).update(**validated_data)
            instance.refresh_from_db()
            instance.save()
            return instance

    def create(self, validated_data):
        with transaction.atomic():
            # create user and token
            user_info = validated_data.pop('user')
            user = User.objects.create_user(
                username=user_info.get("email", uuid.uuid4()),
                email=user_info.get("email", None),
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
            )
            Token.objects.get_or_create(user=user)

            # create account
            instructor = Instructor.objects.create(
                user=user,
                account_type='instructor',
                **validated_data,
            )
            return instructor

    class Meta:
        model = Instructor
        read_only_fields = (
            'account_type',
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'user_uuid',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'account_type',
            'updated_at',
            'created_at',
            'biography',
            'experience',
            'subjects',
            'language',
        )


class InstructorAvailablitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InstructorAvailability
        read_only_fields = (
            'updated_at',
            'created_at',
        )
        fields = (
            'instructor',
            'monday_start_time',
            'monday_end_time',
            'tuesday_start_time',
            'tuesday_end_time',
            'wednesday_start_time',
            'wednesday_end_time',
            'thursday_start_time',
            'thursday_end_time',
            'friday_start_time',
            'friday_end_time',
            'saturday_start_time',
            'saturday_end_time',
            'sunday_start_time',
            'sunday_end_time',
            'updated_at',
            'created_at',
        )


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    def get_token(self, obj):
        return obj.user.auth_token.key

    def update(self, instance, validated_data):
        with transaction.atomic():
            if "user" in validated_data:
                user_info = validated_data.pop('user')
                User.objects.filter(id=instance.user.id).update(**user_info)
            Admin.objects.filter(user__id=instance.user.id).update(**validated_data)
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
            if validated_data['admin_type'] == 'owner':
                user.is_staff = True
                user.save()
            Token.objects.get_or_create(user=user)

            # create account
            admin = Admin.objects.create(
                user=user,
                account_type='admin',
                **validated_data
            )
            return admin

    class Meta:
        model = Admin
        read_only_fields = (
            'account_type',
            'updated_at',
            'created_at',
        )
        fields = (
            'user',
            'user_uuid',
            'admin_type',
            'gender',
            'birth_date',
            'address',
            'city',
            'phone_number',
            'state',
            'zipcode',
            'account_type',
            'updated_at',
            'created_at',
        )