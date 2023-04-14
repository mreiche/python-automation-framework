# Python automation framework

Python implementation of [Testerra](https://github.com/telekom/testerra) API.

## Usage
```python
from core.by import By
from core.page import Page
from core.webdrivermanager import WebDriverManager

# Create WebDriverManager
manager = WebDriverManager()

# Get the WebDriver
webdriver = manager.get_webdriver()

# Create a page
page = Page(webdriver)

# Visit URL
page.open("http://google.com")

# Find element
element = page.find(By.id("q"))

# Perform actions
element.click()

# Perform assertions
element.expect.text.be("Clicked")

# Shutdown all sessions
manager.shutdown_all()
```

## Page Objects
```python
from core.page import Page
from core.by import By
from core.uielement import TestableUiElement
from selenium.webdriver.remote.webdriver import WebDriver
from core.webdrivermanager import WebDriverManager

class StartPage(Page):
    def __init__(self, webdriver: WebDriver):
        super().__init__(webdriver)
        self._greeter = self.find(By.id("greeter"))
    
    @property
    def greeter(self) -> TestableUiElement:
        return self._greeter

class LoginPage(Page):
    def __init__(self, webdriver: WebDriver):
        super().__init__(webdriver)
        self._login_btn = self.find(By.id("login"))
        
    def login(self):
        self._login_btn.click()
        return self.create_page(StartPage)

manager = WebDriverManager()
webdriver = manager.get_webdriver()
login_page = LoginPage(webdriver)
start_page = login_page.login()
start_page.greeter.expect.text.be("Welcome")
```
## Components
*tbd*

## Missing features (todos)

### WebDriver
- Configuration hooks

### Assertions
- Screenshots
- Rect

### Actions
- Scroll To
- Highlight
- ContextClick/DoubleClick
