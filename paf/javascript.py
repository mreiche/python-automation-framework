from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from paf.common import Location


def scroll_to_center(webdriver: WebDriver, web_element: WebElement, offset: Location):
    webdriver.execute_script(f"""const elementRect = arguments[0].getBoundingClientRect();
const absoluteElementTop = elementRect.top + window.pageYOffset;
const absoluteElementLeft = elementRect.left + window.pageXOffset;
const middle = absoluteElementTop - (window.innerHeight / 2);
const center = absoluteElementLeft - (window.innerWidth / 2);
window.scrollTo(center+{offset.x}, middle+{offset.y});
""", web_element)


def scroll_to_top(webdriver: WebDriver, web_element, offset: Location):
    webdriver.execute_script("window.scrollTo({ left: arguments[0].offsetLeft+arguments[1], top: arguments[0].offsetTop+arguments[2] });", web_element, offset.x, offset.y)
