from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),
    path('suralar/', views.suralar, name='suralar'),
    path("sura/<int:index>/", views.sura_detail, name="sura_detail"),

    path("qidiruv/", views.search, name="search"),

    path("kokler/", views.kokler_index, name="kokler"),
    path("kokler/<str:root>/", views.kokler_root, name="kokler_root"),

    path("fihrist/", views.fihrist_index, name="fihrist"),
    path("fihrist/<slug:slug>/", views.fihrist_topic, name="fihrist_topic"),

    path("taqqoslash/", views.ayet_karsilastirma, name="taqqoslash"),   
    path("satrlar/", views.satrlar, name="satrlar"),                    
    path("el-mufredat/", views.el_mufredat, name="el_mufredat"),       
    path("el-mucem/", views.el_mucem, name="el_mucem"),   
    path("asmaul-husna/", views.asmaul_husna, name="asmaul_husna"),
]
