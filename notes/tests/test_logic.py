from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreationEditDelete(TestCase):
    """Тестируем создание, удаление, редактирование заметки"""

    NOTES = {
        ('first_note'): {
            ('title'): ('Заголовок первой заметки'),
            ('text'): ('Текст первой заметки')
        },
        ('second_note'): {
            ('title'): ('Заголовок второй заметки'),
            ('text'): ('Текст второй заметки')
        },
        ('edited_note'): {
            ('title'): ('Отредактированный заголовок заметки'),
            ('text'): ('Отредактированный текст заметки')
        }
    }

    TARGET_URLS = {
        'add_page': 'notes:add',
        'edit_page': 'notes:edit',
        'delete_page': 'notes:delete',
        'success_page': 'notes:success'
    }

    FORM_WARNING = slugify(NOTES['first_note']['title']) + WARNING

    NOTE_WAS_NOT_ADDED = 1

    NOTE_WAS_ADDED = 2

    NOTE_WAS_DELETED = 0

    NOTE_WAS_NOT_DELETED = 1

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            author=cls.author,
            title=cls.NOTES['first_note']['title'],
            text=cls.NOTES['first_note']['text'],
            slug=slugify(cls.NOTES['first_note']['title'])
        )

        cls.form_data = {
            'author': cls.author,
            'title': cls.NOTES['second_note']['title'],
            'text': cls.NOTES['second_note']['text'],
            'slug': slugify(cls.NOTES['second_note']['title'])
        }
        cls.create_url = reverse(cls.TARGET_URLS['add_page'])
        cls.edit_url = reverse(cls.TARGET_URLS['edit_page'],
                               kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse(cls.TARGET_URLS['delete_page'],
                                 kwargs={'slug': cls.note.slug})
        cls.success_url = reverse(cls.TARGET_URLS['success_page'])

    def test_anonymous_user_cant_create_note(self):
        """Тестируем, что анонимный пользователь не может создать заметку"""
        self.client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTE_WAS_NOT_ADDED)

    def test_user_can_create_note(self):
        """Тестируем, что залогиненный пользователь может создать заметку"""
        self.author_client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTE_WAS_ADDED)
        note = Note.objects.last()
        self.assertEqual(note.title, self.NOTES['second_note']['title'])
        self.assertEqual(note.slug, slugify(self.NOTES['second_note']
                                            ['title']))
        self.assertEqual(note.text, self.NOTES['second_note']['text'])

    def test_slug_uniqueness(self):
        """Тестируем, что заметка с не уникальным slug не будет создана
        и сработает текст ошибки
        """
        self.form_data['slug'] = slugify(self.NOTES['first_note']['title'])
        response = self.author_client.post(self.create_url,
                                           data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.FORM_WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTE_WAS_NOT_ADDED)

    def test_author_can_delete_note(self):
        """Тестируем, что автор может удалить свою заметку
        и будет перенаправлен
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTE_WAS_DELETED)

    def test_user_cant_delete_someone_elses_note(self):
        """Тестируем, что залогиненный пользователь
        не может удалить чужую заметку
        """
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.NOTE_WAS_NOT_DELETED)
