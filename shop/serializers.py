from rest_framework import serializers
from .models import (
    Category, Product, Order, OrderItem, Master, 
    Post, PostComment, Follow, WishlistItem, Review
)
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage, Address, NotificationSettings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class MasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ['id', 'shop_name', 'description', 'avatar', 'phone', 'email', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    master = MasterSerializer(read_only=True)
    master_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'image', 
                  'category', 'category_id', 'master', 'master_id', 'created_at']
        read_only_fields = ['slug']


class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_price', 'quantity']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 
                  'comment', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['id', 'total_price', 'status', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            total += item_data['product_price'] * item_data['quantity']
        order.total_price = total
        order.save()
        return order


class OrderItemReadSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'product_price', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total() if hasattr(obj, 'get_total') else obj.product_price * obj.quantity


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'total_price', 'items']


class PostCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostComment
        fields = ['id', 'author_name', 'content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.shop_name', read_only=True)
    master_avatar = serializers.ImageField(source='master.avatar', read_only=True)
    master_id = serializers.IntegerField(source='master.id', read_only=True)
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'master', 'master_id', 'master_name', 'master_avatar', 'title', 'content', 
                  'image', 'video_url', 'created_at', 'views_count', 'comments_count', 
                  'likes_count', 'user_liked']
    
    def get_comments_count(self, obj):
        return obj.comments.filter(is_published=True).count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_user_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class FollowSerializer(serializers.ModelSerializer):
    master_id = serializers.IntegerField(write_only=True)
    master = MasterSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'user', 'master', 'master_id', 'created_at']
        read_only_fields = ['id', 'user', 'master', 'created_at']


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ProductDetailSerializer(ProductSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    is_wishlisted = serializers.SerializerMethodField()
    
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['reviews', 'reviews_count', 'average_rating', 'is_wishlisted']
    
    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlisted_by.filter(user=request.user).exists()
        return False


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


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'text', 'is_read', 'created_at', 'is_owner']
        read_only_fields = ['id', 'sender', 'sender_name', 'created_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender


class ChatRoomSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.shop_name', read_only=True)
    master_avatar = serializers.ImageField(source='master.avatar', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'master', 'master_name', 'master_avatar', 'customer', 'customer_name',
                  'order', 'last_message', 'unread_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return ChatMessageSerializer(msg, context=self.context).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'address_line', 'city', 'postal_code', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ['email_notifications', 'sms_notifications', 'order_updates', 'promotions']


class UserProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    notification_settings = NotificationSettingsSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'addresses', 'notification_settings']
        read_only_fields = ['id', 'username']

OrderSerializer = OrderReadSerializer