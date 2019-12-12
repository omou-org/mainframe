from rest_framework import serializers
from datetime import datetime

from pricing.models import Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        read_only_fields = (
            'id',
            'timestamp'
        )
        fields = (
            'course_id_list',
            'category',
            'academic_level',
            'min_capacity',
            'max_capacity',
        )