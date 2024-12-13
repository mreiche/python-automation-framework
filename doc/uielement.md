# UiElement

*UiElements* are adapters for *WebElements*, but they do not contain a reference, but only a locator instead, which will lookup for the according *WebElement* everytime.
Additionally, every action performed or property read is capsuled in a retry sequence.

You can create *UiElements* using [Locators](locators.md) and organize them in [Pages](page_objects.md) and [Components](components.md).

## Actions
```python
from paf.uielement import UiElement
from paf.locator import By

ui_element: UiElement

# Performs a click on the element
ui_element.click()

# Hovers an element
ui_element.hover()

# Performs a context click on the element
ui_element.context_click()

# Performs a double click on the element
ui_element.double_click()

# Drags and drops an element to a target element
ui_element.drag_and_drop_to(target)

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
with ui_element.find_web_element() as web_element:
    pass
```

## Asserting conditions
```python
from paf.uielement import UiElement
ui_element: UiElement

# Element is display
ui_element.expect.displayed(True)

# Element is enabled
ui_element.expect.enabled(True)

# Element is selected
ui_element.expect.selected(True)

# Element text equals a case sensitive string
ui_element.expect.text.be("Hello")

# Element text equals a lower case string
ui_element.expect.text.map(str.lower).be("hello")

# Element text contains a string
ui_element.expect.text.contains("World").be(True)

# Element text contains the following words
ui_element.expect.text.has_words("Hello", "World").be(True)

# Element text matches regular expression
ui_element.expect.text.matches("d\sW").be(True)

# Element's CSS property equals a value
ui_element.expect.css("display").be("block")

# Element has classes "main" and "nav"
ui_element.expect.classes("main", "nav").be(True)

# Element's "max-length" attribute is greater or equal than 3
ui_element.expect.attribute("max-length").greater_equal_than(3).be(True)

# Element's value is between 3 and 5
ui_element.expect.value.between(3, 5).be(True)

# Element bounds intersects with the browsers viewport
ui_element.expect.visible(True)

# Element bounds are inside the browsers viewport
ui_element.expect.fully_visible(True)

# Take screenshot
path = ui_element.take_screenshot()
```

The advantage of this chained assertion API is,
that you can easily perform multiple assertions on the same property.
```python
text = ui_element.expect.text

text.not_be("Wrong")
text.starts_with("Hello").be(True)
text.map(str.upper).ends_with("WELCOME").be(True)
text.length.between(10, 20).be(True)
```

## Waiting for conditions

Instead of `expect`, use write `wait_for` to prevent raising `AssertionError`.

```python
if ui_element.wait_for.enabled.be(True):
    ui_element.click()
```

## Reading values

You can also read the actual value of the assertions.

```python
text = ui_element.expect.text.actual
```


## Element lists

All actions on *UiElement* are performed on the first found element by default. But you can access other elements the following way.

```python
first = ui_element.first
last = ui_element.last
second = ui_element[1]
```

To get the amount of found elements use:
```python
count = ui_element.expect.count.actual
```

You can also iterate over all found items:

```python
for item in ui_element:
    pass
```

## Shadow root support
When you identify shadow root elements, the `find()` method will search within the element's shadow root. 
```python
from paf.page import FinderPage

finder: FinderPage

element_with_shadow_root = finder.find("my-shadow-root-component")
element_with_shadow_root.find("h1").expect.text.be("Component headline")
```

## Frames support
When you identify frame elements, the `find()` method will automatically switch to the frame's context.

```python
frame = finder.find("frame")
frame.find("div").expect.text.be("Text in frame")
```

## Inexistent elements

If you know, that an element doesn't exists and you won't break the API, you can create an `InexistentUiElement`.

```python
from paf.uielement import InexistentUiElement

def get_switch():
    return InexistentUiElement()
```
