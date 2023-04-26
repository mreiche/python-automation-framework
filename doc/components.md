## Components

Components are like page objects, adapters for Website features. But different from that, they contain one root element as it's DOM origin. They can be seen as hybrids between [Page](page_objects.md) and [UiElement](uielement.md).

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
