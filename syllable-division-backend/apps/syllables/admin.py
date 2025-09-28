from django.contrib import admin
from .models import Syllable

@admin.register(Syllable)
class SyllableAdmin(admin.ModelAdmin):
    
    list_display = ("id", "word", "syllables_count")
    search_fields = ("word",)

    def syllables_count(self, obj):
        data = getattr(obj, "syllables", None)
        return len(data) if isinstance(data, (list, tuple)) else 0
    syllables_count.short_description = "Syllables"
   