from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Artwork(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="artworks",
        verbose_name="Пользователь",
    )
    hash = models.CharField(
        max_length=26, unique=True, db_index=True, verbose_name="Хеш (ULID)"
    )

    original_file = models.ImageField(
        upload_to="originals/", max_length=255, verbose_name="Оригинал (JPG)"
    )
    thumbnail_file = models.ImageField(
        upload_to="thumbs/", max_length=255, verbose_name="Превью (WebP)"
    )

    # Метаданные
    model_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Модель"
    )
    positive_prompt = models.TextField(
        blank=True, null=True, verbose_name="Positive Prompt"
    )
    negative_prompt = models.TextField(
        blank=True, null=True, verbose_name="Negative Prompt"
    )
    seed = models.BigIntegerField(blank=True, null=True, verbose_name="Seed")
    steps = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Steps (Шаги)"
    )
    cfg_scale = models.FloatField(blank=True, null=True, verbose_name="CFG Scale")
    width = models.PositiveIntegerField(blank=True, null=True, verbose_name="Ширина")
    height = models.PositiveIntegerField(blank=True, null=True, verbose_name="Высота")

    uploaded_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата загрузки"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Арт"
        verbose_name_plural = "Арты"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["user", "-uploaded_at"], name="artwork_user_date_idx"),
            models.Index(fields=["user", "model_name"], name="artwork_user_model_idx"),
        ]

    def __str__(self) -> str:
        return f"Artwork {self.hash[:8]}"

    def get_absolute_url(self):
        return reverse("artwork_detail", kwargs={"hash": self.hash})

    def save(self, *args, **kwargs):
        if not self.pk and self.original_file and self.thumbnail_file:
            sharded_path = f"{self.hash[0:2]}/{self.hash[2:4]}/{self.hash[4:6]}/"
            self.original_file.name = f"{sharded_path}{self.hash}.jpg"
            self.thumbnail_file.name = f"{sharded_path}{self.hash}.webp"
        super().save(*args, **kwargs)


class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories",
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
