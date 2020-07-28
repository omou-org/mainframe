import graphene
from graphene import Field, ID, Int, List, String, Float
from graphene_django.types import DjangoObjectType
from graphene.types.json import JSONString

from django.db.models import Q

from pricing.models import PriceRule, Discount, MultiCourseDiscount, DateRangeDiscount, PaymentMethodDiscount
from course.models import Course
from account.models import Parent

from course.mutations import AcademicLevelEnum


class AmountTypeEnum(graphene.Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class DiscountInterface(graphene.Interface):
    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    amount = graphene.Float()
    amount_type = AmountTypeEnum()
    active = graphene.Boolean()

    class Meta:
        description = 'Shared discount properties'


class PriceRuleType(DjangoObjectType):
    class Meta:
        model = PriceRule


class DiscountType(DjangoObjectType):
    class Meta:
        interfaces = (DiscountInterface, )
        model = Discount


class MultiCourseDiscountType(DjangoObjectType):
    class Meta:
        interfaces = (DiscountInterface, )
        model = MultiCourseDiscount


class DateRangeDiscountType(DjangoObjectType):
    class Meta:
        interfaces = (DiscountInterface, )
        model = DateRangeDiscount


class PaymentMethodDiscountType(DjangoObjectType):
    class Meta:
        interfaces = (DiscountInterface, )
        model = PaymentMethodDiscount


class DiscountQuoteType(graphene.ObjectType):
    id = Int()
    name = String()
    amount = Float()


class PriceQuoteType(graphene.ObjectType):
    subTotal = Float()
    discountTotal = Float()
    priceAdjustment = Float()
    accountBalance = Float()
    total = Float()
    discounts = List(DiscountQuoteType)
    parent = Int()


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
            date_range_discounts = []

            for discount in date_range_discounts:
                if discount.id not in disabled_discounts and discount.active:
                    if discount.amount_type == 'percent':
                        amount = float(course.hourly_tuition)*(100.0-float(discount.amount))/100.0
                    else:
                        amount = float(discount.amount)
                    total_discount_val += amount
                    used_discounts.append({"id" : discount.id, "name" : discount.name, "amount" : amount})

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
                    used_discounts.append({"id" : discount.id, "name" : discount.name, "amount" : amount})
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
            used_discounts.append({"id" : discount.id, "name" : discount.name, "amount" : amount})

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


class ClassQuote(graphene.InputObjectType):
    course_id=ID(name='course')
    sessions=Int()
    student_id=ID(name='student')


class TutoringQuote(graphene.InputObjectType):
    category_id=ID(name='category')
    academic_level=AcademicLevelEnum()
    duration=Float()
    sessions=Int()


class Query(object):
    priceRule = Field(PriceRuleType, priceRule_id=ID())
    discount = Field(DiscountType, discount_id=ID())
    multiCourseDiscount = Field(MultiCourseDiscountType, multiCourseDiscount_id=ID())
    dateRangeDiscount = Field(DateRangeDiscountType, dateRangeDiscount_id=ID())
    paymentMethodDiscount = Field(PaymentMethodDiscountType, paymentMethodDiscount_id=ID())

    priceRules = List(PriceRuleType)
    discounts = List(DiscountType)
    multiCourseDiscounts = List(MultiCourseDiscountType)
    dateRangeDiscounts = List(DateRangeDiscountType)
    paymentMethodDiscounts = List(PaymentMethodDiscountType)

    priceQuote = Field(PriceQuoteType,
                    method=String(required=True),
                    disabled_discounts=List(ID),
                    price_adjustment=Float(),
                    classes=List(ClassQuote),
                    tutoring=List(TutoringQuote),
                    parent=ID(name='parent', required=True)
                    )


    def resolve_priceQuote(self, info, **kwargs):
        quote = price_quote_total(kwargs)

        return PriceQuoteType(
            subTotal = quote["sub_total"],
            priceAdjustment = quote["price_adjustment"],
            accountBalance = quote["account_balance"],
            total = quote["total"],
            discounts = quote["discounts"],
            parent = kwargs["parent"]
        )


    def resolve_priceRule(self, info, **kwargs):
        return PriceRule.objects.get(id=kwargs.get('priceRule_id'))


    def resolve_priceRules(self, info, **kwargs):
        return PriceRule.objects.all()


    def resolve_discount(self, info, **kwargs):
        return Discount.objects.get(id=kwargs.get('discount_id'))


    def resolve_discounts(self, info, **kwargs):
        return Discount.objects.all()


    def resolve_multiCourseDiscount(self, info, **kwargs):
        return MultiCourseDiscount.objects.get(id=kwargs.get('multiCourseDiscount_id'))


    def resolve_multiCourseDiscounts(self, info, **kwargs):
        return MultiCourseDiscount.objects.all()


    def resolve_dateRangeDiscount(self, info, **kwargs):
        return DateRangeDiscount.objects.get(id=kwargs.get('dateRangeDiscount_id'))


    def resolve_dateRangeDiscounts(self, info, **kwargs):
        return DateRangeDiscount.objects.all()


    def resolve_paymentMethodDiscount(self, info, **kwargs):
        return PaymentMethodDiscount.objects.get(id=kwargs.get('paymentMethodDiscount_id'))


    def resolve_paymentMethodDiscounts(self, info, **kwargs):
        return PaymentMethodDiscount.objects.all()
