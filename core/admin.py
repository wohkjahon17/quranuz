from django.contrib import admin
from .models import Surah, Ayah, Root, Lexeme, Occurrence, Topic, TopicVerse

admin.site.register(Surah)
admin.site.register(Ayah)
admin.site.register(Root)
admin.site.register(Lexeme)
admin.site.register(Occurrence)
admin.site.register(Topic)
admin.site.register(TopicVerse)
