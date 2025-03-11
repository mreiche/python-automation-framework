import re

import inject
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from paf.common import Point, Size
from paf.control import change
from paf.manager import WebDriverManager
from paf.page import PageFactory, Page, FinderPage
from paf.request import WebDriverRequest
from test import get_webdriver
from test import finder, page_factory


def test_assertions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com")
    assert finder.wait_for.url.be("https://testpages.eviltester.com/styled/index.html")

    expected_title = "Web Testing and Automation Practice Application Pages"

    finder.expect.title.be(expected_title)
    assert finder.name == "FinderPage"
    assert str(finder) == finder.name
    assert finder.webdriver.title == expected_title

    with pytest.raises(AssertionError, match=re.escape("Expected FinderPage.url [https://testpages.eviltester.com/styled/index.html] ends with [index.html] to be [False]")):
        with change(retry_count=0):
            finder.expect.url.ends_with("index.html").be(False)


def test_create_page_from_page(page_factory: PageFactory):
    webdriver = get_webdriver(WebDriverRequest())
    page = page_factory.create_page(Page)
    other_page = page._create_page(Page)
    assert isinstance(other_page, Page)
    assert page.webdriver == other_page.webdriver
    assert page.webdriver == webdriver


def test_create_page_without_webdriver(page_factory: PageFactory):
    webdriver = get_webdriver(WebDriverRequest())
    page = page_factory.create_page(Page)
    assert page.webdriver == webdriver
    assert isinstance(page, Page)
    assert isinstance(page.webdriver, WebDriver)


def test_scroll_until_visible(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = finder._find("#p41")
    height = p.expect.bounds.actual.height
    while p.wait_for.fully_visible(False):
        finder.scroll_by(y=height)

    p.expect.fully_visible(True)


def test_absolute_viewport(page_factory: PageFactory):
    request = WebDriverRequest("viewport")
    request.window_position = Point(10, 20)
    request.window_size = Size(1024, 768)
    webdriver = get_webdriver(request)
    finder = page_factory.create_page(FinderPage, webdriver)
    viewport = finder.get_absolute_viewport()

    assert viewport.origin.x >= request.window_position.x
    assert viewport.origin.y >= request.window_position.y
    assert viewport.size.width <= request.window_size.width
    assert viewport.size.height <= request.window_size.height


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
