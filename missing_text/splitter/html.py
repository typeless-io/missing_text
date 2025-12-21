"""Functions for HTML-based text splitting."""


def html_tag_attribute_splitter(
    html_content: str, tag: str, attribute: str = None
) -> list[str]:
    """
    Extracts and splits content within specified HTML tags.

    Args:
        html_content (str): The HTML content to be processed.
        tag (str): The HTML tag to retrieve content from (e.g., 'p', 'div', 'span').
        attribute (str, optional): The attribute to extract. Defaults to None.

    Returns:
        list of str: A list containing the content found within the specified HTML tags.

    Example:
        >>> html_content = "<div>Hello</div><p>World</p><div>Example</div>"
        >>> html_tag_attribute_splitter(html_content, "div")
        ['Hello', 'Example']
    """
    from bs4 import BeautifulSoup

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find and extract all content within the specified tags
    return [element.get_text(strip=False) for element in soup.find_all(tag)]


def html_element_attribute_splitter(
    html_content: str, tag: str, attribute: str
) -> list[str]:
    """
    Extracts and returns the values of a specified attribute from HTML tags.

    Args:
        html_content (str): The HTML content to be processed.
        tag (str): The HTML tag to search for (e.g., 'img', 'a').
        attribute (str): The attribute whose values need to be extracted (e.g., 'src', 'href').

    Returns:
        list of str: A list of attribute values from the specified tags.

    Example:
        >>> html_content = '<img src="image1.jpg"><img src="image2.jpg">'
        >>> html_element_attribute_splitter(html_content, "img", "src")
        ['image1.jpg', 'image2.jpg']
    """
    from bs4 import BeautifulSoup

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all elements with the specified tag and extract the attribute values
    return [
        element.get(attribute)
        for element in soup.find_all(tag)
        if element.get(attribute)
    ]
