from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'test.gif') -> SimpleUploadedFile:
    uploaded = BytesIO()
    Image.new('RGBA', size=(1, 1), color=(155, 0, 0)).save(
        uploaded,
        'gif',
    )
    uploaded.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=uploaded.read(),
        content_type='image/gif',
    )
