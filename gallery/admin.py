import re

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Artwork, Category, Note


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = (
        "short_hash",
        "thumbnail_preview",
        "user",
        "model_name",
        "image_size",
        "tags_count",
        "uploaded_at",
    )
    list_display_links = ("short_hash", "thumbnail_preview")
    list_filter = ("user", "model_name", "uploaded_at")
    search_fields = ("positive_prompt", "model_name")

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "hash")},
        ),
        (
            "Параметры генерации",
            {
                "fields": ("model_name", "seed", "steps", "cfg_scale", "image_size"),
                "classes": ("collapse",),
            },
        ),
        (
            "Промпты",
            {
                "fields": ("positive_prompt", "negative_prompt"),
                "classes": ("wide", "collapse"),
            },
        ),
        (
            "Файлы и даты",
            {
                "fields": ("image_preview", "uploaded_at", "updated_at"),
            },
        ),
    )

    readonly_fields = (
        "hash",
        "user",
        "uploaded_at",
        "updated_at",
        "image_preview",
        "image_size",
    )

    @admin.display(description="Превью")
    def image_preview(self, obj):
        if obj.thumbnail_file:
            return mark_safe(
                f'<img src="{obj.thumbnail_file.url}" style="max-height: 200px; border-radius: 8px;" alt="{obj.hash}"/>'
            )
        return "Нет картинки"

    @admin.display(description="Превью")
    def thumbnail_preview(self, obj):
        if obj.thumbnail_file:
            return mark_safe(
                f'<img src="{obj.thumbnail_file.url}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" alt="{obj.hash}"/>'
            )
        return "—"

    @admin.display(description="Размеры")
    def image_size(self, obj):
        if obj.width and obj.height:
            return f"{obj.width}x{obj.height}"
        return "—"

    @admin.display(description="Кол-во тегов")
    def tags_count(self, obj):
        if not obj.positive_prompt:
            return 0

        tags = [
            re.sub(r"[\(\)\[\]\{\}]|:\d+\.?\d*", "", tag).strip().lower()
            for tag in obj.positive_prompt.split(",")
            if tag.strip()
        ]
        return len(tags)

    @admin.display(description="Хеш (ULID)")
    def short_hash(self, obj):
        if obj.hash:
            return f"{obj.hash[:8]}..."
        return "—"


@admin.register(Category)
class NoteCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    list_filter = ("user",)
    search_fields = ("name",)
    readonly_fields = ("user",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "user", "updated_at")
    list_filter = ("category", "user")
    search_fields = ("title", "body")
    readonly_fields = ("user", "created_at", "updated_at")
