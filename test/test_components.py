from core.by import By
from core.component import Component
from core.page import Page


class MyPage(Page):
    pass


class MyComponent(Component["MyComponent"]):

    @property
    def custom_element(self):
        return self.find(By.id("input"))


page = MyPage(None)


def test_component_name_path():
    component = page.create_component(MyComponent, page.find(By.tag_name("body")))
    assert component.custom_element.name_path == "MyPage > MyComponent > UiElement(By.tag name(body))[0] > UiElement(By.id(input))[0]"


def test_component_list():
    component = page.create_component(MyComponent, page.find(By.tag_name("body")))
