import re

import inject
import pytest
from selenium.webdriver.support.color import Color

from paf.control import change, retry
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.uielement import UiElement, InexistentUiElement, DefaultUiElement
from paf.xpath import XPath
from test import create_webdriver


@pytest.fixture
def finder():
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage, create_webdriver())
    yield finder


def test_basics(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    assert p.name_path == 'UiElement(By.id(para1))[0]'
    assert p.name == p.name_path
    assert str(p) == p.name
    assert finder.webdriver == p.webdriver

    centered = finder.find(".centered")
    p2 = centered.find("#para2")
    p_name = finder.find(By.id("para1"), "paragraph")

    assert p2.name == "UiElement(By.css selector(#para2))[0]"
    assert p2.name_path == "UiElement(By.css selector(.centered))[0] > " + p2.name
    assert p_name.name == "paragraph"


# def test_rect():
#     finder = page_factory.create_page(FinderPage, create_webdriver())
#     finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
#
#     p = finder.find(By.id("para1"))
#     rect = p._get_bounds()
#     assert isinstance(rect, Rect)
#     assert rect.width == 962
#     assert rect.height == 27

def test_assertions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find("#para1")

    # tag name
    p.expect.tag_name.be("p")

    # classes
    p.expect.classes("main").be(True)
    p.expect.classes("sub").be(False)

    text = p.expect.text
    text.be("A paragraph of text")
    text.map(str.upper).be("A PARAGRAPH OF TEXT")
    text.not_be("Bla")
    text.contains("paragraph").be(True)
    text.has_words("paragraph", "text").be(True)
    text.has_words("bla").be(False)
    text.starts_with("A").be(True)
    text.ends_with("text").be(True)
    text.matches("hello").be(False)
    assert text.actual == "A paragraph of text"

    length = p.expect.text.length
    length.be(19)
    length.greater_than(1).be(True)
    length.greater_equal_than(10).be(True)
    length.lower_than(20).be(True)
    length.lower_equal_than(30).be(True)
    length.between(18, 20).be(True)
    length.not_be(30)


def test_text_assertion_fails(finder: FinderPage):
    with pytest.raises(AssertionError, match=re.escape("Expected UiElement(By.css selector(#para1))[0].attribute(data) *undefined* to be [null] after 3 retries")):
        finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
        p = finder.find("#para1")
        p.expect.attribute("data").be("null")


def test_untested_assertion_raises(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
    title = finder.expect.title


def test_wait(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find("#para1")

    assert p.wait_for.tag_name.be("p") is True
    assert p.wait_for.tag_name.be("b") is False


def test_highlight(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    p.highlight(color=Color.from_string("#0f0"))
    p.expect.css("outline").be("rgb(0, 255, 0) solid 5px")


def test_scroll_to_visible(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")

    p = finder.find(By.id("pre1").unique)
    p.expect.visible(False)
    p.scroll_into_view()
    p.expect.visible(True)
    p.expect.fully_visible(True)

    first = finder.find("#p1")
    first.expect.visible(False)
    first.scroll_to_top()
    first.expect.visible(True)
    p.expect.visible(False)


def test_find_sub_elements_list(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")

    # Sub elements
    div = finder.find("#div1")
    p = div.find("p")
    p.expect.attribute("name").be("pName1")

    # Find sub element by XPath
    p2 = div.find(XPath.at("p"))
    p2.expect.attribute("name").be("pName1")

    # Correct XPAth
    div.find(By.xpath("//p")).expect.attribute("name").be("pName1")
    div.find(By.xpath("./p")).expect.attribute("name").be("pName1")

    # List
    p.first.expect.attribute("name").be("pName1")
    p[1].expect.attribute("name").be("pName2")
    p.last.expect.attribute("name").be("pName41")

    for item in p:
        item.expect.attribute("name").be("pName1")
        break


def test_inexistent_sub_element(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")

    # Sub elements
    div = finder.find("#div1")
    inexistent = div.find("#inexistent")
    inexistent.expect.count.be(0)


def test_form(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-html-form-test.html")

    checkbox = finder.find(XPath.at("input").name("checkboxes[]").attribute("value").be("cb3"))
    checkbox.expect.selected(True)

    textarea = finder.find(By.name("comments"))
    textarea.expect.value.be("Comments...")
    textarea.type("Hello World")
    textarea.expect.value.be("Hello World")

    username = finder.find(By.name("username"))
    username.expect.enabled(True)
    username.send_keys("My Name")
    username.expect.value.be("My Name")
    username.clear()
    username.expect.value.be("")

    form = finder.find("#HTMLFormElements")
    form.submit()

    # From Textarea
    finder.find("#_valuecomments").expect.text.be("Hello World")


def test_screenshot(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/find-by-playground-test.html")
    p = finder.find(By.id("pre1").unique)
    path = p.take_screenshot()
    assert path


def test_retry(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find(By.id("button").unique)
    clicks = finder.find(XPath.at("div").id("events").select("p"))
    btn.click()

    with change(retry_count=3, wait_after_fail=0):
        retry(lambda: clicks.expect.count.be(3), lambda e: btn.click())


def test_actions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/events/javascript-events.html")

    click_btn = finder.find("#onclick")
    click_status = finder.find("#onclickstatus")
    click_status.expect.displayed(False)
    click_btn.click()
    click_status.expect.displayed(True)

    hover_btn = finder.find("#onmouseover")
    hover_status = finder.find("#onmouseoverstatus")
    hover_status.expect.displayed(False)
    hover_btn.hover()
    hover_status.expect.displayed(True)

    context_btn = finder.find("#oncontextmenu")
    context_status = finder.find("#oncontextmenustatus")
    context_status.expect.displayed(False)
    context_btn.context_click()
    context_status.expect.displayed(True)

    double_click_btn = finder.find("#ondoubleclick")
    double_click_status = finder.find("#ondoubleclickstatus")
    double_click_status.expect.displayed(False)
    double_click_btn.double_click()
    double_click_status.expect.displayed(True)

    mouse_down_btn = finder.find("#onmousedown")
    mouse_down_status = finder.find("#onmousedownstatus")
    mouse_down_status.expect.displayed(False)
    mouse_down_btn.long_click()
    mouse_down_status.expect.displayed(True)


def test_drag_and_drop(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/drag-drop-javascript.html")

    drag = finder.find(".drag.left")
    drop = finder.find("#droppable1")
    drop.expect.text.be("Drop here")
    drag.drag_and_drop_to(drop)
    drop.expect.text.be("Dropped!")


def test_frames(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/frames/frames-test.html")
    left = finder.find(By.name("left"))
    left.expect.tag_name.be("frame")
    left.find("li").expect.count.be(30)
    left.expect.tag_name.be("frame")

    top = finder.find(By.name("top"))
    exp = top.find(By.class_name("explanation"))
    exp.expect.text.starts_with("This page").be(True)


def test_locate_displayed(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/alerts/fake-alert-test.html")
    ok = finder.find(By.id("dialog-ok").displayed)
    btn = finder.find("#fakealert")

    ok.expect.count.be(0)
    btn.click()
    ok.expect.count.be(1)


def test_uninitialized_ui_element_fails(finder: FinderPage):
    with pytest.raises(Exception) as e:
        ui_element = DefaultUiElement(By.id("id"))
        ui_element.click()

    assert "initialized without WebDriver nor UiElement" in e.value.args[0]


def test_action_on_non_interactable_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/alerts/fake-alert-test.html")
    ok = finder.find("#dialog-ok")
    with pytest.raises(Exception, match=re.escape("Message: element not interactable")):
        with change(retry_count=0):
            ok.click()


def test_fail_message(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
    p1 = finder.find("#para1")
    with pytest.raises(AssertionError, match=re.escape("Expected UiElement(By.css selector(#para1))[0].text [A paragraph of text] mapped ends with [Katze] to be [True]")):
        with change(retry_count=0):
            p1.expect.text.map(str.lower).ends_with("Katze").be(True)


def test_not_unique_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find(By.id("button").unique)
    btn.click()
    btn.click()

    events = finder.find("#events")
    with pytest.raises(Exception, match=re.escape("Expected UiElement(By.css selector(#events))[0] > UiElement(By.tag name(p))[0].text *undefined* to be [click] Element not unique after 0 retries")):
        with change(retry_count=0):
            p = events.find(By.tag_name("p").unique)
            p.expect.text.be("click")


def test_highlight_nonexistent_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    with pytest.raises(Exception, match=re.escape("UiElement(By.css selector(#unkown))[0]: Element not found after 0 retries")):
        with change(retry_count=0):
            unknown = finder.find("#unkown")
            unknown.highlight()


def test_count_nonexistent_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    with pytest.raises(Exception, match=re.escape("Expected UiElement(By.css selector(#unkown))[0] count [0] to be [1] after 0 retries")):
        with change(retry_count=0):
            unknown = finder.find("#unkown")
            unknown.expect.count.be(1)


def test_inexistent_ui_element_wrapper():
    empty_ui_element = InexistentUiElement()
    empty_ui_element.expect.count.be(0)
    assert empty_ui_element.webdriver is None
    empty_ui_element.scroll_to_top()
    empty_ui_element.scroll_into_view()
    empty_ui_element.highlight()
    empty_ui_element.click()
    empty_ui_element.hover()
    empty_ui_element.long_click()
    empty_ui_element.double_click()
    empty_ui_element.drag_and_drop_to(empty_ui_element)
    empty_ui_element.send_keys("test")
    empty_ui_element.type("test")
    empty_ui_element.clear()
    empty_ui_element.submit()
    assert empty_ui_element.take_screenshot() is None
    assert isinstance(empty_ui_element.find("#inexistent"), InexistentUiElement)
    for e in empty_ui_element:
        assert False


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
