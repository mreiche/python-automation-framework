import inject
import pytest
from selenium.webdriver import Keys

from paf.manager import WebDriverManager
from paf.page import PageFactory, FinderPage
from paf.xpath import XPath

finder: FinderPage = None


def setup_function():
    global finder
    page_factory = inject.instance(PageFactory)
    finder = page_factory.create_page(FinderPage)


def test_add_two_todos_and_check_items():
    open_todo_app()
    add_new_todo("Learn Robot Framework")
    add_new_todo("Write Test Cases")
    todo_count().expect.text.be("2 items left")


@pytest.mark.xfail
def test_add_two_todos_and_check_wrong_number_of_items():
    open_todo_app()
    add_new_todo("Learn Robot Framework")
    add_new_todo("Write Test Cases")
    todo_count().expect.text.be("1 item left")


def test_add_todo_and_mark_some_todo():
    open_todo_app()
    add_new_todo("Learn Robot Framework")
    mark_todo("Learn Robot Framework")
    todo_count().expect.text.be("0 items left")


def test_check_if_marked_todos_are_removed():
    open_todo_app()
    add_new_todo("Learn Robot Framework")
    add_new_todo("Write Test Cases")
    mark_one_todo()
    todo_count().expect.text.be("1 item left")


def test_split_todos():
    open_todo_app()
    add_new_todo("Learn Robot Framework", "Write Test Cases", "Sleep")
    todo_count().expect.text.be("3 items left")


def test_add_a_lot_of_todos():
    open_todo_app()
    add_todos(100)
    todo_count().expect.text.be("100 items left")


def add_todos(count: int):
    add_new_todo(*map(lambda x: f"My ToDo Number {x}", range(count)))


def open_todo_app():
    finder.open("https://todomvc.com/examples/vanillajs/")


def add_new_todo(*names):
    for name in names:
        finder.find(".new-todo").type(name).send_keys(Keys.ENTER)


def mark_todo(name: str):
    finder.find(XPath.at("label").text.be(name).preceding("/input")).click()


def mark_one_todo():
    finder.find(XPath.at("li", 1).select("input")).click()


def todo_count():
    return finder.find(".todo-count")


def teardown_function():
    if finder:
        inject.instance(WebDriverManager).shutdown(finder.webdriver)
