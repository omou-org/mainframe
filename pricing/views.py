from django.shortcuts import render
from pricing.models import (
    PriceRule,
    Discount,
    MultiCourseDiscount,
    DateRangeDiscount,
    PaymentMethodDiscount,
)
from account.models import (
    Parent
)

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from mainframe.permissions import IsDev, ReadOnly

from pricing.serializers import (
    PriceRuleSerializer,
    DiscountSerializer,
    MultiCourseDiscountSerializer,
    DateRangeDiscountSerializer,
    PaymentMethodDiscountSerializer,
)

import json
from django.db.models import Q
from course.models import Course
from django.http import JsonResponse
from rest_framework.views import APIView

# shared pricing function
def price_quote_total(body):
    course_students = set()
    sub_total = 0.0      

    disabled_discounts = body.get("disabled_discounts", [])
    used_discounts = []
    total_discount_val = 0.0

    # extract tutoring costs (assuming category/level combo exists)
    for tutor_json in body.get("tutoring", []):
        tutoring_price_rules = PriceRule.objects.filter(
            Q(category = tutor_json["category_id"]) &
            Q(academic_level = tutor_json["academic_level"]) &
            Q(course_type = "tutoring"))[0]
        tuition = float(tutoring_price_rules.hourly_tuition)
        sub_total += tuition * float(tutor_json["duration"])*float(tutor_json["sessions"])  

    # extract course costs and discounts
    for course_json in body.get("classes", []):
        course = Course.objects.filter(id = course_json["course_id"])[0]
        course_sub_total = float(course.hourly_tuition)*float(course_json["sessions"])

        if course.course_type == 'class':
            course_students.add(course_json["student_id"])

            # DateRangeDiscount
            date_range_discounts = DateRangeDiscount.objects.filter(
                (Q(start_date__lte = course.start_date) & Q(end_date__lte = course.end_date)) |
                (Q(start_date__gte = course.start_date) & Q(start_date__lte = course.end_date)) |
                (Q(end_date__gte = course.start_date) & Q(end_date__lte = course.end_date)))
            
            for discount in date_range_discounts:
                if discount.id not in disabled_discounts and discount.active:
                    if discount.amount_type == 'percent':
                        amount = float(course.hourly_tuition)*(100.0-float(discount.amount))/100.0
                    else:
                        amount = float(discount.amount)
                    total_discount_val += amount
                    used_discounts.append({"discount_id" : discount.id, "discount_title" : discount.name, "amount" : amount})
            
            # MultiCourseDiscount (sessions on course basis)            
            multicourse_discounts = MultiCourseDiscount.objects.filter(num_sessions__lte = float(course_json["sessions"]))
            for discount in multicourse_discounts.order_by("-num_sessions"):
                # take highest applicable discount based on session count
                if discount.id not in disabled_discounts and discount.active:
                    if discount.amount_type == 'percent':
                        amount = float(course.hourly_tuition)*(100.0-float(discount.amount))/100.0
                    else:
                        amount = float(discount.amount)
                    total_discount_val += amount
                    used_discounts.append({"discount_id" : discount.id, "name" : discount.name, "amount" : amount, "id": discount.id})
                    break
    
        sub_total += course_sub_total

    # sibling discount
    if len(course_students) > 1:
        total_discount_val += 25
        used_discounts.append(("Siblings Discount", 25))      
    
    # PaymentMethodDiscount
    payment_method = body["method"]
    payment_method_discounts = PaymentMethodDiscount.objects.filter(payment_method=payment_method)
    for discount in payment_method_discounts:
        if discount.id not in disabled_discounts and discount.active:
            if discount.amount_type == 'percent':
                amount = float(sub_total)*(100.0-float(discount.amount))/100.0
            else:
                amount = float(discount.amount)
            total_discount_val += amount
            used_discounts.append({"name" : discount.name, "amount" : amount, "id": discount.id})
    
    # price adjustment
    price_adjustment = body.get("price_adjustment", 0)
    
    # format response data
    response_dict = {}
    response_dict["sub_total"] = sub_total
    response_dict["discount_total"] = total_discount_val
    response_dict["price_adjustment"] = price_adjustment
    response_dict["total"] = sub_total-total_discount_val-price_adjustment

    # parent balance adjustment
    response_dict["account_balance"] = 0.0
    if body.get("parent"):
        parent = Parent.objects.get(user_id=body["parent"])

        if parent.balance < response_dict["total"]:
            balance = float(parent.balance)
        else:
            balance = response_dict["total"]
        response_dict["account_balance"] = balance
        response_dict["total"] -= balance
    
    # round all prices
    for key in response_dict:
        response_dict[key] = round(response_dict[key], 2)

    response_dict["discounts"] = used_discounts
    return response_dict


# Create your views here.

class QuoteTotalView(APIView): 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]

    def post(self, request):
        # load request body
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        return JsonResponse(price_quote_total(body))


class PriceRuleViewSet(viewsets.ModelViewSet):
    """"
    API endpoint that allows prices to be viewed, edited, or created
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsDev | (IsAuthenticated & (IsAdminUser | ReadOnly))]
    queryset = PriceRule.objects.all()
    serializer_class = PriceRuleSerializer


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


