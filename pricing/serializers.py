from rest_framework import serializers
from django.db import transaction
from rest_framework.authtoken.models import Token
from datetime import datetime

from pricing.models import Price, PriceRule, StaticPrice

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        read_only_fields = (
            'id',
            'timestamp',
        )
        fields = (
            'name',
            'hourly_tuition',
        )

class PriceRuleSerializer(serializers.ModelSerializer):
    price = PriceSerializer()

    class Meta:
        model = PriceRule
        read_only_fields = (
            'id',
            'timestamp'
        )
        fields = (
            'price',
            'category',
            'academic_level',
            'min_capacity',
            'max_capacity',
        )

class StaticPriceSerializer(serializers.ModelSerializer):
    price = PriceSerializer()
    course_id_list = serializers.SerializerMethodField()

    def get_course_id_list(self, obj):
        return obj.course_id_list

    def create(self, validated_data):
        with transaction.atomic():
            print(validated_data)
            price_info = validated_data['price']
            del validated_data['price']
            price = Price.objects.create(
                name=price_info['name'],
                hourly_tuition=price_info['hourly_tuition']
            )
            static_price = StaticPrice.objects.create(
                price=price,
                hourly_tuition=price_info['hourly_tuition'],
            )
            print(static_price)
            return static_price


    class Meta:
        model = StaticPrice
        read_only_fields = (
            'id',
            'timestamp',
        )
        fields = (
            'price',
            'course_list',
        )