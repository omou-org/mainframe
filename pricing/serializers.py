from rest_framework import serializers

from pricing.models import  PriceRule, StaticPrice


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
            'min_capacity',
            'max_capacity',
            'updated_at',
            'created_at',
        )
