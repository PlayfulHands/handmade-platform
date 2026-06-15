from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import register, login, logout, current_user

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'masters', views.MasterViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'follows', views.FollowViewSet, basename='follow')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'chat/rooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'notification-settings', views.NotificationSettingsViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/me/', current_user, name='current_user'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]