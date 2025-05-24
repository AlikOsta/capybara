from django.core.management.base import BaseCommand
from app.models import Product, Category, BannerPost

class Command(BaseCommand):
    help = 'Generates all image thumbnails'

    def handle(self, *args, **options):
        self.stdout.write('Generating thumbnails for Products...')
        for product in Product.objects.all():
            if product.image:
                # Принудительно генерируем миниатюры
                self.stdout.write(f'Processing product {product.id}')
                try:
                    product.image_thumbnail.generate()
                    product.image_small.generate()
                    product.image_large.generate()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing product {product.id}: {e}'))

        self.stdout.write('Generating thumbnails for Categories...')
        for category in Category.objects.all():
            if category.image:
                self.stdout.write(f'Processing category {category.id}')
                try:
                    category.image_thumbnail.generate()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing category {category.id}: {e}'))

        self.stdout.write('Generating thumbnails for Banners...')
        for banner in BannerPost.objects.all():
            if banner.image:
                self.stdout.write(f'Processing banner {banner.id}')
                try:
                    banner.image_thumbnail.generate()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing banner {banner.id}: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully generated all thumbnails'))
