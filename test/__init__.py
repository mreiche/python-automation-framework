import threading

import inject

from paf.common import Size
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest


def create_webdriver():
    manager = inject.instance(WebDriverManager)
    request = WebDriverRequest(f"{__name__}{threading.get_ident()}")
    request.browser = "chrome"
    request.window_size = Size(1920, 1080)
    return manager.get_webdriver(request)
