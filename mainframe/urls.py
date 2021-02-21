# mainframe URL Configuration
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from graphene_django.views import GraphQLView
from rest_framework.authtoken import views as auth_views

from mainframe.api_root import views


GraphQLView.graphiql_template = "graphene_graphiql_explorer/graphiql.html"

urlpatterns = [
    path('pricing/', include('pricing.urls')),
    path('scheduler/', include('scheduler.urls')),
    path('search/', include('search.urls')),
    path('course/', include('course.urls')),
    path('account/', include('account.urls')),
    path('payment/', include('invoice.urls')),
    path('onboarding/', include('onboarding.urls')),
    path('admin/', admin.site.urls),
    path('graphql', GraphQLView.as_view(graphiql=True)),
    url(r'^$', views.api_root, name='api_root'),
    url(r'^auth_token/', auth_views.obtain_auth_token),
]
