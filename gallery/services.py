from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from ulid import ULID


class ImageService:
    @classmethod
    def process_and_save(cls, uploaded_file) -> dict:
        """
        Принимает файл из формы, конвертирует, ресайзит и возвращает
        словарь с данными для модели.
        """
        ulid_str = str(ULID())

        img = Image.open(uploaded_file)
        width, height = img.size

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        original_io = BytesIO()
        img.save(original_io, format="JPEG", quality=95, optimize=True)
        original_file = ContentFile(original_io.getvalue(), name=f"{ulid_str}.jpg")

        thumb_io = BytesIO()
        thumb_img = img.copy()
        thumb_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
        thumb_img.save(thumb_io, format="WEBP", quality=80)
        thumb_file = ContentFile(thumb_io.getvalue(), name=f"{ulid_str}.webp")

        return {
            "hash": ulid_str,
            "original_file": original_file,
            "thumbnail_file": thumb_file,
            "width": width,
            "height": height,
        }
