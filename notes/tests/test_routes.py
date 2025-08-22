from http import HTTPStatus
from typing import Any, TypeAlias

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()
# Tuple of pairs 'route - args'
URLs: TypeAlias = tuple[tuple[str, tuple[Any] | None], ...]
UserStatusPairs: TypeAlias = tuple[tuple[type[AbstractUser], HTTPStatus]]


class TestRoutes(TestCase):
    """Тесты маршрутов на сайте."""

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
        """
        Домашняя страница и страницы аутентификации доступны
        анонимному клиенту.
        """
        urls: URLs = (
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
        """
        Список заметок и подробности о заметке доступны
        зарегистрированнному автору заметки.
        """
        urls: URLs = (
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
        )

        self.client.force_login(self.author)

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """
        Со списка заметок, с конкретной заметки и со страниц
        редактирования/удаления конкретной заметки анонимный клиент
        редиректится на страницу логина.
        """
        login_url = reverse('users:login')
        urls: URLs = (
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for name, args in urls:
            url = reverse(name, args=args)
            redirect_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, redirect_url)

    def test_availability_for_note_edit_and_delete(self):
        """
        Редактирование и удаление заметки доступны только автору заметки.
        """
        users_statuses: UserStatusPairs = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls: URLs = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for user, status in users_statuses:
            self.client.force_login(user)

            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
