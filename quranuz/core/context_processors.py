# core/context_processors.py
from .models import Sura  # sizdagi modelga moslang

def common(request):
    return {
        "suralar": Sura.objects.all().order_by("number"),
    }
