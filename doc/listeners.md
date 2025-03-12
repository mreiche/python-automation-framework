from selenium.webdriver.remote.webdriver import WebDriver

# Listeners

*PAF* provides some listener interfaces to intercept internals.

* `ActionListener`: Listens to element actions
* `AssertionListener`: Listens to element assertions
* `WebDriverManagerListener`: Listen to the lifecycle of a *WebDriver*.

## HighlightListener

Highlights actions and assertions on the element. Gets automatically injected when `PAF_DEMO_MODE` is enabled.

## Custom listeners

Implement your custom listener the following way.

```python
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.remote.webdriver import WebDriver
from paf.listener import ActionListener, WebDriverManagerListener
from paf.uielement import UiElement

class MyListener(ActionListener, WebDriverManagerListener, AbstractEventListener):
    # Use this method to handle passed actions
    def action_passed(self, action_name: str, ui_element: UiElement):
        pass
    
    # Use the introduce method to wrap or modify your WebDriver
    def webdriver_introduce(self, webdriver: WebDriver):
        return EventFiringWebDriver(webdriver, self)

    # Use this method to do something right before shutting down the WebDriver
    def before_quit(self, webdriver: WebDriver):
        webdriver.get_cookies()
```
You need to inject your listener at configuration level like:
```python
import inject
from inject import Binder
import paf.config
from paf.listener import ActionListener, WebDriverManagerListener

def _inject(binder: Binder):
    binder.install(paf.config.inject)
    my_listener = MyListener()
    binder.bind(ActionListener, my_listener)
    binder.bind(WebDriverManagerListener, my_listener)

inject.configure(_inject)
```
Make sure, that the environment variable is `PAF_DEMO_MODE=0`, to prevent a duplicate injection of *HighlightListener*. 
