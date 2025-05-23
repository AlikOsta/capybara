
import os
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.base import ContentFile


def apply_exif_orientation(image):
    try:
        exif = image._getexif()
        if not exif:
            return image
        exif_dict = dict(exif.items())
        orientation_key = [k for k, v in ExifTags.TAGS.items() if v == "Orientation"][0]
        orientation = exif_dict.get(orientation_key)

        if orientation == 3:
            image = image.rotate(180, expand=True)
        elif orientation == 6:
            image = image.rotate(270, expand=True)
        elif orientation == 8:
            image = image.rotate(90, expand=True)
    except Exception:
        pass  
    return image


def process_image(image_field, instans_id=None, max_size=(800, 800), format="WEBP", quality=65):

    print('******НАЧАЛО ОБРАБОТКИ ИЗОБРАЖЕНИЯ******')

    if not image_field:
        return None
    
    img = Image.open(image_field)
    img = apply_exif_orientation(img)

    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size)
    
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    output = BytesIO()

    try:
        img.save(output, format=format, quality=quality, optimize=True)
    except OSError:
        img.save(output, format=format, quality=quality)
        
    output.seek(0)
    
    base_name = image_field.name.rsplit(".", 1)[0]
    id_prefix = f"{instans_id}_" if instans_id else ""
    new_name = f"{id_prefix}{base_name}.{format.lower()}"

    return ContentFile(output.read(), name=new_name)

    