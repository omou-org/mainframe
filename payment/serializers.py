from django.db import transaction
from rest_framework import serializers


from course.models import Enrollment
from payment.models import Payment, Registration
# from pricing.serializers import DiscountSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration

        read_only_fields = (
            'id',
            'payment',
            'updated_at',
            'created_at',
        )

        fields = (
            'id',
            'payment',
            'enrollment',
            'num_sessions',
            'updated_at',
            'created_at',
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment

        fields = (
            'id',
            'student',
            'course',
        )


class PaymentSerializer(serializers.ModelSerializer):
    # applied_discounts = DiscountSerializer(many=True)
    registrations = RegistrationSerializer(many=True, write_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        registrations = validated_data.pop("registrations")
        total_amount = (validated_data.get("base_amount") +
                        validated_data.get("price_adjustment"))
        payment = Payment.objects.create(
            **validated_data,
            total_amount=total_amount
        )
        for registration in registrations:
            Registration.objects.create(
                payment=payment,
                enrollment=registration["enrollment"],
                num_sessions=registration["num_sessions"]
            )
        return payment

    class Meta:
        model = Payment

        fields = (
            'id',
            'parent',
            'base_amount',
            # 'applied_discounts',
            'price_adjustment',
            'total_amount',
            'method',
            'enrollments',
            'registrations',
            'updated_at',
            'created_at'
        )

        read_only_fields = (
            'id',
            'total_amount',
            'enrollments',
            'updated_at',
            'created_at'
        )
