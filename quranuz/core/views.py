import re
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse

from .models import (
    Surah, Ayah,
    Root, Lexeme, Occurrence,
    Topic, TopicVerse
)

# --- Ixtiyoriy: Hijriy sana (o‘rnatilmagan bo‘lsa, jim ishlaydi)
try:
    from hijri_converter import convert as hijri_convert  # pip install hijri-converter
except Exception:
    hijri_convert = None


AR_LETTERS = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")

MONTHS_UZ = [
    "yanvar","fevral","mart","aprel","may","iyun",
    "iyul","avgust","sentyabr","oktyabr","noyabr","dekabr"
]
HIJRI_MONTHS_UZ = [
    "Muharram","Safar","Rabi‘ul-avval","Rabi‘us-soniy",
    "Jumodal-avval","Jumodal-oxir","Rajab","Sha’bon",
    "Ramazon","Shavvol","Zulqa‘da","Zulhijja"
]

# ----------------------- Kichik yordamchilar -----------------------

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


def _normalize_harf(raw):
    """
    QueryString’dan kelgan qiymatdan arabcha harfni ajratib oladi.
    Masalan: "{'ch': 'ت', 'c': 0}" -> "ت"
    """
    if not raw:
        return None
    m = re.search(r'[\u0600-\u06FF]', raw)
    return m.group(0) if m else raw


# ----------------------- Oddiy sahifalar -----------------------

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


# ----------------------- Suralar / Oyatlar -----------------------

def suralar(request):
    return render(request, "core/suralar.html")


def sura_goto(request):
    """
    /sura-goto/?s=2&a=3 -> sura sahifasiga yo‘naltiradi.
    s (sura raqami), a (ixtiyoriy – oyat raqami)
    """
    sura = request.GET.get("s") or request.GET.get("sura") or ""
    ayah = request.GET.get("a") or request.GET.get("ayat") or ""

    if not (sura and sura.isdigit()):
        # Form ko‘rinishi (xato bo‘lmasa ham oddiy sahifa ko‘rsatish mumkin)
        return render(request, "core/sura_jump.html", {"error": None})

    sura_no = int(sura)
    url = reverse("sura_detail", kwargs={"index": sura_no})
    if ayah:
        url += f"?a={ayah}"
    return redirect(url)


def sura_detail(request, index: int):
    sura = get_object_or_404(Surah, number=index)  # index emas, number
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




# ----------------------- Köklar (Lugat) -----------------------

def kokler_index(request):
    """
    Köklar ko‘rsatkichi:
      - 28 ta harf ikki qatorga bo‘linadi (UI uchun qulay)
      - ?harf=ب bo‘lsa, shu harf bilan boshlanuvchi köklar chiqadi
    """
    harf_raw = request.GET.get("harf", "")
    harf = _normalize_harf(harf_raw)

    roots = Root.objects.filter(root_ar__startswith=harf) if harf else []

    context = {
        "letters_row1": AR_LETTERS[:14],
        "letters_row2": AR_LETTERS[14:],
        "current": harf,
        "roots": roots,
        "total": len(roots) if hasattr(roots, "__len__") else roots.count(),
    }
    return render(request, "core/kokler_index.html", context)


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
        .order_by("surah__number", "ayah_no")   # <-- shu yer muhim
    )

    ctx = {
        "root": r,
        "forms": forms,
        "occ": occ,
        "total": occ.count(),
    }
    return render(request, "core/kokler_root.html", ctx)



# ----------------------- Fihrist (Mavzular) -----------------------

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
        .order_by("surah__number", "ayah_no")   # <-- shu yer muhim
    )
    return render(request, "core/fihrist_topic.html", {"topic": topic, "verses": verses})

