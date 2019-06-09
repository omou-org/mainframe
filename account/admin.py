from django.contrib import admin
from account.models import (
	Instructor,
	Parent,
	Student,
)

# Register your models here.

admin.site.register(Instructor)
admin.site.register(Parent)
admin.site.register(Student)
