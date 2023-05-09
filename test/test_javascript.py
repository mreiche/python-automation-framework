from paf.common import Size, Rect
from paf.javascript import get_viewport
from paf.request import WebDriverRequest
from test import create_webdriver


def test_viewport():
    request = WebDriverRequest()
    request.browser = "chrome"
    request.window_size = Size(1024, 768)
    webdriver = create_webdriver(request)
    viewport = get_viewport(webdriver)
    assert isinstance(viewport, Rect)
    assert viewport.top == 0
    assert viewport.left == 0
    assert viewport.width == 1024
    assert viewport.height >= 600
