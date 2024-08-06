from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

NOTES_COUNT = 15
User = get_user_model()
TARGET_URLS = {
    ('list_page'): (reverse('notes:list')),
    ('add_page'): (reverse('notes:add'))
}


class TestListPage(TestCase):
    """Тестируем сортировку заметок на странице notes:list"""

    @classmethod
    def setUpTestData(cls) -> None:
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
        response = self.client.get(TARGET_URLS.get('list_page'))
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)


class TestAddPage(TestListPage):
    """Тестируем отрисовку формы маршруту notes:add."""

    def test_authorized_client_has_form(self):
        """Тестируем, что авторизированному пользователю форма доступна"""
        self.client.force_login(self.author)
        response = self.client.get(TARGET_URLS.get('add_page'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
