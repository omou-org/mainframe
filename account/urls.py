from django.urls import path

from account import views

urlpatterns = [
    path('students/get_students/', views.get_students, name='get_students'),
    path('instructors/get_instructors/', views.get_instructors, name='get_instructors'),
]
