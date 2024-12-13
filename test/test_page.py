import re

import inject
import pytest

from paf.control import change
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, Page, FinderPage
from paf.request import WebDriverRequest
from test import create_webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from test import finder


def test_assertions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com")
    assert finder.wait_for.url.be("https://testpages.eviltester.com/styled/index.html")

    expected_title = "Web Testing and Automation Practice Application Pages"

    finder.expect.title.be(expected_title)
    assert finder.name == "Page"
    assert str(finder) == finder.name
    assert finder.webdriver.title == expected_title

    with pytest.raises(AssertionError, match=re.escape("Expected Page.url [https://testpages.eviltester.com/styled/index.html] ends with [index.html] to be [False]")):
        with change(retry_count=0):
            finder.expect.url.ends_with("index.html").be(False)


def test_create_page_from_page():
    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(Page)
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


def test_scroll_until_visible(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = finder._find("#p41")
    height = p.expect.bounds.actual.height
    while p.wait_for.fully_visible(False):
        finder.scroll_by(y=height)

    p.expect.fully_visible(True)


def test_page_dom_differs_page_source(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find(By.id("button").unique)
    btn.click()
    btn.click()
    dom = finder.get_dom()
    page_source = finder.webdriver.page_source
    assert dom != page_source


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
