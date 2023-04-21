from typing import Union

import inject
import pytest

import paf.config

from paf.manager import WebDriverManager


@pytest.fixture(scope="session", autouse=True)
def configure_inject():
    inject.configure(paf.config.inject)


def pytest_exception_interact(
    node: Union["Item", "Collector"],
    call: "CallInfo[Any]",
    report: Union["CollectReport", "TestReport"],
) -> None:
    manager = inject.instance(WebDriverManager)
    for webdriver in manager.webdrivers:
        manager.take_screenshot(webdriver)
