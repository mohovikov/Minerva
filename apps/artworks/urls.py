from django.urls import path
from . import views

app_name = "artworks"

urlpatterns = [
    # Арты
    path("upload/", views.ArtworkUploadView.as_view(), name="upload"),
    path("<str:hash>", views.ArtworkDetailView.as_view(), name="detail"),
    path("<str:hash>/edit", views.ArtworkEditView.as_view(), name="edit"),
    path("<str:hash>/delete", views.ArtworkDeleteView.as_view(), name="delete"),
    path("<str:hash>/download/", views.ArtworkDownloadView.as_view(), name="download"),
    # Категории артов
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
]
