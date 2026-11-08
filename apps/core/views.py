import json
import re
from collections import Counter
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View

from apps.artworks.models import Artwork, Category as ArtworkCategory
from apps.notes.models import Note, Category as NoteCategory
from .forms import (
    CustomUserCreationForm as UserCreationForm,
    CustomUserLoginForm as AuthenticationForm,
    UserSettingsForm,
)
from .models import UserSettings
from .phrases import get_random_login_phrase, get_random_logout_phrase


class IndexView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "index.html"
    context_object_name = "artworks"

    def get_paginate_by(self, queryset):
        settings, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return settings.items_per_page

    def get_queryset(self):
        queryset = (
            Artwork.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-uploaded_at")
        )
        # Фильтр по тегам
        query = self.request.GET.get("q")
        if query:
            search_terms = [term.strip() for term in query.split(",") if term.strip()]
            for term in search_terms:
                queryset = queryset.filter(
                    Q(positive_prompt__icontains=term)
                    | Q(negative_prompt__icontains=term)
                )

        # Фильтр по категории
        category_filter = self.request.GET.get("category")
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)

        # Фильтр по модели
        model_filter = self.request.GET.get("model")
        if model_filter:
            queryset = queryset.filter(model_name=model_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["models"] = (
            Artwork.objects.filter(user=self.request.user)
            .exclude(model_name__isnull=True)
            .exclude(model_name="")
            .values_list("model_name", flat=True)
            .distinct()
            .order_by("model_name")
        )
        context["categories"] = ArtworkCategory.objects.filter(
            user=self.request.user
        ).order_by("name")

        context["current_q"] = self.request.GET.get("q", "")
        context["current_model"] = self.request.GET.get("model", "")
        context["current_category"] = self.request.GET.get("category", "")

        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "statistics.html"

    def _extract_tags(self, prompts, ignored_tags):
        """Вспомогательный метод для парсинга тегов."""
        all_tags = []
        for prompt in prompts:
            if prompt:
                tags = [
                    re.sub(r"[\(\)\[\]\{\}]|:\d+\.?\d*", "", tag).strip().lower()
                    for tag in prompt.split(",")
                    if tag.strip()
                ]
                all_tags.extend([t for t in tags if t not in ignored_tags])
        return all_tags

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_settings, _ = UserSettings.objects.get_or_create(user=user)
        user_artworks = Artwork.objects.filter(user=user)
        context["total_artworks"] = user_artworks.count()

        # 1. Арты по дням
        last_30_days = timezone.now() - timedelta(days=30)
        daily_stats = (
            user_artworks.filter(uploaded_at__gte=last_30_days)
            .annotate(date=TruncDate("uploaded_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        context["dates_json"] = json.dumps(
            [item["date"].strftime("%d.%m.%Y") for item in daily_stats]
        )
        context["counts_json"] = json.dumps([item["count"] for item in daily_stats])

        # 2. Топ-5 моделей
        model_stats = (
            user_artworks.exclude(model_name__isnull=True)
            .exclude(model_name="")
            .values("model_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        context["model_names_json"] = json.dumps(
            [item["model_name"] for item in model_stats]
        )
        context["model_counts_json"] = json.dumps(
            [item["count"] for item in model_stats]
        )

        # 🎯 3. Сбор тегов (ПОЗИТИВНЫЕ)
        pos_prompts = user_artworks.values_list("positive_prompt", flat=True)
        ignored_pos = set(user_settings.get_ignored_positive_tags_list())
        all_pos_tags = self._extract_tags(pos_prompts, ignored_tags=set())
        filtered_pos_tags = self._extract_tags(pos_prompts, ignored_tags=ignored_pos)
        pos_counter_filtered = Counter(filtered_pos_tags)
        pos_counter_all = Counter(all_pos_tags)
        context["pos_tag_names_json"] = json.dumps(
            [t[0] for t in pos_counter_filtered.most_common(15)]
        )
        context["pos_tag_counts_json"] = json.dumps(
            [t[1] for t in pos_counter_filtered.most_common(15)]
        )
        context["all_pos_tags"] = pos_counter_all.most_common()

        # 🎯 4. Сбор тегов (НЕГАТИВНЫЕ)
        neg_prompts = user_artworks.values_list("negative_prompt", flat=True)
        ignored_neg = set(user_settings.get_ignored_negative_tags_list())
        all_neg_tags = self._extract_tags(neg_prompts, ignored_tags=set())
        filtered_neg_tags = self._extract_tags(neg_prompts, ignored_tags=ignored_neg)
        neg_counter_filtered = Counter(filtered_neg_tags)
        neg_counter_all = Counter(all_neg_tags)
        context["neg_tag_names_json"] = json.dumps(
            [t[0] for t in neg_counter_filtered.most_common(15)]
        )
        context["neg_tag_counts_json"] = json.dumps(
            [t[1] for t in neg_counter_filtered.most_common(15)]
        )
        context["all_neg_tags"] = neg_counter_all.most_common()

        # 5. Статистика разрешений
        resolution_stats = (
            user_artworks.exclude(width__isnull=True)
            .exclude(height__isnull=True)
            .values("width", "height")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        context["res_names_json"] = json.dumps(
            [f"{item['width']}x{item['height']}" for item in resolution_stats]
        )
        context["res_counts_json"] = json.dumps(
            [item["count"] for item in resolution_stats]
        )

        # 6. Статистика по заметкам и категориям
        context["total_notes"] = Note.objects.filter(user=user).count()
        context["total_notes_categories"] = NoteCategory.objects.filter(
            user=user
        ).count()
        context["total_artworks_categories"] = ArtworkCategory.objects.filter(
            user=user
        ).count()

        return context


class RegisterUserView(CreateView):
    form_class = UserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Аккаунт успешно создан! Теперь вы можете войти."
        )
        return response


class LoginUserView(LoginView):
    form_class = AuthenticationForm
    template_name = "login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            get_random_login_phrase(form.get_user().username),
        )
        return response


class LogoutUserView(LogoutView):
    def post(self, request, *args, **kwargs):
        username = request.user.username if request.user.is_authenticated else "друг"
        messages.info(request, get_random_logout_phrase(username))
        return super().post(request, *args, **kwargs)


class UserSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = UserSettings
    form_class = UserSettingsForm
    template_name = "settings.html"
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        obj, _ = UserSettings.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Настройки сохранены.")
        return super().form_valid(form)


# Custom Errors
def custom_400(request, exception):
    return render(request, "errors/400.html", status=400)


def custom_403(request, exception):
    return render(request, "errors/403.html", status=403)


def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
