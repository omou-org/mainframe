# mainframe URL Configuration
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken import views as auth_views
from rest_framework.documentation import include_docs_urls

from mainframe.api_root import views


urlpatterns = [
    url(r'^$', views.api_root, name='api_root'),
    url(r'^auth_token/', auth_views.obtain_auth_token),
    url(r'^docs/', include_docs_urls('Omou Backend API Docs')),
    path('api/courses/', include('course.urls')),
    path('api/account/', include('account.urls')),
    path('admin/', admin.site.urls),
]
