from django import forms
from django.core.exceptions import ValidationError

from apps.core.forms import BootstrapFormMixin
from .models import Note, Category


class NoteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "category", "body"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Заголовок заметки"}
            ),
            "category": forms.Select(attrs={"class": "form-select"}),
            "body": forms.Textarea(
                attrs={
                    "class": "form-control font-monospace",
                    "rows": 10,
                    "placeholder": "Текст заметки...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        category_list = kwargs.pop("category_list", None)
        super().__init__(*args, **kwargs)
        if category_list:
            self.fields["category"].queryset = category_list  # type: ignore


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название категории"}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        user = self.instance.user if self.instance.pk else self.initial.get("user")

        if user:
            qs = Category.objects.filter(name=name, user=user)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("У вас уже есть категория с таким названием")

        return name
