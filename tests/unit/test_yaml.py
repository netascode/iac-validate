import pytest

from iac_validate import yaml

pytestmark = pytest.mark.unit


def test_compare_dict():
    destination = {"e1": "abc"}
    source = {"e2": "def"}
    assert yaml.compare_dict(source, destination)
    destination = {"e1": "abc"}
    source = {"e1": "def"}
    assert not yaml.compare_dict(source, destination)
    destination = {"e1": "abc", "e2": "def"}
    source = {"e1": "abc", "e3": "ghi"}
    assert yaml.compare_dict(source, destination)


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
    # deduplicate list items in source
    source = {"list1": [{"name": "1", "list2": [{"name": "1"}, {"name": "1"}]}]}
    destination = {}
    result = {"list1": [{"name": "1", "list2": [{"name": "1"}]}]}
    yaml.merge_dict(source, destination)
    print(destination)
    assert destination == result
    # deduplicate list items in destination
    destination = {"list1": [{"name": "1", "list2": [{"name": "1"}, {"name": "1"}]}]}
    source = {}
    result = {"list1": [{"name": "1", "list2": [{"name": "1"}]}]}
    yaml.merge_dict(source, destination)
    print(destination)
    assert destination == result


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
    # not merge list items with completely different dict attributes
    destination = [{"name": "abc"}]
    source_item = {"name2": "def"}
    result = [{"name": "abc"}, {"name2": "def"}]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
    # not merge list items with different nested dict attributes
    destination = [{"name": "abc", "map": {"elem1": "value1"}}]
    source_item = {"name": "abc", "map": {"elem1": "value2"}}
    result = [
        {"name": "abc", "map": {"elem1": "value1"}},
        {"name": "abc", "map": {"elem1": "value2"}},
    ]
    yaml.merge_list_item(source_item, destination)
    assert destination == result
