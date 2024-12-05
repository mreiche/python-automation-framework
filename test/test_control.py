import dataclasses
from time import sleep

from paf.common import Property
from paf.control import change, get_config, retry


def test_change():

    backup_config = dataclasses.replace(get_config())
    assert backup_config.retry_count != 99
    assert backup_config.wait_after_fail != 99

    with change(retry_count=99, wait_after_fail=99):
        global_config = get_config()
        assert global_config.wait_after_fail == 99
        assert global_config.retry_count == 99
        retry(lambda: None)

    global_config = get_config()
    assert global_config.retry_count == backup_config.retry_count
    assert global_config.wait_after_fail == backup_config.wait_after_fail


def test_change_first():
    global_config = get_config()
    assert global_config.retry_count == Property.env(Property.PAF_SEQUENCE_RETRY_COUNT)

    with change(retry_count=0):
        sleep(0.3)
        config = get_config()
        assert config.retry_count == 0


def test_change_second():
    global_config = get_config()
    assert global_config.retry_count == Property.env(Property.PAF_SEQUENCE_RETRY_COUNT)

    with change(retry_count=99):
        sleep(0.1)
        config = get_config()
        assert config.retry_count == 99
