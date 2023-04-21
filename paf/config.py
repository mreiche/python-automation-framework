from inject import Binder

import paf.manager
import paf.page
import paf.control


def inject(binder: Binder):
    binder.install(paf.manager.inject_config)
    binder.install(paf.page.inject_config)
    binder.install(paf.control.inject_config)