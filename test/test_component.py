import json
from functools import cache

import inject
import pytest

from paf.component import Component
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import Page, PageFactory
from paf.xpath import XPath
from test import create_webdriver


@pytest.fixture
def components_page():
    yield inject.instance(PageFactory).create_page(ComponentsPage, create_webdriver())


class ComponentsPage(Page):
    @property
    @cache
    def custom_component(self):
        return self._create_component(MyComponent, self._find(By.tag_name("body")))

    @property
    def table_row(self):
        return self._create_component(TableRow, self._find(XPath.at("table").id("dynamictable").select("tr")))


class MyComponent(Component["MyComponent"]):
    @property
    def type(self):
        return self._find(By.id("input"))


class TableCell(Component["TableCell"]):
    pass


class TableRow(Component["TableRow"]):
    @property
    def col(self):
        return self._find(XPath.at("(th|td)"))

    @property
    def cells(self):
        return self._create_component(TableCell, self.col)


def test_component_name_path(components_page: ComponentsPage):
    component = components_page.custom_component.type
    assert component.name_path == "ComponentsPage > MyComponent > UiElement(By.tag name(body))[0] > UiElement(By.id(input))[0]"
    assert str(component) == "UiElement(By.id(input))[0]"


def test_component_name(components_page: ComponentsPage):
    component = components_page.custom_component.type
    assert component.__str__() == "UiElement(By.id(input))[0]"


def test_component_list_name(components_page: ComponentsPage):
    component = components_page.custom_component.last
    assert component.name_path == "ComponentsPage > MyComponent > UiElement(By.tag name(body))[-1]"


def test_component_list(components_page: ComponentsPage):
    components_page.open("https://testpages.herokuapp.com/styled/tag/dynamic-table.html")
    rows = components_page.table_row
    assert rows.name_path == "ComponentsPage > TableRow > UiElement(By.xpath(//table[@id='dynamictable']//tr))[0]"
    rows.expect.count.be(3)
    rows.first.col.first.expect.text.be("name")
    rows.first.col.last.expect.text.be("age")

    assert rows.last.col.first.wait_for.text.be("George")
    rows.last.col.last.expect.text.be("42")

    assert rows[1].cells.wait_for.text.be("Bob")

    for row in rows:
        row.highlight()


def test_component_scrolling(components_page: ComponentsPage):
    components_page.open("https://testpages.herokuapp.com/styled/tag/dynamic-table.html")
    rows = components_page.table_row
    json_data = components_page._find("#jsondata")
    details = components_page._find("details")
    details.click()

    data = []
    for i in range(100):
        data.append({"name": f"name-{i}", "age": i})

    json_data.clear()
    json_data.send_keys(json.dumps(data))
    refresh_btn = components_page._find("#refreshtable")
    refresh_btn.click()

    rows.last.scroll_into_view()
    rows.first.expect.visible(False)
    rows.first.scroll_to_top()
    rows.last.expect.visible(False)


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
