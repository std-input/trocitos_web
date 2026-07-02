from django.db import models

class Category(models.Model):
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    emoji = models.CharField('Emoji', max_length=10, blank=True, default='🍩')
    description = models.CharField('Descripción', max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.name)
            slug = base
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.emoji} {self.name}'


class Product(models.Model):
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=0)
    emoji = models.CharField('Emoji', max_length=10, blank=True, default='')
    description = models.TextField('Descripción', blank=True, default='')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products',
        verbose_name='Categoría'
    )
    image = models.ImageField('Imagen', upload_to='products/')
    available = models.BooleanField('Disponible', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['category__name', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.name)
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} — ${self.price}'


class Cobertura(models.Model):
    name = models.CharField('Nombre', max_length=100)
    price = models.DecimalField('Precio por dona', max_digits=10, decimal_places=0)
    emoji = models.CharField('Emoji', max_length=10, blank=True, default='')

    class Meta:
        verbose_name = 'Cobertura'
        verbose_name_plural = 'Coberturas'
        ordering = ['name']

    def __str__(self):
        return f'{self.emoji} {self.name} — ${self.price}/don'


class CharolaConfig(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name='charola_config',
        verbose_name='Producto', limit_choices_to={'category': 'charolas'}
    )
    size = models.PositiveIntegerField('Cantidad de donas')

    class Meta:
        verbose_name = 'Configuración de charola'
        verbose_name_plural = 'Configuraciones de charolas'

    def __str__(self):
        return f'{self.product.name} ({self.size} donas)'


class Order(models.Model):
    STATUS = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
    ]
    customer_name = models.CharField('Nombre del cliente', max_length=200)
    customer_phone = models.CharField('Teléfono', max_length=50)
    items = models.JSONField('Productos')
    total = models.DecimalField('Total', max_digits=10, decimal_places=0)
    status = models.CharField('Estado', max_length=20, choices=STATUS, default='pending')
    notified = models.BooleanField('Notificado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} — {self.customer_name} — ${self.total}'
