from selenium.webdriver.common.keys import Keys

from core.by import By
from core.page import Page
from core.webdrivermanager import WebDriverManager

manager: WebDriverManager = None


def setup_module():
    global manager
    manager = WebDriverManager()


def test_yahoo():
    webdriver = manager.get_webdriver()
    page = Page(webdriver)

    page.open('http://www.yahoo.com')
    page.expect.title.contains("Yahoo").be(True)
    cookie_btn = page.find(By.name("agree"))
    cookie_btn.expect.text.contains("akzeptieren").be(True)
    cookie_btn.click()

    search_box = page.find(By.name("p"))
    search_box.input("seleniumhq")
    search_box.send_keys(Keys.ENTER)


def teardown_module():
    global manager
    manager.shutdown_all()
