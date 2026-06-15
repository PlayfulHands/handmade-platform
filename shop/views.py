from datetime import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import models

from .models import (
    Category, Product, Order, Master, 
    Post, PostComment, PostLike, Follow, 
    WishlistItem, Review, Address, NotificationSettings
)
from .serializers import (
    CategorySerializer, ProductSerializer, OrderSerializer, 
    MasterSerializer, PostSerializer, PostCommentSerializer,
    FollowSerializer, WishlistItemSerializer, ReviewSerializer,
    ProductDetailSerializer, AddressSerializer, NotificationSettingsSerializer, UserProfileSerializer
)

from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatMessageSerializer

# ===== СЕРИАЛИЗАТОРЫ ДЛЯ АУТЕНТИФИКАЦИИ =====
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    shop_name = serializers.CharField()
    phone = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(status='published')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'views_count']
    
    def get_queryset(self):
        # Базовый queryset — все опубликованные товары
        queryset = Product.objects.filter(status='published')
        
        # Фильтр по категории
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Фильтр по мастеру (если передан параметр)
        master_id = self.request.query_params.get('master')
        if master_id and master_id != 'null':
            queryset = queryset.filter(master_id=master_id)
        
        # Для обычных пользователей (включая мастеров на главной) 
        # НЕ нужно ограничивать только своими товарами.
        # Если нужно показывать мастеру все его товары (включая черновики) — 
        # это следует делать через отдельный эндпоинт, например /api/products/my-products/
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        master_id = self.request.data.get('master_id')
        if master_id:
            try:
                master = Master.objects.get(id=master_id)
                serializer.save(master=master, status='moderation')
            except Master.DoesNotExist:
                serializer.save()
        else:
            serializer.save()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({
            'success': True,
            'order_id': order.id,
            'message': 'Заказ успешно создан'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        order = self.get_object()
        if order.status != 'shipped':
            return Response({'error': 'Заказ не в доставке'}, status=400)
        
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        return Response({'success': True, 'message': 'Заказ подтвержден'})


class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = []
    
    def get_queryset(self):
        return Master.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        master = self.get_object()
        serializer = self.get_serializer(master)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get', 'put', 'patch'], url_path='profile')
    def profile(self, request):
        master = Master.objects.first()
        if not master:
            return Response({'error': 'Мастер не найден'}, status=404)
        
        if request.method == 'GET':
            serializer = self.get_serializer(master)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(master, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'], url_path='products')
    def master_products(self, request, pk=None):
        master = self.get_object()
        products = Product.objects.filter(master=master, status='published')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='posts')
    def master_posts(self, request, pk=None):
        master = self.get_object()
        posts = Post.objects.filter(master=master, is_published=True)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


# ===== ПОСТЫ (БЛОГ) =====
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user if request.user.is_authenticated else None
        
        if user:
            like, created = PostLike.objects.get_or_create(post=post, user=user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            like, created = PostLike.objects.get_or_create(post=post, session_key=session_key)
        
        if not created:
            like.delete()
            return Response({'liked': False, 'count': post.likes.count()})
        
        return Response({'liked': True, 'count': post.likes.count()})
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = PostCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def feed(self, request):
        posts = self.get_queryset()[:30]
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='master/(?P<master_id>[^/.]+)')
    def master_posts(self, request, master_id=None):
        posts = self.get_queryset().filter(master_id=master_id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


# ===== ПОДПИСКИ =====
class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]  # Убедись, что это есть
    
    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return Response({'error': 'Необходимо авторизоваться'}, status=401)
        
        master_id = request.data.get('master_id')
        if not master_id:
            return Response({'error': 'master_id required'}, status=400)
        
        try:
            master = Master.objects.get(id=master_id)
        except Master.DoesNotExist:
            return Response({'error': 'Мастер не найден'}, status=404)
        
        follow = Follow.objects.filter(user=request.user, master=master)
        if follow.exists():
            follow.delete()
            return Response({'followed': False})
        else:
            Follow.objects.create(user=request.user, master=master)
            return Response({'followed': True})


# ===== ИЗБРАННОЕ =====
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistItemSerializer
    permission_classes = []
    
    def get_queryset(self):
        return WishlistItem.objects.all()
    
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id required'}, status=400)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)
        
        user = User.objects.first()
        
        wishlist_item = WishlistItem.objects.filter(user=user, product=product)
        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({'wishlisted': False})
        else:
            WishlistItem.objects.create(user=user, product=product)
            return Response({'wishlisted': True})
    
    @action(detail=False, methods=['get'], url_path='list')
    def wishlist_list(self, request):
        items = self.get_queryset()
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


# ===== ОТЗЫВЫ =====
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(is_published=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)')
    def product_reviews(self, request, product_id=None):
        reviews = self.get_queryset().filter(product_id=product_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Фильтруем комнаты, где пользователь является покупателем или мастером
        return ChatRoom.objects.filter(
            models.Q(customer=self.request.user) |
            models.Q(master__user=self.request.user)
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        master_id = request.data.get('master')
        if not master_id:
            return Response({'error': 'master_id required'}, status=400)
        try:
            master = Master.objects.get(id=master_id)
        except Master.DoesNotExist:
            return Response({'error': 'Master not found'}, status=404)
        # Создаём или получаем существующую комнату
        room, created = ChatRoom.objects.get_or_create(
            customer=request.user,
            master=master
        )
        serializer = self.get_serializer(room)
        status_code = 201 if created else 200
        return Response(serializer.data, status=status_code)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        room = self.get_object()
        room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        messages = room.messages.all()
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='send')
    def send_message(self, request, pk=None):
        room = self.get_object()
        text = request.data.get('text')
        if not text:
            return Response({'error': 'Текст сообщения обязателен'}, status=400)
        message = ChatMessage.objects.create(room=room, sender=request.user, text=text)
        room.save(update_fields=['updated_at'])
        serializer = ChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=201)


# ===== АУТЕНТИФИКАЦИЯ =====
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', '')
        )
        master = Master.objects.create(
            user=user,
            shop_name=serializer.validated_data['shop_name'],
            phone=serializer.validated_data['phone'],
            email=serializer.validated_data['email'],
            description=''
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'master_id': master.id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Логин и пароль обязательны'}, status=400)
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        
        try:
            master = user.master
            master_id = master.id
        except Master.DoesNotExist:
            master_id = None
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'master_id': master_id
        })
    else:
        return Response(
            {'error': 'Неверный логин или пароль'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            # Если нет refresh токена, просто возвращаем успех (клиент уже очистил токены)
            return Response({'message': 'Выход выполнен'}, status=status.HTTP_200_OK)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Успешный выход'}, status=status.HTTP_200_OK)
    except Exception as e:
        # Даже при ошибке возвращаем 200, чтобы клиент не падал
        print(f"Logout error: {e}")
        return Response({'message': 'Выход выполнен'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def current_user(request):
    if not request.user.is_authenticated:
        first_user = User.objects.first()
        if first_user:
            serializer = UserSerializer(first_user)
            try:
                master = Master.objects.get(user=first_user)
                master_id = master.id
                master_data = MasterSerializer(master).data
            except Master.DoesNotExist:
                master_id = None
                master_data = None
            return Response({
                'user': serializer.data,
                'master_id': master_id,
                'master': master_data
            })
        return Response({'error': 'Пользователь не найден'}, status=404)
    
    serializer = UserSerializer(request.user)
    try:
        master = Master.objects.get(user=request.user)
        master_id = master.id
        master_data = MasterSerializer(master).data
    except Master.DoesNotExist:
        master_id = None
        master_data = None
    
    return Response({
        'user': serializer.data,
        'master_id': master_id,
        'master': master_data
    })

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='set-default')
    def set_default(self, request, pk=None):
        address = self.get_object()
        # Сбрасываем default у всех адресов пользователя
        Address.objects.filter(user=request.user).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'status': 'default set'})


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get', 'put'], url_path='my')
    def my_settings(self, request):
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        if request.method == 'PUT':
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
        serializer = self.get_serializer(settings)
        return Response(serializer.data)