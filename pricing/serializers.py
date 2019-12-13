from rest_framework import serializers

from pricing.models import PriceRule


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
