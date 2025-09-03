from django.db import models

class Surah(models.Model):
    index = models.PositiveSmallIntegerField(unique=True)
    name_ar = models.CharField(max_length=64, blank=True)

    # YANGI maydonlar:
    name_uz = models.CharField(max_length=96, blank=True)      # Fotiha, Baqara, …
    nuzul_order = models.PositiveSmallIntegerField(null=True, blank=True)
    nuzul_place = models.CharField(max_length=10, blank=True)  # "Makkiy" / "Madaniy"
    ayat_count = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("index",)

    def __str__(self):
        return f"{self.index} — {self.name_ar}"



class Ayah(models.Model):
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE)
    number_in_surah = models.PositiveSmallIntegerField()
    text_ar = models.TextField()

    class Meta:
        unique_together = ("surah", "number_in_surah")
        ordering = ("surah__index", "number_in_surah")

    def __str__(self):
        return f"{self.surah.index}:{self.number_in_surah}"


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
        ordering = ("surah__index", "ayah_no")

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
        ordering = ("surah__index", "ayah_no")

    def __str__(self):
        return f"{self.topic.title}: {self.surah.index}:{self.ayah_no}"
