# Python automation framework

Python implementation of [Testerra](https://github.com/telekom/testerra) API.

This is not a test framework, but it implements some assertion features anyway.

## Prerequisites

**MacOS**
```shell
brew install chromedriver
```

**Windows**
```shell
choco install chromedriver
```
**Linux**
```shell
apt install chromedriver
```

## Quick start

```python
import inject
import paf.config
from paf.locator import By
from paf.page import FinderPage, PageFactory
from paf.manager import WebDriverManager

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
element.type("Search")

# Perform assertions
element.expect.text.be("Search")
```





## Feature list

- [UiElement features](doc/uielement.md)
- [Page objects](doc/page_objects.md)
- [Components](doc/components.md)
- [Managing WebDrivers](doc/webdriver.md)

### Missing features (todos)

#### Assertions
- Rect

#### Actions
- ContextClick/DoubleClick

## Environment variables

* `PAF_BROWSER_SETTING=chrome:90`: Sets the requested browser name and it's version.
* `PAF_WINDOW_SIZE=1920x1080`: Sets the browsers default window size.
* `PAF_SCREENSHOTS_DIR=screenshots`: Sets the screenshots directory.


## Run the tests
```shell
PYTHONPATH="." pytest --numprocesses=4 test
```

## Utils

```javascript
xpath = "//dt[.//text()='Title:']/following-sibling::dd[1]"
snapshot = document.evaluate(xpath, document.body, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE)
snapshot.snapshotItem(0).textContent
```
