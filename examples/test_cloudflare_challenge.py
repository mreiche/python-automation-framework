import logging
import random
import time

import inject
import pyautogui
import pytest
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from paf.common import Point, Rect, Size
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.request import WebDriverRequest
from paf.uielement import UiElement
from paf.xpath import XPath
from test import create_webdriver


@pytest.fixture
def finder():
    page_factory = inject.instance(PageFactory)
    request = WebDriverRequest("cloudflare")
    request.window_position = Point(-1024,0)
    request.window_maximize = True
    finder = page_factory.create_page(FinderPage, create_webdriver(request))
    yield finder


def connect_mouse_move_event(webdriver: WebDriver, web_element: WebElement, prefix: str=""):
    webdriver.execute_script("""
    const element = arguments[0];
    const prefix = arguments[1];
    document.onmousemove = function(e) {
        console.log(prefix + " move", e.pageX, e.pageY)
    }
    document.onclick = function(e) {
        console.log(prefix + "click", e.pageX, e.pageY)
    }
    """, web_element, prefix)

def get_shadow_root_div(finder: FinderPage):
    return finder.find(
        XPath.at("div")
        .classes("main-content")
        .select("div")
        .attribute("style")
        .be("display: grid;")
        .select("div/div")
        , "shadow_root_div")

def get_viewport_label_position(shadow_root_div: UiElement):
    iframe = shadow_root_div.find("iframe")
    shadow_root_body = iframe.find("body")

    point = Point()
    label = shadow_root_body.find("#content").find("label")
    if label.wait_for.displayed(True):
        for element in label.get_path():
            if element == shadow_root_div:
                break
            elif isinstance(element, UiElement):
                rect = element.expect.bounds.actual
                point = point + rect.origin

    label_size = label.expect.bounds.actual.size
    return point + Size(label_size.width / 2, label_size.height / 2)


# https://www.zenrows.com/blog/selenium-cloudflare-bypass
def test_bypass_cloudflare_challenge(finder: FinderPage):
    finder.open("https://www.scrapingcourse.com/cloudflare-challenge")
    shadow_root_div = get_shadow_root_div(finder)

    def _click_position(pos: Point):
        action = ActionBuilder(finder.webdriver)
        action.pointer_action.move_to_location(pos.x, pos.y)
        action.pointer_action.click()
        action.perform()

    _click_position(get_viewport_label_position(shadow_root_div))

    pass

def test_bypass_cloudflare_challenge_pyautogui(finder: FinderPage):
    finder.open("https://www.scrapingcourse.com/cloudflare-challenge")
    shadow_root_div = get_shadow_root_div(finder)

    def _init_position():
        rect = finder.get_absolute_viewport()
        logging.info(f"Init: {rect}")
        _move_mouse_to(rect.origin)

    def _move_mouse_to(pos: Point):
        duration = _rand_time()
        pyautogui.moveTo(x=pos.x, y=pos.y, duration=duration, tween=pyautogui.easeInOutQuad)
        time.sleep(duration)
        logging.info("Moved")

    #def _move_mouse_by(pos: Point):
    #    pyautogui.moveRel(xOffset=pos.x, yOffset=pos.y, duration=_rand_time(), tween=pyautogui.easeInOutQuad)
    #    logging.info("Moved")

    def _rand_time():
        return (random.random()*2)+0.3

    def _click_selenium(pos: Point):
        ActionChains(finder.webdriver).move_by_offset(pos.x,pos.y).click().perform()

    #def _click_pyautogui(pos: Point):
        #pyautogui.click(x=-1110, y=558, clicks=1, duration=_rand_time(), tween=pyautogui.easeInOutQuad)

    _init_position()
    label_position = get_viewport_label_position(shadow_root_div)
    _click_selenium(label_position)

    pass

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
