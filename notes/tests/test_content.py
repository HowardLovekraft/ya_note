from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='Пользователь 1')
        cls.user2 = User.objects.create(username='Пользователь 2')
        cls.notes = Note.objects.bulk_create(
            Note(
                    title=f'Заметка №{i}',
                    text=f'Текст {i}{i}',
                    slug=f'note-{i}',
                    author=cls.user1
                ) for i in range(3)
        ) + Note.objects.bulk_create(
            Note(
                title=f'Заметочка №{i}',
                text=f'Текст {i}{i}',
                slug=f'note-{i}',
                author=cls.user1
            ) for i in range(4, 6)
        )

    def test_notes_order(self):
        """
        Заметки должны выводится от самой старой к самой свежой.
        (сортировка по внутреннему id)
        Самая свежая - внизу.
        """
        url = reverse('notes:list')
        self.client.force_login(self.user1)
        response = self.client.get(url)
        object_list = response.context['object_list']
        all_names = [note.title for note in object_list]
        sorted_names = [
            note.title for note in sorted(
                object_list, key=lambda note_: note_.id
            )
        ]
        self.assertEqual(all_names, sorted_names)

    def test_user_can_view_only_himself_notes(self):
        """Пользователь видит в списке только заметки, созданные им."""
        author = self.user1
        self.client.force_login(author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']

        for note in object_list:
            with self.subTest(note=note):
                self.assertEqual(note.author, author)


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Важная заметка',
            text='42!!!',
            slug='important-note',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=('important-note',))

    def test_note_detail_availability(self):
        """
        Проверяет наличие объекта модели Note в шаблоне
        детальной информации о заметке.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('note', response.context)
        self.assertIsInstance(response.context['note'], Note)
