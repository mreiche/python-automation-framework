from paf.locator import By
from paf.xpath import XPath


def test_text_functions():
    assert str(XPath.at("myElement").text.be("Exakt")) == "//myElement[.//text()='Exakt']"
    assert str(XPath.at("myElement").text.contains("Contains")) == "//myElement[contains(.//text(),'Contains')]"
    assert str(XPath.at("myElement").text.starts_with("Start")) == "//myElement[starts-with(.//text(),'Start')]"
    assert str(XPath.at("myElement").text.ends_with("End")) == "//myElement[ends-with(.//text(),'End')]"


def test_deep_selection():
    assert str(XPath.at("button").attribute("data-qa").present.encloses("span").text.be("Klick mich")) == "//button[@data-qa and descendant::span[.//text()='Klick mich']]"


def test_XPath_with_XPath():
    assert str(XPath.at("body").encloses(XPath.at("div"))) == "//body[descendant::div]"


def test_XPath_with_By():
    assert str(XPath.at("body").encloses(By.tag_name("div"))) == "//body[descendant::div]"


def test_select_sibling():
    assert str(XPath.at("body").select("dd").text.be("Title").following("/dt")) == "//body//dd[.//text()='Title']/following-sibling::dt"
    assert str(XPath.at("body").select("dd").text.be("Title").following("dt")) == "//body//dd[.//text()='Title']/following::dt"
    assert str(XPath.at("body").select("dd").text.be("Title").preceding("/dt")) == "//body//dd[.//text()='Title']/preceding-sibling::dt"
    assert str(XPath.at("body").select("dd").text.be("Title").preceding("dt")) == "//body//dd[.//text()='Title']/preceding::dt"


def test_class_selection():
    assert str(XPath.at("body").select("nav").classes("container")) == "//body//nav[contains(concat(' ', normalize-space(@class), ' '), ' container ')]"


def test_position():
    assert str(XPath.at("body", 1)) == "//body[1]"
    assert str(XPath.at("body", 0)) == "//body[1]"
    assert str(XPath.at("body", -1)) == "//body[last()]"
