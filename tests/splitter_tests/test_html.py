from missing_text.splitter.html import (
    html_tag_attribute_splitter,
    html_element_attribute_splitter,
)


def test_html_tag_attribute_splitter():
    html_content = "<div>Hello</div><p>World</p><div>Example</div>"
    assert html_tag_attribute_splitter(html_content, "div") == ["Hello", "Example"]


def test_html_tag_attribute_splitter_with_nested_tags():
    html_content = "<div>Outer <span>Inner</span> Text</div>"
    assert html_tag_attribute_splitter(html_content, "div") == ["Outer Inner Text"]
    assert html_tag_attribute_splitter(html_content, "span") == ["Inner"]


def test_html_element_attribute_splitter():
    html_content = '<img src="image1.jpg"><img src="image2.jpg">'
    assert html_element_attribute_splitter(html_content, "img", "src") == [
        "image1.jpg",
        "image2.jpg",
    ]


def test_html_element_attribute_splitter_with_missing_attributes():
    html_content = '<img src="image1.jpg"><img><img src="image2.jpg">'
    assert html_element_attribute_splitter(html_content, "img", "src") == [
        "image1.jpg",
        "image2.jpg",
    ]
