from django.urls import include, path
from rest_framework import routers
from .views import AccountsSearchView, CoursesSearchView

urlpatterns = [
    path(r'account/', AccountsSearchView.as_view(), name="accounts search"),
    path(r'courses/', CoursesSearchView.as_view(), name="courses search"),
]