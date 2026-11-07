from django.contrib import admin

from .models import Category, Note


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
