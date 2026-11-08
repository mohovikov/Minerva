from django.contrib import admin
from .models import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "items_per_page",
        "ignored_positive_tags_short",
        "ignored_negative_tags_short",
    )
    search_fields = ("user__username", "user__email")
    list_filter = ("items_per_page",)
    autocomplete_fields = ("user",)
    readonly_fields = ("user",)

    @admin.display(description="Игнор. Positive")
    def ignored_positive_tags_short(self, obj):
        if not obj.ignored_positive_tags:
            return "—"
        return obj.ignored_positive_tags[:50] + (
            "..." if len(obj.ignored_positive_tags) > 50 else ""
        )

    @admin.display(description="Игнор. Negative")
    def ignored_negative_tags_short(self, obj):
        if not obj.ignored_negative_tags:
            return "—"
        return obj.ignored_negative_tags[:50] + (
            "..." if len(obj.ignored_negative_tags) > 50 else ""
        )
