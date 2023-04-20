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
