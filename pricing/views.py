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
        
        course_students = set()
        sub_total = 0.0      

        disabled_discounts = body.get("disabled_discounts", [])
        usedDiscounts = []
        totalDiscountVal = 0.0

        # extract tutoring costs (assuming category/level combo exists)
        for TutorJSON in body.get("tutoring", []):
            tutoring_priceRules = PriceRule.objects.filter(
                Q(category = TutorJSON["category_id"]) &
                Q(academic_level = TutorJSON["academic_level"]) &
                Q(course_type = "Tutoring"))
            tuition = tutoring_priceRules[0].hourly_tuition
            sub_total += tuition * TutorJSON["duration"] * TutorJSON["sessions"]  

        # extract course costs and discounts
        for CourseJSON in body.get("courses", []):
            course = Course.objects.filter(course_id = CourseJSON["course_id"])
            course_subTotal = course.tuition*CourseJSON["sessions"]

            if course.type == 'C':
                course_students.add(course.user.id)

                # DateRangeDiscount
                dateRange_discounts = DateRangeDiscount.objects.filter(
                    Q(start_date__lte = course.start_date) &
                    Q(end_date__gte = course.end_date))
                
                for discount in dateRange_discounts:
                    if discount.id not in disabled_discounts and discount.active:
                        if discount.amount_type == 'percent':
                            amount = course_subTotal*(100.0-discount.amount)/100.0
                        else:
                            amount = discount.amount
                        totalDiscountVal += amount
                        usedDiscounts.append((discount.name, amount))
                
                # MultiCourseDiscount (sessions on course basis)            
                multiCourse_discounts = MultiCourseDiscount.objects.filter(num_sessions__lte = CourseJSON["sessions"])
                for discount in multiCourse_discounts.order_by("-num_sessions"):
                    # take highest applicable discount based on session count
                    if discount.id not in disabled_discounts and discount.active:
                        if discount.amount_type == 'percent':
                            amount = course_subTotal*(100.0-discount.amount)/100.0
                        else:
                            amount = discount.amount
                        totalDiscountVal += amount
                        usedDiscounts.append((discount.name, amount))
                        break
        
            sub_total += course_subTotal

         # sibling discount
        if len(course_students) > 1:
            totalDiscountVal += 25
            usedDiscounts.append(("Siblings Discount", 25))      
        
        # PaymentMethodDiscount
        payment_method = body["payment_method"]
        payment_method_discounts = PaymentMethodDiscount.objects.filter(payment_method=payment_method)
        for discount in payment_method_discounts:
            if discount.id not in disabled_discounts and discount.active:
                if discount.amount_type == 'percent':
                    amount = sub_total*(100.0-discount.amount)/100.0
                else:
                    amount = discount.amount
                totalDiscountVal += amount
                usedDiscounts.append((discount.name, amount))
        
        # price adjustment
        price_adjustment = body("price_adjustment", 0)

        data = {
            "sub_total" : sub_total,
            "discounts" : json.dumps(usedDiscounts),
            "price_adjustment" : price_adjustment,
            "total" : sub_total-totalDiscountVal-price_adjustment 
        }
        return JsonResponse(data)

class QuoteRuleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def get(self, request):
        # load request body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        priceRules = PriceRule.objects.filter(
            Q(category = body["category_id"]) &
            Q(academic_level = body["academic_level"]) &
            Q(course_type = body["course_size"]))

        data = {
            "per_session" : priceRules[0].hourly_tuition * body["duration"],
            "total" :  priceRules[0].hourly_tuition * body["duration"] * body["sessions"]
        }
        return JsonResponse(data)


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
