from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from typing import Tuple

from notes.models import Note

User = get_user_model()
paths_names_with_slug: Tuple[str] = ('notes:detail', 'notes:edit',
                                     'notes:delete')
paths_names_without_slug: Tuple[str] = ('notes:add', 'notes:list',
                                        'notes:success', 'notes:home')


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        """Готовим объекты для тестов"""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст',
        )

    def test_home_and_success_pages(self) -> None:
        """Тестируем доступность главной страницы и уведомления об успехе"""
        for index, name in enumerate(paths_names_without_slug):
            if name == 'notes:success':
                self.client.force_login(self.author)
            if name == 'notes:success' or name == 'notes:home':
                url = reverse(paths_names_without_slug[index])
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_with_slug(self) -> None:
        """Тестируем доступность маршрутов для автора/не автора заметки:
        'notes:detail',
        'notes:edit',
        'notes:delete'
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in paths_names_with_slug:
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous_client(self) -> None:
        """Тестируем редирект анонимного пользователя
        на страницу логина по маршруту users:login
        """
        for name in paths_names_without_slug + paths_names_with_slug:
            if name == 'notes:home' or name == 'notes:success':
                continue
            with self.subTest(name=name):
                if name in paths_names_with_slug:
                    url = reverse(name, kwargs={'slug': self.note.slug})
                else:
                    url = reverse(name)
                redirect_url = f'{settings.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
