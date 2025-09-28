from rest_framework import serializers
from .models import Syllable

class SyllableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllable
        fields = '__all__'