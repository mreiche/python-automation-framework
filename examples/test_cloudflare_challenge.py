import inject
import pytest
from selenium.webdriver.remote.webelement import WebElement

from paf.control import change
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.xpath import XPath
from test import create_webdriver


@pytest.fixture
def finder():
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage, create_webdriver())
    yield finder


# https://www.zenrows.com/blog/selenium-cloudflare-bypass
def test_bypass_cloudflare_challenge(finder: FinderPage):
    finder.open("https://www.scrapingcourse.com/cloudflare-challenge")
    iframe_div = finder.find(
        XPath.at("div")
        .classes("main-content")
        .select("div")
        .attribute("style")
        .be("display: grid;")
        .select("div/div")
    )

    label = iframe_div.find("iframe").find("body").find("#content").find("label").click()

    pass

    # non_shadow_root = finder.find("body")
    # if non_shadow_root.wait_for.displayed(True):
    #     with non_shadow_root.find_web_element() as web_element:
    #         ret = web_element.shadow_root
    #         pass

    # if iframe_div.wait_for.displayed(True):
    #     with iframe_div.find_web_element() as web_element:
    #         web_element: WebElement
    #         web_element.shadow_root
        #return web_element.w.execute_script('return arguments[0].shadowRoot', web_element)
        #web_element.getShadowRoot()
    #iframe = iframe_div.find("iframe")
    #checkbox = iframe.find(XPath.at("div").id("content").select("checkbox"))
    #iframe = finder.find(By.xpath("/html/body/div[1]/div/div[1]/div/div//iframe"))
    pass
