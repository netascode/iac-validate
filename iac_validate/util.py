# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

from typing import Any, Dict, List


def merge_list_item(
    source_item: Any, destination: List[Any], deep_merge: bool = True
) -> None:
    """Merge item into list."""
    if isinstance(source_item, dict) and deep_merge:
        # check if we have an item in destination with matching primitives
        for dest_item in destination:
            match = True
            comparison = False
            for k, v in source_item.items():
                if isinstance(v, dict) or isinstance(v, list):
                    continue
                elif k in dest_item and v == dest_item[k]:
                    comparison = True
                    continue
                else:
                    comparison = True
                    match = False
            if comparison and match:
                merge_dict_list(source_item, dest_item)
                return
    elif source_item in destination:
        return
    destination.append(source_item)


def merge_dict_list(
    source: Dict[Any, Any], destination: Dict[Any, Any], deep_merge_list: bool = True
) -> Dict[Any, Any]:
    """Merge two nested dict/list structures."""
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dict_list(value, node)
        elif isinstance(value, list):
            if key not in destination:
                destination[key] = value
            if isinstance(destination[key], list):
                for i in value:
                    merge_list_item(i, destination[key], deep_merge_list)
        else:
            destination[key] = value
    return destination
