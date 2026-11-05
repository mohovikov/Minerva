from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("stats/", views.StatisticsView.as_view(), name="stats"),
    path("register/", views.RegisterUserView.as_view(), name="register"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("logout/", views.LogoutUserView.as_view(), name="logout"),
    # Artworks
    path(
        "artwork/upload/",
        views.ArtworkUploadView.as_view(),
        name="artwork_upload",
    ),
    path(
        "artwork/<str:hash>",
        views.ArtworkDetailView.as_view(),
        name="artwork_detail",
    ),
    path(
        "artwork/<str:hash>/delete",
        views.ArtworkDeleteView.as_view(),
        name="artwork_delete",
    ),
    path(
        "artwork/<str:hash>/edit",
        views.ArtworkEditView.as_view(),
        name="artwork_edit",
    ),
    path(
        "artwork/<str:hash>/download/",
        views.ArtworkDownloadView.as_view(),
        name="download_art",
    ),
    # Заметки
    path("notes/", views.NoteListView.as_view(), name="notes"),
    path("notes/new/", views.NoteCreateView.as_view(), name="note_new"),
    path("notes/<int:pk>/edit/", views.NoteUpdateView.as_view(), name="note_edit"),
    path("notes/<int:pk>/delete/", views.NoteDeleteView.as_view(), name="note_delete"),
    # Категории
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_new"),
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
