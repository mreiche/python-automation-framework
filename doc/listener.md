# Listener

The *Listener* interface provides methods that are called, when an action or assertion is performed.

Implement your custom listener the following way

```python
from paf.listener import Listener
from paf.uielement import UiElement

class MyListener(Listener):
    def action_passed(
        self,
        action_name: str,
        ui_element: UiElement
    ):
        pass
```
You need to inject your listener at configuration level like:
```python
import inject
from inject import Binder
import paf.config
from paf.listener import Listener

def _inject(binder: Binder):
    binder.install(paf.config.inject)
    binder.bind(Listener, MyListener())

inject.configure(_inject)
```
Make sure, that the environment variable is `PAF_DEMO_MODE=0`, to prevent a duplicate injection of *HighlightListener*. 
