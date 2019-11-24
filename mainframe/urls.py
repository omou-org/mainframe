# mainframe URL Configuration
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authtoken import views as auth_views
from rest_framework import permissions

from mainframe.api_root import views


schema_view = get_schema_view(
   openapi.Info(
      title="Omou Backend API",
      default_version='v1',
      description="Documentation for Omou's Backend API",
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('search/', include('search.urls')),
    path('course/', include('course.urls')),
    path('account/', include('account.urls')),
    path('admin/', admin.site.urls),
    url(r'^$', views.api_root, name='api_root'),
    url(r'^auth_token/', auth_views.obtain_auth_token),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
