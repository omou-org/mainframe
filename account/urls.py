from django.conf.urls import url

from account.views import StudentListView


urlpatterns = [
    url(
        r'students/get_students/',
        StudentListView.as_view(),
        name="student_list",
    ),
]
