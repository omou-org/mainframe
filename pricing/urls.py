from django.urls import include, path
from rest_framework import routers
from pricing import views

router = routers.DefaultRouter()
router.register(r'rule', views.PriceRuleViewSet)
router.register(r'discount', views.DiscountViewSet)
router.register(r'discount-multi-course', views.MultiCourseDiscountViewSet)
router.register(r'discount-date-range', views.DateRangeDiscountViewSet)
router.register(r'discount-payment-method', views.PaymentMethodDiscountViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(r'quote/', views.QuoteTotalView.as_view())
]
