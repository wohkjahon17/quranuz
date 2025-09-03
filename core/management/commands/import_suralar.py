# core/management/commands/import_suralar.py
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Surah

# 114 ta sura uchun OZBEKCHA LOTIN nomlari (index tartibida)
UZ_NAMES = [
    "Fotiha","Baqara","Oli Imron","Niso","Moida","An’om","A’rof","Anfol","Tavba","Yunus",
    "Hud","Yusuf","Ra’d","Ibrohim","Hijr","Nahl","Isro","Kahf","Maryam","Toha",
    "Anbiyo","Haj","Mo’minun","Nur","Furqon","Shuaro","Naml","Qasas","Ankabut","Rum",
    "Luqmon","Sajda","Ahzob","Saba","Fotir","Yosin","Soffat","Sod","Zumar","G‘ofir (Mo‘min)",
    "Fussilat","Shuro","Zuxruf","Duxon","Josiya","Ahqof","Muhammad","Fath","Hujurot","Qof",
    "Zoriyot","Tur","Najm","Qamar","Rahmon","Voqea","Hadid","Mujodala","Hashr","Mumtahana",
    "Saff","Juma","Munofiqun","Tag‘obun","Taloq","Tahrim","Mulk","Qalam","Hoqqa","Ma’orij",
    "Nuh","Jinn","Muzzammil","Muddassir","Qiyomat","Insan (Dahr)","Mursalat","Naba","Nazi‘at","Abasa",
    "Takvir","Infitor","Mutaffifun","Inshiqoq","Buruj","Toriq","A‘lo","G‘oshiya","Fajr","Balad",
    "Shams","Layl","Duho","Inshiroh","Tin","Alaq","Qadr","Bayyina","Zilzol","Odiyat",
    "Qori‘a","Takosur","Asr","Humaza","Fil","Quraysh","Mo‘un","Kavsar","Kofirun","Nasr",
    "Lahab (Masad)","Ixlos","Falaq","Nos"
]

# Siz yuborgan matn (Diyanet jadvali) — to‘liq 114 qatordan iborat:
RAW_TR = """
Fâtiha Suresi / سُورَةُ الفَاتِحَة  	1	5-Mekkî	7
Bakara Suresi / سُورَةُ البَقَرَة  	2	87-Medenî	286
Âl-i İmrân Suresi / سُورَةُ آل عِمرَان  	3	89-Medenî	200
Nisâ Suresi / سُورَةُ النِّسَاء  	4	92-Medenî	176
Mâide Suresi / سُورَةُ المَائدة  	5	112-Medenî	120
En’âm Suresi / سُورَةُ الاٴنعَام  	6	55-Mekkî	165
A’râf Suresi / سُورَةُ الاٴعرَاف  	7	39-Mekkî	206
Enfâl Suresi / سُورَةُ الاٴنفَال  	8	88-Medenî	75
Tevbe Suresi / سُورَةُ التّوبَة  	9	113-Medenî	129
Yûnus Suresi / سُورَةُ يُونس  	10	51-Mekkî	109
Hûd Suresi / سُورَةُ هُود  	11	52-Mekkî	123
Yûsuf Suresi / سُورَةُ يُوسُف  	12	53-Mekkî	111
Ra’d Suresi / سُورَةُ الرّعد  	13	96-Mekkî	43
İbrahim Suresi / سُورَةُ إبراهيم  	14	72-Mekkî	52
Hicr Suresi / سُورَةُ الحِجر  	15	54-Mekkî	99
Nahl Suresi / سُورَةُ النّحل  	16	70-Mekkî	128
İsrâ Suresi / سُورَةُ بنى اسرآئيل / الإسرَاء  	17	50-Mekkî	111
Kehf Suresi / سُورَةُ الكهف  	18	69-Mekkî	110
Meryem Suresi / سُورَةُ مَريَم  	19	44-Mekkî	98
Tâ-Hâ Suresi / سُورَةُ طٰه  	20	45-Mekkî	135
Enbiyâ Suresi / سُورَةُ الاٴنبياء  	21	73-Mekkî	112
Hac Suresi / سُورَةُ الحَجّ  	22	103-Medenî	78
Mü’minûn Suresi / سُورَةُ المؤمنون  	23	74-Mekkî	118
Nûr Suresi / سُورَةُ النُّور  	24	102-Medenî	64
Furkân Suresi / سُورَةُ الفُرقان  	25	42-Mekkî	77
Şu’arâ Suresi / سُورَةُ الشُّعَرَاء  	26	47-Mekkî	227
Neml Suresi / سُورَةُ النَّمل  	27	48-Mekkî	93
Kasas Suresi / سُورَةُ القَصَص  	28	49-Mekkî	88
Ankebût Suresi / سُورَةُ العَنكبوت  	29	85-Mekkî	69
Rûm Suresi / سُورَةُ الرُّوم  	30	84-Mekkî	60
Lokman Suresi / سُورَةُ لقمَان  	31	57-Mekkî	34
Secde Suresi / سُورَةُ السَّجدَة  	32	75-Mekkî	30
Ahzâb Suresi / سُورَةُ الاٴحزَاب  	33	90-Medenî	73
Sebe’ Suresi / سُورَةُ سَبَإ  	34	58-Mekkî	54
Fâtır Suresi / سُورَةُ فَاطِر  	35	43-Mekkî	45
Yâsîn Suresi / سُورَةُ يسٓ  	36	41-Mekkî	83
Sâffât Suresi / سُورَةُ الصَّافات  	37	56-Mekkî	182
Sâd Suresi / سُورَةُ صٓ  	38	38-Mekkî	88
Zümer Suresi / سُورَةُ الزُّمَر  	39	59-Mekkî	75
Mü’min Suresi / سُورَةُ مؤمن / غَافر  	40	60-Mekkî	85
Fussilet Suresi / سُورَةُ حٰمٓ السجدة / فُصّلَت  	41	61-Mekkî	54
Şûrâ Suresi / سُورَةُ الشّورى  	42	62-Mekkî	53
Zuhruf Suresi / سُورَةُ الزّخرُف  	43	63-Mekkî	89
Duhân Suresi / سُورَةُ الدّخان  	44	64-Mekkî	59
Câsiye Suresi / سُورَةُ الجَاثية  	45	65-Mekkî	37
Ahkâf Suresi / سُورَةُ الاٴحقاف  	46	66-Mekkî	35
Muhammed Suresi / سُورَةُ محَمَّد  	47	95-Medenî	38
Fetih Suresi / سُورَةُ الفَتْح  	48	111-Medenî	29
Hucurât Suresi / سُورَةُ الحُجرَات  	49	106-Medenî	18
Kâf Suresi / سُورَةُ قٓ  	50	34-Mekkî	45
Zâriyât Suresi / سُورَةُ الذّاريَات  	51	67-Mekkî	60
Tûr Suresi / سُورَةُ الطُّور  	52	76-Mekkî	49
Necm Suresi / سُورَةُ النّجْم  	53	23-Mekkî	62
Kamer Suresi / سُورَةُ القَمَر  	54	37-Mekkî	55
Rahmân Suresi / سُورَةُ الرَّحمٰن  	55	97-Mekkî	78
Vâkı’a Suresi / سُورَةُ الواقِعَة  	56	46-Mekkî	96
Hadîd Suresi / سُورَةُ الحَديد  	57	94-Medenî	29
Mücâdele Suresi / سُورَةُ المجَادلة  	58	105-Medenî	22
Haşr Suresi / سُورَةُ الحَشر  	59	101-Medenî	24
Mümtehine Suresi / سُورَةُ المُمتَحنَة  	60	91-Medenî	13
Saff Suresi / سُورَةُ الصَّف  	61	109-Medenî	14
Cum’a Suresi / سُورَةُ الجُمُعَة  	62	110-Medenî	11
Münâfikûn Suresi / سُورَةُ المنَافِقون  	63	104-Medenî	11
Teğâbun Suresi / سُورَةُ التّغَابُن  	64	108-Medenî	18
Talâk Suresi / سُورَةُ الطّلاَق  	65	99-Medenî	12
Tahrîm Suresi / سُورَةُ التّحْريم  	66	107-Medenî	12
Mülk Suresi / سُورَةُ المُلك  	67	77-Mekkî	30
Kalem Suresi / سُورَةُ القَلَم  	68	2-Mekkî	52
Hâkka Suresi / سُورَةُ الحَاقَّة  	69	78-Mekkî	52
Me’âric Suresi / سُورَةُ المعَارج  	70	79-Mekkî	44
Nûh Suresi / سُورَةُ نُوح  	71	71-Mekkî	28
Cin Suresi / سُورَةُ الجنّ  	72	40-Mekkî	28
Müzzemmil Suresi / سُورَةُ المُزمّل  	73	3-Mekkî	20
Müddessir Suresi / سُورَةُ المدَّثِّر  	74	4-Mekkî	56
Kıyâme Suresi / سُورَةُ القِيامَة  	75	31-Mekkî	40
İnsan Suresi / سُورَةُ دهر / الإنسَان  	76	98-Medenî	31
Mürselât Suresi / سُورَةُ المُرسَلات  	77	33-Mekkî	50
Nebe’ Suresi / سُورَةُ النّبَإِ  	78	80-Mekkî	40
Nâzi’ât Suresi / سُورَةُ النَّازعَات  	79	81-Mekkî	46
Abese Suresi / سُورَةُ عَبَسَ  	80	24-Mekkî	42
Tekvîr Suresi / سُورَةُ التّكوير  	81	7-Mekkî	29
İnfitâr Suresi / سُورَةُ الانفِطار  	82	82-Mekkî	19
Mutaffifîn Suresi / سُورَةُ المطفّفِين  	83	86-Mekkî	36
İnşikâk Suresi / سُورَةُ الانشقاق  	84	83-Mekkî	25
Bürûc Suresi / سُورَةُ البُرُوج  	85	27-Mekkî	22
Târık Suresi / سُورَةُ الطّارق  	86	36-Mekkî	17
A’lâ Suresi / سُورَةُ الاٴعلى  	87	8-Mekkî	19
Gâşiye Suresi / سُورَةُ الغَاشِية  	88	68-Mekkî	26
Fecr Suresi / سُورَةُ الفَجر  	89	10-Mekkî	30
Beled Suresi / سُورَةُ البَلَد  	90	35-Mekkî	20
Şems Suresi / سُورَةُ الشّمس  	91	26-Mekkî	15
Leyl Suresi / سُورَةُ الليْل  	92	9-Mekkî	21
Duhâ Suresi / سُورَةُ الضّحى  	93	11-Mekkî	11
İnşirâh Suresi / سُورَةُ الْاِنْشِرَاحِ  	94	12-Mekkî	8
Tîn Suresi / سُورَةُ التِّين  	95	28-Mekkî	8
Alak Suresi / سُورَةُ العَلق  	96	1-Mekkî	19
Kadr Suresi / سُورَةُ القَدر  	97	25-Mekkî	5
Beyyine Suresi / سُورَةُ البَيِّنَة  	98	100-Medenî	8
Zilzâl Suresi / سُورَةُ الزّلزَلة  	99	93-Medenî	8
Âdiyât Suresi / سُورَةُ العَاديَات  	100	14-Mekkî	11
Kâri’a Suresi / سُورَةُ القَارعَة  	101	30-Mekkî	11
Tekâsür Suresi / سُورَةُ التّكاثُر  	102	16-Mekkî	8
Asr Suresi / سُورَةُ العَصر  	103	13-Mekkî	3
Hümeze Suresi / سُورَةُ الهُمَزة  	104	32-Mekkî	9
Fil Suresi / سُورَةُ الفِيل  	105	19-Mekkî	5
Kureyş Suresi / سُورَةُ القُرَيش  	106	29-Mekkî	4
Mâ’ûn Suresi / سُورَةُ المَاعون  	107	17-Mekkî	7
Kevser Suresi / سُورَةُ الكَوثَر  	108	15-Mekkî	3
Kâfirûn Suresi / سُورَةُ الكافِرون  	109	18-Mekkî	6
Nasr Suresi / سُورَةُ النّصر  	110	114-Medenî	3
Tebbet Suresi / سُورَةُ لهب / المَسَد  	111	6-Mekkî	5
İhlâs Suresi / سُورَةُ الإخلاص  	112	22-Mekkî	4
Felâk Suresi / سُورَةُ الفَلَق  	113	20-Medenî	5
Nâs Suresi / سُورَةُ النَّاس  	114	21-Medenî	6
""".strip()

LINE_RE = re.compile(
    r"""^
    (?P<title>.+?)              # "Fâtiha Suresi / سُورَةُ ..."
    \s+ (?P<index>\d{1,3})      # Qur'on tartibi
    \s+ (?P<nuzul>\d{1,3})-(?P<place>Mekkî|Medenî)
    \s+ (?P<ayat>\d{1,3})
    $""", re.X
)

def _place_tr_to_uz(p: str) -> str:
    return "Makkiy" if "Mekk" in p else "Madaniy"

class Command(BaseCommand):
    help = "Import suralar from embedded Turkish table + Uzbek names"

    def add_arguments(self, parser):
        parser.add_argument("--wipe", action="store_true", help="Oldingi Surah yozuvlarini o‘chirish")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["wipe"]:
            Surah.objects.all().delete()

        created, updated = 0, 0
        for line in RAW_TR.splitlines():
            line = line.strip()
            if not line or line.startswith("NOT"):
                continue
            m = LINE_RE.match(line)
            if not m:
                raise SystemExit(f"Parse xatosi: {line}")

            idx = int(m.group("index"))
            nuzul_order = int(m.group("nuzul"))
            nuzul_place = _place_tr_to_uz(m.group("place"))
            ayat = int(m.group("ayat"))

            title = m.group("title")
            # "Latin / Arabic[/Arabic2/...]" -> Arabic oxirgi bo'lim
            if " / " in title:
                arabic = title.split("/")[-1].strip()
            else:
                arabic = title.strip()

            defaults = {
                "name_ar": arabic,
                "name_uz": UZ_NAMES[idx-1] if 1 <= idx <= 114 else "",
                "nuzul_order": nuzul_order,
                "nuzul_place": nuzul_place,
                "ayat_count": ayat,
            }

            obj, is_created = Surah.objects.update_or_create(index=idx, defaults=defaults)
            created += int(is_created)
            updated += int(not is_created)

        self.stdout.write(self.style.SUCCESS(f"OK — yangi: {created}, yangilangan: {updated}"))
