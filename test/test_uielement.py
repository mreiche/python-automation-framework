import inject

import paf.config
from paf.locator import By
from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage


def setup_module():
    inject.configure(paf.config.inject)


def test_finder_page():
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage)
    element = finder.find(By.id("id"))
    assert element.name_path == 'UiElement(By.id(id))[0]'


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
