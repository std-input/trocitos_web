from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cobertura, CharolaConfig, Order

admin.site.site_header = '🍩 Trocitos — Panel de Administración'
admin.site.site_title = 'Trocitos Admin'
admin.site.index_title = 'Bienvenida, administradora'
admin.site.enable_nav_sidebar = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'name', 'category', 'price_display', 'available', 'updated_at']
    list_editable = ['available']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = [
        ('Información del producto', {
            'fields': ['name', 'slug', 'category', 'price', 'emoji', 'description']
        }),
        ('Imagen', {
            'fields': ['image', 'image_preview_large'],
            'classes': ['wide']
        }),
        ('Disponibilidad', {
            'fields': ['available']
        }),
    ]
    readonly_fields = ['image_preview_large']

    def get_readonly_fields(self, request, obj=None):
        ro = list(self.readonly_fields)
        if obj:
            ro.append('slug')
        return ro

    def price_display(self, obj):
        return f'${obj.price}'
    price_display.short_description = 'Precio'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:contain;border-radius:8px;background:#f5f5f5">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Vista previa'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;object-fit:contain;'
                'border-radius:12px;background:#f5f5f5;padding:10px">',
                obj.image.url
            )
        return 'Sin imagen'
    image_preview_large.short_description = 'Vista previa grande'


class CharolaConfigInline(admin.StackedInline):
    model = CharolaConfig
    extra = 0
    verbose_name = 'Configuración de charola'
    verbose_name_plural = 'Configuración de charola'


@admin.register(Cobertura)
class CoberturaAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'name', 'price_display', 'price']
    list_editable = ['price']

    def price_display(self, obj):
        return f'${obj.price}/dona'
    price_display.short_description = 'Precio'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id_display', 'customer_name', 'customer_phone', 'total_display', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone']
    actions = ['mark_completed']
    readonly_fields = ['customer_name', 'customer_phone', 'items_display', 'total', 'created_at']
    fieldsets = [
        ('Datos del cliente', {
            'fields': ['customer_name', 'customer_phone']
        }),
        ('Pedido', {
            'fields': ['items_display', 'total']
        }),
        ('Estado', {
            'fields': ['status', 'created_at']
        }),
    ]

    def id_display(self, obj):
        return f'#{obj.pk}'
    id_display.short_description = 'Pedido'

    def total_display(self, obj):
        return f'${obj.total}'
    total_display.short_description = 'Total'

    def items_display(self, obj):
        if not obj.items:
            return '—'
        lines = []
        for item in obj.items:
            detail = f' ({item.get("detail", "")})' if item.get('detail') else ''
            lines.append(
                f'{item.get("emoji", "•")} {item["name"]}{detail} × {item["qty"]} = ${item["qty"] * item["price"]}'
            )
        return format_html('<br>'.join(lines) + f'<br><br><strong>Total: ${obj.total}</strong>')
    items_display.short_description = 'Productos'

    @admin.action(description='Marcar como completados')
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(CharolaConfig)
