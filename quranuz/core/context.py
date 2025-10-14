from django.utils import timezone
from .constants import ASMA_UL_HUSNA
try:
    from hijri_converter import convert as hijri_convert
except Exception:
    hijri_convert = None

MONTHS_UZ = [
    "yanvar","fevral","mart","aprel","may","iyun",
    "iyul","avgust","sentyabr","oktyabr","noyabr","dekabr"
]
WEEKDAYS_UZ = [
    "Dushanba","Seshanba","Chorshanba","Payshanba","Juma","Shanba","Yakshanba"
]
HIJRI_MONTHS_UZ = [
    "Muharram","Safar","Rabi‘ul-avval","Rabi‘us-soniy",
    "Jumodal-avval","Jumodal-oxir","Rajab","Sha’bon",
    "Ramazon","Shavvol","Zulqa‘da","Zulhijja"
]

def dates(request):
    now = timezone.localtime()  
   
    greg_date_uz = f"{now.year} {MONTHS_UZ[now.month-1].capitalize()} {now.day}, {WEEKDAYS_UZ[now.weekday()]}"
    greg_time_uz = now.strftime("%H:%M:%S")

    hijri_date_ar = ""
    if hijri_convert:
        h = hijri_convert.Gregorian(now.year, now.month, now.day).to_hijri()
        hijri_date_ar = f"{h.year} {HIJRI_MONTHS_UZ[h.month-1]} {h.day}"

    return {
        "greg_date_uz": greg_date_uz,
        "greg_time_uz": greg_time_uz,
        "hijri_date_ar": hijri_date_ar,
         "asmaul_husna": ASMA_UL_HUSNA,
    }
