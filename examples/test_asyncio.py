import asyncio

import inject
import pytest

from examples.test_google import StartPage
from paf.manager import WebDriverManager
from paf.page import PageFactory
from paf.request import WebDriverRequest
from test import get_webdriver


@pytest.mark.asyncio
async def test_run_in_tasks():
    tasks = []
    for i in range(5):
        task = asyncio.to_thread(run_google_search, i)
        tasks.append(task)

    data = await asyncio.gather(*tasks, return_exceptions=True)

    assert len(data) == 5
    for text in data:
        assert text.__contains__("Testerra")


def run_google_search(i: int):
    request = WebDriverRequest(f"asyncio{i}")
    webdriver = get_webdriver(request)
    page_factory = inject.instance(PageFactory)
    webdriver_manager = inject.instance(WebDriverManager)

    start_page = page_factory.create_page(StartPage, webdriver)
    start_page.open("https://google.de")
    start_page.accept_cookies()
    result_page = start_page.search("Testerra")
    result_page.result.first.headline.expect.text.contains("Testerra").be(True)
    text = result_page.result.first.headline.expect.text.actual

    webdriver_manager.shutdown(webdriver)

    return text
