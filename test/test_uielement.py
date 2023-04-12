from selenium.webdriver.common.keys import Keys

from core.by import By
from core.page import Page
from core.webdrivermanager import WebDriverManager

manager: WebDriverManager = None


def setup_module():
    global manager
    manager = WebDriverManager()


class YahooStartPage(Page):
    pass


def test_yahoo():
    webdriver = manager.get_webdriver()
    page = YahooStartPage(webdriver)

    page.open('http://www.yahoo.com')
    page.expect.title.contains("Yahoo").be(True)
    page.expect.title.length.greater_than(10).be(True)
    cookie_btn = page.find(By.name("agree").displayed)
    cookie_btn.expect.text.contains("akzeptieren").be(True)
    cookie_btn.click()

    search_box = page.find(By.name("p"))
    search_box.input("seleniumhq")
    search_box.send_keys(Keys.ENTER)


def teardown_module():
    global manager
    manager.shutdown_all()
