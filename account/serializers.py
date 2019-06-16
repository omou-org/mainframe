from rest_framework import serializers

from django.contrib.auth.models import User
from django.db import transaction

from account.models import (
	Instructor,
	Parent,
	Student,
)


class StudentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = (
			'user',
			'gender',
			'address',
			'city',
			'phone_number',
			'state',
			'zipcode',
		)
