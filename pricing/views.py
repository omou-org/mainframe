from django.shortcuts import render
from django.db.models import Q
from django.http import JsonResponse

from course.models import Course

from pricing.models import (
    PriceRule,
    Discount,
    MultiCourseDiscount,
    DateRangeDiscount,
    PaymentMethodDiscount,
)
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from mainframe.permissions import IsDev, ReadOnly
import json

from pricing.serializers import (
    PriceRuleSerializer,
    DiscountSerializer,
    MultiCourseDiscountSerializer,
    DateRangeDiscountSerializer,
    PaymentMethodDiscountSerializer,
)

# Create your views here.


class PriceRuleViewSet(viewsets.ModelViewSet):
    """"
    API endpoint that allows prices to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer

class QuoteTotalView(APIView): 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request):
        # load request body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # payment_method
        # courses
            # course_id
            # sessions
        # tutoring
            # category_id
            # academic_level
            # sessions
            # duration
        # students
            # id
        # disabled_discounts
            # id
        # price_adjustment
        
        course_students = set()

        sub_total_course = 0.0
        sub_total_smallGroup = 0.0
        sub_total_tutoring = 0.0

        # extract courses costs
        for course in body.get("courses", []):
            CourseObject = Course.objects.filter(course_id = course["course_id"])
            tuition = CourseObject.tuition

            if CourseObject.type == 'C':
                course_students.add(CourseObject.user.id)
                sub_total_course += tuition * course.get("sessions", 0)
            if CourseObject.type == 'S':
                sub_total_smallGroup += tuition * course.get("sessions", 0)
            
        # extract tutoring costs (assuming category/level combo exists)
        for tutelage in body.get("tutoring", []):
            tutoring_priceRules = PriceRule.objects.filter(
                Q(category = tutelage.get("category_id","")) &
                Q(academic_level = tutelage.get("academic_level","")))
            tuition = tutoring_priceRules[0].hourly_tuition
            sub_total_tutoring += tuition * tutelage.get("duration", 0) * tutelage.get("sessions", 0)
        
        # total including course tuition, discounts, and price adjustments

        fixedDiscount = 0.0
        percentDiscount = 0.0

        # include price adjustment
        price_adjustment = body.get("price_adjustment", 0)
        total += price_adjustment

        # ignore disabled discounts
        disabled_discounts = body.get("disabled_discounts", [])

        # PaymentMethodDiscount
        payment_method = body.get("payment_method", "")
        payment_method_discounts = PaymentMethodDiscount.objects.filter(payment_method=payment_method)
        for discount in payment_method_discounts:
            pass

        # DateRangeDiscount

        # MultiCourseDiscount


        student_count = 0
        student_count = len(body.get("students", []))
        
        data = {
            "sub_total" : sub_total,
            "discounts" : json.dumps(discounts),
            "price_adjustment" : price_adjustment,
            "total" : total
        }
        return JsonResponse(data)
        
        # sub_total: //sum total of all course tuitions,
        # discounts: [
        # {
        #    amount: 20,
        #    discount_title: "EARLY BIRD"
        #}, 
        #],
        # price_adjustment: 100,
        # total: // total including course tuition, discounts, and price adjustment 

class DiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows custom discounts to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer


class MultiCourseDiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows custom multi-course and account discounts to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = MultiCourseDiscount.objects.all()
    serializer_class = MultiCourseDiscountSerializer


class DateRangeDiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows custom date range discounts to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = DateRangeDiscount.objects.all()
    serializer_class = DateRangeDiscountSerializer


class PaymentMethodDiscountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows custom payment method discounts to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = PaymentMethodDiscount.objects.all()
    serializer_class = PaymentMethodDiscountSerializer
