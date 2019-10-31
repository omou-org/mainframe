from django.urls import include, path
from rest_framework import routers
from .views import AccountsSearchView, CoursesSearchView

#router = routers.DefaultRouter()
#router.register(r'', SearchView.as_view(), base_name="search")

urlpatterns = [
    path(r'account/', AccountsSearchView.as_view(), name="accounts search"),
    path(r'courses/', CoursesSearchView.as_view(), name="courses search")
]
