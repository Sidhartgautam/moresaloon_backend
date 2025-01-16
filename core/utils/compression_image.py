from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def compress_image(image_file, target_size_mb=9, threshold_mb=10):
    threshold_bytes = threshold_mb * 1024 * 1024
    target_size_bytes = target_size_mb * 1024 * 1024

    image_file.seek(0, 2)
    image_size = image_file.tell()
    image_file.seek(0)

    if image_size <= threshold_bytes:
        return image_file
    image = Image.open(image_file)

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    quality = 95
    image_io = BytesIO()

    while True:
        image_io.seek(0)
        image_io.truncate()
        image.save(image_io, format='JPEG', optimize=True, quality=quality)
        current_size = image_io.tell()

        if current_size <= target_size_bytes or quality <= 10:
            break
        quality -= 10

    image_io.seek(0)
    return ContentFile(image_io.read(), name=image_file.name)