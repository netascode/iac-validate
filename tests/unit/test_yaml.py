import pytest

from iac_validate import yaml

pytestmark = pytest.mark.unit


def test_merge_dict():
    # merge dicts
    destination = {"e1": "abc"}
    source = {"e2": "def"}
    result = {"e1": "abc", "e2": "def"}
    yaml.merge_dict(source, destination)
    assert destination == result
    # merge nested dicts
    destination = {"root": {"child1": "abc"}}
    source = {"root": {"child2": "def"}}
    result = {"root": {"child1": "abc", "child2": "def"}}
    yaml.merge_dict(source, destination)
    assert destination == result
    # make sure that the code doesn't hang when merging lists of lists
    source = {
        "switch_link_aggregations": [
            {
                "switch_ports": [
                    {"port_id": "7", "serial": "asd"},
                    {"port_id": "8", "serial": "qwe"},
                ]
            }
        ]
    }
    destination = {}
    yaml.merge_dict(source, destination)
    assert destination == source
    # make sure that merge_dict will not remove duplicate entries
    source = {"root": {"duplicates": [{"name": "abc"}, {"name": "abc"}]}}
    destination = {}
    yaml.merge_dict(source, destination)
    assert destination == source


def test_merge_list_item():
    # merge primitive list items
    destination = ["abc", "def"]
    source_item = "ghi"
    result = ["abc", "def", "ghi"]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # merge matching primitive list items
    destination = ["abc", "def"]
    source_item = "abc"
    result = ["abc", "def"]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # merge matching primitive list items
    destination = ["abc", "def"]
    source_item = "abc"
    result = ["abc", "def"]
    yaml.merge_list_item(source_item, destination, False)
    assert destination == result
    # merge matching dict list items
    destination = [{"name": "abc", "map": {"elem1": "value1", "elem2": "value2"}}]
    source_item = {"name": "abc", "map": {"elem3": "value3"}}
    result = [
        {
            "name": "abc",
            "map": {"elem1": "value1", "elem2": "value2", "elem3": "value3"},
        }
    ]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # append matching dict list items
    destination = [{"name": "abc", "map": {"elem1": "value1", "elem2": "value2"}}]
    source_item = {"name": "abc", "map": {"elem3": "value3"}}
    result = [
        {
            "name": "abc",
            "map": {"elem1": "value1", "elem2": "value2"},
        },
        {
            "name": "abc",
            "map": {"elem3": "value3"},
        },
    ]
    yaml.merge_list_item(source_item, destination, False)
    assert destination == result
    # merge matching dict list items with extra src primitive attribute
    destination = [{"name": "abc", "map": {"elem1": "value1", "elem2": "value2"}}]
    source_item = {"name": "abc", "name2": "def", "map": {"elem3": "value3"}}
    result = [
        {
            "name": "abc",
            "name2": "def",
            "map": {"elem1": "value1", "elem2": "value2", "elem3": "value3"},
        }
    ]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # merge matching dict list items with extra dst primitive attribute
    destination = [
        {"name": "abc", "name2": "def", "map": {"elem1": "value1", "elem2": "value2"}}
    ]
    source_item = {"name": "abc", "map": {"elem3": "value3"}}
    result = [
        {
            "name": "abc",
            "name2": "def",
            "map": {"elem1": "value1", "elem2": "value2", "elem3": "value3"},
        }
    ]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # merge matching dict list items with extra dst and src primitive attribute
    destination = [{"name": "abc", "name2": "def"}]
    source_item = {"name": "abc", "name3": "ghi"}
    result = [{"name": "abc", "name2": "def", "name3": "ghi"}]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
