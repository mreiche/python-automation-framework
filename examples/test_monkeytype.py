import inject
import pytest

from paf.control import change
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from test import get_webdriver


@pytest.fixture
def finder():
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage, get_webdriver())
    yield finder


def test_typespeed(finder: FinderPage):
    finder.open("https://monkeytype.com")

    input_container = finder.find("#wordsInput")
    words_container = finder.find("#words")

    active_word = words_container.find(".active")

    with change(wait_after_fail=3):
        while active_word.wait_for.displayed(True):
            word = active_word.expect.text.actual
            input_container.send_keys(word)
            input_container.send_keys(" ")


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
