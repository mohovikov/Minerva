from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Artwork, Note, Category


class BaseArtworkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            existing_models = (
                Artwork.objects.filter(user=user)
                .exclude(model_name__isnull=True)
                .exclude(model_name="")
                .values_list("model_name", flat=True)
                .distinct()
                .order_by("model_name")
            )
            self.existing_models = existing_models
            self.fields["model_name"].widget.attrs.update(
                {"list": "model-list", "autocomplete": "off"}
            )


class BootstrapFormMixin(forms.ModelForm):
    """
    Миксин, который автоматически добавляет классы Bootstrap
    и подсвечивает поля с ошибками.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget_type = field.widget.__class__.__name__

            if widget_type in ["CheckboxInput", "RadioSelect"]:
                css_class = "form-check-input"
            elif widget_type in ["Select", "SelectMultiple"]:
                css_class = "form-select"
            else:
                css_class = "form-control"

            if self.is_bound and field_name in self.errors:
                css_class += " is-invalid"

            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {css_class}".strip()


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control form-control-sm"

            if self.errors and field_name in self.errors:
                field.widget.attrs["class"] += " is-invalid"


class CustomUserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control form-control-sm"

            if self.errors and field_name in self.errors:
                field.widget.attrs["class"] += " is-invalid"


class ArtworkUploadForm(BootstrapFormMixin, BaseArtworkForm):
    image = forms.ImageField(
        label="Изображение",
        required=True,
        widget=forms.FileInput(
            attrs={"class": "form-control", "accept": "image/png, image/jpeg"}
        ),
    )

    class Meta:
        model = Artwork
        exclude = ["hash", "original_file", "thumbnail_file", "user", "uploaded_at"]

        widgets = {
            "positive_prompt": forms.Textarea(
                attrs={"rows": 9, "class": "form-control"}
            ),
            "negative_prompt": forms.Textarea(
                attrs={"rows": 5, "class": "form-control"}
            ),
            "model_name": forms.TextInput(attrs={"class": "form-control"}),
            "seed": forms.NumberInput(attrs={"class": "form-control"}),
            "steps": forms.NumberInput(attrs={"class": "form-control"}),
            "cfg_scale": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.1"}
            ),
        }


class ArtworkEditForm(BootstrapFormMixin, BaseArtworkForm):
    class Meta:
        model = Artwork
        exclude = [
            "hash",
            "original_file",
            "thumbnail_file",
            "user",
            "width",
            "height",
            "uploaded_at",
            "updated_at",
        ]

        widgets = {
            "positive_prompt": forms.Textarea(
                attrs={
                    "rows": 10,
                    "class": "font-monospace",
                    "style": "font-size: 0.85rem;",
                }
            ),
            "negative_prompt": forms.Textarea(
                attrs={
                    "rows": 7,
                    "class": "font-monospace",
                    "style": "font-size: 0.85rem;",
                }
            ),
            # "model_name": forms.TextInput(attrs={"class": "form-control"}),
            # "seed": forms.NumberInput(attrs={"class": "form-control"}),
            "steps": forms.NumberInput(attrs={"min": "1"}),
            "cfg_scale": forms.NumberInput(attrs={"step": "0.1", "min": "0.1"}),
        }


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
