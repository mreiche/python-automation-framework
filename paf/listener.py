from abc import abstractmethod

from paf.assertion import AbstractAssertion


class Listener:
    def action_passed(self, action_name: str):  # pragma: no cover
        pass

    def action_failed(self, action_name: str, exception: Exception):  # pragma: no cover
        pass

    def action_failed_finally(self, action_name: str, exception: Exception):  # pragma: no cover
        pass

    def assertion_passed(self, assertion: AbstractAssertion):  # pragma: no cover
        pass

    def assertion_failed(self, assertion: AbstractAssertion, exception: Exception):  # pragma: no cover
        pass

    def assertion_failed_finally(self, assertion: AbstractAssertion, exception: Exception):  # pragma: no cover
        pass
