from paf.common import Size, Rect
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from paf.javascript import get_viewport


def test_viewport():
    request = WebDriverRequest()
    request.browser = "chrome"
    request.window_size = Size(1024, 768)
    manager = WebDriverManager()
    webdriver = manager.get_webdriver(request)
    viewport = get_viewport(webdriver)
    assert isinstance(viewport, Rect)
    assert viewport.top == 0
    assert viewport.left == 0
    assert viewport.width == 1024
    assert viewport.height >= 600
