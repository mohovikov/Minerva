from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import BaseDetailView

from .models import Artwork, Category
from .forms import ArtworkUploadForm, ArtworkEditForm, CategoryForm
from .services import ImageService


# Арты
class ArtworkUploadView(LoginRequiredMixin, CreateView):
    form_class = ArtworkUploadForm
    template_name = "artworks/upload.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        files = self.request.FILES.getlist("images")
        if not files:
            messages.error(self.request, "Вы не прикрепили файл изображения.")
            return self.form_invalid(form)
        count = 0
        for file in files:
            try:
                image_data = ImageService.process_and_save(file)

                artwork = Artwork(user=self.request.user, **image_data)
                artwork.save()
                count += 1
            except Exception as e:
                messages.error(
                    self.request, f"Ошибка при загрузке {file.name}: {str(e)}"
                )

        if count > 0:
            messages.success(self.request, f"Успешно загружено {count} артов.")
        if "_addanother" in self.request.POST:
            return redirect("artworks:upload")
        return redirect("index")


class ArtworkDetailView(LoginRequiredMixin, DetailView):
    model = Artwork
    template_name = "artworks/detail.html"
    context_object_name = "artwork"
    object: Artwork

    def get_object(self, queryset=None):
        artwork = get_object_or_404(
            Artwork.objects.select_related("category", "user"),
            hash=self.kwargs.get("hash"),
        )
        if artwork.user.pk != self.request.user.pk and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет доступа к этому арту")

        return artwork

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_art = self.object

        similar_artworks = (
            Artwork.objects.filter(user=self.request.user)
            .exclude(id=current_art.pk)
            .filter(
                Q(model_name=current_art.model_name) | Q(category=current_art.category)
            )
            .select_related("category")
            .order_by("-uploaded_at")[:8]
        )

        context["similar_artworks"] = similar_artworks
        return context


class ArtworkEditView(LoginRequiredMixin, UpdateView):
    model = Artwork
    form_class = ArtworkEditForm
    template_name = "artworks/edit.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        artwork = get_object_or_404(
            Artwork.objects.select_related("category", "user"),
            hash=self.kwargs.get("hash"),
        )
        if artwork.user.pk != self.request.user.pk and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет прав на редактирование")
        return artwork

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, "Изменения сохранены")
        if "_continue" in self.request.POST:
            return redirect("artworks:edit", hash=self.object.hash)

        return redirect("artworks:detail", hash=self.object.hash)


class ArtworkDeleteView(LoginRequiredMixin, DeleteView):
    model = Artwork
    success_url = reverse_lazy("index")

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)

        if artwork.user.pk != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("У вас нет прав на удаление этого арта")

        return artwork

    def post(self, request, *args, **kwargs):
        messages.success(
            self.request, "Арт удален, а дисковое пространство освобождено."
        )

        return super().post(request, *args, **kwargs)


class ArtworkDownloadView(LoginRequiredMixin, BaseDetailView):
    model = Artwork

    def get_object(self, queryset=None):
        hash_str = self.kwargs.get("hash")
        artwork = get_object_or_404(Artwork, hash=hash_str)

        if artwork.user.pk != self.request.user and not self.request.user.is_staff:
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


# Категории
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "artworks/categories/list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return (
            Category.objects.filter(user=self.request.user)
            .annotate(artworks_count=Count("artworks"))
            .order_by("name")
        )


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "artworks/categories/create_or_edit.html"
    success_url = reverse_lazy("artworks:category_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"user": self.request.user}
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Категория создана.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "artworks/categories/create_or_edit.html"
    success_url = reverse_lazy("artworks:category_list")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"user": self.request.user}
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Категория обновлена.")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    success_url = reverse_lazy("artworks:category_list")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Категория удалена. Арты сохранены.")
        return super().get_success_url()
