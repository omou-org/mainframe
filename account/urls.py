from django.conf.urls import url
from django.urls import path

from account.views import StudentListView


urlpatterns = [
    url(
        r'students/get_students/',
        StudentListView.as_view(),
        name="student_list",
    ),
]



# urlpatterns = [
#     path('students/get_students/', views.get_students, name='get_students'),
#     path('instructors/get_instructors/', views.get_instructors, name='get_instructors'),
#     path('parents/get_parents/', views.get_parents, name='get_parents'),
# ]
