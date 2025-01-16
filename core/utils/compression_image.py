from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def compress_image(image_file, target_size_mb=9, threshold_mb=10):
    from PIL import Image
    from io import BytesIO
    from django.core.files.base import ContentFile

    threshold_bytes = threshold_mb * 1024 * 1024  # Convert MB to bytes
    target_size_bytes = target_size_mb * 1024 * 1024

    # Get the size of the input image
    image_file.seek(0, 2)
    image_size = image_file.tell()
    image_file.seek(0)

    # If the image is already below the threshold, return it as is
    if image_size <= threshold_bytes:
        return image_file

    # Open the image using PIL
    image = Image.open(image_file)

    # Convert RGBA to RGB if needed
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Prepare for compression
    quality = 95
    image_io = BytesIO()

    while True:
        image_io.seek(0)
        image_io.truncate()
        # Save the image with reduced quality
        image.save(image_io, format='JPEG', optimize=True, quality=quality)
        current_size = image_io.tell()

        # Break the loop if the image is compressed enough or quality is too low
        if current_size <= target_size_bytes or quality <= 10:
            break
        quality -= 10

    # Create a new ContentFile for the compressed image
    image_io.seek(0)
    compressed_image = ContentFile(image_io.read(), name=image_file.name)
    return compressed_image