from django.urls import include, path
from rest_framework import routers
from .views import SearchView

#router = routers.DefaultRouter()
#router.register(r'', SearchView.as_view(), base_name="search")

urlpatterns = [
    path(r'', SearchView.as_view(), name="search")
]