from rest_framework import serializers

from promo.models import Promo


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo

        fields = (
            'id',
            'discount_type',
            'discount',
            'start_date_time',
            'end_date_time',
            'sessions'
        )
