import inject
import pytest
from selenium.webdriver.support.color import Color

import paf.config
from paf.common import Property
from paf.listener import Listener, HighlightListener
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from test import create_webdriver


@pytest.fixture
def finder():
    finder = inject.instance(PageFactory).create_page(FinderPage, create_webdriver())
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    yield finder


@pytest.fixture(scope="function")
def listener(monkeypatch):
    assert Property.env(Property.PAF_DEMO_MODE) == "0"
    monkeypatch.setenv(Property.PAF_DEMO_MODE.name, "1")
    inject.clear_and_configure(paf.config.inject)
    listener = inject.instance(Listener)
    assert isinstance(listener, HighlightListener)

    yield listener

    monkeypatch.setenv(Property.PAF_DEMO_MODE.name, "0")
    inject.clear_and_configure(paf.config.inject)


def test_highlight_action(finder: FinderPage, listener: Listener):
    btn = finder.find("#button")
    btn.click()
    btn.expect.css("outline").be("rgb(255, 255, 0) solid 5px")


def test_highlight_failed_assertion(finder: FinderPage, listener: Listener):
    btn = finder.find("#button")

    with pytest.raises(Exception):
        btn.expect.text.be("Katze")

    btn.expect.css("outline").be("rgb(255, 0, 0) solid 5px")
    assert not btn.wait_for.text.raise_exception


def test_highlight_passed_assertion(finder: FinderPage, listener: Listener):
    btn = finder.find("#button")
    btn.expect.value.be("click me")
    btn.expect.css("outline").be("rgb(0, 255, 0) solid 5px")


def test_highlight_not_found_log(finder: FinderPage, listener: Listener, caplog):
    inexistent = finder.find("#inexistent")

    with pytest.raises(Exception):
        inexistent.click()

    assert len(caplog.records) == 1
    for record in caplog.records:
        assert "Cannot highlight UiElement(By.css selector(#inexistent))[0]: Element not found" in record.message


def test_highlight_action_success_skips_highlighting(finder: FinderPage, listener: Listener):
    btn = finder.find("#button")
    btn.highlight(Color.from_string("#888888"))
    with btn.find_web_element() as web_element:
        assert web_element.value_of_css_property("outline") == "rgb(136, 136, 136) solid 5px"


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
