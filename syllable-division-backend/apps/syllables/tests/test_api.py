from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Syllable

class SyllableAPITests(APITestCase):
    def setUp(self):
        self.syllable_data = {
            'word': 'example',
            'syllables': ['ex', 'am', 'ple']
        }
        self.syllable = Syllable.objects.create(**self.syllable_data)

    def test_create_syllable(self):
        response = self.client.post(reverse('syllable-list'), self.syllable_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Syllable.objects.count(), 2)

    def test_get_syllable(self):
        response = self.client.get(reverse('syllable-detail', args=[self.syllable.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['word'], self.syllable.word)

    def test_update_syllable(self):
        updated_data = {'word': 'updated_example', 'syllables': ['up', 'dat', 'ed', 'ex', 'am', 'ple']}
        response = self.client.put(reverse('syllable-detail', args=[self.syllable.id]), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.syllable.refresh_from_db()
        self.assertEqual(self.syllable.word, 'updated_example')

    def test_delete_syllable(self):
        response = self.client.delete(reverse('syllable-detail', args=[self.syllable.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Syllable.objects.count(), 0)