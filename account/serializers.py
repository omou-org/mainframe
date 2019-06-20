from rest_framework import serializers


from account.models import (
	Student,
)


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
