from typing import Union

import inject
import pytest
import logging
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
    if inject.is_configured():
        manager = inject.instance(WebDriverManager)
        for webdriver in manager.webdrivers:
            path = manager.take_screenshot(webdriver)
            logging.error(f"Took screenshot: {path}")
