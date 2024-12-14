import logging

import inject
import pytest
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains

from paf.common import Point
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.request import WebDriverRequest
from paf.uielement import UiElement
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
    shadow_root_div = finder.find(
        XPath.at("div")
        .classes("main-content")
        .select("div")
        .attribute("style")
        .be("display: grid;")
        .select("div/div")
    )

    finder.webdriver.execute_script("""
var cursorX;
var cursorY;
document.onmousemove = function(e) {
    console.log(e.pageX, e.pageY)
}
""")

    if shadow_root_div.wait_for.displayed(True):
        iframe = shadow_root_div.find("iframe")
        shadow_root_body = iframe.find("body")
        label = shadow_root_body.find("#content").find("label")
        if label.wait_for.displayed(True):
            label.highlight()
            point = Point()
            for element in label.get_path():
                if isinstance(element, UiElement):
                    rect = element.expect.bounds.actual
                    point.add(rect)
                    logging.info(f"{rect.__dict__} - {point.__dict__}")

            with label.find_web_element() as web_element:
                ActionChains(shadow_root_div.webdriver).move_to_element_with_offset(web_element, 1,1).click().perform()


def test_undetected_chromedriver():
    driver = uc.Chrome(
        use_subprocess=False,
        headless=False,
    )
    manager = inject.instance(WebDriverManager)
    request = WebDriverRequest("undetected")
    manager.introduce_webdriver(driver, request)
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage, manager.get_webdriver(request))
    finder.open("https://www.scrapingcourse.com/cloudflare-challenge")
    finder.find("#main-content").expect.text.contains("You bypassed the Cloudflare challenge!").be(True)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
