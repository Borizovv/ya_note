from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm
from notes.tests.test_data import (User, NOTES_COUNT, TARGET_URLS)


class TestListPage(TestCase):
    """Тестируем сортировку заметок по маршруту notes:list"""

    @classmethod
    def setUpTestData(cls):
        all_notes = []
        cls.author = User.objects.create(username='Автор')
        for index in range(NOTES_COUNT):
            note = Note(title=f'Заметка {index}', text='Текст заметки.',
                        author=cls.author, slug=index)
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

    def test_notes_order(self):
        """Тестируем сортировку заметок по id"""
        self.client.force_login(self.author)
        response = self.client.get(reverse(TARGET_URLS['list_page']))
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)

    def test_authorized_client_has_form(self):
        """Тестируем, что авторизированному пользователю форма доступна"""
        self.client.force_login(self.author)
        response = self.client.get(reverse(TARGET_URLS['add_page']))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
