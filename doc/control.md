# Execution controlling

## Retry sequences

Usually, every action is capsuled by a retry sequence.

So when you have a text element

```python
from paf.uielement import UiElement

text_element: UiElement
```
the assertion is performed multiple times as defined in env variable `PAF_SEQUENCE_RETRY_COUNT`.

```python
text_element.expect.count.be(1)
```

But if you want to perform multiple actions in a retry sequence, you can use the following code.

```python
import inject
from paf.control import Control

control = inject.instance(Control)

control.retry(lambda: text_element.expect.count.be(1))
```

If you want to perform an action when the conditions failed, use the following construct.

This will refresh the page until the text element is present.

```python
control.retry(lambda: text_element.expect.count.be(1), lambda: text_element.webdriver.refresh())
```

You can also tweak the execution a bit, by overriding timings for the sequence.

```python
control.retry(
    action=lambda: text_element.expect.count.be(1),
    on_fail=lambda: text_element.webdriver.refresh(),
    count=3,
    wait_after_fail=0
)
```
