from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("page/", views.page_goto, name="page_goto"),

    # Suralar / oyatlar
    path("suralar/", views.suralar, name="suralar"),
    path("sura/<int:index>/", views.sura_detail, name="sura_detail"),
    path("sura-goto/", views.sura_goto, name="sura_goto"),

    # Qidiruv
    path("search/", views.search, name="search"),

    # Koklar (lug‘at)
    path("kokler/", views.kokler_index, name="kokler_index"),
    path("kokler/<str:root>/", views.kokler_root, name="kokler_root"),

    # Fihrist
    path("fihrist/", views.fihrist_index, name="fihrist_index"),
    path("fihrist/<slug:slug>/", views.fihrist_topic, name="fihrist_topic"),

    # Boshqa sahifalar
    path("taqqoslash/", views.ayet_karsilastirma, name="taqqoslash"),
    path("satrlar/", views.satrlar, name="satrlar"),
    path("el-mufredat/", views.el_mufredat, name="el_mufredat"),
    path("el-mucem/", views.el_mucem, name="el_mucem"),
]
