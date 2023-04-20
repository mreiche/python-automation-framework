import threading

import inject
import pytest
from selenium.webdriver.support.color import Color

import paf.config
from paf.common import Size, Rect
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.request import WebDriverRequest


page_factory: PageFactory = None

def setup_module():
    global page_factory
    inject.configure(paf.config.inject)
    page_factory = inject.instance(PageFactory)


def create_webdriver():
    manager = inject.instance(WebDriverManager)
    request = WebDriverRequest(f"{__name__}{threading.get_ident()}")
    request.browser = "chrome"
    request.window_size = Size(1920, 1080)
    return manager.get_webdriver(request)


def test_finder_page():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    assert p.name_path == 'UiElement(By.id(para1))[0]'


def test_rect():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    rect = p._get_bounds()
    assert isinstance(rect, Rect)
    assert rect.width == 962
    assert rect.height == 27


def test_highlight():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    p.highlight(color=Color.from_string("#0f0"))
    p.expect.css("outline").be("rgb(0, 255, 0) solid 5px")


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
