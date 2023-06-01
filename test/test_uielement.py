import inject
import pytest
from selenium.webdriver.support.color import Color

from paf.control import Control
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.uielement import UiElement
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
    with pytest.raises(AssertionError) as e:
        finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
        p = finder.find("#para1")
        p.expect.attribute("data").be("null")

    assert "Expected UiElement(By.css selector(#para1))[0].attribute(data) *undefined* to be [null] after 3 retries" in \
           e.value.args[0]


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

    control = inject.instance(Control)
    btn.click()
    control.retry(
        action=lambda: clicks.expect.count.be(3),
        on_fail=lambda e: btn.click(),
        wait_after_fail=0,
        count=3
    )


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
        ui_element = UiElement(By.id("id"))
        ui_element.click()

    assert "initialized without WebDriver nor UiElement" in e.value.args[0]


def test_action_on_non_interactable_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/alerts/fake-alert-test.html")
    ok = finder.find("#dialog-ok")
    with pytest.raises(Exception) as e:
        ok.click()

    assert "Message: element not interactable" in e.value.args[0]


def test_not_unique_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/key-click-display-test.html")
    btn = finder.find(By.id("button").unique)
    btn.click()
    btn.click()

    events = finder.find("#events")
    with pytest.raises(Exception) as e:
        p = events.find(By.tag_name("p").unique)
        p.expect.text.be("click")

    assert "Not unique" in e.value.args[0]


def test_not_found_fails(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
    with pytest.raises(Exception) as e:
        unknown = finder.find("#unkown")
        unknown.highlight()

    assert "Not found" in e.value.args[0]


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
