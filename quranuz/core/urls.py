from django.urls import path
from . import views
from django.urls import path
from . import views
from core.views import roots_letters
from django.contrib import admin
from django.urls import path
from core.views import roots_letters
urlpatterns = [
    # Asosiy sahifalar
    path("", views.home, name="home"),
    path("suralar/", views.suralar, name="suralar"),
    path("fihrist/", views.fihrist, name="fihrist"),
    path("search/", views.search, name="search"),
    path("taqqoslash/", views.taqqoslash, name="taqqoslash"),

    # Ildiz (Kökler)
    path("kokler/", views.kokler_index, name="kokler"),
    path("kokler/harflar/", views.roots_letters, name="roots-letters"),
    path("kokler/<str:letter>/", views.roots_by_letter, name="roots-by-letter"),
    path("kokler/root/<path:root>/", views.kokler_root, name="kokler_root"),

    # Suralar
    path("suralar/<int:number>/", views.sura_detail, name="sura_detail"),
    path("suralar/goto/", views.sura_goto, name="sura_goto"),

    # Boshqa
    path("page-goto/", views.page_goto, name="page_goto"),
    path("satrlar/", views.satrlar, name="satrlar"),

    # Lug‘atlar
    path("lugat/el-mucem/", views.el_mucem, name="el_mucem"),
    path("lugat/el-mufredat/", views.el_mufredat, name="el_mufredat"),
]