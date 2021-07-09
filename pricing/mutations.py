import graphene
from graphql import GraphQLError

from account.models import Admin
from pricing.models import (
    TuitionPrice,
    TuitionRule,
    Discount,
    # MultiCourseDiscount,
    # DateRangeDiscount,
    # PaymentMethodDiscount,
)
from pricing.schema import (
    AmountTypeEnum,
    TuitionRuleType,
    DiscountType,
    # MultiCourseDiscountType,
    # DateRangeDiscountType,
    # PaymentMethodDiscountType,
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

        instructors = validated_data.pop("instructors", [])
        hourly_tuition = validated_data.pop("hourly_tuition", None)
        all_instructors_apply = validated_data.pop("all_instructors_apply", None)

        # editing
        if "rule_id" in validated_data:
            rule_id = validated_data.pop("rule_id")
            tuition_rule_set = TuitionRule.objects.business(business_id).filter(id=rule_id)  
            if not tuition_rule_set.exists():
                raise GraphQLError("Failed update mutation. TuitionRule with id does not exist.")

            tuition_rule = tuition_rule_set.first()
            general_tuition_rule = TuitionRule.objects.business(business_id).filter(
                category=tuition_rule.category,
                course_type=tuition_rule.course_type
            )

            if general_tuition_rule.count() > 1:
                raise GraphQLError("Failed mutation. Some instructors already paired with TuitionRules of the same category and type.")
            
            general_tuition_rule.update(**validated_data)
            tuition_rule.refresh_from_db()            
        # creating
        else:
            existing_rules = TuitionRule.objects.business(business_id).filter(
                category=validated_data.get("category_id"),
                course_type=validated_data.get("course_type"),
                instructors__in=instructors
            )
            if existing_rules.count() > 0:
                raise GraphQLError("Failed mutation. TuitionRule already exists.")

            tuition_rule = TuitionRule(
                business_id=business_id, **validated_data
            )
            tuition_rule.save()

        if all_instructors_apply:
            instructors=[]

        # add instructors
        tuition_rule.instructors.set(instructors)
        tuition_rule.save()

        # add tuition price
        TuitionPrice.objects.create(
            hourly_tuition=hourly_tuition,
            tuition_rule=tuition_rule,
            all_instructors_apply=all_instructors_apply
        )

        return CreateTuitionRule(tuition_rule=tuition_rule, created=True)


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
        code = graphene.String()
        amount = graphene.Float()
        amount_type = AmountTypeEnum()
        active = graphene.Boolean()
        auto_apply = graphene.Boolean()
        min_courses = graphene.Int()
        start_date = graphene.types.datetime.Date()
        end_date = graphene.types.datetime.Date()
        payment_method = graphene.String()
        courses = graphene.List(graphene.ID)
        all_courses_apply = graphene.Boolean()

    discount = graphene.Field(DiscountType)
    created = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, **validated_data):
        if Discount.objects.filter(code=validated_data["code"]).exists():
            raise GraphQLError("Failed create mutation. Discount with code already exists.")

        courses = validated_data.pop("courses", None)
        discount = Discount.objects.create(
            **validated_data
        )
        # add courses
        if discount.all_courses_apply:
            courses = []
        discount.courses.set(courses)

        LogEntry.objects.log_action(
            user_id=info.context.user.id,
            content_type_id=ContentType.objects.get_for_model(Discount).pk,
            object_id=discount.id,
            object_repr=discount.code,
            action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
        )
        return CreateDiscount(discount=discount, created=created)


class RetireDiscount(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        
    retired = graphene.Boolean()

    @staticmethod
    @staff_member_required
    def mutate(root, info, id, **validated_data):
        discount = Discount.objects.get(id=id)
        discount.active = False
        discount.save()
        return RetireDiscount(retired=True)

# class CreateMultiCourseDiscount(graphene.Mutation):
#     class Arguments:
#         discount_id = graphene.ID()
#         name = graphene.String()
#         description = graphene.String()
#         amount = graphene.Float()
#         amount_type = AmountTypeEnum()
#         active = graphene.Boolean()
#         num_sessions = graphene.Int()

#     multi_course_discount = graphene.Field(MultiCourseDiscountType)
#     created = graphene.Boolean()

#     @staticmethod
#     @staff_member_required
#     def mutate(root, info, **validated_data):
#         multi_course_discount, created = MultiCourseDiscount.objects.update_or_create(
#             id=validated_data.pop("discount_id", None), defaults=validated_data
#         )

#         LogEntry.objects.log_action(
#             user_id=info.context.user.id,
#             content_type_id=ContentType.objects.get_for_model(Discount).pk,
#             object_id=multi_course_discount.id,
#             object_repr=multi_course_discount.name,
#             action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
#         )
#         return CreateMultiCourseDiscount(
#             multi_course_discount=multi_course_discount, created=created
#         )


# class CreateDateRangeDiscount(graphene.Mutation):
#     class Arguments:
#         discount_id = graphene.ID()
#         name = graphene.String()
#         description = graphene.String()
#         amount = graphene.Float()
#         amount_type = AmountTypeEnum()
#         active = graphene.Boolean()
#         start_date = graphene.types.datetime.Date()
#         end_date = graphene.types.datetime.Date()

#     date_range_discount = graphene.Field(DateRangeDiscountType)
#     created = graphene.Boolean()

#     @staticmethod
#     @staff_member_required
#     def mutate(root, info, **validated_data):
#         date_range_discount, created = DateRangeDiscount.objects.update_or_create(
#             id=validated_data.pop("discount_id", None), defaults=validated_data
#         )

#         LogEntry.objects.log_action(
#             user_id=info.context.user.id,
#             content_type_id=ContentType.objects.get_for_model(Discount).pk,
#             object_id=date_range_discount.id,
#             object_repr=date_range_discount.name,
#             action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
#         )
#         return CreateDateRangeDiscount(
#             date_range_discount=date_range_discount, created=created
#         )


# class CreatePaymentMethodDiscount(graphene.Mutation):
#     class Arguments:
#         discount_id = graphene.ID()
#         name = graphene.String()
#         description = graphene.String()
#         amount = graphene.Float()
#         amount_type = AmountTypeEnum()
#         active = graphene.Boolean()
#         payment_method = graphene.String()

#     payment_method_discount = graphene.Field(PaymentMethodDiscountType)
#     created = graphene.Boolean()

#     @staticmethod
#     @staff_member_required
#     def mutate(root, info, **validated_data):
#         (
#             payment_method_discount,
#             created,
#         ) = PaymentMethodDiscount.objects.update_or_create(
#             id=validated_data.pop("discount_id", None), defaults=validated_data
#         )

#         LogEntry.objects.log_action(
#             user_id=info.context.user.id,
#             content_type_id=ContentType.objects.get_for_model(Discount).pk,
#             object_id=payment_method_discount.id,
#             object_repr=payment_method_discount.name,
#             action_flag=CHANGE if "discount_id" in validated_data else ADDITION,
#         )
#         return CreatePaymentMethodDiscount(
#             payment_method_discount=payment_method_discount, created=created
#         )


class Mutation(graphene.ObjectType):
    create_tuition_rule = CreateTuitionRule.Field()
    delete_tuition_rule = DeleteTuitionRule.Field()
    create_discount = CreateDiscount.Field()
    retire_discount = RetireDiscount.Field()
    # create_multi_course_discount = CreateMultiCourseDiscount.Field()
    # create_date_range_discount = CreateDateRangeDiscount.Field()
    # create_payment_method_discount = CreatePaymentMethodDiscount.Field()
