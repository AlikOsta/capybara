from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

def optimize_image(image_field, max_size=(800, 800), quality=65, format='WEBP'):
    """
    Оптимизирует изображение: изменяет размер, конвертирует в WebP и сжимает.
    
    Args:
        image_field: ImageField объект
        max_size: максимальный размер (ширина, высота)
        quality: качество сжатия (0-100)
        format: формат изображения ('WEBP', 'JPEG', etc.)
    
    Returns:
        ContentFile с оптимизированным изображением
    """
    if not image_field:
        return None
        
    img = Image.open(image_field)
    
    if img.height > max_size[1] or img.width > max_size[0]:
        img.thumbnail(max_size)

    if img.mode != "RGB":
        img = img.convert("RGB")

    output = BytesIO()
    img.save(output, format=format, quality=quality, optimize=True)
    output.seek(0)
    
    base_name = os.path.splitext(os.path.basename(image_field.name))[0]
    return ContentFile(output.read(), name=f"{base_name}.webp")

def create_thumbnail(image_field, size, quality=65):
    """
    Создает миниатюру указанного размера.
    
    Args:
        image_field: ImageField объект
        size: размер миниатюры (ширина, высота)
        quality: качество сжатия (0-100)
    
    Returns:
        ContentFile с миниатюрой
    """
    if not image_field:
        return None
        
    img = Image.open(image_field)
    
    if size[0] == size[1]: 
        width, height = img.size
        if width > height:
            left = (width - height) / 2
            top = 0
            right = (width + height) / 2
            bottom = height
        else:
            left = 0
            top = (height - width) / 2
            right = width
            bottom = (height + width) / 2
        img = img.crop((left, top, right, bottom))
    
    img = img.resize(size, Image.LANCZOS)

    if img.mode != "RGB":
        img = img.convert("RGB")
    
    output = BytesIO()
    img.save(output, format='WEBP', quality=quality, optimize=True)
    output.seek(0)
    
    base_name = os.path.splitext(os.path.basename(image_field.name))[0]
    return ContentFile(output.read(), name=f"{base_name}_{size[0]}x{size[1]}.webp")
