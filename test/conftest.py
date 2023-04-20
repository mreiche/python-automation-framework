import inject
import pytest

import paf.config


@pytest.fixture(scope="session", autouse=True)
def configure_inject():
    inject.configure(paf.config.inject)
