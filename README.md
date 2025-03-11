[![Pypi](https://img.shields.io/pypi/v/python-automation-framework.svg)](https://pypi.org/project/python-automation-framework)
![Tests Status](https://github.com/mreiche/python-automation-framework/actions/workflows/integration-tests.yml/badge.svg)
[![Code Coverage Status](https://codecov.io/github/mreiche/python-automation-framework/branch/main/graph/badge.svg)](https://app.codecov.io/github/mreiche/python-automation-framework)


# PAF - Python Automation Framework

Python implementation of [Testerra](https://github.com/telekom/testerra) API.

It is basically a wrapper for Selenium *WebDriver* and *WebElement* which brings some more comfort features.
This is not a test framework, but it implements assertion features anyway.

The basic concept is, to identify *WebElements* on every action or property accessor to prevent `StaleElementExceptions`.

## Quick start

```python
import inject
import paf.config
from paf.locator import By
from paf.page import FinderPage, PageFactory

# Configure dependency injection
inject.configure(paf.config.inject)

# Instantiate the page factory
page_factory = inject.instance(PageFactory)

# Create a simple finder page
page = page_factory.create_page(FinderPage)

# Visit URL
page.open("https://google.com")

# Find element
element = page.find("#q")

# Perform actions
element.type("Search")

# Perform assertions
element.expect.text.be("Search")
```

### Prerequisites

- You need at least a local *WebDriver* installed.
   ```shell
   brew|choco|apt install chromedriver
   ```

- Python 3.10 (or higher).

## Feature list

- [UiElements](doc/uielement.md)
- [Locators](doc/locators.md)
- [Page objects](doc/pages.md)
- [Components](doc/components.md)
- [Managing WebDrivers](doc/manager.md)
- [Execution controlling](doc/control.md)
- [Inject listener](doc/listeners.md)

### Missing features (tdb)

- Rect assertions
- Drag & Drop over frames

## Environment variables

* `PAF_BROWSER_SETTING=chrome:90`: Sets the requested browser name and it's version.
* `PAF_WINDOW_SIZE=1920x1080`: Sets the browsers initial window size.
* `PAF_WINDOW_POSITION=0x0`: Place the initial window to a different location/screen.
* `PAF_WINDOW_MAXIMIZE=False`: Maximize the initial window.
* `PAF_SCREENSHOTS_DIR=screenshots`: Sets the screenshots' directory.
* `PAF_SEQUENCE_WAIT_AFTER_FAIL=0.3`: Wait in seconds whenever a sequence action fails. 
* `PAF_SEQUENCE_RETRY_COUNT=3`: Retry count for every sequence action.
* `PAF_DEMO_MODE=0`: Enables the demo mode by highlighting actions and assertions.
* `PAF_SELENIUM_SERVER_URL=http://127.0.0.1:4444`: Uses Selenium server if set.
* `PAF_DRIVER_PATH`: Path to Webdriver binary
* `PAF_BINARY_PATH`: Path to User agent's binary

## Examples

Some real world examples.

1. [test_google.py](examples/test_google.py): is a regular Google search, implemented with [Page Objects](doc/pages.md) and [Components](doc/components.md). 
2. [test_todo_mvc.py](examples/test_todo_mvc.py): are re-implemented test cases from the [Robot Framework TodoMVC](https://docs.robotframework.org/docs/examples/todo) example. It's IMHO developer friendly, better readable and less code. 
3. [test_asyncio.py](examples/test_asyncio.py): Parallel execution via `asyncio`.
4. [test_monkeytype.py](examples/test_monkeytype.py): Typing test on https://monkeytype.com

## Comparison

Comparison of the syntax with other frameworks.

**Pylenium**
```python
py.get("a[href='/about']").should().have_text("About")

find("a[href='/about']").expect.text.be("About")
```
**SeleniumBase**
```python
self.assert_text_not_visible("Thanks for your purchase.", "#app .success")

find("#app .success").expect.text.not_be("Thanks for your purchase.")
```
**Selene**
```python
browser.all('#rso>div').should(have.size_greater_than(5)) \
    .first.should(have.text('Selenium automates browsers'))

div = find("#rso>div")
div.expect.count.greater_than(5).be(True)
div.first.expect.text.be("Selenium automates browsers")
```

References: https://www.nextgenerationautomation.com/post/python-test-automation-frameworks

## Developer area

### Testing
#### Run the tests on your local machine
```shell
PAF_TEST_HEADLESS=1 PAF_TEST_LOCAL_SELENIUM=0 pytest --cov=paf -n=4 test
```

#### Build test base container (for use in GitHub Actions)
```shell
podman build -f ubuntu-base.Dockerfile --arch=amd64 -t paf-test-base:latest
source build.env
echo $DOCKER_CONTAINER_REGISTRY_TOKEN | podman login -u mreiche --password-stdin ghcr.io
podman push paf-test-base:latest docker://ghcr.io/mreiche/paf-test-base:latest
```

#### Build test runner container (for testing)
Run tests within container
```shell
podman run -e PAF_TEST_HEADLESS=1 -e PAF_TEST_CONTAINER=1 -e PAF_TEST_LOCAL_SELENIUM=0 paf-test-base:latest pytest --cov=paf -n=4 test
```

#### Run local selenium server
```shell
wget https://github.com/SeleniumHQ/selenium/releases/download/selenium-4.9.0/selenium-server-4.9.0.jar -O selenium-server.jar
java -jar selenium-server.jar standalone --host 127.0.0.1
```

### Debug XPaths in Browser's Developer Console

```javascript
xpath = "//dt[.//text()='Title:']/following-sibling::dd[1]"
snapshot = document.evaluate(xpath, document.body, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE)
snapshot.snapshotItem(0).textContent
```

### Release update
1. Update version in `setup.py`
2. Package library
    ```shell
    python setup.py sdist
    ```
3. Publish library
    ```shell
    twine upload dist/python_automation_framework-[version].tar.gz
    ```

### References
- https://stackoverflow.com/questions/64033686/how-can-i-use-private-docker-image-in-github-actions
- https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
- https://stackoverflow.com/questions/46052736/python-proxy-class
- https://chromedriver.chromium.org/
- Make stealth WebDriver: https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver
