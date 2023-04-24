# Execution controlling

## Retry sequences

```python
import inject
from paf.control import Control, Config
from paf.uielement import UiElement

control = inject.instance(Control)
text_element: UiElement

def _action():
    text_element.expect.count.be(1)    

def _on_fail():
    text_element.webdriver.refresh()

control.retry(_action, _on_fail, config=Config(retry_count=3, wait_after_fail=0))
```
