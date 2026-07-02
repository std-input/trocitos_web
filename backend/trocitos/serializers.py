from rest_framework import serializers
from .models import Category, Product, Cobertura, CharolaConfig, Order


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'emoji', 'description']


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    charola_size = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'emoji', 'description',
                  'category', 'category_id', 'image_url', 'charola_size', 'available']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_charola_size(self, obj):
        try:
            return obj.charola_config.size
        except CharolaConfig.DoesNotExist:
            return None


class CoberturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobertura
        fields = ['id', 'name', 'price', 'emoji']


class CharolaConfigSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = CharolaConfig
        fields = ['id', 'product_id', 'size', 'product_name']


class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'emoji']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_phone', 'items', 'total', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

    def validate_items(self, value):
        if not value or not isinstance(value, list):
            raise serializers.ValidationError('Debe incluir al menos un producto')
        for item in value:
            if not all(k in item for k in ('name', 'qty', 'price')):
                raise serializers.ValidationError('Cada producto debe tener name, qty, price')
            if item['qty'] < 1:
                raise serializers.ValidationError('La cantidad debe ser al menos 1')
        return value

    def validate_total(self, value):
        expected = sum(
            item['price'] * item['qty']
            for item in self.initial_data.get('items', [])
        )
        if float(value) != float(expected):
            raise serializers.ValidationError('El total no coincide con los productos')
        return value
