# Execution controlling

## Retry sequences

```python
import inject
from paf.control import Control
from paf.uielement import UiElement

control = inject.instance(Control)
text_element: UiElement

control.retry(
    action=lambda: text_element.expect.count.be(1),
    on_fail=lambda: text_element.webdriver.refresh(),
    count=3,
    wait_after_fail=0
)
```
