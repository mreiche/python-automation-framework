import logging
import random
import time
from functools import cache

import inject
import pyautogui
import pytest
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from paf import control
from paf.common import Point, Rect, Size
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage, Page
from paf.request import WebDriverRequest
from paf.uielement import UiElement
from paf.xpath import XPath
from test import create_webdriver


@pytest.fixture
def cloudflare():
    page_factory = inject.instance(PageFactory)
    request = WebDriverRequest("cloudflare")
    request.window_position = Point(-1024,0)
    request.window_maximize = True
    page = page_factory.create_page(CloudflarePage, create_webdriver(request))
    yield page


@pytest.fixture()
def cloudflare_undetected():
    driver = uc.Chrome(
        use_subprocess=False,
        headless=False,
    )
    manager = inject.instance(WebDriverManager)
    request = WebDriverRequest("undetected")
    manager.introduce_webdriver(driver, request)
    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(CloudflarePage, manager.get_webdriver(request))
    yield page


class CloudflarePage(Page):
    @property
    @cache
    def shadow_root_div(self):
        return self._find(
            XPath.at("div")
            .classes("main-content")
            .select("div")
            .attribute("style")
            .be("display: grid;")
            .select("div/div")
            , "shadow_root_div")

    def is_present(self):
        return self.shadow_root_div.wait_for.displayed(True)

    def is_waiting_for_confirmation(self):
        return self.label.wait_for.displayed(True)

    @property
    @cache
    def label(self):
        iframe = self.shadow_root_div.find("iframe")
        shadow_root_body = iframe.find("body")
        label = shadow_root_body.find("#content").find("label")
        return label

    def get_label_viewport_position(self):
        point = Point()
        label = self.label
        shadow_root_div = self.shadow_root_div
        for element in label.get_path():
            if element == shadow_root_div:
                break
            elif isinstance(element, UiElement):
                rect = element.expect.bounds.actual
                point = point + rect.origin

        label_size = label.expect.bounds.actual.size
        return point + Size(label_size.width / 2, label_size.height / 2)

    def click_confirmation_label(self):
        pos = self.get_label_viewport_position()
        self.click_position(pos)

    def click_position(self, pos: Point):
        action = ActionBuilder(self.webdriver)
        action.pointer_action.move_to_location(pos.x, pos.y)
        action.pointer_action.click()
        action.perform()

# def connect_mouse_move_event(webdriver: WebDriver, web_element: WebElement, prefix: str=""):
#     webdriver.execute_script("""
#     const element = arguments[0];
#     const prefix = arguments[1];
#     document.onmousemove = function(e) {
#         console.log(prefix + " move", e.pageX, e.pageY)
#     }
#     document.onclick = function(e) {
#         console.log(prefix + "click", e.pageX, e.pageY)
#     }
#     """, web_element, prefix)

def bypass_cloudflare(cloudflare: CloudflarePage):
    cloudflare.shadow_root_div.expect.displayed(True)
    if cloudflare.is_waiting_for_confirmation():
        cloudflare.click_confirmation_label()

## https://www.zenrows.com/blog/selenium-cloudflare-bypass
def bypass_cloudflare_challenge(cloudflare: CloudflarePage):
    cloudflare.open("https://www.scrapingcourse.com/cloudflare-challenge")
    bypass_cloudflare(cloudflare)
    finder = cloudflare._create_page(FinderPage)
    finder.find("#main-content").expect.text.contains("You bypassed the Cloudflare challenge!").be(True)

def test_bypass_cloudflare_challenge(cloudflare: CloudflarePage):
    bypass_cloudflare_challenge(cloudflare)

def test_bypass_cloudflare_challenge_undetected(cloudflare_undetected: CloudflarePage):
    bypass_cloudflare_challenge(cloudflare_undetected)

def test_bypass_cloudflare_gitlab(cloudflare: CloudflarePage):
    cloudflare.open("https://gitlab.com/users/sign_in")
    bypass_cloudflare(cloudflare)
    pass

def test_bypass_cloudflare_gitlab_undetected(cloudflare_undetected: CloudflarePage):
    cloudflare_undetected.open("https://gitlab.com/users/sign_in")
    bypass_cloudflare(cloudflare_undetected)
    pass

# def test_bypass_cloudflare_challenge_pyautogui(finder: FinderPage):
#     finder.open("https://www.scrapingcourse.com/cloudflare-challenge")
#     shadow_root_div = get_shadow_root_div(finder)
#
#     def _init_position():
#         rect = finder.get_absolute_viewport()
#         logging.info(f"Init: {rect}")
#         _move_mouse_to(rect.origin)
#
#     def _move_mouse_to(pos: Point):
#         duration = _rand_time()
#         pyautogui.moveTo(x=pos.x, y=pos.y, duration=duration, tween=pyautogui.easeInOutQuad)
#         time.sleep(duration)
#         logging.info("Moved")
#
#     #def _move_mouse_by(pos: Point):
#     #    pyautogui.moveRel(xOffset=pos.x, yOffset=pos.y, duration=_rand_time(), tween=pyautogui.easeInOutQuad)
#     #    logging.info("Moved")
#
#     def _rand_time():
#         return (random.random()*2)+0.3
#
#     def _click_selenium(pos: Point):
#         ActionChains(finder.webdriver).move_by_offset(pos.x,pos.y).click().perform()
#
#     #def _click_pyautogui(pos: Point):
#         #pyautogui.click(x=-1110, y=558, clicks=1, duration=_rand_time(), tween=pyautogui.easeInOutQuad)
#
#     _init_position()
#     label_position = get_label_viewport_position(shadow_root_div)
#     _click_selenium(label_position)
#
#     pass

def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
