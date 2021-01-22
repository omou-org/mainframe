from django.urls import include, path
from rest_framework import routers
from .views import FileUpload

urlpatterns = [
    path('import', FileUpload.as_view())
]