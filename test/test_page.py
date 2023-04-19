import inject
from selenium.webdriver.common.keys import Keys

import paf.config
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, Page
from paf.uielement import InteractiveUiElement


def setup_module():
    inject.configure(paf.config.inject)


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


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
