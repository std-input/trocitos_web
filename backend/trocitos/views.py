import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from .models import Category, Product, Cobertura, CharolaConfig, Order
from .serializers import (
    CategorySerializer, ProductSerializer, CoberturaSerializer,
    CharolaConfigSerializer, OrderSerializer
)

logger = logging.getLogger(__name__)


@xframe_options_exempt
@ensure_csrf_cookie
def index(request):
    return render(request, 'trocitos/index.html')


@method_decorator(cache_control(public=True, max_age=300), name='dispatch')
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes_by_action = {
        'list': [permissions.AllowAny],
        'retrieve': [permissions.AllowAny],
        'create': [permissions.IsAdminUser],
        'update': [permissions.IsAdminUser],
        'partial_update': [permissions.IsAdminUser],
        'destroy': [permissions.IsAdminUser],
    }

    def get_permissions(self):
        perms = self.permission_classes_by_action.get(
            self.action, [permissions.IsAdminUser]
        )
        return [p() for p in perms]

    def get_queryset(self):
        qs = Product.objects.all()
        user = self.request.user
        if self.action == 'list' and (not user or not user.is_staff):
            qs = qs.filter(available=True)
        return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if not request.user or not request.user.is_staff:
            response['Cache-Control'] = 'public, max-age=300'
        return response


@method_decorator(cache_control(public=True, max_age=300), name='dispatch')
class CoberturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cobertura.objects.all()
    serializer_class = CoberturaSerializer


@method_decorator(cache_control(public=True, max_age=300), name='dispatch')
class CharolaConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CharolaConfig.objects.all()
    serializer_class = CharolaConfigSerializer


@api_view(['GET', 'POST'])
def orders_view(request):
    if request.method == 'GET':
        if not request.user or not request.user.is_staff:
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()

            # Send Telegram notification
            if settings.TG_TOKEN:
                _send_telegram(order)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _send_telegram(order):
    items_lines = []
    for item in order.items:
        emoji = item.get('emoji', '•')
        detail = f' ({item.get("detail", "")})' if item.get('detail') else ''
        items_lines.append(
            f'• {emoji} {item["name"]}{detail} × {item["qty"]} = ${item["qty"] * item["price"]}'
        )

    msg = (
        f'🍩✨ *NUEVO PEDIDO #{order.pk}*\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'👤 *Cliente:* {order.customer_name}\n'
        f'📱 *Teléfono:* {order.customer_phone}\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'🛒 *Productos:*\n'
        + '\n'.join(items_lines) + '\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'💰 *TOTAL: ${order.total}*\n'
        f'🕐 *Hora:* {order.created_at.strftime("%d/%m/%Y %I:%M %p")}\n'
        f'━━━━━━━━━━━━━━━━━━━━━━\n'
        f'_Responde a este mensaje para contactar al cliente_ 💬'
    )

    payload = json.dumps({
        'chat_id': settings.TG_CHAT_ID,
        'text': msg,
        'parse_mode': 'Markdown',
    }).encode()

    req = Request(
        f'https://api.telegram.org/bot{settings.TG_TOKEN}/sendMessage',
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    try:
        urlopen(req, timeout=10)
        order.notified = True
        order.save(update_fields=['notified'])
    except URLError as e:
        logger.error(f'Telegram notification failed: {e}')


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def orders_pending_count(request):
    count = Order.objects.filter(status='pending').count()
    return Response({'pending': count})
