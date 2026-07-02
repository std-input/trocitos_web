from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'coberturas', views.CoberturaViewSet, basename='cobertura')
router.register(r'charolas', views.CharolaConfigViewSet, basename='charola')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('api/orders/', views.orders_view, name='orders'),
    path('api/orders/pending-count/', views.orders_pending_count, name='orders-pending-count'),
]
