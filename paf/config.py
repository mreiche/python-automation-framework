from inject import Binder

import paf.common
import paf.control
import paf.manager
import paf.page
from paf.common import Property
from paf.listener import Listener, HighlightListener


def inject(binder: Binder):
    binder.install(paf.manager.inject_config)
    binder.install(paf.page.inject_config)
    binder.install(paf.common.inject_config)
    if Property.env(Property.PAF_DEMO_MODE) == "1":
        binder.bind(Listener, HighlightListener())
