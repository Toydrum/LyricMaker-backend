from django.urls import path
from .views import divide_syllables, split_text, split_and_syllabify

urlpatterns = [
    path("divide/", divide_syllables, name="divide_syllables"),
    path("split/", split_text, name="split_text"),
    path("split-syllables/", split_and_syllabify, name="split_and_syllabify"),
]