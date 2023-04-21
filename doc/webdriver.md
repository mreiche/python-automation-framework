# WebDriver management

## Request a WebDriver session

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

```python
import inject
from paf.manager import WebDriverManager

manager = inject.instance(WebDriverManager)
webdriver = manager.get_webdriver()
```

## Request multiple WebDriver sessions

Request a WebDriver with another request name 
```python
import inject
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest

manager = inject.instance(WebDriverManager)
request = WebDriverRequest("another")
webdriver = manager.get_webdriver(request)
```

## Shutdown WebDriver sessions

```python
import inject
from paf.manager import WebDriverManager
from paf.request import WebDriverRequest

manager = inject.instance(WebDriverManager)
request = WebDriverRequest()
webdriver = manager.get_webdriver()

manager.shutdown(webdriver)
manager.shutdown_session(request.session)
manager.shutdown_all()
```

## Take screenshot
```python
manager.take_screenshot()
```
