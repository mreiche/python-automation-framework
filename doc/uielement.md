# UiElement features

## Actions
```python
from paf.uielement import UiElement
from paf.locator import By

ui_element: UiElement

# Performs a click on the element
ui_element.click()

# Types the string to the element and checks it's value
ui_element.type("Hello World")

# Sends keys to the element
ui_element.send_keys("Hello World")

# Clears the element
ui_element.clear()

# Highlights an element using Javascript
ui_element.highlight()

# Scrolls an element into the viewport using Javascript
ui_element.scroll_into_view()

# Scrolls an element to the top of the viewport using Javascript
ui_element.scroll_to_top()

# Finds another element below this element
ui_element.find(By.name("div"))

# Find the according WebElement
ui_element.find_web_element(lambda web_element: None)
```

## Asserting conditions
```python
from paf.uielement import UiElement
ui_element: UiElement

# Element is display
ui_element.expect.displayed.be(True)

# Element is enabled
ui_element.expect.enabled.be(True)

# Element is selected
ui_element.expect.selected.be(True)

# Element text equals "Hello"
ui_element.expect.text.be("Hello")

# Element text contains "World"
ui_element.expect.text.contains("World").be(True)

# Element text matches regular expression
ui_element.expect.text.matches("d\sW").be(True)

# Element's CSS property equals a value
ui_element.expect.css("display").be("block")

# Element's "max-length" attribute is greater or equal than 3
ui_element.expect.attribute("max-length").greater_equal_than(3).be(True)

# Element's value is between 3 and 5
ui_element.expect.value.between(3, 5).be(True)

# Element bounds intersects with the browsers viewport
ui_element.expect.visible.be(True)

# Element bounds are inside the browsers viewport
ui_element.expect.fully_visible.be(True)
```

## Waiting for conditions

Instead of `expect`, use write `wait_for` to prevent raising `AssertionError`.

```python
from paf.uielement import UiElement
ui_element: UiElement

if ui_element.wait_for.enabled.be(True):
    ui_element.click()
```

## Reading values

You can also read the actual value of the assertions.

```python
from paf.uielement import UiElement
ui_element: UiElement

text = ui_element.expect.text.actual
```
