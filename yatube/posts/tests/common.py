from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def image(name: str = 'test.gif') -> SimpleUploadedFile:
    uploaded = BytesIO()
    image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
    image.save(uploaded, 'gif')
    uploaded.seek(0)
    return SimpleUploadedFile(
        name='test.gif',
        content=uploaded.read(),
        content_type='image/gif',
    )
