## Page Objects

Page objects are adapters for Websites, that provide methods and actions for their features.

For example: Create a page object, that represents the start page of a website.
```python
from paf.page import Page
from paf.locator import By
from pages import UserPage

class StartPage(Page):
    def login(self, username: str, password: str):
        self._find("#username").type(username)
        self._find("#password").type(password)
        self._find("#login").click()
        return self._create_page(UserPage)
```

This page provides the method `login` which leads to the `UserPage`.

```python
from paf.page import Page
from paf.locator import By
from paf.uielement import TestableUiElement

class UserPage(Page):
    @property
    def greeter(self) -> TestableUiElement:
        return self._find("#greeter")
```

The `UserPage` provides a property named `greeter`, which may be a container for login messages.

You can combine these pages now the following way. 

```python
import inject
import paf.config
from paf.page import PageFactory
from pages import StartPage

inject.configure(paf.config.inject)
page_factory = inject.instance(PageFactory)

start_page = page_factory.create_page(StartPage)
user_page = start_page.login("user", "secret")
user_page.greeter.expect.text.contains("Welcome").be(True)
```
