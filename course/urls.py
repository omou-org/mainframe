from django.urls import path

from course import views

urlpatterns = [
    path('catalog/', views.get_catalog, name='catalog'),
    path('catalog/categories', views.getCourseCategories, name='catalog'),
]
