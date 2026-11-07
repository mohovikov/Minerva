from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes_categories",
        verbose_name="Пользователь",
    )
    name = models.CharField(max_length=50, verbose_name="Название")

    class Meta:
        verbose_name = "Категория заметок"
        verbose_name_plural = "Категории заметок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_user_category"
            )
        ]

    def __str__(self):
        return self.name


class Note(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notes",
        verbose_name="Пользователь",
    )
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Содержимое")

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notes",
        verbose_name="Категория",
    )

    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заметка"
        verbose_name_plural = "Заметки"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "-updated_at"], name="note_user_date_idx"),
        ]

    def __str__(self):
        return self.title
