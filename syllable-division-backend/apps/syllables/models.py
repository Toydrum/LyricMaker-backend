from django.db import models

class Syllable(models.Model):
    word = models.CharField(max_length=255)
    syllables = models.JSONField()

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = 'Syllable'
        verbose_name_plural = 'Syllables'