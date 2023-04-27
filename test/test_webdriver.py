import inject
import threading

from paf.manager import WebDriverManager
from paf.request import WebDriverRequest

manager: WebDriverManager = None
manager_thread_id: int = 0


def setup():
    global manager, manager_thread_id
    manager = inject.instance(WebDriverManager)
    manager_thread_id = threading.current_thread().ident


def test_manager_singleton():
    manager2 = inject.instance(WebDriverManager)
    assert manager2 == manager


def test_take_screenshot():
    manager.get_webdriver()
    for webdriver in manager.webdrivers:
        path = manager.take_screenshot(webdriver)
        assert path.exists()


def test_shutdown_by_session_key():
    request = WebDriverRequest("test")
    webdriver = manager.get_webdriver(request)
    manager.shutdown_session(request.session)

def teardown_module():
    manager.shutdown_all()
