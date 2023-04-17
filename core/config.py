from inject import Binder

import core.webdrivermanager
import core.page


def inject(binder: Binder):
    binder.install(core.webdrivermanager.inject_config)
    binder.install(core.page.inject_config)
