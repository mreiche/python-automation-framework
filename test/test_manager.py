import os
import shutil
from pathlib import Path

import inject
import threading

import pytest

from paf.common import Property
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest


@pytest.fixture
def manager():
    yield inject.instance(WebDriverManager)


def test_manager_singleton(manager: WebDriverManager):
    manager2 = inject.instance(WebDriverManager)
    assert manager2 == manager


def test_take_screenshot(manager: WebDriverManager):
    manager.get_webdriver()
    for webdriver in manager.webdrivers:
        path = manager.take_screenshot(webdriver)
        assert path.exists()


def test_shutdown_by_session_key(manager: WebDriverManager):
    request = WebDriverRequest("test")
    manager.get_webdriver(request)
    manager.shutdown_session(request.session)


def test_shutdown_unknown_session_fails(manager: WebDriverManager):
    with pytest.raises(Exception) as e:
        manager.shutdown_session("unknown")

    assert "Unknown session: unknown" in e.value.args[0]


def test_take_screenshot_fails(monkeypatch, manager: WebDriverManager):
    monkeypatch.setenv(Property.PAF_SCREENSHOTS_DIR.name, "read-only-screenshots")
    dir = Path(Property.env(Property.PAF_SCREENSHOTS_DIR))
    dir.mkdir(parents=True, exist_ok=True)
    os.chmod(dir, 555)
    webdriver = manager.get_webdriver()
    path = manager.take_screenshot(webdriver)
    assert path is None
    os.chmod(dir, 775)
    shutil.rmtree(dir)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
