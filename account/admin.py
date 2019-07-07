from django.contrib import admin
from account.models import (
    Admin,
    Instructor,
    Parent,
    Student,
)

# Register your models here.
admin.site.register(Admin)
admin.site.register(Instructor)
admin.site.register(Parent)
admin.site.register(Student)
