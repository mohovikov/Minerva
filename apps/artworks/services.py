import json

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
        img = Image.open(uploaded_file)

        comfy_data = cls._extract_comfyui_params(img)
        ulid_str = str(ULID())
        width, height = img.size

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        original_io = BytesIO()
        img.save(original_io, format="JPEG", quality=85, optimize=True)
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
            "positive_prompt": comfy_data.get("positive_prompt", None),
            "negative_prompt": comfy_data.get("negative_prompt", None),
            "model_name": comfy_data.get("model_name", None),
            "seed": comfy_data.get("seed", None),
            "steps": comfy_data.get("steps", None),
            "cfg_scale": comfy_data.get("cfg_scale", None),
        }

    @staticmethod
    def _extract_comfyui_params(img: Image.Image) -> dict:
        """Внутренний метод для парсинга JSON из уже открытого изображения."""
        try:
            prompt_json_str = img.info.get("prompt")
            if not prompt_json_str:
                return {}

            data = json.loads(prompt_json_str)
            params = {}

            for node_id, node in data.items():
                if "KSampler" in node.get("class_type", ""):
                    inputs = node.get("inputs", {})
                    params["seed"] = inputs.get("seed")
                    params["steps"] = inputs.get("steps")
                    params["cfg_scale"] = inputs.get("cfg")

                    pos_id = inputs.get("positive", [None])[0]
                    neg_id = inputs.get("negative", [None])[0]

                    if pos_id and pos_id in data:
                        params["positive_prompt"] = (
                            data[pos_id].get("inputs", {}).get("text", "")
                        )
                    if neg_id and neg_id in data:
                        params["negative_prompt"] = (
                            data[neg_id].get("inputs", {}).get("text", "")
                        )
                    break

            # Ищем модель
            for node_id, node in data.items():
                if "CheckpointLoader" in node.get("class_type", ""):
                    model_name = node.get("inputs", {}).get("ckpt_name", "")
                    if model_name.endswith(".safetensors"):
                        model_name = model_name[:-12]
                    elif model_name.endswith(".ckpt"):
                        model_name = model_name[:-5]

                    params["model_name"] = model_name
                    break

            return params
        except Exception as e:
            print(f"Ошибка парсинга ComfyUI: {e}")
            return {}
