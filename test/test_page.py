import inject

from paf.manager import WebDriverManager
from paf.page import PageFactory, Page
from test import create_webdriver

page_factory: PageFactory = None


def setup_module():
    global page_factory
    page_factory = inject.instance(PageFactory)


def test_page():
    page = page_factory.create_page(Page, create_webdriver())
    page.open("https://testpages.herokuapp.com")
    page.expect.title.be("Selenium Test Page")
    page.expect.url.be("https://testpages.herokuapp.com/styled/index.html")

# def test_yahoo():
#     class YahooStartPage(Page):
#         @property
#         def cookie_btn(self) -> InteractiveUiElement:
#             return self._find(By.name("agree").displayed)
#
#         @property
#         def search_box(self) -> InteractiveUiElement:
#             return self._find(By.name("p"))
#
#     page_factory = inject.instance(PageFactory)
#     page = page_factory.create_page(YahooStartPage)
#     page.open('http://www.yahoo.com')
#     page.expect.title.contains("Yahoo").be(True)
#     page.expect.title.length.greater_than(10).be(True)
#     page.cookie_btn.expect.count.be(1)
#     page.cookie_btn.expect.text.contains("akzeptieren").be(True)
#     page.cookie_btn.click()
#
#     page.search_box.type("seleniumhq")
#     page.search_box.send_keys(Keys.ENTER)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
