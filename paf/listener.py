import logging

from selenium.webdriver.support.color import Color

from paf import javascript
from paf.assertion import AbstractAssertion
from paf.common import NotFoundException


class Listener:
    def action_passed(
        self,
        action_name: str,
        ui_element: "UiElement"
    ):  # pragma: no cover
        pass

    def action_failed(
        self,
        action_name: str,
        ui_element: "UiElement",
        exception: Exception
    ):  # pragma: no cover
        pass

    def action_failed_finally(
        self,
        action_name: str,
        ui_element: "UiElement",
        exception: Exception
    ):  # pragma: no cover
        pass

    def assertion_passed(
        self,
        assertion: AbstractAssertion,
        ui_element: "UiElement"
    ):  # pragma: no cover
        pass

    def assertion_failed(
        self,
        assertion: AbstractAssertion,
        ui_element: "UiElement",
        exception: Exception
    ):  # pragma: no cover
        pass

    def assertion_failed_finally(
        self,
        assertion: AbstractAssertion,
        ui_element: "UiElement",
        exception: Exception
    ):  # pragma: no cover
        pass


class HighlightListener(Listener):

    def _highlight_with_color(self, ui_element: "UiElement", color: str):
        try:
            with ui_element.find_web_element() as web_element:
                javascript.highlight(ui_element.webdriver, web_element, Color.from_string(color))

        except Exception as e:
            logging.warning(f"Cannot highlight {ui_element.name_path}: {e}")

    def action_passed(
        self,
        action_name: str,
        ui_element: "UiElement"
    ):
        if action_name == "highlight":
            return

        self._highlight_with_color(ui_element, "#ff0")

    def action_failed_finally(
        self,
        action_name: str,
        ui_element: "UiElement",
        exception: Exception
    ):
        if action_name == "highlight":
            return

        if not isinstance(exception, NotFoundException):
            self._highlight_with_color(ui_element, "#f00")

    def assertion_passed(
        self,
        assertion: AbstractAssertion,
        ui_element: "UiElement"
    ):
        if assertion.raise_exception:
            self._highlight_with_color(ui_element, "#0f0")

    def assertion_failed_finally(
        self,
        assertion: AbstractAssertion,
        ui_element: "UiElement",
        exception: Exception
    ):
        if not isinstance(exception, NotFoundException) and assertion.raise_exception:
            self._highlight_with_color(ui_element, "#f00")
