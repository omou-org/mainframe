from django.db import models

class Student(models.Model):
	# Gender
	MALE = 'M'
	FEMALE = 'F'
	UNSPECIFIED = 'U'
	GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
		(UNSPECIFIED, 'Unspecified'),
    )

	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	email = models.CharField(max_length=20)
	gender = models.CharField(
		max_length=1,
		choices=GENDER_CHOICES,
		default=UNSPECIFIED,
	)
	created_at = models.DateTimeField('date created')
