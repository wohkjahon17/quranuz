from datetime import datetime
try:
    # pip install hijri-converter
    from hijri_converter import convert
except Exception:
    convert = None

UZ_MONTHS = [
    "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
    "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
]
UZ_WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]

AR_MONTHS = ["محرم","صفر","ربيع الأول","ربيع الآخر","جمادى الأولى","جمادى الآخرة",
             "رجب","شعبان","رمضان","شوال","ذو القعدة","ذو الحجة"]
AR_WEEKDAYS = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]

def dates(request):
    now = datetime.now()

    # Milodiy (uz)
    g = f"{now.year} {UZ_MONTHS[now.month-1]} {now.day}, {UZ_WEEKDAYS[now.weekday()]}"

    # Hijriy (arabcha)
    if convert:
        h = convert.Gregorian(now.year, now.month, now.day).to_hijri()
        h_str = f"{h.year} {AR_MONTHS[h.month-1]} {h.day}, {AR_WEEKDAYS[now.weekday()]}"
    else:
        # kutubxona yo‘q bo‘lsa, vaqtincha bo‘sh
        h_str = "—"

    return {"greg_date_uz": g, "hijri_date_ar": h_str}
