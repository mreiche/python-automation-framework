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
