from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from notes.tests.test_data import (User,
                                   PATHS_NAMES_WITHOUT_SLUG,
                                   PATHS_NAMES_WITH_SLUG
                                   )

from notes.models import Note


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

    def test_home_and_success_pages(self):
        """Тестируем доступность главной страницы и уведомления об успехе"""
        for index, name in enumerate(PATHS_NAMES_WITHOUT_SLUG):
            if name == 'notes:success':
                self.client.force_login(self.author)
            if name == 'notes:success' or name == 'notes:home':
                url = reverse(PATHS_NAMES_WITHOUT_SLUG[index])
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_with_slug(self):
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
            for name in PATHS_NAMES_WITH_SLUG:
                with self.subTest(user=user, name=name):
                    url = reverse(name, kwargs={'slug': self.note.slug})
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous_client(self):
        """Тестируем редирект анонимного пользователя
        на страницу логина по маршруту users:login
        """
        for name in PATHS_NAMES_WITHOUT_SLUG + PATHS_NAMES_WITH_SLUG:
            if name == 'notes:home' or name == 'notes:success':
                continue
            with self.subTest(name=name):
                if name in PATHS_NAMES_WITH_SLUG:
                    url = reverse(name, kwargs={'slug': self.note.slug})
                else:
                    url = reverse(name)
                redirect_url = f'{settings.LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
