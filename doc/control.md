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
from paf.control import retry

retry(lambda: text_element.expect.count.be(1))
```

If you want to perform an action when the conditions failed, use the following construct.

This will refresh the page until the text element is present.

```python
retry(lambda: text_element.expect.count.be(1), lambda: text_element.webdriver.refresh())
```

You can also tweak the execution a bit, by overriding timings for the sequence.

```python
from paf.control import change

with change(retry_count=3, wait_after_fail=0):
    retry(lambda: text_element.expect.count.be(1), lambda: text_element.webdriver.refresh())
```
