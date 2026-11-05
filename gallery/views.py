import json
import re
from collections import Counter
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.detail import BaseDetailView


from .forms import (
    ArtworkEditForm,
    CategoryForm,
    CustomUserCreationForm as UserCreationForm,
    CustomUserLoginForm as AuthenticationForm,
    ArtworkUploadForm,
    NoteForm,
)
from .models import Artwork, Category, Note
from .phrases import get_random_login_phrase, get_random_logout_phrase
from .services import ImageService


class IndexView(LoginRequiredMixin, ListView):
    model = Artwork
    template_name = "index.html"
    context_object_name = "artworks"
    paginate_by = 24

    def get_queryset(self):
        queryset = Artwork.objects.filter(user=self.request.user).order_by(
            "-uploaded_at"
        )
        query = self.request.GET.get("q")
        model_filter = self.request.GET.get("model")

        if query:
            queryset = queryset.filter(
                Q(positive_prompt__icontains=query)
                | Q(negative_prompt__icontains=query)
            )

        # 4. Фильтр по модели
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

        context["current_q"] = self.request.GET.get("q", "")
        context["current_model"] = self.request.GET.get("model", "")
        context["total_artworks"] = Artwork.objects.filter(
            user=self.request.user
        ).count()

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

        top_tags = Counter(all_tags).most_common(15)
        tag_names = [item[0] for item in top_tags]
        tag_counts = [item[1] for item in top_tags]

        # 🎯 4. Распределение по разрешениям
        resolution_stats = (
            user_artworks.exclude(width__isnull=True)
            .exclude(height__isnull=True)
            .values("width", "height")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]  # Берем топ-5 разрешений
        )

        # Превращаем в "1024x1024"
        res_names = [f"{item['width']}x{item['height']}" for item in resolution_stats]
        res_counts = [item["count"] for item in resolution_stats]

        context["tag_names_json"] = json.dumps(tag_names)
        context["tag_counts_json"] = json.dumps(tag_counts)
        context["res_names_json"] = json.dumps(res_names)
        context["res_counts_json"] = json.dumps(res_counts)

        # 🎯 5. Статистика по базе знаний
        context["total_notes"] = Note.objects.filter(user=user).count()
        context["total_categories"] = Category.objects.filter(user=user).count()

        # Самая большая категория
        biggest_cat = (
            Category.objects.filter(user=user)
            .annotate(notes_count=Count("notes"))
            .order_by("-notes_count")
            .first()
        )
        context["biggest_category"] = biggest_cat

        # Последняя заметка
        context["latest_note"] = (
            Note.objects.filter(user=user).order_by("-updated_at").first()
        )

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


# Artworks
class ArtworkDetailView(LoginRequiredMixin, DetailView):
    model = Artwork
    template_name = "artworks/detail.html"
    context_object_name = "artwork"

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)
        if artwork.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет доступа к этому арту")

        return artwork


class ArtworkEditView(LoginRequiredMixin, UpdateView):
    model = Artwork
    form_class = ArtworkEditForm
    template_name = "artworks/edit.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)
        if artwork.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет прав на редактирование")
        return artwork

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Изменения сохранены")
        if "_continue" in self.request.POST:
            return redirect("artwork_edit", hash=self.object.hash)

        return redirect("artwork_detail", hash=self.object.hash)


class ArtworkUploadView(LoginRequiredMixin, CreateView):
    form_class = ArtworkUploadForm
    template_name = "artworks/upload.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        image_file = self.request.FILES.get("image")
        if not image_file:
            messages.error(self.request, "Вы не прикрепили файл изображения.")
            return self.form_invalid(form)

        image_data = ImageService.process_and_save(image_file)

        artwork = form.save(commit=False)
        artwork.user = self.request.user
        artwork.hash = image_data["hash"]
        artwork.width = image_data["width"]
        artwork.height = image_data["height"]

        artwork.original_file = image_data["original_file"]
        artwork.thumbnail_file = image_data["thumbnail_file"]

        artwork.save()

        messages.success(self.request, "Арт успешно загружен.")
        if "_continue" in self.request.POST:
            return redirect("artwork_edit", hash=artwork.hash)
        if "_addanother" in self.request.POST:
            return redirect("artwork_upload")
        return redirect("index")


class ArtworkDeleteView(LoginRequiredMixin, DeleteView):
    model = Artwork
    success_url = reverse_lazy("index")

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)

        if artwork.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет прав на удаление этого арта")

        return artwork

    def post(self, request, *args, **kwargs):
        artwork = self.get_object()

        if artwork.original_file:
            artwork.original_file.delete(save=False)
        if artwork.thumbnail_file:
            artwork.thumbnail_file.delete(save=False)

        messages.success(
            self.request, "Арт удален, а дисковое пространство освобождено."
        )

        return super().post(request, *args, **kwargs)


class ArtworkDownloadView(LoginRequiredMixin, BaseDetailView):
    model = Artwork

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)

        if artwork.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет доступа к этому арту")

        return artwork

    def render_to_response(self, context, **response_kwargs):
        artwork = self.get_object()

        file_path = artwork.original_file.path
        filename = f"Minerva_{artwork.hash[:8]}.jpg"

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=filename,
        )


# Заметки
class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/list.html"
    context_object_name = "notes"
    paginate_by = 12

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(user=self.request.user)
        return context


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/create_or_edit.html"
    success_url = reverse_lazy("notes")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Заметка сохранена в базе знаний")
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/create_or_edit.html"
    success_url = reverse_lazy("notes")

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Заметка обновлена.")
        return super().form_valid(form)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy("notes")

    def get_success_url(self):
        messages.success(self.request, "Заметка удалена из базы знаний.")
        return super().get_success_url()


# Категории
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "categories/list.html"
    context_object_name = "categories"
    paginate_by = 12

    def get_queryset(self):
        return (
            Category.objects.filter(user=self.request.user)
            .annotate(notes_count=Count("notes"))
            .order_by("-notes_count", "name")
        )


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/create_or_edit.html"
    success_url = reverse_lazy("categories")

    def form_valid(self, form):
        messages.success(self.request, "Категория обновлена")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"user": self.request.user}
        return kwargs

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/create_or_edit.html"
    success_url = reverse_lazy("categories")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"user": self.request.user}
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Новая категория готова к использованию.")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("categories")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Категория удалена. Заметки сохранены.")
        return super().get_success_url()


# Custom Errors
def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_403(request, exception):
    return render(request, "errors/403.html", status=403)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
