from django.contrib.auth import get_user_model
from notes.forms import WARNING
from pytils.translit import slugify
from typing import Final, Dict, Tuple


User = get_user_model()

NOTES: Dict[str, Dict[str, str]] = {
    'first_note': {
        'title': 'Заголовок первой заметки',
        'text': 'Текст первой заметки'
    },
    'second_note': {
        'title': 'Заголовок второй заметки',
        'text': 'Текст второй заметки'
    },
    'edited_note': {
        'title': 'Отредактированный заголовок заметки',
        'text': 'Отредактированный текст заметки'
    }
}
TARGET_URLS: Dict[str, str] = {
    'add_page': 'notes:add',
    'edit_page': 'notes:edit',
    'delete_page': 'notes:delete',
    'success_page': 'notes:success',
    'list_page': 'notes:list',
}
PATHS_NAMES_WITH_SLUG: Tuple[str] = ('notes:detail', 'notes:edit',
                                     'notes:delete')
PATHS_NAMES_WITHOUT_SLUG: Tuple[str] = ('notes:add', 'notes:list',
                                        'notes:success', 'notes:home')


FORM_WARNING: str = slugify(NOTES['first_note']['title']) + WARNING
NOTE_WAS_NOT_ADDED: Final[int] = 1
NOTE_WAS_NOT_DELETED: Final[int] = 1
NOTE_WAS_ADDED: Final[int] = 2
NOTE_WAS_DELETED: Final[int] = 0
NOTES_COUNT: Final[int] = 15
