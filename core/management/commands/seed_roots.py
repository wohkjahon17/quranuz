from django.core.management.base import BaseCommand
from core.models import Root

DATA = {
    "ص": [
        "صبر","صدق","صرخ","صعد","صفح","صحب","صرم","صرع","صرف","صقل",
        "صلب","صلح","صلو","صوم","صور","صيح","صوت","صيغ","صيد","صحا",
        "صحو","صدد","صدم","صنع","صهر","صوب","صوب","صوب","صحف","صغر"
    ],
    # xohlasangiz boshqa harflarni ham qo‘shasiz:
    # "س": ["سبح","سجد",...],
    # ...
}

class Command(BaseCommand):
    help = "Seed initial Arabic triliteral roots (Root.root_ar)"

    def add_arguments(self, parser):
        parser.add_argument("--letter", help="Only this letter (e.g. ص)")

    def handle(self, *args, **opts):
        only = opts.get("letter")
        total = 0
        for ch, roots in DATA.items():
            if only and ch != only:
                continue
            for r in roots:
                obj, created = Root.objects.get_or_create(root_ar=r)
                if created:
                    total += 1
        self.stdout.write(self.style.SUCCESS(f"Done. Inserted: {total}"))
