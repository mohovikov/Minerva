from django.db import models
from django.contrib.auth.models import User


class UserSettings(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name="Пользователь",
    )
    ignored_positive_tags = models.TextField(
        blank=True,
        default="masterpiece, best quality, high quality, absurdres, newest, very aesthetic, very awa, amazing quality",
        verbose_name="Игнорируемые Positive-теги",
        help_text="Через запятую. Данный список тегов не будет учитыватся в статистике позитивных тегов.",
    )

    ignored_negative_tags = models.TextField(
        blank=True,
        default="worst quality, low quality, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry",
        verbose_name="Игнорируемые Negative-теги",
        help_text="Через запятую. Данный список тегов не будет учитыватся в статистике позитивных тегов.",
    )

    items_per_page = models.PositiveIntegerField(
        default=24,
        verbose_name="Артов на страницу",
        help_text="Сколько артов показывать в галерее (например, 24, 48, 96).",
    )

    def get_ignored_positive_tags_list(self):
        """Возвращает список тегов, разбивая строку по запятым."""
        if not self.ignored_positive_tags:
            return []
        return [
            tag.strip().lower()
            for tag in self.ignored_positive_tags.split(",")
            if tag.strip()
        ]

    def get_ignored_negative_tags_list(self):
        """Возвращает список тегов, разбивая строку по запятым."""
        if not self.ignored_negative_tags:
            return []
        return [
            tag.strip().lower()
            for tag in self.ignored_negative_tags.split(",")
            if tag.strip()
        ]

    class Meta:
        verbose_name = "Настройки пользователя"
        verbose_name_plural = "Настройки пользователей"

    def __str__(self):
        return f"Настройки {self.user.username}"
