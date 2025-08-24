from http import HTTPStatus
from typing import Final

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметок')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.DEFAULT_NOTES_COUNT: int = Note.objects.count()

        cls.create_url = reverse('notes:add')
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'title': 'Название заметки',
            'text': 'Текст заметки'
        }

    def test_user_can_create_note(self):
        response = self.author_client.post(self.create_url,
                                           data=self.form_data)
        self.assertRedirects(response, self.redirect_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.DEFAULT_NOTES_COUNT+1)

    def test_anonymous_client_cant_create_note(self):
        self.client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.DEFAULT_NOTES_COUNT)


class TestNoteEditDelete(TestCase):
    
    NEW_NOTE_TITLE: Final[str] = 'Новое название заметки'
    NEW_NOTE_TEXT: Final[str] = 'Новый текст заметки'
    NOTE_SLUG: Final[str] = 'the-note'  

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметок')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Другой автор заметок')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Название заметки',
            text='Текст заметки',
            slug=cls.NOTE_SLUG,
            author=cls.author
        )
        cls.DEFAULT_NOTES_COUNT: int = Note.objects.count()

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redirect_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug  # doesn't change
        }

    def test_user_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redirect_url)

        self.note.refresh_from_db()
        self.assertEqual(self.NEW_NOTE_TITLE, self.note.title)
        self.assertEqual(self.NEW_NOTE_TEXT, self.note.text)
        self.assertEqual(self.NOTE_SLUG, self.note.slug)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.DEFAULT_NOTES_COUNT)

    def test_user_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.redirect_url)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.DEFAULT_NOTES_COUNT)
