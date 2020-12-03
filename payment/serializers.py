from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework import serializers

from account.models import Parent
from comms.models import Email
from comms.templates import PAYMENT_CONFIRM_TEMPLATE
from course.models import Enrollment
from payment.models import Invoice, Registration, Deduction
from pricing.serializers import DiscountSerializer


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
            'invoice',
            'updated_at',
            'created_at',
        )

        fields = (
            'id',
            'attendance_start_date',
            'invoice',
            'enrollment',
            'num_sessions',
            'enrollment_details',
            'updated_at',
            'created_at',
        )


class DeductionSerializer(serializers.ModelSerializer):
    discount_details = DiscountSerializer(read_only=True, source='Discount')

    class Meta:
        model = Deduction

        read_only_fields = (
            'id',
            'invoice',
            'updated_at',
            'created_at',
        )

        fields = (
            'id',
            'invoice',
            'discount',
            'amount',
            'discount_details',
            'updated_at',
            'created_at',
        )


class InvoiceSerializer(serializers.ModelSerializer):
    registrations = RegistrationSerializer(many=True, source='registration_set')
    deductions = DeductionSerializer(many=True, source='deduction_set')

    @transaction.atomic
    def create(self, validated_data):
        registrations = validated_data.pop("registration_set")
        deductions = validated_data.pop("deduction_set")
        invoice = Invoice.objects.create(
            **validated_data,
        )

        # deduct account_balance from parent balance
        if validated_data["account_balance"] > 0.0:
            parent = Parent.objects.get(user_id = validated_data["parent"])
            parent.balance -= validated_data["account_balance"]
            parent.save()

        # create deductions
        for deduction in deductions:
            Deduction.objects.create(
                invoice=invoice,
                discount=deduction["discount"],
                amount=deduction["amount"]
            )
        
        # create registrations
        registration_objs = []
        for registration in registrations:
            registration_obj = Registration.objects.create(
                invoice=invoice,
                enrollment=registration["enrollment"],
                num_sessions=registration["num_sessions"]
            )
            registration_objs.append(registration_obj)

            LogEntry.objects.log_action(
                user_id=self.context['user_id'],
                content_type_id=ContentType.objects.get_for_model(Registration).pk,
                object_id=registration_obj.id,
                object_repr=f"{registration_obj.enrollment.student.user.first_name} {registration_obj.enrollment.student.user.last_name}, {registration_obj.enrollment.course.title}",
                action_flag=ADDITION
            )

        payment_data = {
            "parent_name": invoice.parent.user.first_name,
            "business_name": settings.BUSINESS_NAME,
            "receipt_text": f"You've paid {invoice.total} for {len(registrations)} classes",
            "total_tuition": float(invoice.total),
            "payment_id": invoice.id,
            "enrollments": {
                "course": [{
                    "title": registration.enrollment.course.title,
                    "start_date": registration.attendance_start_date.strftime("%Y-%m-%d"),
                    "end_date": registration.enrollment.course.end_date.strftime("%Y-%m-%d"),
                    "availabilities": [{
                        "day_of_week": availability.day_of_week,
                        "start_time": availability.start_time.strftime("%H:%M"),
                        "end_time": availability.end_time.strftime("%H:%M"),
                    } for availability in registration.enrollment.course.active_availability_list],
                    "instructor": {
                        "first_name": registration.enrollment.course.instructor.user.first_name,
                        "last_name": registration.enrollment.course.instructor.user.last_name
                    }
                } for registration in registration_objs]
            }
        }

        Email.objects.create(
            template_id=PAYMENT_CONFIRM_TEMPLATE,
            recipient=invoice.parent.user.email,
            data=payment_data
        )

        return invoice

    class Meta:
        model = Invoice

        fields = (
            'id',
            'parent',
            'sub_total',
            'price_adjustment',
            'total',
            'account_balance',
            'discount_total',
            'method',
            'registrations',
            'deductions',
            'payment_status',
            'updated_at',
            'created_at'
        )

        read_only_fields = (
            'id',
            'updated_at',
            'created_at'
        )
