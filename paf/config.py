from inject import Binder

import paf.webdrivermanager
import paf.page


def inject(binder: Binder):
    binder.install(paf.webdrivermanager.inject_config)
    binder.install(paf.page.inject_config)
