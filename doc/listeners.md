# Listeners

*PAF* provides some listener interfaces to intercept internals.

* `ActionListener`: Listens to element actions
* `AssertionListener`: Listens to element assertions
* `WebDriverManagerListener`: Listen to the lifecycle of a *WebDriver*

## HighlightListener

Highlights actions and assertions on the element. Gets automatically injected when `PAF_DEMO_MODE` is enabled.

## Custom listeners

Implement your custom listener the following way

```python
from paf.listener import ActionListener, WebDriverManagerListener
from paf.uielement import UiElement

class MyListener(ActionListener, WebDriverManagerListener):
    def action_passed(self, action_name: str, ui_element: UiElement):
        pass
    def webdriver_closed(self, webdriver: WebDriver):
        pass
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
