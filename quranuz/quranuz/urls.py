from django.contrib import admin
from django.urls import path, include
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", core_views.home, name="home"),
    path("search/", core_views.search, name="search"),
    path("suralar/", core_views.suralar, name="suralar"),
    path("kokler/", core_views.roots_letters, name="kokler_index"),
    path("kokler/<str:letter>/", core_views.roots_by_letter, name="kokler_by_letter"),
    path("fihrist/", core_views.roots_letters, name="fihrist_index"),  

   path("", include("core.urls")),
]
