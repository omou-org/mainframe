from django.urls import path

from course import views

urlpatterns = [
    path('catalog/', views.get_catalog, name='get_catalog'),
    path('catalog/categories', views.get_course_categories, name='get_course_categories'),
    path('catalog/categories/<int:category_id>',
         views.get_courses_for_category, name='category-courses')
]
