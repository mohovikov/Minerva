from pathlib import Path
from django.conf import settings


def version_context(request):
    version_file = Path(settings.BASE_DIR) / "VERSION"
    version = "dev"

    if version_file.exists():
        try:
            version = version_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    return {"APP_VERSION": version}
