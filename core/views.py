import re
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Surah, Ayah, Root, Lexeme, Occurrence, Topic, TopicVerse
import math
from django.db.models import Count
from django.db.models.functions import Substr
from django.shortcuts import render
from .models import Root 
from django.utils import timezone
from .constants import ASMA_UL_HUSNA
try:
    from hijri_converter import convert as hijri_convert  # pip install hijri-converter
except Exception:
    hijri_convert = None

AR_LETTERS = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun","iyul",
             "avgust","sentyabr","oktyabr","noyabr","dekabr"]
HIJRI_MONTHS_UZ = [
    "Muharram","Safar","Rabi‘ul-avval","Rabi‘us-soniy",
    "Jumodal-avval","Jumodal-oxir","Rajab","Sha’bon",
    "Ramazon","Shavvol","Zulqa‘da","Zulhijja"
]
def ayet_karsilastirma(request):
    """Oyatlarni taqqoslash (placeholder sahifa)."""
    return render(request, "core/ayet_karsilastirma.html")

def satrlar(request):
    """Satrlar (satrlararo ko‘rinish) — placeholder."""
    return render(request, "core/satrlar.html")

def el_mufredat(request):
    """EL-Mufredat — placeholder sahifa."""
    return render(request, "core/el_mufredat.html")

def el_mucem(request):
    """EL-Mu‘cem EL-Mufehres — placeholder sahifa."""
    return render(request, "core/el_mucem.html")
 
def asmaul_husna(request):
    return render(request, "core/asmaul_husna.html", {"asma": ASMA_UL_HUSNA})
def _today_strings():
    now = timezone.localtime()
    greg = f"{now.day} {MONTHS_UZ[now.month-1]} {now.year}"
    hijri = ""
    if hijri_convert:
        h = hijri_convert.Gregorian(now.year, now.month, now.day).to_hijri()
        hijri = f"{h.day} {HIJRI_MONTHS_UZ[h.month-1]} {h.year}"
    return greg, hijri
# Arab alifbosi (köklar filtri uchun)
    AR_LETTERS = ["ا","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش",
              "ص","ض","ط","ظ","ع","غ","ف","ق","ك","ل","م","ن","ه","و","ي"]
 
    """
    Ro‘yxatni n ta ustunga tarqatadi (1,6,11... 2,7,12... usulida),
    sahifadagi grid uchun qulay.
    """
    cols = [[] for _ in range(num_cols)]
    for i, x in enumerate(items):
        cols[i % num_cols].append(x)
    return cols
# core/views.py

def home(request):
    # Endi bu yerda harflar yo‘q — bosh sahifa toza
    return render(request, "core/home.html")


def suralar(request):
    lst = Surah.objects.all().only("index", "name_uz", "name_ar", "nuzul_order", "nuzul_place", "ayat_count")
    return render(request, "core/suras.html", {"suras": lst})


def sura_detail(request, index):
    sura = get_object_or_404(Surah, index=index)
    ayat = Ayah.objects.filter(surah=sura).order_by("number_in_surah")
    greg, hijri = _today_strings()
    return render(
        request,
        "core/sura_detail.html",   # yoki sizda qanday nom bo‘lsa, o‘shani qo‘ying
        {"sura": sura, "ayahs": ayat, "greg_date": greg, "hijri_date": hijri}
    )
def search(request):
    q = request.GET.get("q", "").strip()
    sura_results = Surah.objects.none()
    ayah_results = Ayah.objects.none()
    if q:
        sura_results = Surah.objects.filter(name_ar__icontains=q).order_by("index")
        ayah_results = (
            Ayah.objects.filter(text_ar__icontains=q)
            .select_related("surah")
            .order_by("surah__index", "number_in_surah")[:100]
        )
    return render(request, "core/search.html", {"q": q, "sura_results": sura_results, "ayah_results": ayah_results})

# --- Köklar ---
def _normalize_harf(raw):
    """QueryString'dan kelgan harfdan faqat arabcha belgini olamiz.
       Masalan: "{'ch': 'ت', 'c': 0}" -> "ت" """
    if not raw:
        return None
    m = re.search(r'[\u0600-\u06FF]', raw)
    return m.group(0) if m else raw

def kokler_index(request):
    harf_raw = request.GET.get("harf")          # foydalanuvchi bosgan narsa
    harf = _normalize_harf(harf_raw)            # faqat arabcha belgini olamiz

    roots = Root.objects.filter(root_ar__startswith=harf) if harf else []

    context = {
        "letters": AR_LETTERS,   # muqim 28 harf
        "current": harf,
        "roots": roots
    }
    return render(request, "core/kokler_index.html", context)


from django.db.models import Count
from django.db.models.functions import Substr

# Skrinshot tartibida harflar
AAR_LETTERS = ["ا","ب","ت","ث","ج","ح","خ","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ع","غ","ف","ق","ك","ل","م","ن","ه","و","ي"]



def _to_columns(objs, num_cols=6):
    """QuerySet/listni n ta ustunga taqsimlash"""
    cols = [[] for _ in range(num_cols)]
    for i, obj in enumerate(objs):
        cols[i % num_cols].append(obj)
    return cols

def kokler_index(request):
    harf = request.GET.get("harf", "")
    roots = Root.objects.filter(root_ar__startswith=harf) if harf else []

    # 7 × 2 ta ustunli bo‘lishi uchun ikkita qatorda bo‘lib beramiz
    row1 = AR_LETTERS[:14]
    row2 = AR_LETTERS[14:]

    context = {
        "letters_row1": row1,
        "letters_row2": row2,
        "current": harf,
        "roots": roots,
        "total": len(roots),
    }
    return render(request, "core/kokler_index.html", context)

def kokler_root(request, root):
    r = get_object_or_404(Root, root_ar=root)

    forms = Lexeme.objects.filter(root=r).order_by("form_ar")

    occ = (
        Occurrence.objects.filter(lexeme__root=r)
        .select_related("lexeme", "surah")
        .order_by("surah__index", "ayah_no")
    )

    ctx = {
        "root": r,
        "forms": forms,
        "occ": occ,
        "total": occ.count(),
    }
    return render(request, "core/kokler_root.html", ctx)

# --- Fihrist ---
def fihrist_index(request):
    topics = Topic.objects.order_by("title")
    return render(request, "core/fihrist_index.html", {"topics": topics})

def fihrist_topic(request, slug):
    topic = get_object_or_404(Topic, slug=slug)
    verses = (
        TopicVerse.objects.filter(topic=topic)
        .select_related("surah")
        .order_by("surah__index", "ayah_no")
    )
    return render(request, "core/fihrist_topic.html", {"topic": topic, "verses": verses})
