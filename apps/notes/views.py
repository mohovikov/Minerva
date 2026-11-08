from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy

from .models import Note, Category
from .forms import NoteForm, CategoryForm


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
    success_url = reverse_lazy("notes:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Заметка сохранена в базе знаний")
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/create_or_edit.html"
    success_url = reverse_lazy("notes:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["category_list"] = Category.objects.filter(user=self.request.user)
        return kwargs

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Заметка обновлена.")
        return super().form_valid(form)


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy("notes:list")

    def get_success_url(self):
        messages.success(self.request, "Заметка удалена из базы знаний.")
        return super().get_success_url()


# Категории
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "notes/categories/list.html"
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
    template_name = "notes/categories/create_or_edit.html"
    success_url = reverse_lazy("notes:category_list")

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
    template_name = "notes/categories/create_or_edit.html"
    success_url = reverse_lazy("notes:category_list")

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
    success_url = reverse_lazy("notes:category_list")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Категория удалена. Заметки сохранены.")
        return super().get_success_url()
