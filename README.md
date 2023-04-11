# Python automation framework

Python implementation of [Testerra](https://github.com/telekom/testerra) API.

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

# Find elements
element = page.find(By.id("q"))

# Perform actions
element.click()

# Perform assertions
element.expect.text.be("Clicked")

# Shutdown all sessions
manager.shutdown_all()
```


## Missing features (todos)

- list support
- components support
- full assertions support
- full actions support
