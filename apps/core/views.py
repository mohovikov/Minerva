import json
import re
from collections import Counter
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, TemplateView

from apps.artworks.models import Artwork, Category
from apps.notes.models import Note, Category as NoteCategory
from .forms import (
    CustomUserCreationForm as UserCreationForm,
    CustomUserLoginForm as AuthenticationForm,
)
from .phrases import get_random_login_phrase, get_random_logout_phrase


class IndexView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "index.html"
    context_object_name = "artworks"
    paginate_by = 24

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
        context["categories"] = Category.objects.filter(
            user=self.request.user
        ).order_by("name")

        context["current_q"] = self.request.GET.get("q", "")
        context["current_model"] = self.request.GET.get("model", "")
        context["current_category"] = self.request.GET.get("category", "")

        return context


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_artworks = Artwork.objects.filter(user=self.request.user)

        # 1. Арты по дням (за последние 30 дней)
        last_30_days = timezone.now() - timedelta(days=30)
        daily_stats = (
            user_artworks.filter(uploaded_at__gte=last_30_days)
            .annotate(date=TruncDate("uploaded_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        dates = [item["date"].strftime("%d.%m.%Y") for item in daily_stats]
        counts = [item["count"] for item in daily_stats]

        # 2. Топ-5 моделей
        model_stats = (
            user_artworks.exclude(model_name__isnull=True)
            .exclude(model_name="")
            .values("model_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        model_names = [item["model_name"] for item in model_stats]
        model_counts = [item["count"] for item in model_stats]

        context["total_artworks"] = user_artworks.count()
        context["dates_json"] = json.dumps(dates)
        context["counts_json"] = json.dumps(counts)
        context["model_names_json"] = json.dumps(model_names)
        context["model_counts_json"] = json.dumps(model_counts)

        prompts = user_artworks.values_list("positive_prompt", flat=True)
        all_tags = []
        for prompt in prompts:
            if prompt:
                tags = [
                    re.sub(r"[\(\)\[\]\{\}]|:\d+\.?\d*", "", tag).strip().lower()
                    for tag in prompt.split(",")
                    if tag.strip()
                ]
                all_tags.extend(tags)

        counter = Counter(all_tags)

        top_tags = counter.most_common(15)
        tag_names = [item[0] for item in top_tags]
        tag_counts = [item[1] for item in top_tags]
        context["all_tags"] = counter.most_common()

        resolution_stats = (
            user_artworks.exclude(width__isnull=True)
            .exclude(height__isnull=True)
            .values("width", "height")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        res_names = [f"{item['width']}x{item['height']}" for item in resolution_stats]
        res_counts = [item["count"] for item in resolution_stats]

        context["tag_names_json"] = json.dumps(tag_names)
        context["tag_counts_json"] = json.dumps(tag_counts)
        context["res_names_json"] = json.dumps(res_names)
        context["res_counts_json"] = json.dumps(res_counts)

        # 🎯 5. Статистика по базе знаний
        context["total_notes"] = Note.objects.filter(user=user).count()
        context["total_categories"] = NoteCategory.objects.filter(user=user).count()

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


# Custom Errors
def custom_400(request, exception):
    return render(request, "errors/400.html", status=400)


def custom_403(request, exception):
    return render(request, "errors/403.html", status=403)


def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
