import inject
import pytest
from selenium.webdriver.support.color import Color

from paf.control import Control
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.xpath import XPath
from test import create_webdriver

page_factory: PageFactory = None


def setup_module():
    global page_factory
    page_factory = inject.instance(PageFactory)


@pytest.fixture
def finder():
    finder = page_factory.create_page(FinderPage, create_webdriver())
    yield finder


def test_finder_page(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find(By.id("para1"))
    assert p.name_path == 'UiElement(By.id(para1))[0]'
    assert p.name == p.name_path


# def test_rect():
#     finder = page_factory.create_page(FinderPage, create_webdriver())
#     finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
#
#     p = finder.find(By.id("para1"))
#     rect = p._get_bounds()
#     assert isinstance(rect, Rect)
#     assert rect.width == 962
#     assert rect.height == 27

def test_text_assertions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")

    p = finder.find("#para1")

    p.expect.tag_name.be("p")

    text = p.expect.text
    text.be("A paragraph of text")
    text.contains("paragraph").be(True)
    text.has_words("paragraph", "text").be(True)
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
    p.expect.visible.be(False)
    p.scroll_into_view()
    p.expect.visible.be(True)
    p.expect.fully_visible.be(True)

    first = finder.find("#p1")
    first.expect.visible.be(False)
    first.scroll_to_top()
    first.expect.visible.be(True)
    p.expect.visible.be(False)


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
    checkbox.expect.selected.be(True)

    textarea = finder.find(By.name("comments"))
    textarea.expect.value.be("Comments...")
    textarea.type("Hello World")
    textarea.expect.value.be("Hello World")

    username = finder.find(By.name("username"))
    username.expect.enabled.be(True)
    username.send_keys("My Name")
    username.expect.value.be("My Name")
    username.clear()
    username.expect.value.be("")


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
    control.retry(lambda: clicks.expect.count.be(3), lambda: btn.click(), wait_after_fail=0, count=3)


def test_actions(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/events/javascript-events.html")

    click_btn = finder.find("#onclick")
    click_status = finder.find("#onclickstatus")
    click_status.expect.displayed.be(False)
    click_btn.click()
    click_status.expect.displayed.be(True)

    hover_btn = finder.find("#onmouseover")
    hover_status = finder.find("#onmouseoverstatus")
    hover_status.expect.displayed.be(False)
    hover_btn.hover()
    hover_status.expect.displayed.be(True)

    context_btn = finder.find("#oncontextmenu")
    context_status = finder.find("#oncontextmenustatus")
    context_status.expect.displayed.be(False)
    context_btn.context_click()
    context_status.expect.displayed.be(True)

    double_click_btn = finder.find("#ondoubleclick")
    double_click_status = finder.find("#ondoubleclickstatus")
    double_click_status.expect.displayed.be(False)
    double_click_btn.double_click()
    double_click_status.expect.displayed.be(True)


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


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
