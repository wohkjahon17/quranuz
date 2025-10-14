from django.db import models

class Surah(models.Model):
    index = models.PositiveSmallIntegerField(unique=True)
    number = models.PositiveIntegerField(unique=True)
    name_ar = models.CharField(max_length=100)
    name_uz = models.CharField(max_length=150, blank=True)
    ayah_count = models.PositiveIntegerField(default=7)

    name_uz = models.CharField(max_length=96, blank=True)      # Fotiha, Baqara, …
    nuzul_order = models.PositiveSmallIntegerField(null=True, blank=True)
    nuzul_place = models.CharField(max_length=10, blank=True)  # "Makkiy" / "Madaniy"
    ayat_count = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("index",)

    def __str__(self):
        return f"{self.index} — {self.name_ar}"



class Ayah(models.Model):
    surah = models.ForeignKey('core.Surah', on_delete=models.CASCADE, related_name='ayahs')
    number = models.PositiveSmallIntegerField()
    text_ar = models.TextField()
    text_uz = models.TextField(blank=True)

    class Meta:
        ordering = ['surah__number', 'number']

    def __str__(self):
        return f"{self.surah.index}:{self.number_in_surah}"

class Surah(models.Model):
    number = models.PositiveSmallIntegerField(db_column='index', unique=True)
    name_ar = models.CharField(max_length=64)
    name_uz = models.CharField(max_length=64)
    ayah_count = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['number']   # yoki siz xohlagan tartib
        db_table = 'core_surah' # agar jadval nomi custom bo'lsa


class Ayah(models.Model):
    surah = models.ForeignKey('core.Surah', on_delete=models.CASCADE, related_name='ayahs')
    number = models.PositiveSmallIntegerField()
    text_ar = models.TextField()

    class Meta:
        ordering = ['surah__number', 'number']

# --- Köklar (Ildizlar) ---
class Root(models.Model):
    root_ar = models.CharField(max_length=32, unique=True)  # masalan: "هُوَ"

    def __str__(self):
        return self.root_ar


class Lexeme(models.Model):
    root = models.ForeignKey(Root, on_delete=models.CASCADE)
    form_ar = models.CharField(max_length=64)        # so‘z shakli
    translit = models.CharField(max_length=64, blank=True)
    pos = models.CharField(max_length=32, blank=True)       # so‘z turi: Fe’l/Ism/Zam.
    gloss = models.CharField(max_length=128, blank=True)    # qisqa izoh (uz)

    class Meta:
        unique_together = ("root", "form_ar")
        ordering = ("form_ar",)

    def __str__(self):
        return f"{self.form_ar} ({self.root.root_ar})"


class Occurrence(models.Model):
    lexeme = models.ForeignKey(Lexeme, on_delete=models.CASCADE)
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    ayah_no = models.PositiveSmallIntegerField()
    token_index = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["surah", "ayah_no"])]
        ordering = ["surah", "ayah_no", "id"]  

    def __str__(self):
        return f"{self.lexeme.form_ar} @ {self.surah.index}:{self.ayah_no}"


# --- Fihrist (mavzular) ---
class Topic(models.Model):
    slug = models.SlugField(unique=True, max_length=64)
    title = models.CharField(max_length=128)

    def __str__(self):
        return self.title


class TopicVerse(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    ayah_no = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("topic", "surah", "ayah_no")
        indexes = [models.Index(fields=["surah", "ayah_no"])]
        ordering = ["surah", "ayah_no", "id"]

    def __str__(self):
        return f"{self.topic.title}: {self.surah.index}:{self.ayah_no}"
