from functools import cache

import inject

import paf.config
from paf.component import Component
from paf.locator import By
from paf.page import Page, PageFactory
from paf.manager import WebDriverManager


class MyPage(Page):
    @property
    @cache
    def custom_component(self):
        return self._create_component(MyComponent, self._find(By.tag_name("body")))


class MyComponent(Component["MyComponent"]):
    @property
    def type(self):
        return self._find(By.id("input"))


def test_component_name_path():
    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(MyPage)
    assert page.custom_component.type.name_path == "MyPage > MyComponent(UiElement(By.tag name(body))[0]) > UiElement(By.id(input))[0]"


def test_component_list():
    page_factory = inject.instance(PageFactory)
    page = page_factory.create_page(MyPage)
    assert page.custom_component.list.last.name_path == "MyPage > MyComponent(UiElement(By.tag name(body))[-1])"


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
