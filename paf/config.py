from inject import Binder

import paf.common
import paf.control
import paf.manager
import paf.page
import paf.listener


def inject(binder: Binder):
    binder.install(paf.manager.inject_config)
    binder.install(paf.page.inject_config)
    binder.install(paf.common.inject_config)
    binder.install(paf.listener.inject_config)
