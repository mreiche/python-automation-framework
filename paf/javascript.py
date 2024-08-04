from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.color import Color

from paf.common import Point, Rect
from paf.dom import Attribute


def scroll_to_center(webdriver: WebDriver, web_element: WebElement, offset: Point):
    webdriver.execute_script(f"""const element = arguments[0];
const left = arguments[1];
const top = arguments[2];

const elementRect = element.getBoundingClientRect();
const absoluteElementTop = elementRect.top + window.pageYOffset;
const absoluteElementLeft = elementRect.left + window.pageXOffset;
const middle = absoluteElementTop - (window.innerHeight / 2);
const center = absoluteElementLeft - (window.innerWidth / 2);
window.scrollTo(center+left, middle+top);
""", web_element, offset.x, offset.y)


def scroll_to_top(webdriver: WebDriver, web_element: WebElement, offset: Point):
    webdriver.execute_script("""const element = arguments[0];
const left = arguments[1];
const top = arguments[2];

window.scrollTo({ left: element.offsetLeft+left, top: element.offsetTop+top });""", web_element, offset.x, offset.y)


def get_viewport(webdriver: WebDriver):
    data = webdriver.execute_script("return [window.pageXOffset.toString(), window.pageYOffset.toString(), window.innerWidth.toString(), window.innerHeight.toString()];")
    assert isinstance(data, list)
    return Rect(x=int(data[0]), y=int(data[1]), width=int(data[2]), height=int(data[3]))


def highlight(webdriver: WebDriver, web_element: WebElement, color: Color, timeout_ms: int = 2000):
    webdriver.execute_script("""const element = arguments[0];
const color = arguments[1];
const timeout = arguments[2];

const origOutline = element.style.outline;
element.style.cssText += "outline: 5px solid " + color + " !important";
window.setTimeout(function() {
    element.style.outline = origOutline;
}, timeout);""", web_element, color.hex, timeout_ms)


def set_attribute(webdriver: WebDriver, web_element: WebElement, attribute: str | Attribute, value: any):
    webdriver.execute_script("""const element = arguments[0];
element.setAttribute(arguments[1], arguments[2]);""", web_element, attribute, value)
