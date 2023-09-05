import dataclasses

from paf.control import change, __get_global_config, retry


def test_config():

    backup = dataclasses.replace(__get_global_config())
    assert backup.retry_count != 99
    assert backup.wait_after_fail != 99

    with change(retry_count=99, wait_after_fail=99):
        global_config = __get_global_config()
        assert global_config.wait_after_fail == 99
        assert global_config.retry_count == 99
        retry(lambda: None)

    global_config = __get_global_config()
    assert global_config.retry_count == backup.retry_count
    assert global_config.wait_after_fail == backup.wait_after_fail
