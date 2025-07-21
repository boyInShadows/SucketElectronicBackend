from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    formatted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_formatted_price(self, obj):
        # Format with comma as thousands separator, remove decimal if .00
        price = int(obj.price) if obj.price == int(obj.price) else obj.price
        return "{:,}".format(price) 