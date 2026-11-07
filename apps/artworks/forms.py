from django import forms
from django.core.exceptions import ValidationError

from apps.core.forms import BootstrapFormMixin, MultipleFileField, MultipleFileInput
from .models import Artwork, Category


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


class ArtworkUploadForm(BootstrapFormMixin, BaseArtworkForm):
    images = MultipleFileField(
        label="Выберите файлы",
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/png, image/jpeg",
            }
        ),
    )

    class Meta:
        model = Artwork
        exclude = [
            "hash",
            "original_file",
            "thumbnail_file",
            "user",
            "width",
            "height",
            "user",
            "uploaded_at",
        ]

    def clean_images(self):
        files = self.files.getlist("images")
        if not files:
            raise forms.ValidationError("Выберите хотя бы один файл")
        if len(files) > 15:
            raise forms.ValidationError(
                f"Вы выбрали {len(files)} файлов. За один раз можно загружать не более 15."
            )
        return files


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
            "seed": forms.TextInput(attrs={"placeholder": "Например: 1583333275"}),
            "steps": forms.NumberInput(attrs={"min": "1", "step": "1"}),
            "cfg_scale": forms.NumberInput(attrs={"step": "0.1", "min": "0.1"}),
        }


class CategoryForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "color", "style"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Например: Готово, В работе"}
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
                raise ValidationError("У вас уже есть категория с таким названием.")
        return name
