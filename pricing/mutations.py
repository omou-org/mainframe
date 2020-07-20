import graphene
from graphql import GraphQLError

from pricing.models import (
    PriceRule,
    Discount,
    MultiCourseDiscount,
    DateRangeDiscount,
    PaymentMethodDiscount
)
from pricing.schema import (
    PriceRuleType,
    DiscountType,
    MultiCourseDiscountType,
    DateRangeDiscountType,
    PaymentMethodDiscountType
)
from course.mutations import AcademicLevelEnum, CourseTypeEnum

from graphql_jwt.decorators import login_required, staff_member_required
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class AmountTypeEnum(graphene.Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class CreatePriceRule(graphene.Mutation):
    class Arguments:
        rule_id = graphene.ID(name='id')
        name = graphene.String(required=True)
        hourly_tuition = graphene.Float(required=True)
        category_id = graphene.Int(name="category", required=True)
        academic_level = AcademicLevelEnum(required=True)
        course_type = CourseTypeEnum(required=True)
    
    price_rule = graphene.Field(PriceRuleType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        existing_rules = PriceRule.objects.filter(
            Q(category=validated_data['category_id']) &
            Q(academic_level=validated_data['academic_level']) &
            Q(course_type=validated_data['course_type']))
        if 'rule_id' not in validated_data and existing_rules.count() > 0:
            raise GraphQLError('Failed mutation. PriceRule already exists.')

        if 'rule_id' in validated_data:
            rule_id = validated_data.get('rule_id')
            if not PriceRule.objects.filter(id=rule_id).exists():
                raise GraphQLError('Failed update mutation. PriceRule does not exist.')
        price_rule, created = PriceRule.objects.update_or_create(
            id=validated_data.pop('rule_id', None),
            defaults=validated_data
        )

        return CreatePriceRule(price_rule=price_rule, created=created)


class DeletePriceRule(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    deleted = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        try:
            price_rule_obj = PriceRule.objects.get(id=validated_data.get('id'))
        except ObjectDoesNotExist:
            raise GraphQLError('Failed delete mutation. PriceRule does not exist.')
        price_rule_obj.delete()
        return DeletePriceRule(deleted=True)


class CreateDiscount(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        amount = graphene.Float(required=True)
        amount_type = AmountTypeEnum(required=True)
        active = graphene.Boolean(required=True)

    discount = graphene.Field(DiscountType)
    
    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        discount = Discount.objects.create(**validated_data)
        return CreateDiscount(discount=discount)


class CreateMultiCourseDiscount(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        amount = graphene.Float(required=True)
        amount_type = AmountTypeEnum(required=True)
        active = graphene.Boolean(required=True)
        num_sessions = graphene.Int(required=True)

    multi_course_discount = graphene.Field(MultiCourseDiscountType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        multi_course_discount = MultiCourseDiscount.objects.create(**validated_data)
        return CreateMultiCourseDiscount(multi_course_discount=multi_course_discount)


class CreateDateRangeDiscount(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        amount = graphene.Float(required=True)
        amount_type = AmountTypeEnum(required=True)
        active = graphene.Boolean(required=True)
        start_date = graphene.types.datetime.Date(required=True)
        end_date = graphene.types.datetime.Date(required=True)

    date_range_discount = graphene.Field(DateRangeDiscountType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        date_range_discount = DateRangeDiscount.objects.create(**validated_data)
        return CreateDateRangeDiscount(date_range_discount=date_range_discount)


class CreatePaymentMethodDiscount(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        amount = graphene.Float(required=True)
        amount_type = AmountTypeEnum(required=True)
        active = graphene.Boolean(required=True)
        payment_method =graphene.String(required=True)
    
    payment_method_discount = graphene.Field(PaymentMethodDiscountType)

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        payment_method_discount = PaymentMethodDiscount.objects.create(**validated_data)
        return CreatePaymentMethodDiscount(payment_method_discount=payment_method_discount)


class Mutation(graphene.ObjectType):
    create_pricerule = CreatePriceRule.Field()
    delete_pricerule = DeletePriceRule.Field()
    create_discount = CreateDiscount.Field()
    create_multicoursediscount = CreateMultiCourseDiscount.Field()
    create_daterangediscount = CreateDateRangeDiscount.Field()
    create_paymentmethoddiscount = CreatePaymentMethodDiscount.Field()
