from django.urls import include, path
from rest_framework import routers
from .views import AccountsSearchView, CoursesSearchView, SessionsSearchView

urlpatterns = [
    path(r"account/", AccountsSearchView.as_view(), name="accounts search"),
    path(r"course/", CoursesSearchView.as_view(), name="courses search"),
    path(r"session/", SessionsSearchView.as_view(), name="sessions search"),
]
