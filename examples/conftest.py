import os

import inject
import pytest

import paf.config
from paf.common import Property


@pytest.fixture(scope="session", autouse=True)
def configure_inject():
    os.environ[Property.PAF_DEMO_MODE.name] = "1"
    inject.configure(paf.config.inject)
