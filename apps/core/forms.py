from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserSettings


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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_clean(d, initial) for d in data]
        else:
            result = [single_clean(data, initial)]
        return result


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


class UserSettingsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ["items_per_page", "ignored_positive_tags", "ignored_negative_tags"]
        widgets = {
            "items_per_page": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "100"}
            ),
            "ignored_positive_tags": forms.Textarea(
                attrs={"class": "form-control-sm font-monospace", "rows": 9}
            ),
            "ignored_negative_tags": forms.Textarea(
                attrs={"class": "form-control-sm font-monospace", "rows": 6}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["items_per_page"].widget.attrs["min"] = 1
        self.fields["items_per_page"].widget.attrs["max"] = 100
