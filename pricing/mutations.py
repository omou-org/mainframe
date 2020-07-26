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
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class AmountTypeEnum(graphene.Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class CreatePriceRule(graphene.Mutation):
    class Arguments:
        rule_id = graphene.ID(name='id')
        name = graphene.String()
        hourly_tuition = graphene.Float()
        category_id = graphene.Int(name="category")
        academic_level = AcademicLevelEnum()
        course_type = CourseTypeEnum()
    
    price_rule = graphene.Field(PriceRuleType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        existing_rules = PriceRule.objects.filter(
            Q(category=validated_data.get('category_id')) &
            Q(academic_level=validated_data.get('academic_level')) &
            Q(course_type=validated_data.get('course_type')))
        if 'rule_id' not in validated_data and existing_rules.count() > 0:
            raise GraphQLError('Failed mutation. PriceRule already exists.')

        if 'rule_id' in validated_data:
            rule_id = validated_data.get('rule_id')
            if not PriceRule.objects.filter(id=rule_id).exists():
                raise GraphQLError('Failed update mutation. PriceRule does not exist.')
        price_rule, created = PriceRule.objects.update_or_create(
            id=validated_data.get('rule_id', None),
            defaults=validated_data
        )

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(PriceRule).pk,
            object_id=price_rule.id,
            object_repr=str(price_rule.id),
            action_flag=CHANGE if 'rule_id' in validated_data else ADDITION
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
        
        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(PriceRule).pk,
            object_id=price_rule_obj.id,
            object_repr=str(price_rule_obj.id),
            action_flag=DELETION
        )
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

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=discount.id,
            object_repr=discount.name,
            action_flag=ADDITION
        )
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

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=multi_course_discount.id,
            object_repr=multi_course_discount.name,
            action_flag=ADDITION
        )
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

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=date_range_discount.id,
            object_repr=date_range_discount.name,
            action_flag=ADDITION
        )
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

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=payment_method_discount.id,
            object_repr=payment_method_discount.name,
            action_flag=ADDITION
        )
        return CreatePaymentMethodDiscount(payment_method_discount=payment_method_discount)


class Mutation(graphene.ObjectType):
    create_pricerule = CreatePriceRule.Field()
    delete_pricerule = DeletePriceRule.Field()
    create_discount = CreateDiscount.Field()
    create_multicoursediscount = CreateMultiCourseDiscount.Field()
    create_daterangediscount = CreateDateRangeDiscount.Field()
    create_paymentmethoddiscount = CreatePaymentMethodDiscount.Field()
