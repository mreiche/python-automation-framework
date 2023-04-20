# UiElement features

```python
from paf.uielement import UiElement
from paf.locator import By

ui_element: UiElement

# Highlights an element using Javascript
ui_element.highlight()

# Scrolls an element into the viewport using Javascript
ui_element.scroll_into_view()

# Scrolls an element to the top of the viewport using Javascript
ui_element.scroll_to_top()

# Finds another element below this element
ui_element.find(By.name("div"))
```

-
