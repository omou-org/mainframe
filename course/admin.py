from django.contrib import admin
from course.models import Course, CourseCategory

# Register your models here.

admin.site.register(Course)
admin.site.register(CourseCategory)
