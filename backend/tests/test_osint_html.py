from bs4 import BeautifulSoup
from bs4.element import Tag

from app.services.osint_service import _get_tag_attribute


def _tag(markup: str) -> Tag:
    element = BeautifulSoup(markup, "html.parser").find()
    assert isinstance(element, Tag)
    return element


def test_attribute_helper_handles_missing_attrs_mapping() -> None:
    tag = _tag("<meta content='summary'>")
    tag.attrs = None
    assert _get_tag_attribute(tag, "content") is None


def test_attribute_helper_handles_missing_attribute() -> None:
    assert _get_tag_attribute(_tag("<meta name='description'>"), "content") is None


def test_attribute_helper_returns_string_attribute() -> None:
    assert _get_tag_attribute(_tag("<meta content='summary'>"), "content") == "summary"


def test_attribute_helper_joins_multi_valued_attribute() -> None:
    assert _get_tag_attribute(_tag("<div class='alpha beta'>"), "class") == "alpha beta"


def test_attribute_helper_handles_empty_multi_valued_attribute() -> None:
    tag = _tag("<div class='alpha'>")
    tag.attrs["class"] = []
    assert _get_tag_attribute(tag, "class") is None
