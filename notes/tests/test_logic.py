from http import HTTPStatus


from notes.tests.test_data import (User, NOTES, TARGET_URLS,
                                   NOTE_WAS_NOT_DELETED, NOTE_WAS_ADDED,
                                   NOTE_WAS_DELETED, NOTE_WAS_NOT_ADDED,
                                   FORM_WARNING)
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from pytils.translit import slugify


class TestNoteCreationEditDelete(TestCase):
    """Тестируем создание, удаление, редактирование заметки"""

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
            title=NOTES['first_note']['title'],
            text=NOTES['first_note']['text'],
            slug=slugify(NOTES['first_note']['title'])
        )

        cls.form_data = {
            'author': cls.author,
            'title': NOTES['second_note']['title'],
            'text': NOTES['second_note']['text'],
            'slug': slugify(NOTES['second_note']['title'])
        }
        cls.create_url = reverse(TARGET_URLS['add_page'])
        cls.edit_url = reverse(TARGET_URLS['edit_page'],
                               kwargs={'slug': cls.note.slug})
        cls.delete_url = reverse(TARGET_URLS['delete_page'],
                                 kwargs={'slug': cls.note.slug})
        cls.success_url = reverse(TARGET_URLS['success_page'])

    def notes_count(self):
        """Считаем количество заметок"""
        return Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        """Тестируем, что анонимный пользователь не может создать заметку"""
        self.client.post(self.create_url, data=self.form_data)
        self.assertEqual(self.notes_count(), NOTE_WAS_NOT_ADDED)

    def test_user_can_create_note(self):
        """Тестируем, что залогиненный пользователь может создать заметку"""
        self.author_client.post(self.create_url, data=self.form_data)
        self.assertEqual(self.notes_count(), NOTE_WAS_ADDED)
        note = Note.objects.last()
        self.assertEqual(note.title, NOTES['second_note']['title'])
        self.assertEqual(note.slug, slugify(NOTES['second_note']
                                            ['title']))
        self.assertEqual(note.text, NOTES['second_note']['text'])

    def test_slug_uniqueness(self):
        """Тестируем, что заметка с не уникальным slug не будет создана
        и сработает текст ошибки
        """
        self.form_data['slug'] = slugify(NOTES['first_note']['title'])
        response = self.author_client.post(self.create_url,
                                           data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=FORM_WARNING
        )
        self.assertEqual(self.notes_count(), NOTE_WAS_NOT_ADDED)

    def test_author_can_delete_note(self):
        """Тестируем, что автор может удалить свою заметку
        и будет перенаправлен
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(self.notes_count(), NOTE_WAS_DELETED)

    def test_user_cant_delete_someone_elses_note(self):
        """Тестируем, что залогиненный пользователь
        не может удалить чужую заметку
        """
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.notes_count(), NOTE_WAS_NOT_DELETED)

    def test_author_can_edit_note(self):
        """Тестируем, что автор может редактировать свою заметку"""
        self.form_data['title'] = NOTES['edited_note']['title']
        self.form_data['text'] = NOTES['edited_note']['text']
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTES['edited_note']['title'])
        self.assertEqual(self.note.text, NOTES['edited_note']['text'])

    def test_user_cant_edit_someone_elses_note(self):
        """Тестируем, что залогиненный пользователь
        не может редактировать чужую заметку
        """
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
