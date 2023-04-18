# Python automation framework

Python implementation of [Testerra](https://github.com/telekom/testerra) API.
This is not a test framework, but it implements some assertion features anyway.

## Usage

```python
import inject

from paf.locator import By
from paf.page import FinderPage, PageFactory
from paf.webdrivermanager import WebDriverManager
import paf.config

# Configure dependency injection
inject.configure(paf.config.inject)

# Instantiate the page factory
page_factory = inject.instance(PageFactory)

# Create a simple finder page
page = page_factory.create_page(FinderPage)

# Visit URL
page.open("https://google.com")

# Find element
element = page.find(By.id("q"))

# Perform actions
element.click()

# Perform assertions
element.expect.text.be("Clicked")

# Get the WebDriverManager instance
manager = inject.instance(WebDriverManager)

# Shutdown all sessions
manager.shutdown_all()
```

## Page Objects

More detailed page objects.

```python
import inject
import paf.config
from paf.page import Page, PageFactory
from paf.locator import By
from paf.uielement import TestableUiElement

class StartPage(Page):
    @property
    def greeter(self) -> TestableUiElement:
        return self._find(By.id("greeter"))


class LoginPage(Page):
    @property
    def _login_btn(self):
        return self._find(By.id("login"))

    def login(self):
        self._login_btn.click()
        return self._create_page(StartPage)

inject.configure(paf.config.inject)
page_factory = inject.instance(PageFactory)
login_page = page_factory.create_page(LoginPage)
start_page = login_page.login()
start_page.greeter.expect.text.be("Welcome")
```

## Components

Components are custom element containers.

```python
import inject
import paf.config
from paf.locator import By
from paf.component import Component
from paf.page import Page, PageFactory


class MyComponent(Component["MyComponent"]):
    @property
    def input(self):
        return self._find(By.id("input"))


class MyPage(Page):
    @property
    def custom_component(self):
        return self._create_component(MyComponent, self._find(By.tag_name("body")))


inject.configure(paf.config.inject)
page_factory = inject.instance(PageFactory)
page = page_factory.create_page(MyPage)
page.custom_component.input.type("Hello World")
```

## Missing features (todos)

### WebDriver
- Configuration hooks

### Assertions
- Screenshots
- Rect

### Actions
- Highlight
- ContextClick/DoubleClick

## Utils

```javascript
xpath = "//dt[.//text()='Title:']/following-sibling::dd[1]"
snapshot = document.evaluate(xpath, document.body, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE)
snapshot.snapshotItem(0).textContent
```
