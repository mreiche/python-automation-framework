import dataclasses

from paf.control import config, __get_global_config, retry


def test_config():

    backup = dataclasses.replace(__get_global_config())

    with config(count=99, wait_after_fail=99):
        global_config = __get_global_config()
        assert global_config.wait_after_fail == 99
        assert global_config.retry_count == 99
        retry(lambda: None)

    global_config = __get_global_config()
    assert global_config.retry_count == backup.retry_count
    assert global_config.wait_after_fail == backup.wait_after_fail
