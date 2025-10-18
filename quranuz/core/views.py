import re
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.http import Http404
from django.shortcuts import render
from django.http import HttpResponse
from .constants import ASMA_UL_HUSNA
from .constants import ARABIC_LETTERS
from .models import (
    Surah, Ayah,
    Root, Lexeme, Occurrence,
    Topic, TopicVerse
)
def home(request):
    return redirect("core:roots-letters")

def roots_letters(request, letter=None):
    return render(request, "core/kokler.html", {"letters": LETTERS, "letter": letter})

def taqqoslash(request):
    return render(request, "core/taqqoslash.html")

def search(request):
    q = request.GET.get("q", "").strip()
    return HttpResponse(f"Qidiruv (test): {q}")

def roots_by_letter(request, letter):
    if letter not in LETTERS:
        raise Http404("Noto'g'ri harf")
    return roots_letters(request, letter=letter)
try:
    from hijri_converter import convert as hijri_convert  
except Exception:
    hijri_convert = None



def _today_strings():
    """
    UI header/footer uchun bugungi sana (gregorian + hijriy).
    Hijriy konverter bo‘lmasa, faqat gregorian qaytaradi.
    """
    now = timezone.localtime()
    greg = f"{now.day} {MONTHS_UZ[now.month-1]} {now.year}"
    hijri = ""
    if hijri_convert:
        h = hijri_convert.Gregorian(now.year, now.month, now.day).to_hijri()
        hijri = f"{h.day} {HIJRI_MONTHS_UZ[h.month-1]} {h.year}"
    return greg, hijri
def roots_by_letter(request, letter):
    if letter not in ARABIC_LETTERS:
        raise Http404("Bunday harf yo‘q.")
    roots = ROOTS_BY_LETTER.get(letter, [])
    return render(request, "core/kokler.html", {
        "letters": ARABIC_LETTERS,
        "letter": letter,
        "roots": roots,
    })

def roots_letters(request):
    return kokler_index(request)


def _normalize_harf(raw):
    """
    QueryString’dan kelgan qiymatdan arabcha harfni ajratib oladi.
    Masalan: "{'ch': 'ت', 'c': 0}" -> "ت"
    """
    if not raw:
        return None
    m = re.search(r'[\u0600-\u06FF]', raw)
    return m.group(0) if m else raw


def home(request):
    """Bosh sahifa."""
    return render(request, "core/home.html")


def ayet_karsilastirma(request):
    """Oyatlarni taqqoslash — placeholder sahifa."""
    return render(request, "core/ayet_karsilastirma.html")


def satrlar(request):
    """Satrlar (satrlararo ko‘rinish) — placeholder sahifa."""
    return render(request, "core/satrlar.html")


def el_mufredat(request):
    """EL-Mufredat — placeholder sahifa."""
    return render(request, "core/el_mufredat.html")


def el_mucem(request):
    """EL-Mu‘cem EL-Mufehres — placeholder sahifa."""
    return render(request, "core/el_mucem.html")


def page_goto(request):
    """Oddiy sahifa ko‘rsatish (masalan, preview yoki statik sahifalar)."""
    p = request.GET.get("p", "1")
    return render(request, "core/page.html", {"page_no": p})

def suralar(request):
    return render(request, "core/suralar.html")

def asmaul_husna(request):
    return render(request, "core/asmaul_husna.html", {"asma": ASMA_UL_HUSNA})
def sura_goto(request):
    """
    /sura-goto/?s=2&a=3 -> sura sahifasiga yo‘naltiradi.
    s (sura raqami), a (ixtiyoriy – oyat raqami)
    """
    sura = request.GET.get("s") or request.GET.get("sura") or ""
    ayah = request.GET.get("a") or request.GET.get("ayat") or ""

    if not (sura and sura.isdigit()):
        return render(request, "core/sura_jump.html", {"error": None})

    sura_no = int(sura)
    url = reverse("sura_detail", kwargs={"index": sura_no})
    if ayah:
        url += f"?a={ayah}"
    return redirect(url)


def sura_detail(request, index: int):
    sura = get_object_or_404(Surah, number=index) 
    ayahs = Ayah.objects.filter(surah=sura).order_by("number_in_surah")
    greg, hijri = _today_strings()
    return render(request, "core/sura_detail.html", {
        "sura": sura, "ayahs": ayahs, "greg_date": greg, "hijri_date": hijri
    })



def search(request):
    q = request.GET.get("q", "").strip()
    sura_results = Surah.objects.none()
    ayah_results = Ayah.objects.none()
    if q:
        sura_results = Surah.objects.filter(name_ar__icontains=q).order_by("number")
        ayah_results = (
            Ayah.objects
            .filter(text_ar__icontains=q)
            .select_related("surah")
            .order_by("surah__number", "number_in_surah")[:100]
        )
    return render(request, "core/search.html",
                  {"q": q, "sura_results": sura_results, "ayah_results": ayah_results})

def kokler_index(request):
    return render(request, "core/kokler.html", {
        "letters": ARABIC_LETTERS,
        "letter": None,
        "roots": []
    })

def kokler_root(request, root):
    """
    Bitta kök sahifasi: shakllar (lexeme) va oyatlarda uchrashlari.
    """
    r = get_object_or_404(Root, root_ar=root)

    forms = Lexeme.objects.filter(root=r).order_by("form_ar")
    occ = (
        Occurrence.objects
        .filter(lexeme__root=r)
        .select_related("lexeme", "surah")
        .order_by("surah__number", "ayah_no") 
    )

    ctx = {
        "root": r,
        "forms": forms,
        "occ": occ,
        "total": occ.count(),
    }
    return render(request, "core/kokler_root.html", ctx)

def fihrist(request):
    return render(request, "core/fihrist.html")

def fihrist_index(request):
    """Mavzular ro‘yxati (fihrist)."""
    topics = Topic.objects.order_by("title")
    return render(request, "core/fihrist_index.html", {"topics": topics})

def fihrist_topic(request, slug):
    """Tanlangan mavzuga bog‘liq oyatlar ro‘yxati."""
    topic = get_object_or_404(Topic, slug=slug)
    verses = (
        TopicVerse.objects
        .filter(topic=topic)
        .select_related("surah")
        .order_by("surah__number", "ayah_no") 
    )
    return render(request, "core/fihrist_topic.html", {"topic": topic, "verses": verses})

