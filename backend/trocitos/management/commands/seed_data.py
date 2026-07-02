from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from trocitos.models import Category, Product, Cobertura, CharolaConfig
import requests

User = get_user_model()

CATEGORIES = [
    {'name': 'Charolas', 'emoji': '🍩', 'description': 'Charolas con coberturas a elegir'},
    {'name': 'Salseras', 'emoji': '🥣', 'description': 'Salsas para dipping y acompañar'},
    {'name': 'Cajas', 'emoji': '🎁', 'description': 'El regalo perfecto y más especial'},
]

PRODUCTS = [
    {
        'name': 'Charola 12 Con Cobertura', 'price': 770, 'emoji': '🍩',
        'description': '12 minidonas con las coberturas que elijas. Perfecta para 3-4 personas.',
        'cat': 'Charolas', 'charola_size': 12,
        'image_url': 'https://img.icons8.com/emoji/512/doughnut-emoji.png',
    },
    {
        'name': 'Charola 15 Con Cobertura', 'price': 900, 'emoji': '🍩',
        'description': '15 minidonas con coberturas a elegir. La más popular.',
        'cat': 'Charolas', 'charola_size': 15,
        'image_url': 'https://img.icons8.com/emoji/512/doughnut-emoji.png',
    },
    {
        'name': 'Salsera Dulce de Leche', 'price': 100, 'emoji': '🍮',
        'description': 'Dulce de leche cremoso artesanal para acompañar tus minidonas.',
        'cat': 'Salseras', 'charola_size': None,
        'image_url': 'https://img.icons8.com/emoji/512/pudding-emoji.png',
    },
    {
        'name': 'Salsera Leche Condensada', 'price': 90, 'emoji': '🥛',
        'description': 'Suave y dulce leche condensada para un toque especial.',
        'cat': 'Salseras', 'charola_size': None,
        'image_url': 'https://img.icons8.com/emoji/512/glass-of-milk-emoji.png',
    },
    {
        'name': 'Salsera Nutella', 'price': 150, 'emoji': '🌰',
        'description': 'Cremosa Nutella para los amantes del chocolate y avellanas.',
        'cat': 'Salseras', 'charola_size': None,
        'image_url': 'https://img.icons8.com/emoji/512/chestnut-emoji.png',
    },
    {
        'name': 'Caja Trocitos Premium', 'price': 1800, 'emoji': '🎁',
        'description': 'Caja surtida premium con nuestras mejores minidonas. El regalo ideal.',
        'cat': 'Cajas', 'charola_size': None,
        'image_url': 'https://img.icons8.com/emoji/512/wrapped-gift-emoji.png',
    },
]

COBERTURAS = [
    {'name': 'Leche Condensada', 'price': 3, 'emoji': '🥛'},
    {'name': 'Dulce de Leche', 'price': 7, 'emoji': '🍮'},
    {'name': 'Chocolate', 'price': 10, 'emoji': '🍫'},
    {'name': 'Chocolate Blanco', 'price': 15, 'emoji': '🤍'},
    {'name': 'Nutella', 'price': 20, 'emoji': '🌰'},
]


class Command(BaseCommand):
    help = 'Puebla la base de datos con categorías, productos y coberturas iniciales'

    def handle(self, *args, **options):
        cat_map = {}
        for data in CATEGORIES:
            cat, created = Category.objects.get_or_create(name=data['name'], defaults=data)
            cat_map[data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Categoría: {cat.emoji} {cat.name}'))

        for data in PRODUCTS:
            charola_size = data.pop('charola_size', None)
            image_url = data.pop('image_url')
            cat_name = data.pop('cat')
            data['category'] = cat_map[cat_name]
            product, created = Product.objects.get_or_create(name=data['name'], defaults=data)
            if created:
                self._download_image(product, image_url)
                if charola_size:
                    CharolaConfig.objects.create(product=product, size=charola_size)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Producto: {product.name}'))
            else:
                self.stdout.write(f'  - Ya existe: {product.name}')

        for data in COBERTURAS:
            _, created = Cobertura.objects.get_or_create(name=data['name'], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Cobertura: {data["name"]}'))
            else:
                self.stdout.write(f'  - Ya existe: {data["name"]}')

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin', '', 'admin123')
            self.stdout.write(self.style.SUCCESS('  ✓ Superusuario creado: admin / admin123'))
        else:
            self.stdout.write('  - Superusuario ya existe')

        self.stdout.write(self.style.SUCCESS('\n✅ Seed completado'))

    def _download_image(self, product, url):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                ext = url.split('.')[-1].split('?')[0]
                if ext not in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
                    ext = 'png'
                filename = f'{product.slug}.{ext}'
                product.image.save(filename, ContentFile(resp.content), save=True)
                self.stdout.write(f'    Imagen descargada: {filename}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'    No se pudo descargar imagen: {e}'))
