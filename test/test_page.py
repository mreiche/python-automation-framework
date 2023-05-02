import inject
import pytest

from paf.manager import WebDriverManager
from paf.page import PageFactory, Page


@pytest.fixture
def page():
    yield inject.instance(PageFactory).create_page(Page)


def test_assertions(page: Page):
    page.open("https://testpages.herokuapp.com")
    assert page.wait_for.url.be("https://testpages.herokuapp.com/styled/index.html")

    page.expect.title.be("Selenium Test Pages")
    assert page.webdriver.title == "Selenium Test Pages"


def test_create_page(page: Page):
    other_page = page._create_page(Page)
    assert isinstance(other_page, Page)
    assert page.webdriver == other_page.webdriver


def test_scroll_until_visible(page: Page):
    page.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = page._find("#p41")
    height = p.expect.bounds.actual.height
    while p.wait_for.fully_visible.be(False):
        page.scroll_by(y=height)

    p.expect.fully_visible.be(True)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
