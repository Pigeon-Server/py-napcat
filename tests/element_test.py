from py_napcat import Element


def test_element_parser():
    data = {"type": "text", "data": {"text": "test_data"}}
    print(Element.parse_element(data))
