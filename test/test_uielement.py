import inject
from selenium.webdriver.support.color import Color

from paf.control import Control
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.xpath import XPath
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

def test_assertions():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find("#para1")

    p.expect.tag_name.be("p")

    text = p.expect.text
    text.be("A paragraph of text")
    text.contains("paragraph").be(True)
    text.has_words("paragraph", "text").be(True)
    text.matches("hello").be(False)

    length = p.expect.text.length
    length.be(19)
    length.greater_than(1).be(True)
    length.greater_equal_than(10).be(True)
    length.lower_than(20).be(True)
    length.lower_equal_than(30).be(True)
    length.between(18, 20).be(True)
    length.not_be(30)


def test_highlight():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    p.highlight(color=Color.from_string("#0f0"))
    p.expect.css("outline").be("rgb(0, 255, 0) solid 5px")


def test_scroll_until_visible():
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


def test_retry():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find(By.id("button").unique)
    clicks = finder.find(XPath.at("div").id("events").select("p"))

    control = inject.instance(Control)
    btn.click()
    control.retry(lambda: clicks.expect.count.be(3), lambda: btn.click(), wait_after_fail=0)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
