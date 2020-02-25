from django.db import transaction
from rest_framework import serializers


from course.models import Course, Enrollment
# from course.serializers import CourseSerializer
from payment.models import Payment, Registration
# from pricing.serializers import DiscountSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        ref_name = 'enrollment_for_registration'

        fields = (
            'student',
            'course',
        )


class RegistrationSerializer(serializers.ModelSerializer):
    enrollment_details = EnrollmentSerializer(read_only=True, source='enrollment')

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
            'attendance_start_date',
            'payment',
            'enrollment',
            'num_sessions',
            'enrollment_details',
            'updated_at',
            'created_at',
        )


class PaymentSerializer(serializers.ModelSerializer):
    # applied_discounts = DiscountSerializer(many=True)
    registrations = RegistrationSerializer(many=True, source='registration_set')

    @transaction.atomic
    def create(self, validated_data):
        registrations = validated_data.pop("registration_set")
        payment = Payment.objects.create(
            **validated_data,
        )
        for registration in registrations:
            Registration.objects.create(
                payment=payment,
                enrollment=registration["enrollment"],
                num_sessions=registration["num_sessions"]
            )
            # enrollment = Enrollment.objects.get(id=registration["enrollment"])
            # if enrollment.course.course_type in (Course.TUTORING, Course.SMALL_GROUP):
            #     if enrollment.sessions_left < registration["num_sessions"]:
            #         serializer = CourseSerializer()
            #         data = {
            #             "end_date": registration["new_end_date"]
            #         }
            #         serializer.update(enrollment.course, data)

        return payment

    class Meta:
        model = Payment

        fields = (
            'id',
            'parent',
            'sub_total',
            # 'applied_discounts',
            'price_adjustment',
            'total',
            'account_balance',
            'discount_total',
            'method',
            'registrations',
            'updated_at',
            'created_at'
        )

        read_only_fields = (
            'id',
            'updated_at',
            'created_at'
        )
