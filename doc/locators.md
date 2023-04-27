# Locators

Adapters like [Pages](pages.md), [Components](components.md) or [UiElements](uielement.md), provide public `find()` or protected `_find()` methods to locate *UiElements*.

You can create a *FinderPage*, which is simple *Page* implementation with a public `find()` method.

```python
from paf.page import FinderPage
from paf.locator import By
from paf.xpath import XPath

page = page_factory.create_page(FinderPage)

# Locate element by id
page.find(By.id("id"))

# Locate element by CSS selector
page.find("#id")

# Same as above
page.find(By.css_selector("#id"))

# Locate element by name
page.find(By.name("email"))

# Locate element by name
page.find(By.class_name("class"))

# Locate element by tag name
page.find(By.tag_name("input"))

# Locate element by XPath string
page.find(By.xpath("//body"))

# Locate element by XPath object
page.find(XPath.at("div"))
```

## More locator features

The *By* locator supports some more useful features.

```python
from paf.locator import By

# Locate only display items
By.id("id").displayed

# Locate only unique elements
By.name("email").unique

# Locate elements using filters
By.tag_name("input").filter(lambda web_element: web_element.is_selected())
```

## XPath

`find()` methods also accept instances of the `XPath` builder. It helps to create failsafe XPaths with common useful features.

```python
from paf.xpath import XPath

# //body
XPath.at("body")

# /body
XPath.at("/body")

# //body//div
XPath.at("body").select("div")

# //div[//a]
XPath.at("div").encloses("a")

# //div[@name='input']
XPath.at("div").attribute("name").be("input")
```

### More complex queries

Locate by text words

```python
XPath.at("div").select("span").text.contains("Hello")
```
```html
<div><span>Hallo</span</div>
<div><span>Cava</span</div>
<div>
  <span>Hello World</span> <!-- Located -->
</div>
```

```python
XPath.at("div").encloses("span").text.contains("Hello")
```
```html
<div><span>Hallo</span</div>
<div><span>Cava</span</div>
<div><span>Hello World</span></div> <!-- Located -->
```

Locate by classes
```python
XPath.at("div").classes("one", "three")
```
```html
<div class="one two">One</div>
<div class="one two three">Two</div> <!-- Located -->
<div class="three">Three</div>
```


Locate siblings

```python
XPath.at("li").text.be("Title").following("/li")
```

```html
<li>Title</li>
<li>Hello World</li> <!-- Located -->
```

Positions

```python
XPath.at("ul").select("li", -1)
```
```html
<ul>
  <li>One</li>
  <li>Two</li>
  <li>Three</li> <!-- Located -->
</ul>
```
