import inject

from paf.common import Point
from paf.manager import WebDriverManager
from paf.page import FinderPage
from test import finder


def test_rect(finder: FinderPage):
    finder.open("https://testpages.herokuapp.com/styled/basic-web-page-test.html")
    p = finder.find("#para1")
    rect = p.expect.bounds.actual
    point = Point(10, 20)
    point.add(rect)

    assert point.x > 10
    assert point.y > 20


def teardown_module():
    inject.instance(WebDriverManager).shutdown_all()
