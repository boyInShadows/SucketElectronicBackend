from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import Product, Cart, CartItem, Order, OrderItem, VerificationCode, Category, Article, Message
from .serializers import (
    ProductSerializer, CartSerializer, CartItemSerializer,
    OrderSerializer, OrderItemSerializer, UserSerializer,
    VerificationCodeSerializer, RegisterSerializer, CategorySerializer, ArticleSerializer, MessageSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client
from django.conf import settings
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os

logger = logging.getLogger(__name__)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_admin

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category_id', None)
        search = self.request.query_params.get('search', None)
        
        print(f"Filtering products with category_id: {category_id}")
        
        if category_id is not None:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
                print(f"Found {queryset.count()} products for category {category_id}")
            except (ValueError, TypeError) as e:
                print(f"Error converting category_id: {e}")
                return Product.objects.none()
        
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            # Handle file upload
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Generate a unique filename
                filename = f"products/{os.urandom(8).hex()}_{image_file.name}"
                # Save the file
                path = default_storage.save(filename, ContentFile(image_file.read()))
                # Get the full URL
                image_url = request.build_absolute_uri(settings.MEDIA_URL + path)
                request.data['image'] = image_url

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Error creating product: {e}")
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            instance = self.get_object()
            # Handle file upload for update
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Generate a unique filename
                filename = f"products/{os.urandom(8).hex()}_{image_file.name}"
                # Save the file
                path = default_storage.save(filename, ContentFile(image_file.read()))
                # Get the full URL
                image_url = request.build_absolute_uri(settings.MEDIA_URL + path)
                request.data['image'] = image_url

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            instance = self.get_object()
            # Delete associated image file if it exists
            if instance.image:
                try:
                    # Extract the path from the URL
                    image_path = instance.image.split(settings.MEDIA_URL)[-1]
                    default_storage.delete(image_path)
                except:
                    pass
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(user=self.request.user, cart=cart)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'send_verification_code':
            return VerificationCodeSerializer
        elif self.action == 'register':
            return RegisterSerializer
        return None

    @action(detail=False, methods=['post'], url_path='send-verification-code')
    def send_verification_code(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            
            # Invalidate any existing codes for this phone
            VerificationCode.objects.filter(
                phone=phone,
                is_used=False
            ).update(is_used=True)
            
            # Create new verification code
            code = VerificationCode.objects.create(phone=phone)
            
            # Print the verification code to console for testing
            print(f"\n\nVerification code for {phone}: {code.code}\n\n")
            
            return Response({
                'message': 'کد تایید ارسال شد',
                'code': code.code  # For testing purposes
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        # In a real application, you might want to:
        # 1. Add the token to a blacklist
        # 2. Clear any session data
        # 3. Perform additional cleanup
        
        return Response({
            'message': 'شما با موفقیت از حساب کاربری خود خارج شدید'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def register(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Registration error: {str(e)}")  # For debugging
            return Response({
                'error': 'خطا در ثبت نام. لطفا دوباره تلاش کنید.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = get_user_model().objects.get(username=username)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                })
        except get_user_model().DoesNotExist:
            pass
            
        return Response({
            'error': 'نام کاربری یا رمز عبور اشتباه است'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        # Debug information
        print("\n=== User Authentication Debug ===")
        print("Request headers:", dict(self.request.headers))
        print("User object:", self.request.user)
        print("User ID:", self.request.user.id)
        print("Username:", self.request.user.username)
        print("is_admin:", self.request.user.is_admin)
        print("is_staff:", self.request.user.is_staff)
        print("is_active:", self.request.user.is_active)
        print("==============================\n")

        # Check if user is admin
        if not self.request.user.is_admin:
            print("Access denied: User is not an admin")
            return get_user_model().objects.none()

        print("Access granted: User is an admin")
        return get_user_model().objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Prevent deletion of superusers
            if instance.is_superuser:
                return Response(
                    {"detail": "حذف کاربران مدیر کل امکان‌پذیر نیست"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Log the deletion attempt
            print(f"\n=== User Deletion Debug ===")
            print(f"Deleting user: {instance.username}")
            print(f"Deleting user ID: {instance.id}")
            print(f"Deleting user is_superuser: {instance.is_superuser}")
            print(f"Requested by: {request.user.username}")
            print("==========================\n")
            
            # Perform the deletion
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error in destroy: {str(e)}")
            return Response(
                {"detail": "خطا در حذف کاربر"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error in list: {str(e)}")
            return Response(
                {"detail": "خطا در دریافت اطلاعات کاربران"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access for all methods

    def get_queryset(self):
        queryset = Category.objects.all()
        slug = self.request.query_params.get('slug', None)
        
        if slug is not None:
            queryset = queryset.filter(slug=slug)
            print(f"Filtering categories by slug: {slug}")
            print(f"Found {queryset.count()} categories")
        
        return queryset

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = category.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Only allow admin to create
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای ایجاد دسته‌بندی را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Only allow admin to update
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای ویرایش دسته‌بندی را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only allow admin to delete
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای حذف دسته‌بندی را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        # Check if category has any products
        if instance.products.exists():
            return Response(
                {"detail": "این دسته‌بندی دارای محصول است و نمی‌توان آن را حذف کرد"},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all().order_by('-created_at')
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای ایجاد مقاله را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای ویرایش مقاله را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, 'is_admin', False):
            return Response(
                {"detail": "شما دسترسی لازم برای حذف مقاله را ندارید"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]