import inject
from selenium.webdriver.support.color import Color

from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from test import create_webdriver

page_factory: PageFactory = None


def setup_module():
    global page_factory
    page_factory = inject.instance(PageFactory)


def test_finder_page():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    assert p.name_path == 'UiElement(By.id(para1))[0]'


# def test_rect():
#     finder = page_factory.create_page(FinderPage, create_webdriver())
#     finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
#
#     p = finder.find(By.id("para1"))
#     rect = p._get_bounds()
#     assert isinstance(rect, Rect)
#     assert rect.width == 962
#     assert rect.height == 27


def test_highlight():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    p.highlight(color=Color.from_string("#0f0"))
    p.expect.css("outline").be("rgb(0, 255, 0) solid 5px")


def test_scroll_and_visible():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")

    p = finder.find(By.id("pre1").unique)
    p.expect.visible.be(False)
    p.scroll_into_view()
    p.expect.visible.be(True)
    p.expect.fully_visible.be(True)


def test_screenshot():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = finder.find(By.id("pre1").unique)
    path = p.take_screenshot()
    assert path


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
