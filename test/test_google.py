from functools import cache

from selenium.webdriver import Keys

from paf.locator import By
from paf.component import Component
from paf.page import Page, PageFactory
import inject
import paf.config
from paf.webdrivermanager import WebDriverManager
from paf.xpath import XPath


class ResultItem(Component["ResultItem"]):
    @property
    @cache
    def headline(self):
        return self._find(By.tag_name("h3"))


class ResultPage(Page):
    @property
    @cache
    def _result_container(self):
        return self._find(XPath.at("div").attribute("id").be("search").encloses("div").classes("g"))

    @property
    @cache
    def result(self):
        return self._create_component(ResultItem, self._result_container)


class StartPage(Page):
    @property
    @cache
    def _search_field(self):
        return self._find(By.name("q"))

    @property
    @cache
    def _search_btn(self):
        return self._find(By.name("btnK"))

    @property
    @cache
    def _accept_cookies_btn(self):
        return self._find(By.id("L2AGLb"))

    def accept_cookies(self):
        if self._accept_cookies_btn.wait_for.displayed.be(True):
            self._accept_cookies_btn.click()
            self._accept_cookies_btn.expect.displayed.be(False)

    def search(self, search: str):
        self._search_field.type(search)
        self._search_btn.send_keys(Keys.ENTER)
        return self._create_page(ResultPage)


def setup_module():
    inject.configure(paf.config.inject)


def test_search():
    page_factory = inject.instance(PageFactory)
    start_page = page_factory.create_page(StartPage)
    start_page.open("https://google.de")
    start_page.accept_cookies()
    result_page = start_page.search("Testerra")
    result_page.result.list.first.headline.expect.text.contains("Testerra").be(True)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
