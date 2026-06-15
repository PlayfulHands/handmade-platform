from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Master

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Клиент', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Доставка', {
            'fields': ('address', 'comment')
        }),
        ('Информация о заказе', {
            'fields': ('total_price', 'status', 'created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'product_price')
    list_filter = ('order',)
    readonly_fields = ('order', 'product_name', 'product_price', 'quantity')

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'phone', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('shop_name', 'user__username', 'email', 'phone')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Информация о магазине', {
            'fields': ('shop_name', 'description', 'avatar')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
    )