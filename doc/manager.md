# WebDriver management

## Request a WebDriver session

This configures a default *WebDriver*

```python
import inject
import paf.config
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest
from selenium.webdriver import ChromeOptions
from paf.common import Size

inject.configure(paf.config.inject)

request = WebDriverRequest()
request.browser = "chrome"
request.browser_version = "90"
request.options = ChromeOptions()
request.window_size = Size(1920, 1080)

manager = inject.instance(WebDriverManager)
webdriver = manager.get_webdriver(request)
```

## Reuse a WebDriver session

When no *WebDriverRequest* is passed, the default *WebDriver* will be returned.

```python
webdriver = manager.get_webdriver()
```

## Request multiple WebDriver sessions

Request a WebDriver with another request name 
```python
request = WebDriverRequest("another")
webdriver = manager.get_webdriver(request)

# Get the request name of a WebDriver sessions
name = manager.get_request_name(webdriver)
assert name == "another"
```

## Connect to Selenium

```python
request = WebDriverRequest()
request.server_url = "http://remote.server:4444"
webdriver = manager.get_webdriver(request)
```

## Introduce a preconfigured WebDriver

If you need fine-tuned *WebDrivers*, you can pass them as default.

```python
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service

webdriver = Chrome(Service(executable_path="/opt/chromedriver"))
# Make sure you update your webdriver reference
webdriver = manager.introduce_webdriver(webdriver, WebDriverRequest())
```
You can also use the [WebDriverManagerListener interface](listeners.md).


## Shutdown WebDriver sessions

```python
request = WebDriverRequest()
webdriver = manager.get_webdriver()

manager.shutdown(webdriver)
manager.shutdown_session(request.name)
manager.shutdown_all()
```

## Take screenshot
```python
try:
    path = manager.take_screenshot()
    assert path is not None
except Exception as e:
    logger.error(f"Unable to take screenshot because of: {e}")
```
