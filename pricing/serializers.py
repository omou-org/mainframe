from rest_framework import serializers

from pricing.models import (
    PriceRule,
    Discount,
    DateRangeDiscount,
    MultiCourseDiscount,
    PaymentMethodDiscount,
)


class PriceRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRule
        read_only_fields = (
            'id',
            'updated_at',
            'created_at',
        )
        fields = (
            'id',
            'name',
            'hourly_tuition',
            'category',
            'academic_level',
            'course_type',
            'updated_at',
            'created_at',
        )


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        read_only_fields = (
            'id',
            'updated_at',
            'created_at',
        )
        fields = (
            'id',
            'name',
            'description',
            'amount',
            'amount_type',
            'active',
            'updated_at',
            'created_at',
        )


class MultiCourseDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiCourseDiscount
        read_only_fields = (
            'id',
            'updated_at',
            'created_at',
        )
        fields = (
            'id',
            'name',
            'description',
            'num_sessions',
            'amount',
            'amount_type',
            'active',
            'updated_at',
            'created_at',
        )


class DateRangeDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DateRangeDiscount
        read_only_fields = (
            'id',
            'updated_at',
            'created_at',
        )
        fields = (
            'id',
            'name',
            'description',
            'start_date',
            'end_date',
            'amount',
            'amount_type',
            'updated_at',
            'created_at',
        )


class PaymentMethodDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodDiscount
        read_only_fields = (
            'id',
            'updated_at',
            'created_at',
        )
        fields = (
            'id',
            'name',
            'description',
            'payment_method',
            'amount',
            'amount_type',
            'active',
            'updated_at',
            'created_at',
        )

