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
    AmountTypeEnum,
    PriceRuleType,
    DiscountType,
    MultiCourseDiscountType,
    DateRangeDiscountType,
    PaymentMethodDiscountType
)
from course.mutations import AcademicLevelEnum, CourseTypeEnum

from graphql_jwt.decorators import login_required, staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


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
        discount_id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        amount = graphene.Float()
        amount_type = AmountTypeEnum()
        active = graphene.Boolean()

    discount = graphene.Field(DiscountType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        discount, created = Discount.objects.update_or_create(
            id=validated_data.pop('discount_id', None),
            defaults=validated_data
        )
        return CreateDiscount(discount=discount, created=created)


class CreateMultiCourseDiscount(graphene.Mutation):
    class Arguments:
        discount_id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        amount = graphene.Float()
        amount_type = AmountTypeEnum()
        active = graphene.Boolean()
        num_sessions = graphene.Int()

    multi_course_discount = graphene.Field(MultiCourseDiscountType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        multi_course_discount, created = MultiCourseDiscount.objects.update_or_create(
            id=validated_data.pop('discount_id', None),
            defaults=validated_data
        )
        return CreateMultiCourseDiscount(multi_course_discount=multi_course_discount, created=created)


class CreateDateRangeDiscount(graphene.Mutation):
    class Arguments:
        discount_id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        amount = graphene.Float()
        amount_type = AmountTypeEnum()
        active = graphene.Boolean()
        start_date = graphene.types.datetime.Date()
        end_date = graphene.types.datetime.Date()

    date_range_discount = graphene.Field(DateRangeDiscountType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        date_range_discount, created = DateRangeDiscount.objects.update_or_create(
            id=validated_data.pop('discount_id', None),
            defaults=validated_data
        )
        return CreateDateRangeDiscount(date_range_discount=date_range_discount, created=created)


class CreatePaymentMethodDiscount(graphene.Mutation):
    class Arguments:
        discount_id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        amount = graphene.Float()
        amount_type = AmountTypeEnum()
        active = graphene.Boolean()
        payment_method = graphene.String()

    payment_method_discount = graphene.Field(PaymentMethodDiscountType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        payment_method_discount, created = PaymentMethodDiscount.objects.update_or_create(
            id=validated_data.pop('discount_id', None),
            defaults=validated_data
        )
        return CreatePaymentMethodDiscount(payment_method_discount=payment_method_discount, created=created)


class Mutation(graphene.ObjectType):
    create_price_rule = CreatePriceRule.Field()
    delete_price_rule = DeletePriceRule.Field()
    create_discount = CreateDiscount.Field()
    create_multi_course_discount = CreateMultiCourseDiscount.Field()
    create_date_range_discount = CreateDateRangeDiscount.Field()
    create_payment_method_discount = CreatePaymentMethodDiscount.Field()
