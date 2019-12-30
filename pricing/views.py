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
            tutoring_priceRules = PriceRule.objects.get(
                Q(category = TutorJSON["category_id"]) &
                Q(academic_level = TutorJSON["academic_level"]) &
                Q(course_type = "tutoring"))
            tuition = float(tutoring_priceRules.hourly_tuition)
            sub_total += tuition * float(TutorJSON["duration"]) * int(TutorJSON["sessions"])  

        # extract course costs and discounts
        for CourseJSON in body.get("courses", []):
            course = Course.objects.get(course_id = CourseJSON["course_id"])
            course_subTotal = float(course.tuition)*int(CourseJSON["sessions"])

            if course.type == 'C':
                course_students.add(CourseJSON["student_id"])

                # DateRangeDiscount
                dateRange_discounts = DateRangeDiscount.objects.filter(
                    (Q(start_date__lte = course.start_date) & Q(end_date__lte = course.end_date)) |
                    (Q(start_date__gte = course.start_date) & Q(start_date__lte = course.end_date)) |
                    (Q(end_date__gte = course.start_date) & Q(end_date__lte = course.end_date)))
                
                for discount in dateRange_discounts:
                    if discount.id not in disabled_discounts and discount.active:
                        if discount.amount_type == 'percent':
                            amount = float(course.tuition)*(100.0-float(discount.amount))/100.0
                        else:
                            amount = float(discount.amount)
                        totalDiscountVal += amount
                        usedDiscounts.append({"discount_title" : discount.name, "amount" : amount})
                
                # MultiCourseDiscount (sessions on course basis)            
                multiCourse_discounts = MultiCourseDiscount.objects.filter(num_sessions__lte = CourseJSON["sessions"])
                for discount in multiCourse_discounts.order_by("-num_sessions"):
                    # take highest applicable discount based on session count
                    if discount.id not in disabled_discounts and discount.active:
                        if discount.amount_type == 'percent':
                            amount = float(course.tuition)*(100.0-float(discount.amount))/100.0
                        else:
                            amount = float(discount.amount)
                        totalDiscountVal += amount
                        usedDiscounts.append({"discount_title" : discount.name, "amount" : amount})
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
                    amount = float(sub_total)*(100.0-float(discount.amount))/100.0
                else:
                    amount = float(discount.amount)
                totalDiscountVal += amount
                usedDiscounts.append({"discount_title" : discount.name, "amount" : amount})
        
        # price adjustment
        price_adjustment = body.get("price_adjustment", 0)

        # format response data
        ResponseDict = {}
        ResponseDict["sub_total"] = sub_total
        ResponseDict["discounts"] = usedDiscounts
        ResponseDict["price_adjustment"] = price_adjustment
        ResponseDict["total"] = sub_total-totalDiscountVal-price_adjustment      
        
        return JsonResponse(ResponseDict)


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
            "per_session" : float(priceRules[0].hourly_tuition) * float(body["duration"]),
            "total" :  float(priceRules[0].hourly_tuition) * float(body["duration"]) * int(body["sessions"])
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
