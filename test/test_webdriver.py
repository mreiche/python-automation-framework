import inject
import threading

from paf.manager import WebDriverManager

manager: WebDriverManager = None
manager_thread_id: int = 0


def setup():
    global manager, manager_thread_id
    manager = inject.instance(WebDriverManager)
    manager_thread_id = threading.current_thread().ident


def test_manager_singleton():
    manager2 = inject.instance(WebDriverManager)
    assert manager2 == manager


def teardown_module():
    manager.shutdown_all()
