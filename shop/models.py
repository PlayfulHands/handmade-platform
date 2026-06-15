from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework import serializers
# Сначала Master
class Master(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master')
    shop_name = models.CharField('Название магазина', max_length=200)
    description = models.TextField('Описание', blank=True)
    avatar = models.ImageField('Аватар', upload_to='masters/', blank=True, null=True)
    cover = models.ImageField('Обложка', upload_to='masters/covers/', blank=True, null=True)  # НОВОЕ
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    created_at = models.DateTimeField('Дата регистрации', auto_now_add=True)
    products_sold = models.PositiveIntegerField('Продано товаров', default=0)  # НОВОЕ
    rating = models.FloatField('Рейтинг', default=0)  # НОВОЕ
    
    def __str__(self):
        return self.shop_name
    
    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'


# Потом Category
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField('Изображение', upload_to='categories/', blank=True, null=True)  # НОВОЕ

    def __str__(self):
        return self.name


# Потом Product
class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('moderation', 'На модерации'),
        ('published', 'Опубликован'),
        ('rejected', 'Отклонен'),
        ('archived', 'В архиве'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField('Главное фото', upload_to='products/', blank=True, null=True)
    images = models.JSONField('Дополнительные фото', default=list, blank=True)  # НОВОЕ
    options = models.JSONField('Опции кастомизации', default=dict, blank=True)  # НОВОЕ
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # НОВОЕ
    views_count = models.PositiveIntegerField('Просмотры', default=0)  # НОВОЕ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Order
class Order(models.Model):
    STATUS_CHOICES = [
        ('awaiting_payment', 'Ожидает оплаты'),
        ('paid', 'Оплачен, ожидает подтверждения'),
        ('processing', 'В обработке'),
        ('shipped', 'Передан в доставку'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
        ('dispute', 'Спор/Арбитраж'),
    ]
    
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    address = models.TextField('Адрес доставки')
    comment = models.TextField('Комментарий к заказу', blank=True)
    tracking_number = models.CharField('Трек-номер', max_length=100, blank=True)  # НОВОЕ
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    paid_at = models.DateTimeField('Дата оплаты', null=True, blank=True)  # НОВОЕ
    shipped_at = models.DateTimeField('Дата отправки', null=True, blank=True)  # НОВОЕ
    completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)  # НОВОЕ
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='awaiting_payment')
    
    total_price = models.DecimalField('Сумма заказа', max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f'Заказ #{self.id} - {self.first_name} {self.last_name}'
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product_id = models.IntegerField('ID товара')
    product_name = models.CharField('Название товара', max_length=200)
    product_price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество')
    
    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'


# ===== ПОСТЫ (БЛОГ МАСТЕРА) =====
class Post(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='posts', verbose_name='Публикации')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_posts', verbose_name='Связанный товар')  # НОВОЕ
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    image = models.ImageField('Изображение', upload_to='posts/', blank=True, null=True)
    video_url = models.URLField('Ссылка на видео', blank=True, null=True)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    views_count = models.PositiveIntegerField('Просмотры', default=0)
    
    def __str__(self):
        return f'{self.title} - {self.master.shop_name}'
    
    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']


# ===== КОММЕНТАРИИ К ПОСТАМ =====
class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Публикация')
    author_name = models.CharField('Имя автора', max_length=100)
    author_email = models.EmailField('Email', blank=True)
    content = models.TextField('Комментарий')
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    is_published = models.BooleanField('Опубликован', default=True)
    
    def __str__(self):
        return f'Комментарий к {self.post.title} от {self.author_name}'
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']


# ===== ЛАЙКИ К ПОСТАМ =====
class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', verbose_name='Публикация')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='post_likes')
    session_key = models.CharField('Ключ сессии', max_length=100, blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    
    class Meta:
        unique_together = ('post', 'user', 'session_key')
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


# ===== ПОДПИСКИ НА МАСТЕРОВ =====
class Follow(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='following')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'master')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return f'{self.user.username} подписан на {self.master.shop_name}'


# ===== ИЗБРАННОЕ (WISHLIST) =====
class WishlistItem(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранные товары'
    
    def __str__(self):
        return f'{self.user.username} добавил {self.product.name}'


# ===== ОТЗЫВЫ НА ТОВАРЫ =====
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='reviews', verbose_name='Пользователь')
    rating = models.PositiveSmallIntegerField('Рейтинг', choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField('Комментарий', blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating}⭐)'

class ChatRoom(models.Model):
    """Комната чата между покупателем и мастером"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_customer')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='chat_rooms')
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_room')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'master')
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f'Чат {self.customer.username} - {self.master.shop_name}'


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.sender.username}: {self.text[:30]}'
    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField('Название (например, "Дом", "Работа")', max_length=100, blank=True)
    address_line = models.CharField('Адрес', max_length=255)
    city = models.CharField('Город', max_length=100)
    postal_code = models.CharField('Почтовый индекс', max_length=20, blank=True)
    is_default = models.BooleanField('Адрес по умолчанию', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f'{self.title or self.address_line} - {self.user.username}'


class NotificationSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    email_notifications = models.BooleanField('Email уведомления', default=True)
    sms_notifications = models.BooleanField('SMS уведомления', default=False)
    order_updates = models.BooleanField('Обновления заказов', default=True)
    promotions = models.BooleanField('Акции и новости', default=False)

    class Meta:
        verbose_name = 'Настройки уведомлений'
        verbose_name_plural = 'Настройки уведомлений'

    def __str__(self):
        return f'Настройки {self.user.username}'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_name')
    total_price = serializers.DecimalField(source='get_total', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'product_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'total_price', 'items']