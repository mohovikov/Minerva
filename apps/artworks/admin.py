from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Artwork, Category


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("user", "hash", "category")},
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
    date_hierarchy = "uploaded_at"
    list_per_page = 24
    list_display = (
        "short_hash",
        "thumbnail_preview",
        "user",
        "category",
        "model_name",
        "image_size",
        "uploaded_at",
    )
    readonly_fields = (
        "hash",
        "user",
        "uploaded_at",
        "updated_at",
        "image_preview",
        "image_size",
    )
    list_display_links = ("short_hash", "thumbnail_preview")
    list_filter = ("user", "category", "model_name", "uploaded_at")
    list_select_related = ("user", "category")
    save_on_top = True
    search_fields = ("positive_prompt", "negative_prompt")
    search_help_text = "Поиск по positive и negative промптам"
    show_full_result_count = False

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
                f'<img src="{obj.thumbnail_file.url}" width="50" height="50" '
                f'style="object-fit: cover; border-radius: 8px;" '
                f'loading="lazy" alt="{obj.hash}"/>'
            )
        return "—"

    @admin.display(description="Размеры")
    def image_size(self, obj):
        if obj.width and obj.height:
            return f"{obj.width}x{obj.height}"
        return "—"

    @admin.display(description="Хеш (ULID)")
    def short_hash(self, obj):
        if obj.hash:
            return f"{obj.hash[:8]}..."
        return "—"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "color", "style")
    list_filter = ("user", "color", "style")
    search_fields = ("name",)
    list_editable = ("color", "style")
