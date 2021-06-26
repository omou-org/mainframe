import graphene
from graphql import GraphQLError

from account.models import Admin
from pricing.models import (
    TuitionPrice,
    TuitionRule,
    Discount,
    MultiCourseDiscount,
    DateRangeDiscount,
    PaymentMethodDiscount,
)
from pricing.schema import (
    AmountTypeEnum,
    TuitionRuleType,
    DiscountType,
    MultiCourseDiscountType,
    DateRangeDiscountType,
    PaymentMethodDiscountType,
)
from course.mutations import CourseTypeEnum

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from graphql_jwt.decorators import login_required, staff_member_required


class CreateTuitionRule(graphene.Mutation):
    class Arguments:
        rule_id = graphene.ID(name="id")
        name = graphene.String()
        hourly_tuition = graphene.Float()
        category_id = graphene.Int(name="category")
        course_type = CourseTypeEnum()
        all_instructors_apply = graphene.Boolean()
        instructors = graphene.List(graphene.ID)
        retired = graphene.Boolean()

    tuition_rule = graphene.Field(TuitionRuleType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        business_id = Admin.objects.get(user__id = info.context.user.id).business.id

        # check if rule with category, course type, and same instructors exists
        existing_rules = TuitionRule.objects.business(business_id).filter(
            category=validated_data.get("category_id"),
            course_type=validated_data.get("course_type"),
            instructors__in=validated_data.get("instructors", [])
        )
        if "rule_id" not in validated_data and existing_rules.count() > 0:
            raise GraphQLError("Failed mutation. TuitionRule already exists.")

        # check if rule with id exists
        if "rule_id" in validated_data and not TuitionRule.objects.business(business_id).filter(id=validated_data.get("rule_id")).exists():
            raise GraphQLError("Failed update mutation. TuitionRule does not exist.")

        # must provide instructors if rule does not apply to all
        if not validated_data.get("all_instructors_apply") and not validated_data.get("instructors"):
            raise GraphQLError("Failed mutation. There must be some instructors provided if not all apply.")
        
        instructors = validated_data.pop("instructors", [])
        hourly_tuition = validated_data.pop("hourly_tuition", None)

        tuition_rule, created = TuitionRule.objects.update_or_create(
            id=validated_data.get("rule_id", None), business_id=business_id, defaults=validated_data
        )

        if validated_data.get("all_instructors_apply"):
            instructors = []
        tuition_rule.instructors.set(instructors)

        if hourly_tuition:
            TuitionPrice.objects.create(hourly_tuition=hourly_tuition, tuition_rule=tuition_rule)

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(TuitionRule).pk,
            object_id=tuition_rule.id,
            object_repr=str(tuition_rule.id),
            action_flag=CHANGE if "rule_id" in validated_data else ADDITION,
        )
        return CreateTuitionRule(tuition_rule=tuition_rule, created=created)


class DeleteTuitionRule(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    deleted = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        business_id = Admin.objects.get(user__id = info.context.user.id).business.id

        try:
            tuition_rule_obj = TuitionRule.objects.business(business_id).get(id=validated_data.get("id"))
        except ObjectDoesNotExist:
            raise GraphQLError("Failed delete mutation. TuitionRule does not exist.")

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(TuitionRule).pk,
            object_id=tuition_rule_obj.id,
            object_repr=str(tuition_rule_obj.id),
            action_flag=DELETION,
        )
        tuition_rule_obj.delete()
        return DeleteTuitionRule(deleted=True)


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
            id=validated_data.pop("discount_id", None), defaults=validated_data
        )

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=discount.id,
            object_repr=discount.name,
            action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
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
            id=validated_data.pop("discount_id", None), defaults=validated_data
        )

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=multi_course_discount.id,
            object_repr=multi_course_discount.name,
            action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
        )
        return CreateMultiCourseDiscount(
            multi_course_discount=multi_course_discount, created=created
        )


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
            id=validated_data.pop("discount_id", None), defaults=validated_data
        )

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=date_range_discount.id,
            object_repr=date_range_discount.name,
            action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
        )
        return CreateDateRangeDiscount(
            date_range_discount=date_range_discount, created=created
        )


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
        (
            payment_method_discount,
            created,
        ) = PaymentMethodDiscount.objects.update_or_create(
            id=validated_data.pop("discount_id", None), defaults=validated_data
        )

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=payment_method_discount.id,
            object_repr=payment_method_discount.name,
            action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
        )
        return CreatePaymentMethodDiscount(
            payment_method_discount=payment_method_discount, created=created
        )


class Mutation(graphene.ObjectType):
    create_tuition_rule = CreateTuitionRule.Field()
    delete_tuition_rule = DeleteTuitionRule.Field()
    create_discount = CreateDiscount.Field()
    create_multi_course_discount = CreateMultiCourseDiscount.Field()
    create_date_range_discount = CreateDateRangeDiscount.Field()
    create_payment_method_discount = CreatePaymentMethodDiscount.Field()
