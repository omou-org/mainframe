from django.urls import include, path
from rest_framework import routers
from .views import AccountsSearchView, CoursesSearchView, AccountsSuggestionsView, CoursesSuggestionsView

urlpatterns = [
    path(r'account/', AccountsSearchView.as_view(), name="accounts search"),
    path(r'courses/', CoursesSearchView.as_view(), name="courses search"),
    path(r'account-suggestions/', AccountsSuggestionsView.as_view(), name="account suggestions"),
    path(r'courses-suggestions/', CoursesSuggestionsView.as_view(), name="course suggestions")
]