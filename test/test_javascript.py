import inject

from paf.common import Size, Rect
import paf.javascript as javascript
from paf.manager import WebDriverManager
from paf.page import FinderPage
from paf.request import WebDriverRequest
from test import create_webdriver
from test import finder


def test_viewport():
    request = WebDriverRequest()
    request.browser = "chrome"
    request.window_size = Size(1024, 768)
    webdriver = create_webdriver(request)
    viewport = javascript.get_viewport(webdriver)
    assert isinstance(viewport, Rect)
    assert viewport.top == 0
    assert viewport.left == 0
    assert viewport.width == 1024
    assert viewport.height >= 600


def test_set_attribute(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
    p = finder.find("#para1")
    with p.find_web_element() as web_element:
        javascript.set_attribute(p.webdriver, web_element, "data-katze", "affe")

    p.expect.attribute("data-katze").be("affe")


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
