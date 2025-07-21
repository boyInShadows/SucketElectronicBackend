from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def latest_products(request):
    latest = Product.objects.order_by('-created_at')[:8]  # Adjust the number as needed
    serializer = ProductSerializer(latest, many=True)
    return Response(serializer.data) 