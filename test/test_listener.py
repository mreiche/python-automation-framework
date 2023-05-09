import inject
import pytest

import paf.config
from paf.common import Property
from paf.listener import Listener, HighlightListener
from paf.page import PageFactory, FinderPage
from test import create_webdriver


@pytest.fixture
def finder():
    finder = inject.instance(PageFactory).create_page(FinderPage, create_webdriver())
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


def test_highlight_listener(finder: FinderPage, listener: Listener):
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find("#button")
    btn.click()
    btn.expect.css("outline").be("rgb(255, 255, 0) solid 5px")

    btn.wait_for.text.be("Katze")
    btn.expect.css("outline").be("rgb(255, 0, 0) solid 5px")
