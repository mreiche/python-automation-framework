import inject
from selenium.webdriver.common.keys import Keys

import core.config
from core.locator import By
from core.page import PageFactory, Page
from core.uielement import TestableUiElement, InteractiveUiElement
from core.webdrivermanager import WebDriverManager


def setup_module():
    inject.configure(core.config.inject)


def test_yahoo():
    class YahooStartPage(Page):
        @property
        def cookie_btn(self) -> InteractiveUiElement:
            return self._find(By.name("agree").displayed)

        @property
        def search_box(self) -> InteractiveUiElement:
            return self._find(By.name("p"))

    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(YahooStartPage)
    page.open('http://www.yahoo.com')
    page.expect.title.contains("Yahoo").be(True)
    page.expect.title.length.greater_than(10).be(True)
    page.cookie_btn.expect.count.be(1)
    page.cookie_btn.expect.text.contains("akzeptieren").be(True)
    page.cookie_btn.click()

    page.search_box.type("seleniumhq")
    page.search_box.send_keys(Keys.ENTER)


def test_oka():
    class OkaPage(Page):
        @property
        def articles(self) -> TestableUiElement:
            return self._find(By.tag_name("article"))

    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(OkaPage)
    page.open("https://objektkleina.com")
    page.articles.expect.count.be(4)

    for item in page.articles.list:
        print(item.expect.text.actual)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
