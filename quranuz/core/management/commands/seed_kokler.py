from django.core.management.base import BaseCommand
from core.models import Surah, Root, Lexeme, Occurrence

class Command(BaseCommand):
    help = "Köklar uchun namunaviy ma'lumotlarni kiritadi (root=هُوَ)."

    def handle(self, *args, **kwargs):
        # Suralar (agar yo‘q bo‘lsa) — 1 va 2
        s1, _ = Surah.objects.get_or_create(index=1, defaults={"name_ar": "الفاتحة"})
        s2, _ = Surah.objects.get_or_create(index=2, defaults={"name_ar": "البقرة"})

        r, _ = Root.objects.get_or_create(root_ar="هُوَ")
        lex, _ = Lexeme.objects.get_or_create(
            root=r, form_ar="هُوَ",
            defaults={"translit": "huve", "pos": "Zam.", "gloss": "u (u/он)"},
        )

        # Ba'zi uchrashuvlar (Bakara oyatlari misol tariqasida)
        data = [(s2, 29), (s2, 37), (s2, 54), (s2, 61), (s2, 85), (s2, 91), (s2, 96), (s2, 112)]
        cnt = 0
        for sura, ay in data:
            Occurrence.objects.get_or_create(lexeme=lex, surah=sura, ayah_no=ay)
            cnt += 1

        self.stdout.write(self.style.SUCCESS(f"Seed done. Root={r.root_ar}, occurrences added: {cnt}"))
