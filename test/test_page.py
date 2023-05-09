import inject
import pytest

from paf.manager import WebDriverManager
from paf.page import PageFactory, Page
from paf.request import WebDriverRequest
from test import create_webdriver
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture
def page():
    yield inject.instance(PageFactory).create_page(Page, create_webdriver())


def test_assertions(page: Page):
    page.open("https://testpages.herokuapp.com")
    assert page.wait_for.url.be("https://testpages.herokuapp.com/styled/index.html")

    page.expect.title.be("Selenium Test Pages")
    assert page.name == "Page"
    assert str(page) == page.name
    assert page.webdriver.title == "Selenium Test Pages"


def test_create_page_from_page(page: Page):
    other_page = page._create_page(Page)
    assert isinstance(other_page, Page)
    assert page.webdriver == other_page.webdriver


def test_create_page_without_webdriver():
    page_factory = inject.instance(PageFactory)
    webdriver = create_webdriver(WebDriverRequest())
    page = page_factory.create_page(Page)
    assert page.webdriver == webdriver
    assert isinstance(page, Page)
    assert isinstance(page.webdriver, WebDriver)


def test_scroll_until_visible(page: Page):
    page.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = page._find("#p41")
    height = p.expect.bounds.actual.height
    while p.wait_for.fully_visible(False):
        page.scroll_by(y=height)

    p.expect.fully_visible(True)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
