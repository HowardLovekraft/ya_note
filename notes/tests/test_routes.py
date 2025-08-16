from http import HTTPStatus
import unittest

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Ноунейм')
        cls.note = Note.objects.create(
            title='Очень важно!',
            text='Важный текст',
            slug='important',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_availability_for_notes_view(self):
        urls = (
            ('notes:list', None),
            ('notes:detail', (self.note.objects.id,)),
        )
        